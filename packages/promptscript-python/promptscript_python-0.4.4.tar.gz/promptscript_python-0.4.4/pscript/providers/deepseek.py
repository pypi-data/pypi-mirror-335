import logging
import os
from openai import OpenAI
from .openai import OpenAIProvider
from ..config import get_config
from pydantic import BaseModel
from typing import Optional, Type, List, Dict, Any

logger = logging.getLogger(__name__)

class DeekSeekProvider(OpenAIProvider):
    def __init__(self, model_id: str):
        super().__init__(model_id)
        self.config = get_config()
    
    def _get_client(self) -> OpenAI:
        base_url = self.provider_config.base_url
        api_key = os.environ.get(self.provider_config.auth_env_var)
        if not all([base_url, api_key]):
            missing = []
            if not base_url: 
                missing.append(self.provider_config.base_url)
            if not api_key: 
                missing.append(self.provider_config.auth_env_var)
            error_msg = f"Missing required DeekSeek environment variables: {', '.join(missing)}"
            logger.error(error_msg)
            raise ValueError(error_msg)
        logger.debug("Creating DeekSeek client with configuration")
        return OpenAI(
            timeout=self.provider_config.timeout,
            base_url=base_url,
            api_key=api_key
        )

    def _prepare_completion_params(
        self, 
        messages: List[Dict[str, Any]], 
        temperature: float,
        max_tokens: int,
        functions: Optional[List[Dict[str, Any]]] = None,
        response_format: Optional[Type[BaseModel]] = None
    ) -> Dict[str, Any]:
        formatted_messages = self._prepare_messages(messages)
        model_name = self.sub_model_id
        params = {
            "model": model_name,
            "messages": formatted_messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        if functions:
            params["tools"] = [
                spec.schema for spec in self.function_registry.values() if spec.schema is not None
            ]
            params["tool_choice"] = "auto"
        if response_format:
            model_schema = response_format.model_json_schema()
            model_schema = self._enforce_no_additional_props(model_schema)
            params["response_format"] = {
                "type": "json_object",
            }
        return params
