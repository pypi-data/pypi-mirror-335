import importlib
import logging
# import sys <== DEACTIVATING MLX PROVIDER FOR NOW
from .base import BaseProvider
from ..config import get_config
from ..model_registry import get_registry

logger = logging.getLogger(__name__)

MOCK_PROVIDER = None

# Maps a provider key to (module path, class name).
_PROVIDER_MAPPING = {
    'openai': ('pscript.providers.openai', 'OpenAIProvider'),
    'anthropic': ('pscript.providers.anthropic', 'AnthropicProvider'),
    'azure_openai': ('pscript.providers.azure_openai', 'AzureOpenAIProvider'),
    'gemini': ('pscript.providers.gemini', 'GeminiProvider'),
    # DEACTIVATING THESE FOR NOW UNTIL WE GET THEM WORKING PROPERLY
    # 'ollama': ('pscript.providers.ollama', 'OllamaProvider'),
    # 'deepseek': ('pscript.providers.deepseek', 'DeekSeekProvider'),
    # 'openrouter': ('pscript.providers.openrouter', 'OpenRouterProvider'),
}

# DEACTIVATING FOR NOW
# Conditionally add mlx if on macOS
# if sys.platform == 'darwin':
#     _PROVIDER_MAPPING['mlx'] = ('pscript.providers.mlx', 'MLXProvider')

def create_provider(model_id: str) -> BaseProvider:
    if MOCK_PROVIDER is not None:
        logger.debug("Returning mock provider instead of real provider")
        return MOCK_PROVIDER

    try:
        deployment_id, model_name = model_id.split('/', 1)
    except ValueError:
        raise ValueError(
            f"Invalid model ID format: {model_id}. Expected format: deployment/model_name"
        )

    registry = get_registry()
    registry.validate_model_exists(model_id)
    
    # Get configuration
    config = get_config().get_config_dict()
    
    # Check if deployment exists in deployments section
    if "deployments" in config and deployment_id in config["deployments"]:
        deployment_config = config["deployments"][deployment_id]
        provider_id = deployment_config.get("provider")
        
        if not provider_id:
            raise ValueError(f"Deployment '{deployment_id}' missing required 'provider' parameter")
            
        if provider_id not in _PROVIDER_MAPPING:
            raise ValueError(f"No provider implementation found for {provider_id}")
    else:
        # Legacy mode - deployment_id is treated as provider_id
        provider_id = deployment_id
        
        if provider_id not in _PROVIDER_MAPPING:
            raise ValueError(f"No provider implementation found for {provider_id}")

    module_name, class_name = _PROVIDER_MAPPING[provider_id]

    try:
        module = importlib.import_module(module_name)
        provider_class = getattr(module, class_name)
    except ImportError as e:
        raise ImportError(f"Could not import module '{module_name}': {e}")
    except AttributeError as e:
        raise ImportError(f"Module '{module_name}' does not define the class '{class_name}': {e}")

    logger.debug(f"Creating {provider_id} provider instance for model {model_id}")
    return provider_class(model_id)

__all__ = ['BaseProvider']
