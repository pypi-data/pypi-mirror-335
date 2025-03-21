# pscript/prompt.py

import functools
import inspect
import json
import logging
import time
from pydantic import BaseModel
from typing import Callable, Optional, List, Any, Tuple, get_origin, Dict

from .config import get_config
from .context import get_current_context
from .function_analyzer import FunctionAnalyzer
from .log_config import try_latch_logging_level
from .providers import create_provider
from .tracer import get_global_tracer, get_global_context
from .types import Attachment, FunctionConfig, FunctionMetadata, ResponseMetadata
from .utils import type_to_json_schema, wrap_primitive_for_metadata, safe_serialize

logger = logging.getLogger(__name__)

def create_prompt_decorator(decorator_type: str):
    def decorator(*args, 
                  logging_level: Optional[str] = None, 
                  parallel_calls: bool = False, 
                  max_tokens: Optional[int] = None,
                  **config_overrides):
        func = None

        if parallel_calls:
            config_overrides["parallel_calls"] = parallel_calls
            
        if max_tokens is not None:
            config_overrides["max_tokens"] = max_tokens
            
        if len(args) == 1 and callable(args[0]) and not config_overrides:
            func = args[0]
            args = ()

        if logging_level:
            try_latch_logging_level(logging_level)

        def wrapper(target_func: Callable) -> Callable:
            if hasattr(target_func, '__function_metadata__'):
                raise ValueError(
                    f"Function '{target_func.__name__}' is already decorated with "
                    f"@{target_func.__function_metadata__.decorator_type}. Cannot mix pscript decorators."
                )

            analyzer = FunctionAnalyzer()
            fmeta = analyzer.process_function(target_func, config_overrides, decorator_type=decorator_type)
            target_func.__function_metadata__ = fmeta

            @functools.wraps(target_func)
            def inner_wrapper(*iargs, **ikwargs):
                tracer = get_global_tracer()
                logger.debug(f"Executing {decorator_type} function: {target_func.__name__}")

                global_ctx = get_global_context()
                local_ctx = dict(global_ctx)
                sig = inspect.signature(target_func)
                bound_args = sig.bind(*iargs, **ikwargs)
                bound_args.apply_defaults()
                local_ctx.update(dict(bound_args.arguments))

                old_config = global_ctx.get('__config__', None)
                old_function_md = global_ctx.get('__function_metadata__', None)

                global_ctx['__config__'] = fmeta.final_config
                global_ctx['__function_metadata__'] = fmeta

                frame = inspect.currentframe()
                frame.f_locals['__function_metadata__'] = fmeta

                event = tracer.start_event(target_func, local_ctx)
                start_time = time.time()

                try:
                    return_type = fmeta.return_type
                    return_metadata = False
                    
                    if return_type is not None:
                        origin = get_origin(return_type)
                        if origin in (tuple, Tuple):
                            # No exceptions - ban all tuple return types including ResponseMetadata
                            raise TypeError(
                                "Tuple return types are not supported for @prompt functions. "
                                "Use Pydantic models or other JSON-compatible types instead. "
                                "For metadata, use return_metadata=True parameter."
                            )
                    
                    # Only set return_metadata based on explicit parameter
                    global_ctx['__return_metadata__'] = return_metadata
                    
                    result = target_func(*iargs, **ikwargs)
                    
                    tracer.end_event(event, start_time, result=result)
                    logger.debug(f"{decorator_type} function {target_func.__name__} completed")
                    return result
                except Exception as e:
                    tracer.end_event(event, start_time, error=e)
                    raise
                finally:
                    if old_config is None:
                        global_ctx.pop('__config__', None)
                    else:
                        global_ctx['__config__'] = old_config

                    if old_function_md is None:
                        global_ctx.pop('__function_metadata__', None)
                    else:
                        global_ctx['__function_metadata__'] = old_function_md
                    
                    global_ctx.pop('__return_metadata__', None)

            return inner_wrapper

        if func is not None:
            return wrapper(func)

        return wrapper
    return decorator

prompt = create_prompt_decorator('prompt')

def _find_prompt_context() -> dict:
    frame = inspect.currentframe().f_back  
    while frame:
        if '__function_metadata__' in frame.f_locals:
            return frame.f_locals['__function_metadata__']
        frame = frame.f_back
    raise RuntimeError(
        "gen() called but no @prompt-decorated function found in the call stack. "
        "Ensure you're calling gen() inside a @prompt-decorated function."
    )

def resolve_config_value(key: str, overrides: Dict[str, Any], fun_meta: FunctionMetadata, base_config: FunctionConfig) -> Any:
    """
    Resolve a configuration value from multiple sources with proper handling for falsy values.
    
    Args:
        key: The configuration key to resolve
        overrides: Runtime overrides (highest priority)
        fun_meta: Function metadata with config_overrides
        base_config: Base configuration (can be None)
        
    Returns:
        Resolved configuration value
    """
    # Check overrides first (explicitly check for key existence to handle 0, False, etc.)
    if key in overrides:
        return overrides[key]
        
    # Then check function metadata config overrides
    if key in fun_meta.config_overrides:
        return fun_meta.config_overrides[key]
        
    # Check base config if present
    if base_config is not None and hasattr(base_config, key):
        return getattr(base_config, key)
    
    # Fallback to global config
    global_cfg = get_config()
    
    # Map the key to the corresponding config path
    config_path_map = {
        "model": "model.name",
        "temperature": "model.temperature",
        "max_tokens": "model.max_tokens",
        "system_prompt": "system.prompt",
        "max_function_calls": "model_fallback.max_function_calls",
    }
    
    config_path = config_path_map.get(key)
    if config_path:
        value = global_cfg.get(config_path)
        if value is not None:
            return value
    
    # Final fallbacks if nothing found in global config
    defaults = {
        "model": "azure_openai/gpt-4o-mini",
        "temperature": 0.7,
        "max_tokens": 2048,
        "system_prompt": "You are a helpful assistant.",
        "max_function_calls": 10
    }
    
    return defaults.get(key)

def gen(
    prompt_text: str,
    attachments: Optional[List[Attachment]] = None,
    logging_level: Optional[str] = None,
    return_metadata: Optional[bool] = None,
    replay: str = "auto",
    parallel_calls: bool = False,
    max_tokens: Optional[int] = None,
    **overrides
) -> Any:
    """
    Generate text from a language model based on a prompt.
    
    Args:
        prompt_text: The text to send to the language model
        attachments: Optional list of attachments (e.g., images)
        logging_level: Optional logging level override
        return_metadata: Whether to return metadata along with the result
        replay: Replay mode ("auto", "always", "never")
        parallel_calls: Whether to allow parallel function calls
        max_tokens: Optional maximum tokens to generate
        **overrides: Additional overrides for model parameters, including:
            - temperature: Sampling temperature (0.0 to 2.0)
            - system_prompt: System prompt to use
            - azure_openai_endpoint: Azure OpenAI endpoint URL
            - azure_openai_deployment: Azure OpenAI deployment name
            - azure_openai_api_version: Azure OpenAI API version
            - authentication: Authentication method (token/managed)
            - api_key: API key to use
    
    Returns:
        Generated text or structured data from the model
    """
    if parallel_calls:
        overrides["parallel_calls"] = parallel_calls
        
    if max_tokens is not None:
        overrides["max_tokens"] = max_tokens

    global_ctx = get_global_context()
    base_config = global_ctx.get('__config__')
    
    try:
        fun_meta = _find_prompt_context()
        global_ctx['__function_metadata__'] = fun_meta
    except RuntimeError as e:
        raise RuntimeError(
            "gen() called but no @prompt-decorated function found in the call stack. "
            "Ensure you're calling gen() inside a @prompt-decorated function."
        ) from e

    if logging_level:
        try_latch_logging_level(logging_level)

    llm_return_type = fun_meta.return_type if fun_meta else None
    # Determine whether to return metadata
    should_return_metadata = return_metadata if return_metadata is not None else global_ctx.get('__return_metadata__', False)

    tracer = get_global_tracer()
    
    # Handle replay control
    if replay == "stop_all":
        from .tracer import disable_replay
        disable_replay()
    
    # Get current execution context
    context = get_current_context()
    
    # Check if we should use replay
    if replay != "stop" and hasattr(tracer, 'replay_active') and tracer.replay_active:
        # Resolve configuration values
        final_model_name = resolve_config_value("model", overrides, fun_meta, base_config)
        final_temperature = resolve_config_value("temperature", overrides, fun_meta, base_config)
        final_max_tokens = resolve_config_value("max_tokens", overrides, fun_meta, base_config)
        final_system_prompt = resolve_config_value("system_prompt", overrides, fun_meta, base_config)
        
        # Build replay key
        replay_key = {
            'function_name': 'gen',
            'prompt_text': prompt_text,
            'context_id': context.context_id,
            'context_path': context.context_path,
            'model': final_model_name,
            'temperature': float(final_temperature),
            'max_tokens': int(final_max_tokens),
            'system_prompt': final_system_prompt,
        }
        logger.debug(f"Constructed replay key: {replay_key}")
        logger.debug(f"Available replay keys: {list(tracer._replay_cache.keys())}")
        
        try:
            if hasattr(tracer, 'find_replay_match'):
                replay_result = tracer.find_replay_match(replay_key)
                if replay_result is not None:
                    logger.debug("Using replayed result for gen() call")
                    
                    # If metadata requested, add it
                    if should_return_metadata:
                        provider_name = final_model_name.split('/')[0] if '/' in final_model_name else None
                        metadata = ResponseMetadata(
                            model_name=final_model_name,
                            provider=provider_name
                        )
                        
                        replay_result = wrap_primitive_for_metadata(replay_result)
                        replay_result.__response_metadata__ = metadata
                    
                    return replay_result
        except ValueError:
            logger.debug("No replay match found, proceeding with actual execution")
    
    # Continue with normal execution
    event_context = {
        'prompt_text': prompt_text,
        'overrides': overrides,
        'attachments': [att.name or "attachment" for att in attachments or []],
        'function_return_type': str(llm_return_type) if llm_return_type else None
    }
    event = tracer.start_event(gen, event_context)
    start_time = time.time()

    # Resolve configuration values
    final_model_name = resolve_config_value("model", overrides, fun_meta, base_config)
    final_temperature = resolve_config_value("temperature", overrides, fun_meta, base_config)
    final_max_tokens = resolve_config_value("max_tokens", overrides, fun_meta, base_config)
    final_system_prompt = resolve_config_value("system_prompt", overrides, fun_meta, base_config)
    final_max_function_calls = resolve_config_value("max_function_calls", overrides, fun_meta, base_config)
    
    # Resolve Azure OpenAI specific configuration values
    final_api_version = resolve_config_value("api_version", overrides, fun_meta, base_config)
    final_base_url = resolve_config_value("base_url", overrides, fun_meta, base_config)
    final_deployment_name = resolve_config_value("deployment_name", overrides, fun_meta, base_config)
    final_api_key = resolve_config_value("api_key", overrides, fun_meta, base_config)
    final_authentication = resolve_config_value("authentication", overrides, fun_meta, base_config)

    # Extract timeout and retry configuration if present
    final_timeout = overrides.get("timeout", None)
    final_retry = overrides.get("retry", None)
    
    # Specifically extract Azure OpenAI parameters
    azure_openai_endpoint = overrides.get("azure_openai_endpoint")
    azure_openai_deployment = overrides.get("azure_openai_deployment")
    azure_openai_api_version = overrides.get("azure_openai_api_version")
    
    # Create the provider
    functions = None
    provider = create_provider(final_model_name)
    
    # Update provider with runtime configuration
    provider_config = {
        "api_version": final_api_version,
        "base_url": final_base_url,
        "deployment_name": final_deployment_name,
        "api_key": final_api_key,
        "authentication": final_authentication,
        "max_function_calls": final_max_function_calls,
        "temperature": final_temperature,
        "max_tokens": final_max_tokens,
        "system_prompt": final_system_prompt,
        "timeout": final_timeout,
        "retry": final_retry
    }
    
    # Add Azure-specific parameters if they exist
    if azure_openai_endpoint:
        provider_config["azure_openai_endpoint"] = azure_openai_endpoint
    if azure_openai_deployment:
        provider_config["azure_openai_deployment"] = azure_openai_deployment
    if azure_openai_api_version:
        provider_config["azure_openai_api_version"] = azure_openai_api_version
    
    provider.update_config(provider_config)

    if fun_meta and fun_meta.nested_functions:
        functions = []

        frame = inspect.currentframe()
        while frame:
            if frame.f_code.co_name == fun_meta.function_name:
                local_ctx = frame.f_locals
                break
            frame = frame.f_back

        for name, meta in fun_meta.nested_functions.items():
            if name not in local_ctx:
                continue

            actual_func = local_ctx[name]
            if not callable(actual_func):
                continue

            docstring = actual_func.__doc__ or meta["docstring"]
            annotations = dict(getattr(actual_func, "__annotations__", {}))
            if not annotations:
                annotations = meta["annotations"]

            params_schema = {
                "type": "object",
                "properties": {},
                "required": []
            }

            sig = inspect.signature(actual_func)
            for param_name, param in sig.parameters.items():
                param_type = annotations.get(param_name, str)
                params_schema["properties"][param_name] = type_to_json_schema(param_type)
                if param.default == param.empty:
                    params_schema["required"].append(param_name)

            functions.append({
                "type": "function",
                "function": {
                    "name": name,
                    "description": docstring,
                    "parameters": params_schema
                }
            })
            provider.register_function(name, actual_func)

    attachments_info = []
    if attachments:
        for att in attachments:
            attachments_info.append({
                'name': att.name or 'attachment',
                'mime_type': att.mime_type,
                'size': len(att.data)
            })
    replay_key_data = {
        'prompt_text': prompt_text,
        'model': final_model_name,
        'temperature': float(final_temperature),
        'max_tokens': int(final_max_tokens),
        'system_prompt': final_system_prompt,
        'attachments': attachments_info
    }
    replay_key_json = json.dumps(replay_key_data, sort_keys=True)

    replay_cache = global_ctx.get('__replay_cache__', None)
    if replay_cache is not None and replay_key_json in replay_cache:
        logger.debug("Returning replayed result for identical prompt/config/attachments.")
        replayed = replay_cache[replay_key_json]
        tracer.end_event(event, start_time, result=replayed)
        
        # For replayed results with metadata requested, create and attach metadata
        if should_return_metadata:
            metadata = ResponseMetadata(
                model_name=final_model_name,
                provider=final_model_name.split('/')[0] if '/' in final_model_name else None
            )
            # Inject metadata as attribute
            replayed.__response_metadata__ = metadata
            
        return replayed

    messages = [
        {"role": "system", "content": final_system_prompt},
        {"role": "user", "content": prompt_text},
    ]

    # Determine response format based on return type
    response_format = None
    if llm_return_type and isinstance(llm_return_type, type) and issubclass(llm_return_type, BaseModel):
        # If the return type is a Pydantic model, set up response_format
        schema = llm_return_type.model_json_schema()
        response_format = {
            "type": "json_schema",
            "schema": schema
        }
        
    # Record the complete messages sent to LLM in the event (ensure they're serializable)
    # Include additional API parameters like response_format and functions
    event.messages_to_llm = [
        {k: v for k, v in msg.items() if k != 'data'} 
        for msg in messages
    ]
    
    # Add structured output information to event
    if response_format:
        event.metadata['response_format'] = safe_serialize(response_format)
    if functions:
        event.metadata['functions'] = safe_serialize(functions)

    images_param = []
    if attachments:
        for att in attachments:
            # Only track metadata about attachments in the event
            event.metadata['attachments'] = event.metadata.get('attachments', []) + [{
                'name': att.name or "attachment",
                'mime_type': att.mime_type,
                'size_bytes': len(att.data)
            }]
            
            images_param.append({
                'name': att.name or "attachment",
                'data': att.data,
                'mime_types': [att.mime_type]
            })

    call_start_time = time.time()
    provider_result, provider_response = provider.call_model_with_metadata(
        messages,
        images=images_param,
        response_format=llm_return_type,  # Pass the expected return type
        functions=functions,
        expected_return=llm_return_type,
        config_overrides={  
            "max_function_calls": final_max_function_calls,
            "max_tokens": final_max_tokens
        }
    )
    call_end_time = time.time()
    
    # Extract essential data from the provider response
    def extract_essential_response_data(response):
        # Only extract the necessary fields to avoid storing large objects
        essential_data = {}
        
        # Most important properties to save
        if hasattr(response, 'choices') and response.choices:
            essential_data['choices'] = [{
                'message': {'role': choice.message.role, 'content': choice.message.content}
                if hasattr(choice, 'message') else None,
                'finish_reason': choice.finish_reason if hasattr(choice, 'finish_reason') else None
            } for choice in response.choices]
            
        # Save usage statistics if available
        if hasattr(response, 'usage'):
            essential_data['usage'] = {
                'prompt_tokens': getattr(response.usage, 'prompt_tokens', None),
                'completion_tokens': getattr(response.usage, 'completion_tokens', None), 
                'total_tokens': getattr(response.usage, 'total_tokens', None)
            }
            
        # For Anthropic/Claude
        if hasattr(response, 'content') and response.content:
            try:
                essential_data['content'] = [
                    {'type': part.type, 'text': part.text} 
                    for part in response.content 
                    if hasattr(part, 'text')
                ]
            except:
                essential_data['content_text'] = str(response.content)
                
        # Include model name if available
        if hasattr(response, 'model'):
            essential_data['model'] = response.model
            
        return essential_data
    
    response_data = extract_essential_response_data(provider_response)
    event.llm_response = response_data
    event.request_duration_ms = round((call_end_time - call_start_time) * 1000, 2)
    
    provider_name = final_model_name.split('/')[0] if '/' in final_model_name else None
    metadata = ResponseMetadata(
        model_name=final_model_name,
        provider=provider_name,
        request_duration_ms=event.request_duration_ms,
        raw_provider_data_str=None
    )
    
    provider.update_token_usage(event, provider_response)
    
    # Copy token usage to the metadata object for return value
    metadata.prompt_tokens = event.prompt_tokens
    metadata.completion_tokens = event.completion_tokens
    metadata.total_tokens = event.total_tokens
    
    if replay_cache is not None:
        replay_cache[replay_key_json] = provider_result

    tracer.end_event(event, start_time, result=provider_result)
    
    if should_return_metadata:
        provider_result = wrap_primitive_for_metadata(provider_result)
        provider_result.__response_metadata__ = metadata
        
    return provider_result