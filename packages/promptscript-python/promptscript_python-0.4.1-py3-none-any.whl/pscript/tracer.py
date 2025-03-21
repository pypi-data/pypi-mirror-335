# pscript/tracer.py

import functools
import json
import inspect
import logging
import sys
import threading
import time
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, Optional

from .context import get_current_context
from .persistence import JSONPersistenceHandler
from .types import ExecutionEvent
from .utils import safe_serialize

logger = logging.getLogger(__name__)

_global_tracer_instance = None
_global_context = {}
_global_tracer_lock = threading.RLock()

def get_global_context() -> dict:
    global _global_context
    with _global_tracer_lock:
        return _global_context.copy()

class ExecutionTracer:
    def __init__(self, 
                persistence_handler: Optional[JSONPersistenceHandler] = None,
                module_name: Optional[str] = None,
                session_id: Optional[str] = None):
        # Basic tracer attributes
        self.events = {}
        self.persistence_handler = persistence_handler
        self.module_name = module_name or "__main__"
        self.session_id = session_id or str(uuid.uuid4())
        self.session_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.event_stack = []
        
        # New replay attributes
        self._events_lock = threading.RLock()
        self._contexts_lock = threading.RLock()
        self._replay_cache_lock = threading.RLock()
        self._context_id_map_lock = threading.RLock()
        
        self._contexts = {}
        self._replay_cache = {}
        self._context_id_map = {}
        
        self.replay_active = False
        self.match_mode = "strict"
        
        # Initialize root context
        root_context = get_current_context()
        if root_context:
            with self._contexts_lock:
                self._contexts[root_context.context_id] = root_context

    def load_replay_log(self, path: str, activate: bool = True, mode: str = "strict") -> int:
        """
        Load a replay log for replay.
        
        Args:
            path: Path to the replay log file
            activate: Whether to automatically activate replay mode
            mode: Replay mode - "strict", "fuzzy", or "fallback"
            
        Returns:
            Number of replay entries loaded
        """
        try:
            log_path = Path(path)
            if not log_path.exists():
                raise FileNotFoundError(f"Replay log not found: {path}")
            
            with open(log_path, 'r') as f:
                replay_data = json.load(f)
            
            # Build a replay cache for all function calls
            events = replay_data.get("events", [])
            logger.debug(f"Loading replay log with {len(events)} events from {path}")
            
            gen_count = 0
            trace_count = 0
            
            with self._replay_cache_lock:
                self._replay_cache.clear()
                
                for event in events:
                    # Skip events without results
                    if "result" not in event:
                        continue
                        
                    func_name = event.get("function_name")
                    
                    # Process gen calls (original behavior)
                    if func_name == "gen":
                        # Extract prompt text from params
                        params = event.get("params", {})
                        prompt_text = params.get("prompt_text", "")
                        
                        if prompt_text:
                            # Create a simplified key based primarily on prompt text
                            replay_key = {
                                'function_name': 'gen',
                                'prompt_text': prompt_text,
                                'context_path': event.get("metadata", {}).get("context_path", [])
                            }
                            key_json = json.dumps(replay_key, sort_keys=True)
                            self._replay_cache[key_json] = {"result": event["result"]}
                            gen_count += 1
                    
                    # Process all other traced functions - use exact arg matching
                    else:
                        # Extract key parameters
                        params = event.get("params", {})
                        args = params.get("args", [])
                        kwargs = params.get("kwargs", {})
                        
                        # Create a simple key based on function name and exact arguments
                        replay_key = {
                            'function_name': func_name,
                            'args': args,
                            'kwargs': kwargs
                        }
                        key_json = json.dumps(replay_key, sort_keys=True)
                        self._replay_cache[key_json] = {"result": event["result"]}
                        trace_count += 1
            
            logger.debug(f"Loaded {gen_count} gen() calls and {trace_count} traced function calls into replay cache")
            
            # Set replay mode
            self.match_mode = mode
            if activate:
                self.replay_active = True
                
            return len(self._replay_cache)
        except Exception as e:
            logger.error(f"Error loading replay log: {e}")
            raise

    def _generate_replay_key(self, function_name: str, inputs: Dict[str, Any], context_id: str) -> Dict[str, Any]:
        """
        Generate a deterministic key for replay matching.
        
        Args:
            function_name: Name of the function
            inputs: Function inputs
            context_id: ID of the execution context
            
        Returns:
            Dictionary with replay key information
        """
        context = None
        with self._contexts_lock:
            context = self._contexts.get(context_id)
        
        key = {
            'function_name': function_name,
            'context_id': context_id,
        }
        
        if context:
            key['context_path'] = context.context_path
        
        # Add function-specific inputs
        if function_name == "gen":
            key['prompt_text'] = inputs.get("prompt_text", "")
            key['model'] = inputs.get("model", "")
            key['temperature'] = inputs.get("temperature", 0.7)
        else:
            # For other functions, include all inputs
            for k, v in inputs.items():
                key[k] = v
        
        return key

    def _map_contexts_during_replay(self, original_contexts: Dict[str, Dict[str, Any]]) -> Dict[str, str]:
        """
        Map contexts from the original run to the current replay run.
        
        Args:
            original_contexts: Dictionary of contexts from the original run
            
        Returns:
            Dictionary mapping original context IDs to current context IDs
        """
        context_id_map = {}
        
        # Handle different context formats in test vs. actual implementation
        def get_parent_id(ctx):
            # Handle both "parent_context_id" and "parent_id" formats
            if isinstance(ctx, dict):
                return ctx.get("parent_context_id", ctx.get("parent_id"))
            else:
                return getattr(ctx, "parent_context_id", None)
        
        def get_name(ctx):
            # Handle both "name" and "context_name" formats
            if isinstance(ctx, dict):
                return ctx.get("name", ctx.get("context_name", "unknown"))
            else:
                return getattr(ctx, "name", getattr(ctx, "context_name", "unknown"))
        
        # Map root contexts first (those with no parent)
        for orig_id, orig_ctx in original_contexts.items():
            if not get_parent_id(orig_ctx):
                for replay_id, replay_ctx in self._contexts.items():
                    if (not get_parent_id(replay_ctx) and 
                        get_name(replay_ctx) == get_name(orig_ctx)):
                        context_id_map[orig_id] = replay_id
                        break
        
        # Then recursively map child contexts by parent and name
        mapped = True
        while mapped:
            mapped = False
            for orig_id, orig_ctx in original_contexts.items():
                # Skip already mapped contexts
                if orig_id in context_id_map:
                    continue
                    
                # Skip contexts whose parent isn't mapped yet
                parent_id = get_parent_id(orig_ctx)
                if not parent_id or parent_id not in context_id_map:
                    continue
                    
                # Find matching child in replay contexts
                mapped_parent = context_id_map[parent_id]
                for replay_id, replay_ctx in self._contexts.items():
                    if (get_parent_id(replay_ctx) == mapped_parent and
                        get_name(replay_ctx) == get_name(orig_ctx)):
                        context_id_map[orig_id] = replay_id
                        mapped = True
                        break
        
        return context_id_map

    def find_replay_match(self, replay_key: Dict[str, Any]) -> Optional[Any]:
        """
        Find a matching replay entry based on function information.
        
        Args:
            replay_key: Dictionary with key information
            
        Returns:
            Replay result or None if no match found
        """
        with self._replay_cache_lock:
            function_name = replay_key.get('function_name', '')
            
            # Handle gen() calls with existing logic
            if function_name == 'gen':
                # Extract the prompt text from the replay key
                prompt_text = replay_key.get('prompt_text', '')
                if not prompt_text:
                    return None
                
                # Check for an exact match on prompt text
                for key_json, entry in self._replay_cache.items():
                    try:
                        key = json.loads(key_json)
                        if key.get('function_name') == 'gen' and key.get('prompt_text') == prompt_text:
                            logger.debug(f"Found replay match for prompt: '{prompt_text}'")
                            return entry.get("result")
                    except Exception as e:
                        logger.debug(f"Error parsing cache key: {e}")
                
                # If no exact match, try a fuzzy match if enabled
                if self.match_mode in ("fuzzy", "fallback"):
                    for key_json, entry in self._replay_cache.items():
                        try:
                            key = json.loads(key_json)
                            key_prompt = key.get('prompt_text', '')
                            if key_prompt and prompt_text:
                                # Use a simple similarity threshold
                                if self._compute_similarity(key_prompt, prompt_text) >= 0.8:
                                    logger.debug(f"Found fuzzy match for prompt: '{prompt_text}'")
                                    return entry.get("result")
                        except Exception as e:
                            logger.debug(f"Error during fuzzy matching: {e}")
            
            # Handle trace_function calls with exact matching
            else:
                key_json = json.dumps(replay_key, sort_keys=True)
                if key_json in self._replay_cache:
                    logger.debug(f"Found exact match for {function_name}")
                    return self._replay_cache[key_json].get("result")
            
            # If we're in fallback mode, return None to allow live execution
            if self.match_mode == "fallback":
                logger.debug(f"No replay match found for '{function_name}', fallback to live execution")
                return None
            
            # If strict mode and no match found, raise an error
            raise ValueError(f"No replay match found for function: {function_name}")

    def _compute_similarity(self, s1: str, s2: str) -> float:
        """
        Compute similarity between two strings with an enhanced algorithm.
        
        This method uses a combination of Jaccard similarity (character-based)
        and token-based similarity to better match similar prompts during
        fuzzy replay matching.
        
        Args:
            s1: First string
            s2: Second string
            
        Returns:
            Similarity score between 0.0 and 1.0
        """
        if not s1 or not s2:
            return 0.0
        
        # Convert to lowercase for better matching
        s1_lower = s1.lower()
        s2_lower = s2.lower()
        
        # Character-based Jaccard similarity
        chars1 = set(s1_lower)
        chars2 = set(s2_lower)
        char_intersection = len(chars1.intersection(chars2))
        char_union = len(chars1.union(chars2))
        char_similarity = char_intersection / char_union if char_union > 0 else 0.0
        
        # Token-based similarity
        tokens1 = set(s1_lower.split())
        tokens2 = set(s2_lower.split())
        token_intersection = len(tokens1.intersection(tokens2))
        token_union = len(tokens1.union(tokens2))
        token_similarity = token_intersection / token_union if token_union > 0 else 0.0
        
        # Combined similarity score (weighted average)
        # Token similarity is given more weight as it's more meaningful for prompts
        combined_similarity = (0.3 * char_similarity) + (0.7 * token_similarity)
        
        return combined_similarity

    def start_event(self, function: Callable, context: Dict[str, Any]) -> ExecutionEvent:
        """
        Start tracing a function execution event.
        
        Args:
            function: The function being traced
            context: Context information for the event
            
        Returns:
            The created execution event
        """
        sig = inspect.signature(function)
        
        event = ExecutionEvent(
            session_id=self.session_id,
            function_name=function.__name__,
            params=safe_serialize(context.copy())
        )
        
        exec_context = get_current_context()
        if exec_context:
            event.context_id = exec_context.context_id
            
            # Store other context information in metadata, with safer attribute access
            event.metadata['context_path'] = getattr(exec_context, 'context_path', [])
            event.metadata['name'] = getattr(exec_context, 'name', '')
            event.metadata['thread_id'] = getattr(exec_context, 'thread_id', threading.get_ident())
            
            # Ensure the context is registered
            with self._contexts_lock:
                if exec_context.context_id not in self._contexts:
                    self._contexts[exec_context.context_id] = exec_context
        
        if self.event_stack:
            parent_id = self.event_stack[-1]
            event.parent_event_id = parent_id
            parent_event = self.events.get(parent_id)
            if parent_event:
                parent_event.add_child_event(event.id)
                self._persist_event(parent_event)

        # Associate event with current execution context
        current_context = get_current_context()
        if current_context:
            event.context_id = current_context.context_id
            # Save context path in metadata
            event.metadata['context_path'] = current_context.context_path

        event.metadata.update({
            'function_signature': str(sig),
            'function_module': function.__module__
        })

        meta = getattr(function, '__function_metadata__', None)
        if meta:
            model_name = meta.config_overrides.get('model')
            if not model_name:
                from .config import get_config
                model_name = get_config().get('model.name')
            if model_name:
                event.metadata['model_name'] = model_name

        with self._events_lock:
            self.events[event.id] = event
        self.event_stack.append(event.id)
        self._persist_event(event)
        return event

    def end_event(self, 
                event: ExecutionEvent, 
                start_time: float,
                result: Optional[Any] = None, 
                error: Optional[Exception] = None) -> None:
        """
        End tracing a function execution event.
        
        Args:
            event: The execution event to end
            start_time: Start time of the event
            result: Result of the function execution (if successful)
            error: Error from the function execution (if failed)
        """
        end_time = time.time()
        event.end_timestamp = datetime.now()
        event.duration_ms = round((end_time - start_time) * 1000, 2)
        
        if error is not None:
            event.error = str(error)
            event.error_type = type(error).__name__
            import traceback
            event.stack_trace = traceback.format_exc()
        else:
            event.result = safe_serialize(result)

        if self.event_stack and self.event_stack[-1] == event.id:
            self.event_stack.pop()

        self._persist_event(event)

    def get_current_event(self) -> Optional[ExecutionEvent]:
        """
        Get the current execution event being tracked.
        
        Returns:
            The current execution event or None if no event is in progress
        """
        if not self.event_stack:
            return None
        
        current_event_id = self.event_stack[-1]
        return self.events.get(current_event_id)

    def _persist_event(self, event: ExecutionEvent) -> None:
        """
        Persist an execution event.
        
        Args:
            event: The execution event to persist
        """
        if self.persistence_handler:
            try:
                self.persistence_handler.save_event(
                    event,
                    self.module_name,
                    self.session_timestamp
                )
            except Exception as e:
                logger.error(f"Error persisting event {event.id}: {e}")

    def save_trace(self) -> str:
        """
        Save the current trace to a file.
        
        Returns:
            Path to the saved trace file
        """
        return f".promptscript/traces/{self.session_timestamp}_{self.module_name}.json"


def get_global_tracer() -> ExecutionTracer:
    global _global_tracer_instance
    with _global_tracer_lock:
        if _global_tracer_instance is None:
            persistence_path = Path.cwd() / '.promptscript'
            handler = JSONPersistenceHandler(persistence_path)
            _global_tracer_instance = ExecutionTracer(
                persistence_handler=handler,
                module_name=getattr(sys.modules.get('__main__', {}), '__file__', '__main__')
            )
    return _global_tracer_instance


def start_run(module_name: Optional[str] = None, session_id: Optional[str] = None):
    """
    Start a new run with the given module name and session ID.
    Used for testing and to explicitly control execution sessions.
    
    Args:
        module_name: The name of the module being run
        session_id: Optional session ID (auto-generated if not provided)
    """
    global _global_tracer_instance, _global_context
    _global_context = {}
    session_id = session_id or str(uuid.uuid4())
    
    with _global_tracer_lock:
        persistence_path = Path.cwd() / '.promptscript'
        handler = JSONPersistenceHandler(persistence_path)
        _global_tracer_instance = ExecutionTracer(
            persistence_handler=handler,
            module_name=module_name or "__main__",
            session_id=session_id
        )
    
    return session_id


# Public API for replay control
def set_replay_log(path: str, activate: bool = True, mode: str = "strict") -> int:
    """
    Load a replay log for replay.
    
    Args:
        path: Path to the replay log file
        activate: Whether to automatically activate replay mode
        mode: Replay mode - "strict", "fuzzy", or "fallback"
        
    Returns:
        Number of replay entries loaded
    """
    tracer = get_global_tracer()
    return tracer.load_replay_log(path, activate, mode)


def disable_replay() -> None:
    """Disable replay mode entirely."""
    tracer = get_global_tracer()
    tracer.replay_active = False


def enable_replay() -> None:
    """Re-enable replay mode if a replay log has been loaded."""
    tracer = get_global_tracer()
    tracer.replay_active = True


def set_replay_mode(mode: str) -> None:
    """
    Set the replay mode.
    
    Args:
        mode: One of "strict", "fuzzy", or "fallback"
    """
    if mode not in ("strict", "fuzzy", "fallback"):
        raise ValueError(f"Invalid replay mode: {mode}. Must be 'strict', 'fuzzy', or 'fallback'.")
    tracer = get_global_tracer()
    tracer.match_mode = mode


def disable_replay_at(function_name: str) -> None:
    """
    Disable replay for a specific function.
    
    Args:
        function_name: Name of function where replay should stop
    """
    # This is a placeholder for now - will be implemented in runtime logic
    pass

def cache_result(func: Callable = None, *, logging_level: Optional[str] = None) -> Callable:
    """
    Decorator to trace and replay external function calls.
    
    The traced function will:
    1. Be recorded in the replay log during normal execution
    2. Be replayed from the log when replay is active
    
    Args:
        func: The function to decorate
        logging_level: Optional logging level for this function's tracing
        
    Returns:
        Decorated function with tracing and replay capabilities
    """
    def decorator(fn: Callable) -> Callable:
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            # Set logging level if specified
            if logging_level:
                from .log_config import try_latch_logging_level
                try_latch_logging_level(logging_level)
                
            tracer = get_global_tracer()
            
            event_context = {
                'function_name': fn.__name__,
                'args': args,
                'kwargs': kwargs,
            }
            
            logger.debug(f"Starting trace for function: {fn.__name__}")
            event = tracer.start_event(fn, event_context)
            
            if getattr(tracer, 'replay_active', False):
                # Create simple replay key with exact matching
                replay_key = {
                    'function_name': fn.__name__,
                    'args': safe_serialize(args),
                    'kwargs': safe_serialize(kwargs)
                }
                
                logger.debug(f"Replay active for {fn.__name__}, searching for exact match")
                
                try:
                    replay_result = tracer.find_replay_match(replay_key)
                    if replay_result is not None:
                        logger.debug(f"Found replay match for {fn.__name__}")
                        tracer.end_event(event, time.time(), result=replay_result)
                        return replay_result
                except ValueError:
                    logger.debug(f"No replay match found for {fn.__name__}, executing live...")
            
            start_time = time.time()
            try:
                logger.debug(f"Executing function {fn.__name__} with args: {args}, kwargs: {kwargs}")
                result = fn(*args, **kwargs)
                logger.debug(f"Function {fn.__name__} completed successfully")
                tracer.end_event(event, start_time, result=result)
                return result
            except Exception as e:
                logger.debug(f"Function {fn.__name__} failed with error: {e}")
                tracer.end_event(event, start_time, error=e)
                raise
        
        return wrapper
    
    if func is None:
        return decorator
    return decorator(func)