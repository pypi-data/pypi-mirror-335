import os
import yaml
import logging
from pathlib import Path
from typing import Any, Optional, List, Callable

logger = logging.getLogger(__name__)

class ConfigurationError(Exception):
    pass

def deep_merge_dicts(base: dict, override: dict) -> dict:
    for k, v in override.items():
        if (k in base and isinstance(base[k], dict) and isinstance(v, dict)):
            deep_merge_dicts(base[k], v)
        else:
            base[k] = v
    return base

def load_and_merge_config_files(
    default_file: Optional[Path],
    extra_files: List[Path],
    deep_merge_fn: Optional[Callable] = None,
    environment: str = "development"
) -> dict:
    if deep_merge_fn is None:
        deep_merge_fn = deep_merge_dicts
    merged = {}
    if default_file:
        if not default_file.exists():
            raise ValueError(
                f"Default configuration file not found at {default_file}. "
                "This suggests an installation issue with promptscript."
            )
        try:
            with open(default_file) as f:
                default_data = yaml.safe_load(f) or {}
            if environment in default_data:
                env_data = default_data[environment]
            elif "default" in default_data:
                env_data = default_data["default"]
            else:
                env_data = default_data
            merged = deep_merge_fn(merged, env_data)
            logger.debug(f"Loaded default config from {default_file}")
        except Exception as e:
            logger.error(f"Error loading {default_file}: {e}")
            raise
    for config_file in extra_files:
        if config_file.exists():
            try:
                with open(config_file) as f:
                    cfg = yaml.safe_load(f) or {}
                if environment in cfg:
                    env_data = cfg[environment]
                elif "default" in cfg:
                    env_data = cfg["default"]
                else:
                    env_data = cfg
                merged = deep_merge_fn(merged, env_data)
                logger.debug(f"Merged config from {config_file}")
            except Exception as e:
                logger.warning(f"Error loading {config_file}: {e}")
    return merged

def find_config_files(config_filename: str = "promptscript.yml") -> List[Path]:
    files = []
    system_path = Path("/etc/promptscript") / config_filename
    if system_path.exists():
        files.append(system_path)
    home_path = Path.home() / ".promptscript" / config_filename
    if home_path.exists():
        files.append(home_path)
    cur = Path.cwd()
    upstack = []
    while cur != cur.parent:
        local_file = cur / ".promptscript" / config_filename
        if local_file.exists():
            upstack.append(local_file)
        cur = cur.parent
    files.extend(reversed(upstack))
    return files

def flatten_dict(d: dict, parent_key: str = '', sep: str = '_') -> dict:
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)

class Config:
    def __init__(self):
        self._config = {}
        self._load_main_config()
        self._maybe_load_models_file()
        self._validate_config()
        self._data = flatten_dict(self._config, 'default')

    def _load_main_config(self):
        import pscript
        default_conf = Path(pscript.__file__).parent / "promptscript-defaults.yml"
        config_files = find_config_files("promptscript.yml")
        env = os.getenv("PROMPTSCRIPT_ENV", "development")
        merged = load_and_merge_config_files(
            default_file=default_conf,
            extra_files=config_files,
            environment=env
        )
        self._config = merged

    def _maybe_load_models_file(self):
        additional = find_config_files("models.yml")
        if additional:
            # Merge them into self._config
            env = os.getenv("PROMPTSCRIPT_ENV", "development")
            models_merged = load_and_merge_config_files(
                default_file=None,
                extra_files=additional,
                environment=env
            )
            deep_merge_dicts(self._config, models_merged)

    def _validate_config(self):
        c = self._config
        must = ["model","system","persistence","logging"]
        for s in must:
            if s not in c:
                raise ConfigurationError(f"Missing required configuration: {s}")
        
        # Original validation code - providers is required
        if "providers" not in c:
            raise ConfigurationError("Missing required configuration section: 'providers'")
        
        # Handle providers section
        p = c["providers"]
        if not isinstance(p, dict):
            raise ConfigurationError("'providers' must be a dictionary")
        for pn, pc in p.items():
            if not isinstance(pc, dict):
                raise ConfigurationError(f"Provider '{pn}' must be a dictionary")
            if "timeout" not in pc:
                raise ConfigurationError(f"Provider '{pn}' missing 'timeout'")
        
        # Handle optional deployments section (new)
        if "deployments" in c:
            d = c["deployments"]
            if not isinstance(d, dict):
                raise ConfigurationError("'deployments' must be a dictionary")
            for dn, dc in d.items():
                if not isinstance(dc, dict):
                    raise ConfigurationError(f"Deployment '{dn}' must be a dictionary")
                if "timeout" not in dc:
                    raise ConfigurationError(f"Deployment '{dn}' missing 'timeout'")
                if "provider" not in dc:
                    raise ConfigurationError(f"Deployment '{dn}' missing 'provider' parameter")

        if "models" not in c:
            raise ConfigurationError("Missing required configuration section: 'models'")

        p = c["providers"]
        if not isinstance(p, dict):
            raise ConfigurationError("'providers' must be a dictionary")
        for pn, pc in p.items():
            if not isinstance(pc, dict):
                raise ConfigurationError(f"Provider '{pn}' must be a dictionary")
            if "timeout" not in pc:
                raise ConfigurationError(f"Provider '{pn}' missing 'timeout'")

        m = c["models"]
        if not isinstance(m, dict):
            raise ConfigurationError("'models' must be a dictionary")
        for mn, md in m.items():
            if not isinstance(md, dict):
                raise ConfigurationError(f"Model '{mn}' must be a dictionary")
            if "capabilities" not in md or not isinstance(md["capabilities"], list):
                raise ConfigurationError(f"Model '{mn}' must have a 'capabilities' list")
            if "parameters" not in md or not isinstance(md["parameters"], dict):
                raise ConfigurationError(f"Model '{mn}' must have a 'parameters' dict")
            pm = md["parameters"]
            if "temperature_range" not in pm or not isinstance(pm["temperature_range"], list):
                raise ConfigurationError(f"Model '{mn}' missing 'temperature_range' list")
            if "max_tokens_range" not in pm or not isinstance(pm["max_tokens_range"], list):
                raise ConfigurationError(f"Model '{mn}' missing 'max_tokens_range' list")
            if "supports_streaming" not in md or not isinstance(md["supports_streaming"], bool):
                raise ConfigurationError(f"Model '{mn}' must have a boolean 'supports_streaming'")
            if "azure" in md and not isinstance(md["azure"], dict):
                raise ConfigurationError(f"Model '{mn}' 'azure' must be a dictionary if provided")

        s = c["system"]
        if not isinstance(s, dict):
            raise ConfigurationError("'system' must be a dictionary")
        if "prompt" not in s or not isinstance(s["prompt"], str):
            raise ConfigurationError("'system.prompt' must be a string")

        ps = c["persistence"]
        if not isinstance(ps, dict):
            raise ConfigurationError("'persistence' must be a dictionary")
        if "enabled" not in ps or not isinstance(ps["enabled"], bool):
            raise ConfigurationError("'persistence.enabled' must be a boolean")
        if "path" not in ps or not isinstance(ps["path"], str):
            raise ConfigurationError("'persistence.path' must be a string")

        lg = c["logging"]
        if not isinstance(lg, dict):
            raise ConfigurationError("'logging' must be a dictionary")
        if "level" not in lg or not isinstance(lg["level"], str):
            raise ConfigurationError("'logging.level' must be a string")
        if "format" not in lg or not isinstance(lg["format"], str):
            raise ConfigurationError("'logging.format' must be a string")

        mc = c["model"]
        if not isinstance(mc, dict):
            raise ConfigurationError("'model' must be a dictionary")
        if "name" not in mc or not isinstance(mc["name"], str):
            raise ConfigurationError("'model.name' must be a string")
        if "temperature" not in mc or not isinstance(mc["temperature"], (int, float)):
            raise ConfigurationError("'model.temperature' must be a number")
        if "max_tokens" not in mc or not isinstance(mc["max_tokens"], int):
            raise ConfigurationError("'model.max_tokens' must be an integer")

        # Optionally validate `model.strict_mode`
        if "strict_mode" in mc and not isinstance(mc["strict_mode"], bool):
            raise ConfigurationError("'model.strict_mode' must be a boolean if provided")

        # If present, validate model_fallback
        if "model_fallback" in c:
            mf = c["model_fallback"]
            if not isinstance(mf, dict):
                raise ConfigurationError("'model_fallback' must be a dictionary if present")
            if "capabilities" not in mf or not isinstance(mf["capabilities"], list):
                raise ConfigurationError("'model_fallback.capabilities' must be a list")
            if "parameters" not in mf or not isinstance(mf["parameters"], dict):
                raise ConfigurationError("'model_fallback.parameters' must be a dict")
            if "supports_streaming" not in mf or not isinstance(mf["supports_streaming"], bool):
                raise ConfigurationError("'model_fallback.supports_streaming' must be a boolean")

            # Check `parameters` contents
            fallback_params = mf["parameters"]
            if "temperature_range" not in fallback_params or not isinstance(fallback_params["temperature_range"], list):
                raise ConfigurationError("'model_fallback.parameters.temperature_range' must be a list")
            if "max_tokens_range" not in fallback_params or not isinstance(fallback_params["max_tokens_range"], list):
                raise ConfigurationError("'model_fallback.parameters.max_tokens_range' must be a list")

            # Optionally check max_function_calls if present
            if "max_function_calls" in mf and not isinstance(mf["max_function_calls"], int):
                raise ConfigurationError("'model_fallback.max_function_calls' must be an integer if provided")

    def get_config_dict(self) -> dict:
        return self._config

    def get(self, key: str, default: Any = None) -> Any:
        val = self._config
        for part in key.split('.'):
            if not isinstance(val, dict):
                return default
            val = val.get(part)
            if val is None:
                return default
        return val

    def merge_runtime_config(self, **overrides) -> 'Config':
        merged = dict(self._data)
        merged.update(overrides)
        c = Config.__new__(Config)
        c._config = dict(self._config)
        c._data = merged
        return c

_global_config: Optional[Config] = None

def set_global_config(config: Config) -> None:
    global _global_config
    _global_config = config

def get_config() -> Config:
    global _global_config
    if _global_config is None:
        _global_config = Config()
    return _global_config
