import dataclasses
import json
import logging
from pydantic import ValidationError, BaseModel
from typing import Any, List, Dict, Union, Optional, get_origin, get_args, Type, Tuple
from .log_config import format_object
from .types import ResponseMetadata

logger = logging.getLogger(__name__)

def require_response_metadata(obj: Any) -> ResponseMetadata:
    """Get response metadata, raising AttributeError if not present."""
    if not hasattr(obj, "__response_metadata__"):
        raise AttributeError(f"Object {obj!r} must have __response_metadata__ attribute")
    return obj.__response_metadata__

def find_response_metadata(obj: Any) -> Optional[ResponseMetadata]:
    """Find response metadata if it exists, otherwise return None."""
    return getattr(obj, "__response_metadata__", None)

def type_to_json_schema(type_hint: Any) -> Dict[str, Any]:
    def _inner_schema(type_hint: Any) -> Dict[str, Any]:
        origin = get_origin(type_hint)
        if origin is Union:
            args = get_args(type_hint)
            if len(args) == 2 and type(None) in args:
                type_hint = next(arg for arg in args if arg is not type(None))

        if type_hint in (str, Any):
            return {"type": "string"}
        elif type_hint is int:
            return {"type": "integer"}
        elif type_hint is float:
            return {"type": "number"}
        elif type_hint is bool:
            return {"type": "boolean"}
        elif origin in (list, List):
            item_type = get_args(type_hint)[0]
            return {
                "type": "array",
                "items": _inner_schema(item_type)
            }
        elif origin in (dict, Dict):
            key_type, value_type = get_args(type_hint)
            return {
                "type": "object",
                "additionalProperties": _inner_schema(value_type)
            }
        elif isinstance(type_hint, type) and hasattr(type_hint, 'model_json_schema'):
            return type_hint.model_json_schema()
        else:
            return {"type": "string"}

    return _inner_schema(type_hint)

def resolve_expected_type(return_type: Optional[Type]) -> Type:
    if return_type is None:
        return str
        
    origin = get_origin(return_type)
    if origin is Union:
        args = get_args(return_type)
        if type(None) in args:
            return_type = next(t for t in args if t is not type(None))
    return return_type

def validate_type(value: Any, expected_type: Any) -> Any:
    log_value = format_object(value)
    logger.debug(f"Validating type: value={log_value}, expected_type={expected_type}")

    if value is None:
        raise TypeError(f"Expected {expected_type}, got None")

    # Handle regular Union types
    origin = get_origin(expected_type)
    if origin is Union:
        args = get_args(expected_type)
        # Try each type until one works
        for t in args:
            if t is type(None) and value is None:
                return None
            try:
                return validate_type(value, t)
            except TypeError:
                pass
        raise TypeError(f"Value {value} does not match any type in {expected_type}")

    if isinstance(expected_type, type) and issubclass(expected_type, BaseModel):
        if isinstance(value, expected_type):
            return value
        if isinstance(value, dict):
            return expected_type(**value)
        if isinstance(value, str):
            try:
                data = json.loads(value)
                return expected_type(**data)
            except json.JSONDecodeError:
                raise TypeError(f"Cannot convert string '{value}' to {expected_type}")
            except ValidationError as e:
                raise TypeError(f"Validation error: {e}")
        raise TypeError(f"Cannot convert {type(value)} to {expected_type.__name__}")

    if origin is tuple or origin is Tuple:
        if isinstance(value, (tuple, list)):
            args = get_args(expected_type)
            # If it's a homogeneous tuple (Tuple[T, ...])
            if len(args) == 2 and args[1] is Ellipsis:
                item_type = args[0]
                return tuple(validate_type(item, item_type) for item in value)
            # If it's a heterogeneous tuple with defined types for each position
            elif len(args) > 0:
                if len(value) != len(args):
                    raise TypeError(f"Expected tuple of length {len(args)}, got length {len(value)}")
                return tuple(validate_type(item, arg_type) for item, arg_type in zip(value, args))
        elif isinstance(value, str):
            try:
                parsed = json.loads(value)
                if isinstance(parsed, list):
                    return validate_type(parsed, expected_type)
                raise TypeError(f"Expected tuple but parsed JSON is {type(parsed)}")
            except json.JSONDecodeError:
                raise TypeError(f"Cannot convert string '{value}' to tuple")
        raise TypeError(f"Cannot convert {type(value)} to tuple")

    if origin in (list, List):
        item_type = get_args(expected_type)[0] if get_args(expected_type) else Any
        
        # Handle the case where value is a dictionary with 'items' key (common from OpenAI/Azure)
        if isinstance(value, dict) and 'items' in value and isinstance(value['items'], list):
            logger.debug("Found dictionary with 'items' key, extracting items for list conversion")
            value = value['items']
        
        if isinstance(value, str):
            # Try JSON parse
            try:
                parsed = json.loads(value)
                # Also check for items wrapper in JSON string
                if isinstance(parsed, dict) and 'items' in parsed and isinstance(parsed['items'], list):
                    parsed = parsed['items']
                elif not isinstance(parsed, list):
                    raise TypeError(f"Expected list but got {type(parsed)}")
                value = parsed
            except json.JSONDecodeError:
                # If expected list[str] and can't parse as JSON, try splitting lines
                if item_type is str:
                    lines = [line.strip() for line in value.split('\n') if line.strip()]
                    return [validate_type(line, str) for line in lines]
                raise TypeError(f"Cannot convert string '{value}' to list")
                
        if not isinstance(value, list):
            raise TypeError(f"Expected list but got {type(value)}")
            
        converted_list = []
        for item in value:
            converted_list.append(validate_type(item, item_type))
        return converted_list

    if expected_type in (int, float, bool):
        if isinstance(value, str):
            value = value.strip()
            if expected_type is bool:
                # Convert common truthy strings
                return value.lower() in ["true", "1", "yes", "y", "on"]
            try:
                return expected_type(value)
            except (ValueError, TypeError):
                raise TypeError(f"Cannot convert '{value}' to {expected_type.__name__}")
        if not isinstance(value, expected_type):
            raise TypeError(f"Expected {expected_type.__name__}, got {type(value).__name__}")
        return value

    if expected_type is str:
        if not isinstance(value, str):
            raise TypeError(f"Expected str, got {type(value).__name__}")
        return value

    if isinstance(expected_type, type):
        if not isinstance(value, expected_type):
            raise TypeError(f"Expected {expected_type}, got {type(value)}")
        return value

    raise TypeError(f"Cannot validate type for {expected_type}")

def convert_to_expected_type(content: str, expected_type: Optional[Type] = None) -> Any:
    if expected_type is None or expected_type is str:
        return content

    # Resolve special types like tuple[T, ResponseMetadata]
    expected_type = resolve_expected_type(expected_type)
    return validate_type(content, expected_type)

def convert_to_pydantic_model(type_hint: Any) -> Type[BaseModel] | Any:
    origin = get_origin(type_hint)

    if origin is list or origin is dict:
        return Any

    elif isinstance(type_hint, type) and issubclass(type_hint, BaseModel):
        return type_hint

    elif isinstance(type_hint, type) and type_hint in {str, int, float, bool, bytes}:
        return type_hint

    elif get_origin(type_hint) is Union:
        return Any

    else:
        return type_hint

def try_convert_to_pydantic_model(type_hint: Any) -> Optional[Type[BaseModel]]:
    try:
        model = convert_to_pydantic_model(type_hint)
        if isinstance(model, type) and issubclass(model, BaseModel):
            return model
    except Exception as e:
        logger.debug(f"Failed to convert to Pydantic model: {e}")
    return None

def safe_serialize(obj: Any, max_depth: int = 50, _current_depth: int = 0) -> Any:
    if _current_depth >= max_depth:
        return f"<MaxDepthReached type={type(obj).__name__}>"

    if isinstance(obj, (type(None), bool, int, float, str)):
        return obj

    if isinstance(obj, bytes):
        import base64
        return {
            "_type": "binary",
            "base64": base64.b64encode(obj).decode(),
            "size": len(obj),
        }

    if isinstance(obj, BaseModel):
        return safe_serialize(obj.model_dump(), max_depth, _current_depth+1)

    if dataclasses.is_dataclass(obj) and not isinstance(obj, type):
        return safe_serialize(dataclasses.asdict(obj), max_depth, _current_depth+1)

    if isinstance(obj, (list, tuple)):
        return [safe_serialize(item, max_depth, _current_depth+1) for item in obj]

    if isinstance(obj, dict):
        return {
            str(k): safe_serialize(v, max_depth, _current_depth+1)
            for k, v in obj.items()
        }

    if hasattr(obj, "__dict__"):
        new_obj = {}
        for attr, val in obj.__dict__.items():
            new_obj[attr] = safe_serialize(val, max_depth, _current_depth+1)
        return new_obj

    return f"<Unserializable {type(obj).__name__}>"

def ensure_no_additional_props(schema: Dict[str, Any]) -> Dict[str, Any]:
    """Recursively ensure all objects in the schema have additionalProperties = false."""
    def recurse(obj: Dict[str, Any]):
        if obj.get("type") == "object":
            if "additionalProperties" not in obj:
                obj["additionalProperties"] = False
            for prop_schema in obj.get("properties", {}).values():
                if isinstance(prop_schema, dict):
                    recurse(prop_schema)
        elif obj.get("type") == "array":
            items = obj.get("items", {})
            if isinstance(items, dict):
                recurse(items)
    
    from copy import deepcopy
    new_schema = deepcopy(schema)
    recurse(new_schema)
    return new_schema

class MetadataString(str):
    """A string subclass that can hold metadata."""
    pass

class MetadataInt(int):
    """An int subclass that can hold metadata."""
    pass

class MetadataFloat(float):
    """A float subclass that can hold metadata."""
    pass

class MetadataBool(int):
    """A bool subclass that can hold metadata."""
    def __new__(cls, value):
        return super().__new__(cls, bool(value))
    
    def __bool__(self):
        return bool(int(self))
    
    def __eq__(self, other):
        if isinstance(other, bool):
            return bool(self) == other
        return super().__eq__(other)

class MetadataList(list):
    """A list subclass that can hold metadata."""
    pass

class MetadataDict(dict):
    """A dict subclass that can hold metadata."""
    pass

def wrap_primitive_for_metadata(value):
    """Wrap primitive types in metadata-capable versions."""
    if isinstance(value, str):
        return MetadataString(value)
    elif isinstance(value, bool):
        return MetadataBool(value)
    elif isinstance(value, int):
        return MetadataInt(value)
    elif isinstance(value, float):
        return MetadataFloat(value)
    elif isinstance(value, list):
        return MetadataList(value)
    elif isinstance(value, dict):
        return MetadataDict(value)
    return value