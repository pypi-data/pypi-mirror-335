import base64
import json
import logging
import ollama
import re
from pprint import pformat
from pydantic import BaseModel
from typing import Optional, Type, List, Dict, Any, Callable
from .base import BaseProvider
from ..model_registry import ModelCapability
from ..schema_builder import build_function_schema, NotSupportedError
from ..utils import convert_to_expected_type, validate_type

logger = logging.getLogger(__name__)

class ImageJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, bytes):
            preview = base64.b64encode(obj[:20]).decode("utf-8")
            return {
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": "image/jpeg",
                    "data_preview": f"{preview}... ({len(obj)} bytes total)",
                },
            }
        return super().default(obj)

class OllamaProvider(BaseProvider):
    def validate_auth(self) -> None:
        pass

    def _create_function_schema(self, func: Callable) -> Optional[Dict[str, Any]]:
        if func.__name__.startswith("_"):
            return None
        try:
            return build_function_schema(
                func,
                provider_capabilities={"allow_lists": True},
                strict=True,
                format="default",
            )
        except NotSupportedError as e:
            logger.warning(f"Skipping function {func.__name__} for Ollama: {e}")
            return None

    def call_model(
        self,
        messages: List[Dict[str, Any]],
        images: Optional[List[Dict[str, Any]]] = None,
        response_format: Optional[Type[BaseModel]] = None,
        functions: Optional[List[Dict[str, Any]]] = None,
    ) -> Any:
        if images:
            self.model_config.validate_capability(ModelCapability.IMAGES)

        def format_messages(msgs: List[Dict[str, Any]], imgs: Optional[List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
            formatted = []
            for message in msgs:
                role = "assistant" if message["role"] == "model" else message["role"]
                formatted_msg = {"role": role, "content": message["content"]}
                if message["role"] == "user" and imgs and not any(m.get("images") for m in formatted):
                    image_data = []
                    for img in imgs:
                        image_format = self._get_image_type(img["data"])
                        mime_types = img.get("mime_types", [])
                        if image_format not in mime_types:
                            raise ValueError(f"Image format {image_format} not in supported list {mime_types}")
                        image_data.append(img["data"])
                    formatted_msg["images"] = image_data
                formatted.append(formatted_msg)
            return formatted

        formatted_messages = format_messages(messages, images)
        tools = []
        if functions:
            for spec in self.function_registry.values():
                if spec.schema is not None:
                    tools.append(spec.schema)
            logger.debug(f"Generated function tools for Ollama: {json.dumps(tools, indent=2)}")

        @self._create_retry_decorator((Exception,))
        def call_ollama_api(msgs: List[Dict[str, Any]], tools_param: Optional[List[Dict[str, Any]]]) -> Any:
            payload = {"messages": msgs}
            logger.debug(f"Calling Ollama API with params:\n{json.dumps(payload, indent=2, cls=ImageJSONEncoder)}")
            response = ollama.chat(
                model=self.sub_model_id, messages=msgs, stream=False, tools=tools_param
            )
            logger.debug(f"Received Ollama API response:\n{pformat(response)}")
            return response

        response = call_ollama_api(formatted_messages, tools if tools else None)
        if functions and response.get("message", {}).get("tool_calls"):
            call_count = 0
            max_calls = self.model_config.get_max_function_calls() or 10
            conversation = formatted_messages.copy()
            while response.get("message", {}).get("tool_calls") and call_count < max_calls:
                for tool in response["message"].get("tool_calls", []):
                    call_count += 1
                    function_info = tool.get("function", {})
                    function_name = function_info.get("name")
                    function_args = function_info.get("arguments", {})
                    if function_name in self.function_registry:
                        try:
                            result = self.execute_function(function_name, function_args)
                        except Exception as e:
                            result = str(e)
                        logger.debug(f"Executed function '{function_name}' with arguments {function_args}. Result: {result}")
                    else:
                        logger.warning(f"Function not found: {function_name}")
                        result = f"Function '{function_name}' not found."
                    conversation.append({
                        "role": "tool",
                        "content": json.dumps({"result": result if isinstance(result, (dict, list)) else str(result)}),
                    })
                response = call_ollama_api(conversation, tools if tools else None)
                if not response.get("message", {}).get("tool_calls"):
                    break
        content = response.get("message", {}).get("content", "")
        # Remove lines starting with backticks.
        content = "\n".join(line for line in content.splitlines() if not re.match(r"^``", line))
        if response_format is None or response_format is str:
            return content
        if response_format in (int, float, bool):
            return convert_to_expected_type(content, response_format)
        try:
            answer = json.loads(content)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse JSON response: {e}\nResponse content: {content}")
        return validate_type(answer, response_format)
