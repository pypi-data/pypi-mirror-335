# pscript/schema_builder.py

import inspect
from typing import Callable, get_type_hints
from .utils import type_to_json_schema, ensure_no_additional_props

class NotSupportedError(Exception):
    """Raised when a provider or model cannot handle a certain schema shape."""
    pass

def is_schema_array(schema: dict) -> bool:
    """
    Recursively check if 'schema' or any nested part
    has "type":"array".
    """
    if schema.get("type") == "array":
        return True
    if schema.get("type") == "object":
        for prop_schema in schema.get("properties", {}).values():
            if is_schema_array(prop_schema):
                return True
    return False

def build_function_schema(
    func: Callable,
    provider_capabilities: dict = None,
    strict: bool = True,
    format: str = "default"  # "default" or "anthropic"
) -> dict:
    """
    Build a JSON schema for a single function's parameters, with optional
    logic to forbid or degrade certain shapes if the provider doesn't support them.

    :param func: The Python function we want to expose to the LLM
    :param provider_capabilities: A dict of booleans or flags indicating
                                  which shapes/features are supported.
                                  e.g. {"allow_lists": True, "allow_nested_arrays": False}
    :param strict: If True, we remove additionalProperties, etc.
    :param format: "anthropic" => shape is { name, description, input_schema }, 
                   "default" => shape is { type:function, function:{ name, description, parameters } }
    :return: A dictionary in the shape required for that provider's function calling.
    """

    if provider_capabilities is None:
        # By default, assume everything is allowed
        provider_capabilities = {
            "allow_lists": True,
            "allow_nested_arrays": True,
        }

    # Gather docstring
    docstring = inspect.getdoc(func) or ""
    func_name = func.__name__

    # Build the "parameters" object from type hints
    type_hints = get_type_hints(func)
    sig = inspect.signature(func)

    parameters_obj = {
        "type": "object",
        "properties": {},
        "required": [],
        "additionalProperties": False
    }

    for param_name, param in sig.parameters.items():
        if param_name == "self":
            continue  # skip self if a class method

        param_type = type_hints.get(param_name, str)
        param_schema = type_to_json_schema(param_type)

        # Possibly enforce no additional props
        if strict:
            param_schema = ensure_no_additional_props(param_schema)

        # If the provider disallows lists entirely
        if not provider_capabilities.get("allow_lists", True):
            if is_schema_array(param_schema):
                raise NotSupportedError(
                    f"{func_name}: param '{param_name}' is a list[...] type, but lists not allowed."
                )

        parameters_obj["properties"][param_name] = param_schema
        if param.default is param.empty:
            parameters_obj["required"].append(param_name)

    # Now produce final shape
    if format == "anthropic":
        return {
            "name": func_name,
            "description": docstring,
            "input_schema": parameters_obj
        }
    else:
        return {
            "type": "function",
            "function": {
                "name": func_name,
                "description": docstring,
                "parameters": parameters_obj
            }
        }
