import base64
import inspect
import io
import logging
import os
import time
from abc import ABC, abstractmethod
from PIL import Image
from pydantic import BaseModel
from tenacity import retry, stop_after_attempt, wait_random_exponential, retry_if_exception_type, before_log, after_log
from typing import Any, Dict, List, Tuple, Optional, Type, Union, Callable, get_type_hints, get_args, get_origin
from ..config import get_config
from ..model_registry import get_registry
from ..tracer import get_global_tracer
from ..types import ExecutionEvent
from ..utils import ensure_no_additional_props, type_to_json_schema, resolve_expected_type

logger = logging.getLogger(__name__)

class FunctionCallConverter:
    @staticmethod
    def convert_argument(value: Any, expected_type: Type) -> Any:
        if value is None:
            return None
        origin = get_origin(expected_type)
        if origin is Union:
            args = get_args(expected_type)
            if type(None) in args:
                expected_type = next(t for t in args if t is not type(None))
        if origin is list or origin is List:
            if isinstance(value, str):
                try:
                    import ast
                    value = ast.literal_eval(value)
                except (ValueError, SyntaxError):
                    try:
                        import json
                        value = json.loads(value)
                    except json.JSONDecodeError:
                        raise ValueError(f"Cannot convert string '{value}' to list")
            if not isinstance(value, list):
                raise TypeError(f"Expected list but got {type(value)}")
            item_type = get_args(expected_type)[0]
            return [FunctionCallConverter.convert_argument(item, item_type) for item in value]
        if isinstance(expected_type, type) and issubclass(expected_type, BaseModel):
            if isinstance(value, dict):
                return expected_type(**value)
            elif isinstance(value, str):
                try:
                    import json
                    return expected_type(**json.loads(value))
                except json.JSONDecodeError:
                    raise ValueError(f"Cannot convert string '{value}' to {expected_type}")
            elif isinstance(value, expected_type):
                return value
            else:
                raise TypeError(f"Cannot convert {type(value)} to {expected_type}")
        if expected_type in (str, int, float, bool):
            try:
                if isinstance(value, str) and expected_type is not str:
                    value = value.strip()
                    if expected_type is bool:
                        return value.lower() in ('true', '1', 'yes', 'y', 'on')
                return expected_type(value)
            except (ValueError, TypeError):
                raise TypeError(f"Cannot convert {value} ({type(value)}) to {expected_type}")
        return value

    @staticmethod
    def convert_result(result: Any, return_type: Type) -> Any:
        if result is None:
            return None
        origin = get_origin(return_type)
        if origin is Union:
            args = get_args(return_type)
            if type(None) in args:
                return_type = next(t for t in args if t is not type(None))
        if origin is list or origin is List:
            if not isinstance(result, list):
                raise TypeError(f"Expected list return type but got {type(result)}")
            item_type = get_args(return_type)[0]
            converted = [FunctionCallConverter.convert_result(item, item_type) for item in result]
            return converted
        if isinstance(return_type, type) and issubclass(return_type, BaseModel):
            if isinstance(result, dict):
                return return_type(**result).model_dump()
            elif isinstance(result, return_type):
                return result.model_dump()
            else:
                raise TypeError(f"Cannot convert return value {type(result)} to {return_type}")
        if return_type in (str, int, float, bool):
            try:
                return return_type(result)
            except (ValueError, TypeError):
                raise TypeError(f"Cannot convert return value {result} to {return_type}")
        return result

class FunctionSpec:
    def __init__(self, name: str, func: Callable, schema: Optional[Dict[str, Any]], type_hints: Dict[str, Any], strict: bool):
        self.name = name
        self.func = func
        self.schema = schema
        self.type_hints = type_hints
        self.strict = strict

class BaseProvider(ABC):
    def __init__(self, model_id: str):
        self.model_id = model_id
        parts = model_id.split('/', 1)
        self.deployment_id = parts[0]
        self.registry = get_registry()
        self.model_config = self.registry.get_model(model_id)
        
        # Get configuration from either deployments or providers section
        config = get_config().get_config_dict()
        
        # First check deployments section (new approach)
        if "deployments" in config and self.deployment_id in config["deployments"]:
            self.deployment_config = config["deployments"][self.deployment_id]
            self.provider_id = self.deployment_config.get("provider")
            
            # Check if the provider exists in the provider mapping
            if not self.provider_id:
                raise ValueError(f"Deployment '{self.deployment_id}' missing required 'provider' parameter")
        else:
            # Legacy mode - deployment_id is treated as provider_id
            self.provider_id = self.deployment_id
            self.deployment_config = None
        
        # Get provider configuration (for backward compatibility)
        if "providers" in config and self.provider_id in config["providers"]:
            self.provider_config = config["providers"][self.provider_id]
        else:
            # If no provider config found, use deployment config
            self.provider_config = self.deployment_config or {}
        
        # Runtime configuration overrides
        self._config_overrides = {}
        self.function_registry: Dict[str, FunctionSpec] = {}
        self.tracer = get_global_tracer()
        
    def update_config(self, config_overrides: Dict[str, Any]) -> None:
        """
        Update the provider's configuration with runtime values.
        Called by gen() function with values from decorator or parameter overrides.
        """
        for key, value in config_overrides.items():
            if value is not None:
                self._config_overrides[key] = value
    
    def get_config_value(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value, checking runtime overrides first,
        then deployment config, then provider config.
        
        Args:
            key: The configuration key to look up
            default: Default value if not found
            
        Returns:
            The configuration value or default
        """
        # Check runtime overrides first
        if hasattr(self, '_config_overrides') and self._config_overrides:
            # Check for the exact key
            if key in self._config_overrides:
                return self._config_overrides[key]
        
        # Then check deployment config
        if self.deployment_config and key in self.deployment_config:
            value = self.deployment_config[key]
            # If it looks like an environment variable reference, resolve it
            if isinstance(value, str) and not (value.startswith('http://') or value.startswith('https://')):
                env_value = os.environ.get(value)
                if env_value:
                    return env_value
            return value
        
        # Then check model config for Azure-specific values (backward compatibility)
        if key in ["api_version", "deployment_name"] and hasattr(self.model_config, 'azure'):
            azure_mapping = {
                "api_version": "openai_api_version",
                "deployment_name": "azure_deployment"
            }
            
            if key in azure_mapping and hasattr(self.model_config.azure, azure_mapping[key]):
                azure_key = getattr(self.model_config.azure, azure_mapping[key])
                env_value = os.environ.get(azure_key)
                if env_value:
                    return env_value
        
        # Finally check provider config
        if hasattr(self.provider_config, key):
            value = getattr(self.provider_config, key)
            # If it looks like an environment variable reference, resolve it
            if isinstance(value, str) and not (value.startswith('http://') or value.startswith('https://')):
                env_value = os.environ.get(value)
                if env_value:
                    return env_value
            return value
        elif isinstance(self.provider_config, dict) and key in self.provider_config:
            value = self.provider_config[key]
            # If it looks like an environment variable reference, resolve it
            if isinstance(value, str) and not (value.startswith('http://') or value.startswith('https://')):
                env_value = os.environ.get(value)
                if env_value:
                    return env_value
            return value
        
        return default
    
    def _is_pydantic(self, type_hint: Any) -> bool:
        if type_hint is None:
            return False
        origin = get_origin(type_hint)
        if origin is Union:
            args = get_args(type_hint)
            type_hint = next(t for t in args if t is not type(None))
        return isinstance(type_hint, type) and issubclass(type_hint, BaseModel)

    def _check_primitive_short_circuit(self, value: Any, expected_type: Type) -> Optional[Any]:
        if value is None:
            return None
            
        expected_type = resolve_expected_type(expected_type)
        if expected_type is str:
            return None
            
        origin = get_origin(expected_type)
        if origin is Union:
            args = get_args(expected_type)
            if type(None) in args:
                expected_type = next(t for t in args if t is not type(None))
                
        if expected_type in (int, float, bool):
            try:
                if isinstance(value, str):
                    value = value.strip()
                    if expected_type is bool:
                        return value.lower() in ('true', '1', 'yes', 'y', 'on')
                return expected_type(value)
            except (ValueError, TypeError):
                return None
                
        if origin in (list, List):
            if not isinstance(value, list):
                return None
            item_type = get_args(expected_type)[0]
            if item_type in (int, float, bool):
                try:
                    return [self._check_primitive_short_circuit(item, item_type) for item in value]
                except (ValueError, TypeError):
                    return None
                    
        return None

    def iterative_function_call_loop(
        self,
        conversation: List[Dict[str, Any]],
        initial_response: Any,
        max_calls: int,
        extract_tool_calls_cb: Callable[[Any], List[Any]],
        handle_single_tool_call_cb: Callable[[Any, int, int], Any],
        update_conversation_with_tool_result_cb: Callable[[Any, Any, List[Dict[str, Any]]], None],
        check_done_or_reason_cb: Callable[[Any, Any, List[Dict[str, Any]]], Optional[Any]],
        re_invoke_api_cb: Callable[[List[Dict[str, Any]]], Any],
        response_format: Optional[Type[BaseModel]] = None,
        expected_return: Optional[Type] = None,
    ) -> List[Dict[str, Any]]:
        response = initial_response
        function_call_count = 0
        last_result = None
        max_calls = int(max_calls) if max_calls is not None else 10
        
        # Get parallel_calls flag from config_overrides
        parallel_calls = self._config_overrides.get('parallel_calls', False)

        while function_call_count < max_calls:
            tool_calls = extract_tool_calls_cb(response)
            
            if not tool_calls:
                maybe_done = check_done_or_reason_cb(response, last_result, conversation)
                if maybe_done is not None:
                    return maybe_done
                
                function_call_count += 1 # always increment otherwise we'll be stuck in an infinite loop
                response = re_invoke_api_cb(conversation)
                continue
            
            # Modified to handle parallel calls when enabled
            if parallel_calls:
                # Execute all tool calls from this response
                for tool_call in tool_calls:
                    function_call_count += 1
                    if function_call_count > max_calls:
                        raise RuntimeError(f"Function calls exceeded maximum of {max_calls}")
                    
                    result = handle_single_tool_call_cb(tool_call, function_call_count, max_calls)
                    update_conversation_with_tool_result_cb(tool_call, result, conversation)
                    last_result = result  # Update last_result with each result
            else:
                # Original behavior - execute only the first tool call
                first_call = tool_calls[0]
                function_call_count += 1
                if function_call_count > max_calls:
                    raise RuntimeError(f"Function calls exceeded maximum of {max_calls}")
                    
                last_result = handle_single_tool_call_cb(first_call, function_call_count, max_calls)
                update_conversation_with_tool_result_cb(first_call, last_result, conversation)
            
            # Get next response
            response = re_invoke_api_cb(conversation)
            
            maybe_done = check_done_or_reason_cb(response, last_result, conversation)
            if maybe_done is not None:
                return maybe_done
        
        raise RuntimeError(f"Function calls exceeded maximum of {max_calls}")

    @property
    def sub_model_id(self) -> str:
        parts = self.model_id.split('/', 1)
        if len(parts) < 2:
            raise ValueError(f"Invalid model ID format '{self.model_id}'. Must be provider/... at minimum.")
        return parts[1]

    def register_function(self, name: str, func: Callable) -> None:
        """
        Register a function for use in function calling.
        
        Args:
            name: Name of the function
            func: The callable function
            
        Notes:
            Functions with names starting with underscore (_) are considered private
            and will not be exposed to the language model, but they will still be 
            registered for execution to support recursive function calls.
        """
        type_hints = get_type_hints(func)
        
        sig = inspect.signature(func)
        if not sig.parameters:
            raise ValueError(
                f"Function '{name}' must have at least one parameter. "
                "LLM function calling requires functions to accept parameters to be useful. "
                "If your function doesn't need parameters, consider adding a dummy parameter or "
                "restructuring your code to use parameters meaningfully."
            )
        
        # Always create a schema, but for private functions (starting with _), 
        # we'll set it to None when exposing to the model
        from ..schema_builder import build_function_schema, NotSupportedError
        try:
            # For private functions, we still create a schema but won't expose it
            is_private = name.startswith('_')
            schema = None
            
            # Only create a schema for non-private functions
            if not is_private:
                schema = build_function_schema(
                    func, 
                    provider_capabilities={"allow_lists": True}, 
                    strict=True, 
                    format="default"
                )
            
            # Log whether we're registering a private or public function
            if is_private:
                logger.debug(f"Registering private function (not exposed to LLM): {name}")
            else:
                logger.debug(f"Registering public function (exposed to LLM): {name}")
                
            # Register the function regardless of privacy for execution
            self.function_registry[name] = FunctionSpec(name, func, schema, type_hints, strict=True)
            
        except NotSupportedError as e:
            logger.warning(f"Skipping function {func.__name__}: {e}")

    def execute_function(self, name: str, arguments: Dict[str, Any]) -> Any:
        if name not in self.function_registry:
            raise ValueError(f"Unknown function: {name}")
        spec = self.function_registry[name]
        tracer = get_global_tracer()
        context = {"nested_function_name": name, "raw_arguments": arguments, "decorator_type": "nested_function", "model_id": self.model_id}
        event = tracer.start_event(spec.func, context)
        start_time = time.time()
        try:
            converted_args = {}
            for param_name, value in arguments.items():
                expected_type = spec.type_hints.get(param_name, Any)
                converted_args[param_name] = FunctionCallConverter.convert_argument(value, expected_type)
                event.add_metadata(f"param_{param_name}_type", str(expected_type))
                event.add_metadata(f"param_{param_name}_raw", str(value))
                event.add_metadata(f"param_{param_name}_converted", str(converted_args[param_name]))
            logger.debug(f"Executing function {name} with arguments: {converted_args}\n")
            result = spec.func(**converted_args)
            return_type = spec.type_hints.get('return', Any)
            converted_result = FunctionCallConverter.convert_result(result, return_type)
            event.add_metadata("return_type", str(return_type))
            event.add_metadata("raw_result", str(result))
            event.add_metadata("converted_result", str(converted_result))
            logger.debug(f"Function {name} executed successfully\nArguments: {arguments}\nConverted args: {converted_args}\nRaw result: {result}\nConverted result: {converted_result}")
            tracer.end_event(event, start_time, result=converted_result)
            return converted_result
        except Exception as e:
            error = f"Unexpected error in execute_function: {str(e)}"
            tracer.end_event(event, start_time, error=error)
            raise

    def _get_retry_config(self) -> Dict[str, Any]:
        """
        Get retry configuration from provider config and runtime overrides.
        
        Returns:
            Dictionary with retry configuration parameters
        """
        # Default retry settings
        defaults = {
            "wait_multiplier": 2.0,    # Base multiplier for exponential backoff
            "wait_min": 1,             # Minimum wait time in seconds
            "wait_max": 60,            # Maximum wait time in seconds
            "max_attempts": 5,         # Maximum number of retry attempts
            "jitter_factor": 0.1       # Add some jitter to avoid thundering herd
        }
        
        # Check if provider config has retry settings
        provider_retry = {}
        if isinstance(self.provider_config, dict) and "retry" in self.provider_config:
            provider_retry = self.provider_config["retry"]
        
        # Apply provider retry settings if available
        for key in defaults.keys():
            if key in provider_retry:
                defaults[key] = provider_retry[key]
        
        # Apply runtime retry settings if available (highest priority)
        runtime_retry = self._config_overrides.get("retry", {})
        if runtime_retry:
            for key in defaults.keys():
                if key in runtime_retry:
                    defaults[key] = runtime_retry[key]
        
        return defaults

    def _create_retry_decorator(self, exception_types: Tuple[Type[Exception], ...]):
        """
        Create a retry decorator using provider's retry configuration.
        
        Args:
            exception_types: Tuple of exception types that should trigger retries
            
        Returns:
            A configured retry decorator for the specified exceptions
        """
        config = self._get_retry_config()
        
        return retry(
            retry=retry_if_exception_type(exception_types),
            wait=wait_random_exponential(
                multiplier=config["wait_multiplier"], 
                min=config["wait_min"], 
                max=config["wait_max"]
            ),
            stop=stop_after_attempt(config["max_attempts"]),
            before=before_log(logger, logging.DEBUG),
            after=after_log(logger, logging.DEBUG)
        )

    def get_timeout(self) -> int:
        """
        Get the timeout value from provider config or runtime overrides.
        
        Returns:
            Timeout value in seconds
        """
        # Check runtime overrides first (highest priority)
        if "timeout" in self._config_overrides:
            return self._config_overrides["timeout"]
        
        # Then check provider config
        if isinstance(self.provider_config, dict) and "timeout" in self.provider_config:
            return self.provider_config["timeout"]
        
        # Default timeout if not specified
        return 300

    def _get_image_type(self, image_bytes: bytes) -> str:
        try:
            with Image.open(io.BytesIO(image_bytes)) as img:
                if img.format not in ['PNG', 'JPEG']:
                    raise ValueError(f"Unsupported image format: {img.format}")
                return f"image/{img.format.lower()}"
        except Exception as e:
            logger.error(f"Failed to determine image type: {e}")
            raise

    def _encode_image_base64(self, image_bytes: bytes, image_format: str) -> str:
        base64_str = base64.b64encode(image_bytes).decode('utf-8')
        return f"data:image/{image_format};base64,{base64_str}"

    def _normalize_messages(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        normalized = []
        for msg in messages:
            role = msg.get("role")
            role_str = role.value if hasattr(role, "value") else str(role)
            content = msg.get("content", msg.get("value", ""))
            new_msg = {"role": role_str, "content": content}
            if "tool_calls" in msg:
                new_msg["tool_calls"] = msg["tool_calls"]
            if "tool_call_id" in msg:
                new_msg["tool_call_id"] = msg["tool_call_id"]
            normalized.append(new_msg)
        return normalized

    def _format_images_for_message(self, messages: List[Dict[str, Any]], images: Optional[List[Dict[str, Any]]], image_formatter: Callable[[Dict[str, Any]], Dict[str, Any]]) -> List[Dict[str, Any]]:
        if not images:
            return self._normalize_messages(messages)
        normalized = self._normalize_messages(messages)
        for msg in normalized:
            if msg["role"].lower() == "user":
                if isinstance(msg["content"], str):
                    msg["content"] = [{"type": "text", "text": msg["content"]}]
                for img in images:
                    img_block = image_formatter(img)
                    msg["content"].append(img_block)
                break
        return normalized

    def _build_function_schema(self, func: Callable, provider_capabilities: Dict[str, Any], schema_format: str, strict: bool = True) -> Optional[Dict[str, Any]]:
        if func.__name__.startswith('_'):
            return None
        from ..schema_builder import build_function_schema, NotSupportedError
        try:
            return build_function_schema(func, provider_capabilities=provider_capabilities, strict=strict, format=schema_format)
        except NotSupportedError as e:
            logger.warning(f"Skipping function {func.__name__}: {e}")
            return None

    def _handle_tool_call_common(self, tool_name: str, args: Dict[str, Any],
                                call_count: int, max_calls: int) -> Any:
        if call_count > max_calls:
            raise RuntimeError(f"Function calls exceeded maximum of {max_calls} for {self.model_id}")
        logger.debug(f"Executing tool: {tool_name} with args: {args}")
        
        # Unwrap data objects from args if present
        unwrapped_args = {}
        for key, value in args.items():
            if isinstance(value, dict) and "data" in value:
                unwrapped_args[key] = value["data"]
            else:
                unwrapped_args[key] = value
                
        result = self.execute_function(tool_name, unwrapped_args)
        logger.debug(f"Result from tool {tool_name}: {result}")
        return result

    def _handle_tool_call(self, raw_tool_data: Any, call_count: int, max_calls: int,
                        arg_parser: Optional[Callable[[Any], Tuple[str, Dict[str, Any]]]] = None) -> Any:
        if arg_parser:
            tool_name, args = arg_parser(raw_tool_data)
        else:
            tool_name = raw_tool_data.get("name")
            args = raw_tool_data.get("arguments", {})
        return self._handle_tool_call_common(tool_name, args, call_count, max_calls)

    def _get_json_schema(self, type_hint: Optional[Type]) -> Optional[Dict[str, Any]]:
        if type_hint is None:
            return None
        return ensure_no_additional_props(type_to_json_schema(type_hint))

    @abstractmethod
    def _invoke_provider_api(self, params: Dict[str, Any]) -> Any:
        """
        Implement the API call for the specific provider.
        This is the single entry point for all API calls and should:
        1. Handle authentication and client creation
        2. Apply appropriate retry logic using _create_llm_retry_decorator
        3. Make the actual API call
        4. Handle basic error processing
        5. Return the raw provider response
        
        This method must be implemented by all provider subclasses.
        
        Args:
            params: Dictionary containing all parameters needed for the API call
            
        Returns:
            The raw response from the provider API
        """
        pass

    @abstractmethod 
    def _create_llm_retry_decorator(self, func):
        """
        Creates a retry decorator for the specific provider.
        Must be implemented by each provider to handle provider-specific exceptions.
        
        Args:
            func: The function to be decorated with retry logic
            
        Returns:
            The decorated function with provider-specific retry logic
        """
        pass

    def update_token_usage(self, event: "ExecutionEvent", response: Any) -> None:
        """
        Update the event with token usage information from the provider response.
        Each provider should override this method to handle its specific token counting logic.

        Args:
            event: The ExecutionEvent to update
            response: The provider response containing token information
        """
        # Base implementation does nothing - subclasses should override
        pass
    
    def _create_function_schema(self, func: Callable) -> Optional[Dict[str, Any]]:
        """Create a function schema for the given function."""
        # Skip functions with leading underscore - they are considered private
        if func.__name__.startswith('_'):
            return None
        return self._build_function_schema(func, provider_capabilities={"allow_lists": True}, schema_format="default", strict=True)

    def call_model_with_metadata(
        self,
        messages: List[Dict[str, Any]], 
        images: Optional[List[Dict[str, Any]]] = None,
        response_format: Optional[Type[BaseModel]] = None,
        functions: Optional[List[Dict[str, Any]]] = None,
        expected_return: Optional[Type] = None,
        config_overrides: Optional[Dict[str, Any]] = None
    ) -> Tuple[Any, Any]:
        """
        Call the model and collect metadata about the request and response.
        
        Args:
            messages: List of message objects
            images: Optional list of image objects
            response_format: Optional expected response format
            functions: Optional list of function definitions
            expected_return: Optional expected return type
            config_overrides: Optional configuration overrides
            
        Returns:
            Tuple containing (processed_result, raw_response)
        """
        raw_response = None
        start_time = time.time()
        
        prompt_text = ""
        if messages and isinstance(messages, list):
            for msg in messages:
                if isinstance(msg, dict) and msg.get("role") == "user" and "content" in msg:
                    prompt_text = msg["content"]
                    break
        
        metadata_context = {
            "prompt_text": prompt_text,
            "start_time": start_time
        }
        
        original_invoke_provider_api = self._invoke_provider_api
        
        def wrapped_invoke_provider_api(params: Dict[str, Any]) -> Any:
            nonlocal raw_response
            try:
                response = original_invoke_provider_api(params)
                raw_response = response
                return response
            except Exception as e:
                logger.error(f"Error in provider API call: {e}")
                raw_response = {"error": str(e)}
                raise
        
        self._invoke_provider_api = wrapped_invoke_provider_api
        
        try:
            result = self.call_model(
                messages=messages,
                images=images,
                response_format=response_format,
                functions=functions,
                expected_return=expected_return,
                config_overrides=config_overrides
            )
            
            if (hasattr(self, '_client') and self._client and 
                isinstance(self, type) and self.__module__.endswith('gemini')):
                
                metadata_context["gemini_client"] = self._client
                metadata_context["result"] = result
            
            return result, raw_response
        finally:
            self._invoke_provider_api = original_invoke_provider_api

    @abstractmethod
    def call_model(
        self,
        messages: List[Dict[str, Any]], 
        images: Optional[List[Dict[str, Any]]] = None,
        response_format: Optional[Type[BaseModel]] = None,
        functions: Optional[List[Dict[str, Any]]] = None,
        expected_return: Optional[Type] = None,
        config_overrides: Optional[Dict[str, Any]] = None
    ) -> Any:
        """
        Call the model and process the response.
        Must be implemented by each provider to handle provider-specific
        request formatting and response processing.
        
        This method should use _invoke_provider_api as the single entry point
        for making API calls to ensure consistent retry behavior.
        
        Args:
            messages: List of message objects 
            images: Optional list of image objects
            response_format: Optional expected response format
            functions: Optional list of function definitions
            expected_return: Optional expected return type
            config_overrides: Optional configuration overrides
            
        Returns:
            Processed response from the provider
        """
        raise NotImplementedError()