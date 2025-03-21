import logging
import os
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from openai import AzureOpenAI, RateLimitError, APIConnectionError, AuthenticationError
from pydantic import BaseModel
from typing import Any, Dict, List, Optional, Type, get_origin
from .openai import OpenAIProvider
from ..config import get_config

logger = logging.getLogger(__name__)

class AzureOpenAIProvider(OpenAIProvider):
    def __init__(self, model_id: str):
        super().__init__(model_id)
        self.config = get_config()
        self._param_mapping = {
            "azure_openai_endpoint": "base_url",
            "azure_openai_deployment": "deployment_name",
            "azure_openai_api_version": "api_version",
        }
        
    # Override update_config to map Azure-specific friendly parameters to internal ones
    def update_config(self, config_overrides: Dict[str, Any]) -> None:
        """
        Update configuration with special handling for Azure-specific parameters.
        Maps user-friendly parameter names to internal ones used by the provider.
        """
        # Log input parameters for debugging
        logger.debug(f"AzureOpenAIProvider.update_config received: {config_overrides}")
        
        # First, check for Azure-specific parameters and map them to internal names
        for user_key, internal_key in self._param_mapping.items():
            if user_key in config_overrides and config_overrides[user_key] is not None:
                # Map the user-friendly name to the internal one
                config_overrides[internal_key] = config_overrides[user_key]
                logger.debug(f"Mapped {user_key}={config_overrides[user_key]} to {internal_key}")
                
        # Then proceed with the standard update
        super().update_config(config_overrides)
        logger.debug(f"After update_config, _config_overrides: {self._config_overrides}")
    
    # Override get_config_value to handle Azure-specific parameter mapping
    def get_config_value(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value with Azure-specific parameter mapping.
        
        This overrides the base implementation to add support for user-friendly
        parameter names like azure_openai_endpoint, azure_openai_deployment, etc.
        """
        # Check if this is a user-friendly key that maps to an internal one
        if key in self._param_mapping:
            internal_key = self._param_mapping[key]
            # Check for the internal key in overrides
            if hasattr(self, '_config_overrides') and internal_key in self._config_overrides:
                return self._config_overrides[internal_key]
        
        # Check if this is an internal key that might have been set via a user-friendly name
        if key in self._param_mapping.values():
            user_key = next((k for k, v in self._param_mapping.items() if v == key), None)
            if user_key and hasattr(self, '_config_overrides') and user_key in self._config_overrides:
                return self._config_overrides[user_key]
        
        # Fall back to the normal config resolution
        return super().get_config_value(key, default)
    
    def _get_client(self) -> AzureOpenAI:
        """
        Get an Azure OpenAI client with appropriate authentication.
        """
        logger.debug(f"AzureOpenAIProvider._get_client called with _config_overrides: {self._config_overrides}")
        
        # Directly try to get each value using get_config_value which handles the mapping
        base_url = self.get_config_value("base_url", 
                   self.get_config_value("azure_openai_endpoint"))
        
        deployment_name = self.get_config_value("deployment_name", 
                          self.get_config_value("azure_openai_deployment"))
        
        api_version = self.get_config_value("api_version",
                     self.get_config_value("azure_openai_api_version"))
        
        logger.debug(f"Resolved values: base_url={base_url}, deployment_name={deployment_name}, api_version={api_version}")
        
        # If we have all the direct parameters, use them
        if base_url and deployment_name and api_version:
            auth_type = self.get_config_value("authentication", "token")
            
            logger.debug(f"Using direct config parameters: endpoint={base_url}, deployment={deployment_name}, api_version={api_version}, auth_type={auth_type}")
            
            client_args = {
                'timeout': self.get_config_value("timeout", 300),
                'azure_endpoint': base_url,
                'azure_deployment': deployment_name,
                'api_version': api_version,
            }
        # COMPATIBILITY MODE: Check if we have the existing azure configuration in model_config
        elif (hasattr(self.model_config, 'azure_deployment') and 
              hasattr(self.model_config, 'openai_api_version') and
              self.model_config.azure_deployment is not None and
              self.model_config.openai_api_version is not None):
            
            # Use existing approach - get values from environment variables specified in model config
            base_url = os.environ.get(self.provider_config["base_url"])
            azure_deployment = os.environ.get(self.model_config.azure_deployment)
            api_version = os.environ.get(self.model_config.openai_api_version)
            
            # Check required env vars
            required_vars = {
                self.provider_config["base_url"]: base_url,
                self.model_config.azure_deployment: azure_deployment,
                self.model_config.openai_api_version: api_version,
            }
            
            missing = [var_name for var_name, value in required_vars.items() if not value]
            if missing:
                error_msg = f"Missing required Azure environment variables: {', '.join(missing)}"
                logger.error(error_msg)
                raise ValueError(error_msg)
                
            auth_type = self.get_config_value("authentication", "local")
            
            client_args = {
                'timeout': self.get_config_value("timeout", 300),
                'azure_endpoint': base_url,
                'azure_deployment': azure_deployment,
                'api_version': api_version,
            }
        else:
            # NEW APPROACH: Get configuration values with priority order:
            # 1. Runtime overrides (passed via decorator or gen() params)
            # 2. Deployment configuration 
            # 3. Environment variables
            base_url = self.get_config_value("base_url")
            api_version = self.get_config_value("api_version")
            deployment_name = self.get_config_value("deployment_name")
            
            # Check required values
            required_vars = {
                "base_url": base_url,
                "api_version": api_version,
                "deployment_name": deployment_name,
            }
            
            missing = [var_name for var_name, value in required_vars.items() if not value]
            if missing:
                error_msg = f"Missing required Azure OpenAI configuration values: {', '.join(missing)}"
                logger.error(error_msg)
                raise ValueError(error_msg)
                
            auth_type = self.get_config_value("authentication", "local")
            
            client_args = {
                'timeout': self.get_config_value("timeout", 300),
                'azure_endpoint': base_url,
                'azure_deployment': deployment_name,
                'api_version': api_version,
            }

        try:
            if auth_type == 'token':
                # Get API key from runtime config or environment variable
                api_key = self.get_config_value("api_key")
                auth_env_var = self.get_config_value("auth_env_var")
                
                if not api_key and auth_env_var:
                    api_key = os.environ.get(auth_env_var)
                    
                if not api_key:
                    # Try AZURE_OPENAI_API_KEY as a fallback
                    api_key = os.environ.get("AZURE_OPENAI_API_KEY")
                    logger.debug(f"Trying AZURE_OPENAI_API_KEY as fallback: {'found' if api_key else 'not found'}")
                    
                if not api_key:
                    raise ValueError(
                        f"Missing required API key for token-based authentication. "
                        f"Either set the environment variable {auth_env_var}, "
                        f"specify it in configuration, or pass api_key parameter."
                    )
                client_args['api_key'] = api_key
            elif auth_type == 'local':
                # Use DefaultAzureCredential but exclude unnecessary credential types
                # to avoid timeouts when using local az login credentials
                client_args['azure_ad_token_provider'] = get_bearer_token_provider(
                    DefaultAzureCredential(
                        exclude_workload_identity_credential=True,
                        exclude_managed_identity_credential=True,
                        exclude_shared_token_cache_credential=True,
                        exclude_environment_credential=True,
                    ),
                    "https://cognitiveservices.azure.com/.default"
                )
                logger.debug("Using local authentication mode with optimized credential chain")
            else:  # client (default) or managed (backward compatibility)
                # For backward compatibility, treat 'managed' the same as 'client'
                client_args['azure_ad_token_provider'] = get_bearer_token_provider(
                    DefaultAzureCredential(),
                    "https://cognitiveservices.azure.com/.default"
                )
            
            logger.debug(f"Creating Azure OpenAI client with {auth_type} authentication")
            return AzureOpenAI(**client_args)
            
        except AuthenticationError as e:
            if auth_type in ['client', 'managed', 'local']:
                auth_display = "Azure AD" if auth_type == 'client' else auth_type
                error_msg = (
                    f"Failed to authenticate using {auth_display} credentials. Ensure your environment "
                    "is properly configured for Azure authentication. If you need "
                    "to use API key authentication instead, you can set authentication='token' "
                    "in the @prompt decorator or gen() parameters."
                )
            else:
                error_msg = (
                    "Failed to authenticate using API key. Please check your "
                    "API key configuration."
                )
            raise AuthenticationError(f"{error_msg}\nOriginal error: {str(e)}")
        except Exception as e:
            raise ValueError(f"Failed to create Azure OpenAI client: {str(e)}")

    def _create_llm_retry_decorator(self, func):
        """
        Creates a retry decorator for Azure OpenAI API calls.
        Only retry on rate limits and connection errors, not auth errors.
        """
        return self._create_retry_decorator((RateLimitError, APIConnectionError))(func)
    
    # Override _prepare_completion_params to handle Azure-specific deployment
    def _prepare_completion_params(
        self,
        messages: List[Dict[str, Any]],
        temperature: float,
        max_tokens: int,
        functions: Optional[List[Dict[str, Any]]] = None,
        response_format: Optional[Type] = None
    ) -> Dict[str, Any]:
        """
        Prepare the parameters for the completion API call.
        
        For Azure OpenAI, the model parameter is required by the SDK, even though
        the deployment is already specified in the client initialization.
        """
        normalized_msgs = self._normalize_messages(messages)
        
        # For Azure OpenAI, we need to include the model parameter
        # We use the deployment name as the model parameter - it satisfies the SDK requirement
        deployment_name = self.get_config_value("deployment_name", 
                         self.get_config_value("azure_openai_deployment"))
        
        params = {
            "messages": normalized_msgs,
            "stream": False,
            "model": deployment_name  # Add the model parameter required by the SDK
        }
        
        # Handle temperature differently for o3 models
        is_o3_model = 'o3' in self.sub_model_id.lower()
        if not is_o3_model:
            params["temperature"] = temperature
        
        # Max tokens parameter differs between o3 and other models
        if is_o3_model:
            params["max_completion_tokens"] = max_tokens
        else:
            params["max_tokens"] = max_tokens
            
        # Add tools/functions if provided
        tools = []
        if functions:
            for spec in self.function_registry.values():
                if spec.schema is not None:
                    tools.append(spec.schema)
            if tools:
                params["tools"] = tools
                params["tool_choice"] = "auto"

        # Add response_format if provided
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
            
        # Add instrumentation and logging
        logger.debug(f"Azure OpenAI prepared params: {params}")
        
        return params