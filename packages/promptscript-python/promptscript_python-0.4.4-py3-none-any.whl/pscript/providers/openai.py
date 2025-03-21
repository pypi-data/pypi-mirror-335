import json
import logging
import os
import time
from openai import RateLimitError, APIConnectionError, OpenAI, AzureOpenAI
from pydantic import BaseModel
from typing import Optional, Type, List, Dict, Any, Tuple, Union, get_origin
from .base import BaseProvider, FunctionCallConverter
from ..config import get_config
from ..log_config import format_object
from ..types import ExecutionEvent
from ..utils import validate_type, safe_serialize

logger = logging.getLogger(__name__)

class OpenAIProvider(BaseProvider):
    def __init__(self, model_id: str):
        super().__init__(model_id)
        self.config = get_config()
        self._current_tools = None
        self._expected_return = None
        
    def _get_client(self) -> Union[OpenAI, AzureOpenAI]:
        api_key = os.environ.get(self.provider_config["auth_env_var"])
        if not api_key:
            raise ValueError(f"{self.provider_config['auth_env_var']} environment variable is not set")
        
        # Use the enhanced timeout getter
        timeout = self.get_timeout()
        
        return OpenAI(
            api_key=api_key, 
            base_url=self.provider_config["base_url"], 
            timeout=timeout
        )

    def _create_llm_retry_decorator(self, func):
        """
        Creates a retry decorator for OpenAI API calls,
        handling rate limits and connection errors.
        """
        return self._create_retry_decorator((RateLimitError, APIConnectionError))(func)

    def _invoke_provider_api(self, params: Dict[str, Any]) -> Any:
        """
        Single entry point for OpenAI API calls with retry logic.
        """
        @self._create_llm_retry_decorator
        def _call_openai_api(params: Dict[str, Any]):
            logger.debug(f"Calling OpenAI API with params: {format_object(params)}")
            client = self._get_client()
            response = client.chat.completions.create(**params)
            logger.debug(f"Received OpenAI response: {format_object(response)}")
            
            if getattr(response, "error", None) is not None:
                error_code = response.error.get("code", "Unknown")
                if str(error_code) == "429":
                    raise RateLimitError(response.error["message"])
                raise ValueError(f"OpenAI error: {response.error}")
                
            return response
            
        return _call_openai_api(params)

    def _unpack_openai_response(self, response: Any) -> Any:
        if not hasattr(response, "choices") or response.choices is None or not isinstance(response.choices, list) or len(response.choices) == 0:
            error = getattr(response, "error", None)
            if error is not None:
                raise RuntimeError(f"Provider returned error: {error}")
            raise ValueError("Provider response missing choices")
        return response.choices[0].message

    def _extract_openai_tool_calls(self, response: Any) -> List[Any]:
        if response.choices is not None and len(response.choices) > 0:
            choice = response.choices[0]
            if choice.finish_reason == "tool_calls" and choice.message is not None:
                return choice.message.tool_calls
        return []

    def _handle_openai_single_tool_call(self, tool_call: Any, call_count: int, max_calls: int) -> Any:
        try:
            args = json.loads(tool_call.function.arguments)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid function arguments: {e}")
        return self._handle_tool_call_common(tool_call.function.name, args, call_count, max_calls)

    def _update_openai_conversation_with_tool_result(self, tool_call: Any, result: Any, conversation: List[Dict[str, Any]]):
        conversation.append({
            "role": "assistant",
            "content": "",
            "tool_calls": [tool_call]
        })
        conversation.append({
            "role": "tool",
            "content": json.dumps({"result": result if isinstance(result, (list, dict)) else str(result)}),
            "tool_call_id": tool_call.id
        })

    def _check_openai_done_or_reason(self, response: Any, last_result: Any, conversation: List[Dict[str, Any]]) -> Optional[Any]:
        if response is None:
            maybe_short = self._check_primitive_short_circuit(last_result, self._expected_return)
            if maybe_short is not None:
                return maybe_short
            return None

        if not hasattr(response, 'choices') or not response.choices:
            return None
            
        choice = response.choices[0]
        if choice.finish_reason == "stop":
            if self._expected_return is str or self._expected_return is None:
                return choice.message.content

            maybe_short = self._check_primitive_short_circuit(last_result, self._expected_return)
            if maybe_short is not None:
                return maybe_short

            if self._is_pydantic(self._expected_return):
                logger.debug(f"Making final structured call for pydantic type {self._expected_return}")
                return self._finalize_openai_pydantic(conversation, last_result)

            return self._convert_function_result(last_result, choice.message.content, self._expected_return)
        return None

    def _finalize_openai_pydantic(self, conversation: List[Dict[str, Any]], last_result: Any) -> Any:
        if isinstance(last_result, self._expected_return):
            return last_result

        final_params = self._prepare_completion_params(
            conversation,
            float(self.model_config.parameters.temperature_range[0]),
            self.model_config.parameters.max_tokens_range[1],
            functions=None,
            response_format=self._expected_return
        )

        response = self._invoke_provider_api(final_params)
        message = self._unpack_openai_response(response)

        if hasattr(message, "parsed") and message.parsed is not None:
            logger.debug(f"Using auto-parsed response: {message.parsed}")
            if isinstance(message.parsed, dict):
                return self._expected_return(**message.parsed)
            return message.parsed

        content = message.content.strip()
        if not content:
            raise ValueError("Expected a final JSON response, but got empty content")

        try:
            data = json.loads(content)
            return self._expected_return(**data)
        except (json.JSONDecodeError, TypeError) as e:
            logger.error(f"Failed to parse final response: {e}")
            raise ValueError(f"Could not parse response as {self._expected_return.__name__}: {str(e)}")

    def _re_invoke_openai(self, conversation: List[Dict[str, Any]]) -> Any:
        params = self._prepare_completion_params(
            conversation,
            float(self.model_config.parameters.temperature_range[0]),
            self.model_config.parameters.max_tokens_range[1],
            self._current_tools,
            None
        )
        return self._invoke_provider_api(params)

    def _format_messages_with_images(self, messages: List[Dict[str, Any]], images: Optional[List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
        def image_formatter(img):
            return self._build_image_url_block(img)
        return self._format_images_for_message(messages, images, image_formatter)

    def _build_image_url_block(self, img: Dict[str, Any]) -> Dict[str, Any]:
        image_format = self._get_image_type(img["data"])
        mime_types = img.get("mime_types", [])
        if image_format not in mime_types:
            raise ValueError(f"Image format {image_format} not in supported list {mime_types}")
        base64_image = self._encode_image_base64(img["data"], image_format)
        return {"type": "image_url", "image_url": {"url": base64_image}}

    def _handle_single_tool_call(self, tool_call: Any, call_count: int, max_calls: int) -> Any:
        def arg_parser(raw):
            try:
                args = json.loads(raw.function.arguments)
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid function arguments: {e}")
            return (raw.function.name, args)
        return self._handle_tool_call(tool_call, call_count, max_calls, arg_parser)

    def _prepare_completion_params(
        self,
        messages: List[Dict[str, Any]],
        temperature: float,
        max_tokens: int,
        functions: Optional[List[Dict[str, Any]]] = None,
        response_format: Optional[Type] = None
    ) -> Dict[str, Any]:
        normalized_msgs = self._normalize_messages(messages)
        params = {
            "model": self.sub_model_id,
            "messages": normalized_msgs,
            "stream": False
        }
        
        if hasattr(self, '_config_overrides') and 'max_tokens' in self._config_overrides:
            max_tokens = self._config_overrides['max_tokens']

        is_o3_model = 'o3' in self.sub_model_id.lower()
        if not is_o3_model:
            params["temperature"] = temperature
        
        if is_o3_model:
            params["max_completion_tokens"] = max_tokens
        else:
            params["max_tokens"] = max_tokens
        
        tools = []
        if functions:
            for spec in self.function_registry.values():
                if spec.schema is not None:
                    tools.append(spec.schema)
        if tools:
            params["tools"] = tools
            params["tool_choice"] = "auto"

        if response_format:
            if response_format in (int, float, bool):
                type_name = "NumberResponse" if response_format in (int, float) else "BooleanResponse"
                params["response_format"] = {
                    "type": "json_schema",
                    "json_schema": {
                        "name": type_name,
                        "schema": {
                            "type": "object",
                            "properties": {
                                "value": {
                                    "type": "number" if response_format in (int, float) else "boolean"
                                }
                            },
                            "required": ["value"]
                        }
                    }
                }
            else:
                origin = get_origin(response_format)
                if origin in (list, List):
                    schema = self._get_json_schema(response_format)
                    if schema:
                        wrapped_schema = {
                            "type": "object",
                            "properties": {
                                "items": schema
                            },
                            "required": ["items"]
                        }
                        params["response_format"] = {
                            "type": "json_schema",
                            "json_schema": {
                                "name": getattr(response_format, "__name__", "AutoGeneratedSchema"),
                                "schema": wrapped_schema
                            }
                        }

                elif isinstance(response_format, type) and issubclass(response_format, BaseModel):
                    schema = self._get_json_schema(response_format)
                    if schema:
                        params["response_format"] = {
                            "type": "json_schema",
                            "json_schema": {
                                "name": getattr(response_format, "__name__", "AutoGeneratedSchema"),
                                "schema": schema
                            }
                        }
                        
        # Log the response format to the current event if there is one
        if hasattr(self, 'tracer') and response_format:
            current_event = self.tracer.get_current_event()
            if current_event and "response_format" in params:
                # Add response format directly to the event's top-level field
                current_event.add_response_format(safe_serialize(params["response_format"]))
        
        # Log functions to the current event if there are any
        if hasattr(self, 'tracer') and tools:
            current_event = self.tracer.get_current_event()
            if current_event:
                # Add functions directly to the event's top-level field
                current_event.add_functions(safe_serialize(tools))
                
        return params

    def _convert_function_result(self, result: Any, model_response: str, response_format: Optional[Type[BaseModel]]) -> Any:
        if result is not None and response_format is not str:
            try:
                return validate_type(result, response_format)
            except (TypeError, ValueError) as e:
                logger.debug(f"Could not convert function result directly: {e}")

        content = model_response.strip() if model_response else ""
        if not content:
            return None

        parsed = None
        try:
            parsed = json.loads(content)
            if isinstance(parsed, dict):
                if "value" in parsed and response_format in (int, float, bool):
                    return response_format(parsed["value"])
                if "items" in parsed:
                    # This is the key part: keep the 'items' wrapper for validate_type to handle
                    if get_origin(response_format) in (list, List):
                        return validate_type(parsed, response_format)
                    # Only unwrap if not a list type
                    parsed = parsed["items"]
                elif "data" in parsed:
                    parsed = parsed["data"]
        except json.JSONDecodeError:
            parsed = content

        try:
            if response_format and not get_origin(response_format) and issubclass(response_format, BaseModel) and isinstance(parsed, dict):
                return response_format(**parsed)
            return FunctionCallConverter.convert_result(parsed, response_format)
        except Exception as e:
            logger.debug(f"Failed to run FunctionCallConverter.convert_result: {e}")
            return parsed

    def update_token_usage(self, event: "ExecutionEvent", response: Any) -> None:
        if hasattr(response, 'usage'):
            usage = response.usage
            event.prompt_tokens = getattr(usage, 'prompt_tokens', None)
            event.completion_tokens = getattr(usage, 'completion_tokens', None)
            event.total_tokens = getattr(usage, 'total_tokens', None)

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
                # Store the complete parameters for logging
                metadata_context["request_params"] = params
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
            
            # Add the complete parameters to the tracer's event
            if hasattr(self, 'tracer'):
                current_event = self.tracer.get_current_event()
                if current_event and "request_params" in metadata_context:
                    # We store this in metadata since messages_to_llm is typically just the messages
                    current_event.metadata["complete_request"] = safe_serialize(metadata_context["request_params"])
                    
                    # Make sure response_format is also included
                    if "response_format" in metadata_context["request_params"]:
                        current_event.metadata["response_format"] = safe_serialize(
                            metadata_context["request_params"]["response_format"])
            
            return result, raw_response
        finally:
            self._invoke_provider_api = original_invoke_provider_api

    def call_model(
        self,
        messages: List[Dict[str, Any]],
        images: Optional[List[Dict[str, Any]]] = None,
        response_format: Optional[Any] = None,
        functions: Optional[List[Dict[str, Any]]] = None,
        expected_return: Optional[Type] = None,
        config_overrides: Optional[Dict[str, Any]] = None  
    ) -> Any:
        if expected_return and not response_format:
            response_format = expected_return
            
        try:
            normalized_msgs = self._normalize_messages(list(messages))
            formatted_msgs = self._format_messages_with_images(normalized_msgs, images)
            self._current_tools = functions
            self._expected_return = expected_return
            
            temperature = float(self.model_config.parameters.temperature_range[0])
            max_tokens = self.model_config.parameters.max_tokens_range[1]
            
            params = self._prepare_completion_params(
                formatted_msgs,
                temperature,
                max_tokens,
                functions,
                response_format
            )
            
            # Use the standardized API invocation method
            response = self._invoke_provider_api(params)
            message = self._unpack_openai_response(response)
            
            if not response.choices:
                raise ValueError("No choices returned from model")
                
            conversation = normalized_msgs.copy()

            max_calls = (
                config_overrides.get("max_function_calls") if config_overrides else None
            )
            if max_calls is not None:
                max_calls = int(max_calls)  
            else:
                max_calls = self.model_config.get_max_function_calls() or 10
            
            if functions and hasattr(message, 'tool_calls') and message.tool_calls:
                return self.iterative_function_call_loop(
                    conversation=conversation,
                    initial_response=response,
                    max_calls=max_calls,
                    extract_tool_calls_cb=self._extract_openai_tool_calls,
                    handle_single_tool_call_cb=self._handle_openai_single_tool_call,
                    update_conversation_with_tool_result_cb=self._update_openai_conversation_with_tool_result,
                    check_done_or_reason_cb=self._check_openai_done_or_reason,
                    re_invoke_api_cb=self._re_invoke_openai,
                    response_format=response_format,
                    expected_return=expected_return
                )
                
            return self._convert_function_result(None, message.content, expected_return)
                
        except Exception as e:
            logger.error(f"Error in OpenAI API call: {str(e)}")
            raise