import logging
from dataclasses import dataclass
from enum import Enum, auto
from typing import Dict, Optional, Set
from .config import get_config
logger = logging.getLogger(__name__)

class ModelCapability(Enum):
    TEXT = auto()
    IMAGES = auto()
    STRUCTURED_OUTPUT = auto()
    FUNCTION_CALLING = auto()

@dataclass
class TokenLimits:
    max_total: int
    max_prompt: int
    max_completion: int
    def validate_counts(self, prompt_tokens: int, completion_tokens: int) -> None:
        total_tokens = prompt_tokens + completion_tokens
        if total_tokens > self.max_total:
            raise ValueError(f"Total tokens {total_tokens} exceeds limit {self.max_total}")
        if prompt_tokens > self.max_prompt:
            raise ValueError(f"Prompt tokens {prompt_tokens} exceeds limit {self.max_prompt}")
        if completion_tokens > self.max_completion:
            raise ValueError(f"Completion tokens {completion_tokens} exceeds limit {self.max_completion}")

@dataclass
class ModelParameters:
    temperature_range: tuple[float, float] = (0.0, 2.0)
    max_tokens_range: tuple[int, int] = (1, 4096)
    def validate_temperature(self, temp: float) -> None:
        mn, mx = self.temperature_range
        if not mn <= temp <= mx:
            raise ValueError(f"Temperature {temp} outside [{mn},{mx}]")
    def validate_max_tokens(self, tokens: int) -> None:
        mn, mx = self.max_tokens_range
        if not mn <= tokens <= mx:
            raise ValueError(f"max_tokens {tokens} outside [{mn},{mx}]")

@dataclass
class ProviderDefinition:
    base_url: Optional[str]
    timeout: int
    auth_env_var: Optional[str] = None

@dataclass
class ModelDefinition:
    capabilities: Set[ModelCapability]
    token_limits: TokenLimits
    parameters: ModelParameters
    supports_streaming: bool
    azure_deployment: Optional[str] = None
    openai_api_version: Optional[str] = None
    max_function_calls: Optional[int] = None
    def get_max_function_calls(self) -> int:
        return self.max_function_calls if self.max_function_calls is not None else 10
    def validate_capability(self, cap: ModelCapability) -> None:
        if cap not in self.capabilities:
            raise ValueError(f"Model does not support {cap.name}")
    def validate_auth(self) -> None:
        pass

class ModelRegistry:
    def __init__(self):
        self.models: Dict[str, ModelDefinition] = {}
        self.providers: Dict[str, ProviderDefinition] = {}
        self._build_definitions()

    def _build_definitions(self):
        cfg = get_config().get_config_dict()
        providers_cfg = cfg["providers"]
        models_cfg = cfg["models"]

        # Build providers
        for pid, pdef in providers_cfg.items():
            try:
                self.providers[pid] = ProviderDefinition(
                    base_url=pdef.get('base_url'),
                    timeout=pdef.get('timeout', 300),
                    auth_env_var=pdef.get('auth_env_var')
                )
            except Exception as e:
                logger.error(f"Cannot load provider {pid}: {e}")

        # Build known models
        for mid, mdef in models_cfg.items():
            try:
                cset = {ModelCapability[x.upper()] for x in mdef["capabilities"]}
                azure_deploy = mdef.get("azure", {}).get("azure_deployment")
                openai_api_ver = mdef.get("azure", {}).get("openai_api_version")
                mx_func = mdef.get("max_function_calls")
                self.models[mid] = ModelDefinition(
                    capabilities=cset,
                    token_limits=TokenLimits(4096, 3072, 1024),
                    parameters=ModelParameters(
                        temperature_range=tuple(mdef["parameters"]["temperature_range"]),
                        max_tokens_range=tuple(mdef["parameters"]["max_tokens_range"])
                    ),
                    supports_streaming=mdef["supports_streaming"],
                    azure_deployment=azure_deploy,
                    openai_api_version=openai_api_ver,
                    max_function_calls=mx_func
                )
            except Exception as e:
                logger.error(f"Cannot load model {mid}: {e}")

    def get_model(self, model_id: str) -> ModelDefinition:
        cfg = get_config().get_config_dict()
        # If the model is known, return it immediately
        if model_id in self.models:
            return self.models[model_id]

        # Not found -> check strict_mode
        strict_mode = cfg["model"].get("strict_mode", False)
        if strict_mode:
            raise ValueError(f"Unknown model: {model_id} (strict mode is enabled).")

        # If we have no fallback config, we must fail
        if "model_fallback" not in cfg:
            raise ValueError(
                f"Unknown model: {model_id}. No 'model_fallback' defined, and strict_mode=false."
            )

        # Build from fallback
        fallback_cfg = cfg["model_fallback"]
        return self._create_fallback_model_definition(fallback_cfg, model_id)

    def _create_fallback_model_definition(self, fallback_cfg: dict, model_id: str) -> ModelDefinition:
        # Convert capability strings -> ModelCapability
        cap_enum_set = set()
        for cap_str in fallback_cfg["capabilities"]:
            cap_enum_set.add(ModelCapability[cap_str.upper()])

        # Example fallback token limits for all unknown models
        token_limits = TokenLimits(
            max_total=4096,
            max_prompt=3072,
            max_completion=1024
        )

        # Build the parameter object from fallback
        params = ModelParameters(
            temperature_range=tuple(fallback_cfg["parameters"]["temperature_range"]),
            max_tokens_range=tuple(fallback_cfg["parameters"]["max_tokens_range"])
        )

        # Max function calls fallback
        mx_calls = fallback_cfg.get("max_function_calls", 10)

        logger.info(f"Falling back to model_fallback for unregistered model: {model_id}")
        return ModelDefinition(
            capabilities=cap_enum_set,
            token_limits=token_limits,
            parameters=params,
            supports_streaming=fallback_cfg["supports_streaming"],
            azure_deployment=None,
            openai_api_version=None,
            max_function_calls=mx_calls
        )

    def get_provider(self, provider_id: str) -> ProviderDefinition:
        if provider_id not in self.providers:
            raise ValueError(f"Unknown provider: {provider_id}")
        return self.providers[provider_id]

    def validate_model_exists(self, model_id: str) -> None:
        if model_id not in self.models:
            cfg = get_config().get_config_dict()
            strict_mode = cfg["model"].get("strict_mode", False)
            if strict_mode:
                raise ValueError(f"Unknown model: {model_id} (strict mode is enabled).")
            if "model_fallback" not in cfg:
                raise ValueError(
                    f"Unknown model: {model_id}, no fallback available, and not in config."
                )

_registry: Optional['ModelRegistry'] = None

def get_registry() -> ModelRegistry:
    global _registry
    if _registry is None:
        _registry = ModelRegistry()
    return _registry
