import json
import base64
import logging
from typing import Any, Optional

_latched_logging_level: Optional[str] = None
VALID_LEVELS = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}

def format_object(obj: Any, max_length: int = 40) -> str:
    def truncate_string(s: str) -> str:
        if len(s) <= max_length:
            return s
        return f"{s[:20]}...{s[-20:]}"
    def bytes_to_base64(b: bytes) -> str:
        return truncate_string(base64.b64encode(b).decode('utf-8'))
    def truncate_object(o: Any) -> Any:
        if isinstance(o, str):
            return truncate_string(o)
        elif isinstance(o, bytes):
            return bytes_to_base64(o)
        elif isinstance(o, dict):
            return {k: truncate_object(v) for k, v in o.items()}
        elif isinstance(o, list):
            return [truncate_object(item) for item in o]
        elif hasattr(o, '__dict__'):
            return truncate_object(o.__dict__)
        return o
    def json_serializer(o: Any) -> Any:
        if isinstance(o, bytes):
            return bytes_to_base64(o)
        elif hasattr(o, '__dict__'):
            return o.__dict__
        return str(o)
    try:
        json_obj = json.loads(json.dumps(obj, default=json_serializer))
        return json.dumps(truncate_object(json_obj), indent=2)
    except Exception as e:
        return f"Error formatting object: {str(e)}"

def init_logging_once(level: Optional[str] = None):
    global _latched_logging_level
    if _latched_logging_level is not None:
        if level and level.upper() != _latched_logging_level:
            logging.warning(f"Ignoring attempt to change logging level to '{level}'. "
                            f"Already latched at '{_latched_logging_level}'.")
        return
    if not level:
        level = "WARNING"
    if level.upper() not in VALID_LEVELS:
        raise RuntimeError(f"Invalid logging level: {level}")
    numeric_level = getattr(logging, level.upper(), logging.WARNING)
    logging.basicConfig(
        level=numeric_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        force=True
    )
    # Noisy logs
    logging.getLogger('httpx').setLevel(logging.WARNING)
    logging.getLogger('httpcore').setLevel(logging.WARNING)
    logging.getLogger('openai').setLevel(logging.WARNING)
    logging.getLogger('anthropic').setLevel(logging.WARNING)
    logging.getLogger('PIL').setLevel(logging.WARNING)
    logging.getLogger('filelock').setLevel(logging.WARNING)
    _latched_logging_level = level.upper()
    logging.debug(f"Latched logging level set to: {_latched_logging_level}")

def configure_logging(log_level: str = 'WARNING'):
    init_logging_once(log_level)

def try_latch_logging_level(level: Optional[str]) -> None:
    init_logging_once(level)