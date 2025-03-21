import logging
import os
from openai import OpenAI
from .openai import OpenAIProvider
from ..config import get_config

logger = logging.getLogger(__name__)

class OpenRouterProvider(OpenAIProvider):
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
            error_msg = f"Missing required OpenRouter environment variables: {', '.join(missing)}"
            logger.error(error_msg)
            raise ValueError(error_msg)
        logger.debug("Creating OpenRouter client with configuration")
        return OpenAI(
            timeout=self.provider_config.timeout,
            base_url=base_url,
            api_key=api_key
        )
