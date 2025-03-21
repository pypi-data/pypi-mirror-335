import base64
import json
import logging
import os
import time
from anthropic import Anthropic
from pydantic import BaseModel
from tenacity import retry, stop_after_attempt, wait_random_exponential, retry_if_exception_type, before_log
from typing import Callable, Optional, Type, List, Dict, Any, get_origin, get_args
from .base import BaseProvider
from ..log_config import format_object
from ..types import ExecutionEvent
from ..utils import validate_type, try_convert_to_pydantic_model, ensure_no_additional_props, resolve_expected_type

logger = logging.getLogger(__name__)

class AnthropicServiceError(Exception):
    """Base class for Anthropic service-related errors that should trigger retries."""
    pass

class AnthropicRateLimitError(AnthropicServiceError):
    """Raised when Anthropic returns a rate limit error (429)."""
    pass

class AnthropicOverloadedError(AnthropicServiceError):
    """Raised when Anthropic returns an overloaded error (529)."""
    pass

class AnthropicMaxTokensExceededError(AnthropicServiceError):
    def __init__(self, message="Response exceeded max_tokens limit", original_response=None):
        self.original_response = original_response
        super().__init__(message)

class AnthropicProvider(BaseProvider):
    def __init__(self, model_id: str):
        super().__init__(model_id)
        self._expected_return = None
        self._current_functions = None
        self._usage_stats = {
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0
        }

    # Callback methods
    def _extract_anthropic_tool_calls(self, response: Any) -> List[Any]:
        """Extract tool calls from Anthropic response."""
        if response is None or not hasattr(response, 'stop_reason'):
            return []
        if response.stop_reason == "tool_use":
            return [b for b in response.content if getattr(b, "type", None) == "tool_use"]
        return []

    def _handle_anthropic_single_tool_call(self, tool_call: Any, call_count: int, max_calls: int) -> Any:
        """Handle Anthropic tool calls, including structured output tools."""
        if tool_call.name == "extract_values" and isinstance(tool_call.input, dict):
            # Special handling for our structured output tool
            return tool_call.input["values"]  # Return the values directly
        
        # Fall back to normal function handling for other tools
        return self._handle_tool_call_common(tool_call.name, tool_call.input, call_count, max_calls)

    def _update_anthropic_conversation_with_tool_result(self, tool_call: Any, result: Any, conversation: List[Dict[str, Any]]):
        """Update the conversation with a tool call result."""
        assistant_response = [{
            "type": "tool_use",
            "id": tool_call.id,
            "name": tool_call.name,
            "input": tool_call.input
        }]
        conversation.append({"role": "assistant", "content": assistant_response})
        
        result_str = json.dumps(result) if isinstance(result, (dict, list)) else str(result)
        tool_results = [{
            "type": "tool_result",
            "tool_use_id": tool_call.id,
            "content": result_str
        }]
        conversation.append({"role": "user", "content": tool_results})

    def _prepare_structured_tool_for_type(self, expected_type):
        """Create a structured output tool based on the expected return type."""
        if expected_type is None or expected_type is str:
            return None, None
            
        # For Pydantic models
        if isinstance(expected_type, type) and issubclass(expected_type, BaseModel):
            schema = self._anthropic_flatten_json_schema(expected_type)
            if schema:
                wrapped_schema = {
                    "type": "object",
                    "properties": {
                        "values": schema
                    },
                    "required": ["values"]
                }
                tool = {
                    "name": "extract_values",
                    "description": "Extract and structure the information as JSON. Return the structured data in the values field.",
                    "input_schema": wrapped_schema
                }
                return tool, {"type": "tool", "name": "extract_values"}
                
        # For primitive types (bool, int, float)
        elif expected_type in (bool, int, float):
            value_type = "boolean" if expected_type is bool else "number"
            tool = {
                "name": "extract_values",
                "description": f"Extract the answer as a {value_type}. Return only the value as a {value_type}, with no additional text.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "values": {"type": value_type}
                    },
                    "required": ["values"]
                }
            }
            return tool, {"type": "tool", "name": "extract_values"}
            
        # For List types
        origin = get_origin(expected_type)
        if origin in (list, List):
            item_type = get_args(expected_type)[0]
            
            # For lists of primitives
            if item_type in (int, float, bool, str):
                if item_type in (int, float):
                    value_type = "number"
                elif item_type is bool:
                    value_type = "boolean"
                else:
                    value_type = "string"
                    
                tool = {
                    "name": "extract_values",
                    "description": f"Extract all values as a list of {value_type}s. Return only the values as an array.",
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "values": {
                                "type": "array",
                                "items": {"type": value_type}
                            }
                        },
                        "required": ["values"]
                    }
                }
                return tool, {"type": "tool", "name": "extract_values"}
                
            # For lists of Pydantic models
            elif isinstance(item_type, type) and issubclass(item_type, BaseModel):
                schema = self._anthropic_flatten_json_schema(item_type)
                if schema:
                    wrapped_schema = {
                        "type": "object",
                        "properties": {
                            "values": {
                                "type": "array",
                                "items": schema
                            }
                        },
                        "required": ["values"]
                    }
                    tool = {
                        "name": "extract_values",
                        "description": "Extract a list of items and structure each as JSON. Return the structured data in the values field.",
                        "input_schema": wrapped_schema
                    }
                    return tool, {"type": "tool", "name": "extract_values"}
                    
        return None, None

    def _process_structured_response(self, response, last_result):
        """Process a structured response from the 'extract_values' tool."""
        # Check if last_result contains a structured response
        if isinstance(last_result, dict) and "values" in last_result:
            values = last_result["values"]
            
            # For boolean values, handle special cases
            if self._expected_return is bool:
                if isinstance(values, bool):
                    return values
                if isinstance(values, (str, int)):
                    if isinstance(values, str):
                        return values.lower() in ('true', 'yes', 'y', '1', 'on')
                    return bool(values)
                    
            # For other types, use standard validation
            try:
                return validate_type(values, self._expected_return)
            except (TypeError, ValueError) as e:
                logger.debug(f"Could not convert structured response: {e}")
        
        return None

    def _parse_text_response(self, text):
        """Parse a text response when a structured output was expected."""
        if not text:
            return None
            
        # For boolean responses from natural language
        if self._expected_return is bool:
            lower_text = text.lower()
            if any(word in lower_text[:20] for word in ['yes', 'true', 'correct', 'even']):
                return True
            if any(word in lower_text[:20] for word in ['no', 'false', 'incorrect', 'odd']):
                return False
                
        # Try parsing as JSON
        try:
            parsed = json.loads(text)
            
            # Check for values field in parsed JSON
            if isinstance(parsed, dict) and "values" in parsed:
                return self._process_structured_response(None, parsed)
                
            # Try direct validation
            return validate_type(parsed, self._expected_return)
        except (json.JSONDecodeError, TypeError, ValueError):
            pass
            
        # Direct conversion for primitive types
        if self._expected_return is str:
            return text
        
        try:
            from ..utils import convert_to_expected_type
            return convert_to_expected_type(text, self._expected_return)
        except Exception as e:
            logger.debug(f"Failed to parse text response: {e}")
            return None

    def _check_anthropic_done_or_reason(self, response, last_result, conversation):
        """Check if the conversation is complete and process the result."""
        if response is None:
            maybe_short = self._check_primitive_short_circuit(last_result, self._expected_return)
            if maybe_short is not None:
                return maybe_short
            return None

        # Update token usage tracking
        if hasattr(response, 'usage'):
            usage = response.usage
            self._usage_stats = {
                "prompt_tokens": getattr(usage, 'input_tokens', 0),
                "completion_tokens": getattr(usage, 'output_tokens', 0),
                "total_tokens": getattr(usage, 'input_tokens', 0) + getattr(usage, 'output_tokens', 0)
            }

        # Check response status
        if response.stop_reason == "tool_use":
            return None

        if response.stop_reason == "end_turn":
            # First try with last_result if available
            if last_result is not None:
                # Process structured response
                structured_result = self._process_structured_response(response, last_result)
                if structured_result is not None:
                    return structured_result
                
                # Try converting the whole last_result
                try:
                    return validate_type(last_result, self._expected_return)
                except (TypeError, ValueError) as e:
                    logger.debug(f"Could not convert last_result directly: {e}")
                
                # Try primitive type handling
                maybe_short = self._check_primitive_short_circuit(last_result, self._expected_return)
                if maybe_short is not None:
                    return maybe_short

            # If we couldn't get a result from last_result, try parsing the response text
            text = ""
            if response.content:
                for part in response.content:
                    if hasattr(part, 'text') and part.text:
                        text += part.text
            
            text = text.strip()
            result = self._parse_text_response(text)
            
            if result is not None:
                return result
                
            # Final fallback for Pydantic models
            if (isinstance(self._expected_return, type) and 
                issubclass(self._expected_return, BaseModel)):
                logger.debug("Attempting forced final JSON pass via _finalize_anthropic_pydantic.")
                return self._finalize_anthropic_pydantic(conversation, last_result)

        return None

    def _re_invoke_anthropic(self, conversation: List[Dict[str, Any]]) -> Any:
        """Re-invoke the Anthropic API with the updated conversation."""
        request_payload = {
            "model": self.sub_model_id,
            "messages": conversation,
            "temperature": float(self.model_config.parameters.temperature_range[0]),
            "max_tokens": self.model_config.parameters.max_tokens_range[1]
        }
        
        if hasattr(self, '_config_overrides') and 'max_tokens' in self._config_overrides:
            request_payload["max_tokens"] = self._config_overrides["max_tokens"]
        
        if hasattr(self, '_current_functions') and self._current_functions:
            transformed_tools = []
            for tool in self._current_functions:
                if tool.get("type") == "function":
                    transformed_tools.append({
                        "name": tool["function"]["name"],
                        "description": tool["function"]["description"],
                        "input_schema": tool["function"]["parameters"]
                    })
                else:
                    transformed_tools.append(tool)
            request_payload["tools"] = transformed_tools
        
        return self._invoke_provider_api(request_payload)

    def _convert_function_result(self, last_result: Any, text: str) -> Any:
        """Convert tool results or text responses to expected return type."""
        if last_result is not None:
            if isinstance(last_result, dict) and "values" in last_result:
                # Tool returned {values: [...]} - try to convert values directly
                values = last_result["values"]
                try:
                    return validate_type(values, self._expected_return)
                except (TypeError, ValueError) as e:
                    logger.debug(f"Could not convert values directly: {e}")
            else:
                # Try converting entire result
                try:
                    return validate_type(last_result, self._expected_return)
                except (TypeError, ValueError) as e:
                    logger.debug(f"Could not convert last_result directly: {e}")

        # Fall back to text handling if result conversion failed
        text = text.strip()
        if text:
            try:
                parsed = json.loads(text)
                origin = get_origin(self._expected_return)
                if origin in (list, List) and isinstance(parsed, dict):
                    if "values" in parsed:
                        parsed = parsed["values"]
                    elif "data" in parsed:
                        parsed = parsed["data"]
                return validate_type(parsed, self._expected_return)
            except (json.JSONDecodeError, TypeError, ValueError):
                pass

        if self._expected_return is str:
            return text
        return validate_type(text, self._expected_return)

    def _finalize_anthropic_pydantic(self, conversation: List[Dict[str, Any]], last_result: Any) -> Any:
        """Finalize a Pydantic model from the conversation."""
        if isinstance(last_result, self._expected_return):
            return last_result
            
        final_tools = [{
            "name": "ResponseStructuredJSON",
            "description": "Final structured JSON for ResponseStructuredJSON",
            "input_schema": self._expected_return.model_json_schema()
        }]
        
        final_request = {
            "model": self.sub_model_id,
            "messages": conversation + [{
                "role": "user",
                "content": [{
                    "type": "text",
                    "text": "Now please return the final ResponseStructuredJSON as valid JSON. Do not add extra text. Just valid JSON that matches the schema."
                }]
            }],
            "temperature": float(self.model_config.parameters.temperature_range[0]),
            "max_tokens": self.model_config.parameters.max_tokens_range[1],
            "tools": final_tools,
            "tool_choice": {"type": "tool", "name": "ResponseStructuredJSON"}
        }
        
        final_response = self._invoke_provider_api(final_request)
        if final_response.stop_reason == "tool_use":
            if final_response.content[0].name != "ResponseStructuredJSON":
                raise RuntimeError(f"Expected tool name 'ResponseStructuredJSON', got {final_response.content[0].name}")
            final_response_data = json.dumps(final_response.content[0].input)
            if self._expected_return is None or self._expected_return is str:
                return final_response_data
            return self._expected_return.model_validate_json(final_response_data)

    def _create_function_schema(self, func: Callable) -> Optional[Dict[str, Any]]:
        """Create a function schema for the given function."""
        # Skip functions with leading underscore - they are considered private
        if func.__name__.startswith('_'):
            return None
        return self._build_function_schema(func, provider_capabilities={"allow_lists": True}, schema_format="anthropic", strict=True)

    def _handle_single_tool_call(self, tool_name: str, inputs: Any, call_count: int, max_calls: int) -> Any:
        """Handle a single tool call."""
        return self._handle_tool_call({"name": tool_name, "arguments": inputs}, call_count, max_calls)

    def _create_llm_retry_decorator(self, func):
        """Creates a retry decorator specific to Anthropic API calls with max_tokens handling."""
        exception_types = (AnthropicRateLimitError, AnthropicOverloadedError, AnthropicMaxTokensExceededError, ConnectionError)
        
        config = self._get_retry_config() if hasattr(self, '_get_retry_config') else {}
        
        return retry(
            retry=retry_if_exception_type(exception_types),
            wait=wait_random_exponential(
                multiplier=config.get("wait_multiplier", 5.0),
                min=config.get("wait_min", 2),
                max=config.get("wait_max", 120)
            ),
            stop=stop_after_attempt(config.get("max_attempts", 8)),
            before=before_log(logger, logging.DEBUG),
            after=before_log(logger, logging.DEBUG),
            retry_error_callback=self._retry_handler
        )(func)

    def _retry_handler(self, retry_state):
        exception = retry_state.outcome.exception()
        if isinstance(exception, AnthropicMaxTokensExceededError) and hasattr(exception, 'original_response'):
            params = retry_state.args[0] if retry_state.args else {}
            if isinstance(params, dict) and 'max_tokens' in params:
                current_max = params['max_tokens']
                max_limit = self.model_config.parameters.max_tokens_range[1]
                params['max_tokens'] = min(current_max * 2, max_limit)
                logger.info(f"Retrying with increased max_tokens: {params['max_tokens']}")
        return None

    def _get_retry_config(self) -> Dict[str, Any]:
        """
        Get Anthropic-specific retry configuration with more aggressive backoff.
        
        Returns:
            Dictionary with retry configuration parameters
        """
        # Start with base provider's retry config (includes runtime overrides)
        config = super()._get_retry_config()
        
        # Modify default values for Anthropic if not already overridden
        anthropic_defaults = {
            "wait_multiplier": 5.0,    # More aggressive backoff
            "wait_min": 2,             # Start with a longer minimum wait
            "wait_max": 120,           # Allow for longer maximum wait times
            "max_attempts": 8,         # More attempts
            "jitter_factor": 0.2       # More jitter to spread out retries
        }
        
        # Only apply Anthropic defaults if not explicitly set in provider config or runtime overrides
        provider_retry = {}
        if isinstance(self.provider_config, dict) and "retry" in self.provider_config:
            provider_retry = self.provider_config["retry"]
        
        runtime_retry = self._config_overrides.get("retry", {})
        
        for key, value in anthropic_defaults.items():
            # Only use the anthropic default if it's not already set in provider config or runtime overrides
            if key not in provider_retry and key not in runtime_retry:
                config[key] = value
        
        return config

    def _invoke_provider_api(self, params: Dict[str, Any]) -> Any:
        """Single entry point for Anthropic API calls with retry logic."""
        @self._create_llm_retry_decorator
        def _call_anthropic_api(params: Dict[str, Any]):
            logger.debug(f"Calling Anthropic API with params: {format_object(params)}")
            api_key = os.environ.get(self.provider_config["auth_env_var"])
            if not api_key:
                raise ValueError(f"{self.provider_config['auth_env_var']} environment variable is not set")
            
            timeout = self.get_timeout()
            
            client = Anthropic(
                api_key=api_key,
                base_url=self.provider_config["base_url"],
                timeout=timeout
            )
            
            try:
                response = client.messages.create(**params)
                logger.debug(f"Received Anthropic response: {format_object(response)}")
                
                # Check if response was truncated due to max_tokens limit
                if hasattr(response, 'stop_reason') and response.stop_reason == "max_tokens":
                    current_max_tokens = params.get("max_tokens", 1024)
                    new_max_tokens = current_max_tokens * 2
                    
                    # Don't exceed model capability
                    max_limit = self.model_config.parameters.max_tokens_range[1]
                    new_max_tokens = min(new_max_tokens, max_limit)
                    
                    logger.info(f"Response exceeded max_tokens limit ({current_max_tokens}). Retrying with {new_max_tokens} tokens.")
                    raise AnthropicMaxTokensExceededError(
                        f"Response exceeded max_tokens limit. Increasing from {current_max_tokens} to {new_max_tokens}.",
                        original_response=response
                    )
                
                return response
            except Exception as e:
                error_str = str(e)
                
                if "429" in error_str:
                    rate_limit_info = {}
                    
                    if hasattr(e, 'response') and hasattr(e.response, 'headers'):
                        headers = e.response.headers
                        rate_limit_info['limit'] = headers.get('x-ratelimit-limit')
                        rate_limit_info['remaining'] = headers.get('x-ratelimit-remaining')
                        rate_limit_info['reset'] = headers.get('x-ratelimit-reset')
                    
                    logger.warning(f"Anthropic rate limit hit: {rate_limit_info}")
                    
                    if rate_limit_info.get('remaining') == '0':
                        extra_delay = 5.0
                        logger.info(f"Adding extra delay of {extra_delay}s due to severe rate limiting")
                        time.sleep(extra_delay)
                    
                    raise AnthropicRateLimitError(f"Rate limit error: {error_str}")
                    
                elif "529" in error_str or "overloaded_error" in error_str.lower():
                    raise AnthropicOverloadedError(error_str)
                
                raise

        return _call_anthropic_api(params)

    def _anthropic_flatten_json_schema(self, model: Type[BaseModel]) -> Dict[str, Any]:
        """Flatten a Pydantic model's JSON schema for Anthropic."""
        raw = model.model_json_schema()
        flat = self._remove_refs(raw)
        return ensure_no_additional_props(flat)

    def _remove_refs(self, data: Any) -> Any:
        """Remove $ref fields from JSON schema."""
        if isinstance(data, dict):
            data.pop('$ref', None)
            data.pop('$defs', None)
            data.pop('definitions', None)
            for k, v in list(data.items()):
                data[k] = self._remove_refs(v)
        elif isinstance(data, list):
            return [self._remove_refs(x) for x in data]
        return data

    def update_token_usage(self, event: "ExecutionEvent", response: Any) -> None:
        if hasattr(response, 'usage'):
            usage = response.usage
            event.prompt_tokens = getattr(usage, 'input_tokens', None)
            event.completion_tokens = getattr(usage, 'output_tokens', None)
            if event.prompt_tokens is not None and event.completion_tokens is not None:
                event.total_tokens = event.prompt_tokens + event.completion_tokens
        # If we tracked usage in the provider object, use that as fallback
        elif hasattr(self, '_usage_stats'):
            event.prompt_tokens = self._usage_stats.get("prompt_tokens")
            event.completion_tokens = self._usage_stats.get("completion_tokens")
            event.total_tokens = self._usage_stats.get("total_tokens")

    def _execute_function_calls_until_done(
        self,
        ongoing_msgs,
        system_prompt,
        temperature,
        max_tokens,
        pydantic_model,
        response_format,
        functions,
        max_calls=10
    ):
        """Execute function calls until the conversation is complete."""
        # Set expected return type
        if pydantic_model:
            self._expected_return = pydantic_model
        elif response_format:
            self._expected_return = response_format
            
        # Prepare tools list
        tools = []
        
        # Add structured output tool if needed
        structured_tool, force_tool_choice = self._prepare_structured_tool_for_type(self._expected_return)
        if structured_tool:
            tools.append(structured_tool)
            logger.debug(f"Created structured output tool: {structured_tool}")
            
            # Add prompt guidance for using the tool
            prompt_addition = " Extract the information and use the extract_values tool to return it in the correct format."
            if not system_prompt:
                system_prompt = prompt_addition.strip()
            else:
                system_prompt += prompt_addition
    
        # Add function tools - only include non-private functions
        if functions:
            for func in functions:
                if func.get("type") == "function":
                    # Only expose non-private functions to the model
                    func_name = func["function"]["name"]
                    if not func_name.startswith('_'):
                        tools.append({
                            "name": func_name,
                            "description": func["function"]["description"],
                            "input_schema": func["function"]["parameters"]
                        })
                    else:
                        logger.debug(f"Not exposing private function to model: {func_name}")
                else:
                    tools.append(func)
        
        # Add functions from registry
        if self.function_registry:
            for name, spec in self.function_registry.items():
                if not name.startswith('_') and spec.schema is not None:
                    # Check if we already added this tool
                    if not any(t["name"] == name for t in tools):
                        tools.append({
                            "name": name,
                            "description": spec.schema["function"]["description"],
                            "input_schema": spec.schema["function"]["parameters"]
                        })

        # Prepare the request payload
        request_payload = {
            "model": self.sub_model_id,
            "messages": ongoing_msgs,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        if system_prompt:
            request_payload["system"] = system_prompt
            
        if tools:
            request_payload["tools"] = tools
            self._current_functions = tools
            
            # Force tool choice if specified
            if force_tool_choice:
                request_payload["tool_choice"] = force_tool_choice
                logger.debug(f"Forcing tool choice: {force_tool_choice}")
                
        logger.debug(f"Sending request payload: {request_payload}")
        
        # Make the initial API call
        initial_response = self._invoke_provider_api(request_payload)
        logger.debug(f"Received initial response: {initial_response}")
        
        # Process the response iteratively
        return self.iterative_function_call_loop(
            conversation=ongoing_msgs,
            initial_response=initial_response,
            max_calls=max_calls,
            extract_tool_calls_cb=self._extract_anthropic_tool_calls,
            handle_single_tool_call_cb=self._handle_anthropic_single_tool_call,
            update_conversation_with_tool_result_cb=self._update_anthropic_conversation_with_tool_result,
            check_done_or_reason_cb=self._check_anthropic_done_or_reason,
            re_invoke_api_cb=self._re_invoke_anthropic,
            response_format=response_format,
            expected_return=self._expected_return
        )

    def call_model(
        self,
        messages: List[Dict[str, Any]],
        images: Optional[List[Dict[str, Any]]] = None,
        response_format: Optional[Type[BaseModel]] = None,
        functions: Optional[List[Dict[str, Any]]] = None,
        expected_return: Optional[Type] = None,
        config_overrides: Optional[Dict[str, Any]] = None
    ) -> Any:
        """Call the Anthropic model with the given messages and options."""
        logger.debug(f"Preparing to call Anthropic API with model {self.model_id}")
        logger.debug(f"Expected return type: {expected_return}")

        if response_format is None and expected_return is not None:
            response_format = expected_return

        self._expected_return = resolve_expected_type(expected_return)
        self._current_functions = functions

        system_prompt = None
        filtered_msgs = []
        for msg in messages:
            role_str = msg["role"].value if hasattr(msg["role"], "value") else str(msg["role"])
            if role_str.lower() == "system" and system_prompt is None:
                system_prompt = msg.get("value") or msg.get("content", "")
            else:
                filtered_msgs.append(msg)

        def image_formatter(img):
            return {
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": self._get_image_type(img["data"]),
                    "data": base64.b64encode(img["data"]).decode("utf-8")
                }
            }
        ongoing_msgs = self._format_images_for_message(filtered_msgs, images, image_formatter)

        pydantic_model = try_convert_to_pydantic_model(response_format)
        if pydantic_model:
            self._expected_return = pydantic_model
            
        temperature = float(self.model_config.parameters.temperature_range[0])
        if config_overrides and "max_tokens" in config_overrides:
            max_tokens = int(config_overrides["max_tokens"])
        else:
            max_tokens = self.model_config.parameters.max_tokens_range[1]
        
        tools = []
        if functions and self.function_registry:
            for spec in self.function_registry.values():
                if spec.schema is not None:
                    tools.append(spec.schema)

        max_calls = (
            config_overrides.get("max_function_calls") if config_overrides else None
        )
        if max_calls is not None:
            max_calls = int(max_calls)
        else:
            max_calls = self.model_config.get_max_function_calls() or 10

        final_result = self._execute_function_calls_until_done(
            ongoing_msgs, system_prompt, temperature, max_tokens, 
            pydantic_model, response_format, functions, max_calls=max_calls
        )
        return final_result

    def call_model_with_metadata(
        self,
        messages: List[Dict[str, Any]], 
        images: Optional[List[Dict[str, Any]]] = None,
        response_format: Optional[Type[BaseModel]] = None,
        functions: Optional[List[Dict[str, Any]]] = None,
        expected_return: Optional[Type] = None,
        config_overrides: Optional[Dict[str, Any]] = None
    ) -> Any:
        """Call the model and collect metadata."""
        # Reset usage stats
        self._usage_stats = {
            "prompt_tokens": 0,
            "completion_tokens": 0, 
            "total_tokens": 0
        }
        
        # Call the standard implementation and let it update the stats
        return super().call_model_with_metadata(
            messages=messages,
            images=images,
            response_format=response_format,
            functions=functions,
            expected_return=expected_return,
            config_overrides=config_overrides
        )