import ast
import inspect
import logging
import textwrap
from typing import Any, Dict, Tuple, Callable, get_type_hints

from .types import FunctionMetadata, FunctionConfig
from .config import get_config

logger = logging.getLogger(__name__)

class FunctionAnalyzer:
    def __init__(self):
        pass

    def process_function(self, func: Callable, config_overrides: Dict[str, Any], decorator_type: str) -> FunctionMetadata:
        type_hints = get_type_hints(func)
        sig = inspect.signature(func)
        parameters = list(sig.parameters.values())
        param_name = None
        param_type = str
        if parameters:
            param_name = parameters[0].name
            param_type = type_hints.get(param_name, str)

        return_type = type_hints.get('return', str)

        source = inspect.getsource(func)
        source = textwrap.dedent(source)
        tree = ast.parse(source)
        main_func_node, nested_functions = self._analyze_ast_for_function(func, tree)

        pdef = FunctionMetadata(
            nested_functions=nested_functions,
            param_name=param_name,
            param_type=param_type,
            return_type=return_type,
            decorator_type=decorator_type,
            function_name=func.__name__,
            config_overrides=config_overrides
        )

        global_cfg = get_config()
        default_model_name = global_cfg.get("default_model_name", "azure_openai/gpt-4o-mini")
        default_temperature = global_cfg.get("default_model_temperature", 0.7)
        default_max_tokens = global_cfg.get("default_max_tokens", 2048)
        default_system_prompt = global_cfg.get("default_system_prompt", "You are a helpful assistant.")

        user_model = config_overrides.get("model")
        user_temp = config_overrides.get("temperature")
        user_max_tokens = config_overrides.get("max_tokens")
        user_sys_prompt = config_overrides.get("system_prompt")

        final_values = dict(
            model=(user_model if user_model is not None else default_model_name),
            temperature=(user_temp if user_temp is not None else default_temperature),
            max_tokens=(user_max_tokens if user_max_tokens is not None else default_max_tokens),
            system_prompt=(user_sys_prompt if user_sys_prompt is not None else default_system_prompt)
        )

        try:
            typed_config = FunctionConfig(**final_values)
        except Exception as e:
            logger.error(f"Error creating typed config for '{func.__name__}': {e}")
            raise

        pdef.final_config = typed_config
        return pdef

    def _analyze_ast_for_function(self, func: Callable, tree: ast.Module) -> Tuple[ast.FunctionDef, Dict[str, Dict[str, Any]]]:
        main_func_node = None
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == func.__name__:
                main_func_node = node
                break
        if not main_func_node:
            raise ValueError(f"Could not find function definition for '{func.__name__}' in the source.")

        nested_functions = self._extract_nested_functions_ast(func, main_func_node)
        return main_func_node, nested_functions

    def _extract_nested_functions_ast(self, func: Callable, main_func_node: ast.FunctionDef) -> Dict[str, Dict[str, Any]]:
        nested_functions = {}

        def _extract_single_nested_function(node: ast.FunctionDef) -> Dict[str, Any]:
            docstring = ast.get_docstring(node) or ""
            
            annotations = {}
            for arg in node.args.args:
                if arg.annotation:
                    annotation_str = ast.unparse(arg.annotation)
                    try:
                        annotations[arg.arg] = eval(annotation_str, func.__globals__)
                    except Exception as e:
                        logger.warning(f"Could not evaluate type annotation for {arg.arg}: {e}")
                        
            if node.returns:
                return_type_str = ast.unparse(node.returns)
                try:
                    annotations['return'] = eval(return_type_str, func.__globals__)
                except Exception as e:
                    logger.warning(f"Could not evaluate return type annotation: {e}")

            return {
                "docstring": docstring,
                "annotations": annotations
            }

        for node in main_func_node.body:
            if isinstance(node, ast.FunctionDef):
                nested_functions[node.name] = _extract_single_nested_function(node)

        return nested_functions