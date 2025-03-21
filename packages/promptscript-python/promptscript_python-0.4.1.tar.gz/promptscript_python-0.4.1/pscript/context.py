# pscript/context.py

import threading
import uuid
from typing import Optional, Dict, Any, List

class ExecutionContext:
    """
    Represents the execution context for a function or section of code.
    Used to track the flow of execution across function calls and threads.
    """
    def __init__(
        self,
        context_id: Optional[str] = None,
        parent_context_id: Optional[str] = None,
        context_path: Optional[List[str]] = None,
        name: Optional[str] = None,
        thread_id: Optional[int] = None
    ):
        self.context_id = context_id or str(uuid.uuid4())
        self.parent_context_id = parent_context_id
        self.context_path = context_path or []
        self.name = name or f"context_{self.context_id[:8]}"
        self.thread_id = thread_id or threading.get_ident()
    
    def create_child_context(self, name: Optional[str] = None) -> 'ExecutionContext':
        """
        Create a child context that inherits from this context.
        
        Args:
            name: Optional name for the child context
            
        Returns:
            A new ExecutionContext that is a child of this context
        """
        from .tracer import get_global_tracer
        
        child_id = str(uuid.uuid4())
        child_name = name or f"child_{child_id[:8]}"
        
        # Create new path by appending to the parent's path
        child_path = self.context_path.copy()
        child_path.append(f"{self.name}/{child_name}")
        
        child_context = ExecutionContext(
            context_id=child_id,
            parent_context_id=self.context_id,
            context_path=child_path,
            name=child_name,
            thread_id=threading.get_ident()
        )
        
        # Register with the tracer
        tracer = get_global_tracer()
        with tracer._contexts_lock:
            tracer._contexts[child_context.context_id] = child_context
            
        return child_context
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the context to a dictionary representation.
        """
        return {
            "context_id": self.context_id,
            "parent_context_id": self.parent_context_id,
            "context_path": self.context_path,
            "name": self.name,
            "thread_id": self.thread_id
        }


class ThreadLocalContextProvider:
    """
    Provides thread-local storage for execution contexts.
    """
    def __init__(self):
        self._thread_local = threading.local()
        
    def get_current_context(self) -> Optional[ExecutionContext]:
        """
        Get the current execution context for this thread.
        Returns None if no context has been set.
        """
        return getattr(self._thread_local, 'current_context', None)
    
    def set_current_context(self, context: ExecutionContext) -> None:
        """
        Set the current execution context for this thread.
        """
        self._thread_local.current_context = context


# Global instance of the context provider
_context_provider = ThreadLocalContextProvider()

def get_current_context() -> Optional[ExecutionContext]:
    """
    Get the current execution context.
    Returns None if no context has been set.
    """
    return _context_provider.get_current_context()

def set_current_context(context: ExecutionContext) -> None:
    """
    Set the current execution context.
    """
    _context_provider.set_current_context(context)

def reset_current_context() -> None:
    """
    Reset the current thread's execution context to None.
    This is useful for testing or when you want to start fresh with a new root context.
    """
    _context_provider.set_current_context(None)

def create_child_context(name: Optional[str] = None) -> ExecutionContext:
    """
    Create a child context from the current context.
    If no current context exists, a new root context is created.
    
    Args:
        name: Optional name for the context
        
    Returns:
        A new ExecutionContext object
    """
    from .tracer import get_global_tracer
    
    current = get_current_context()
    tracer = get_global_tracer()
    
    if current is None:
        # Creating a root context with no parent
        new_context = ExecutionContext(
            name=name or "root",
            parent_context_id=None  # Explicitly set to None for root contexts
        )
    else:
        # Create child of existing context
        new_context = current.create_child_context(name)
    
    # Register the new context with the tracer
    with tracer._contexts_lock:
        tracer._contexts[new_context.context_id] = new_context
    
    set_current_context(new_context)
    return new_context

def run_in_executor_with_context(executor, func, context, *args, **kwargs):
    """
    Run a function in an executor with the given context.
    
    This helper ensures that execution contexts are properly propagated across
    thread boundaries when using concurrent executors. This is especially important
    for maintaining proper causality tracking during replay.
    
    Args:
        executor: The executor to run the function in (ThreadPoolExecutor, etc.)
        func: The function to run
        context: The execution context to use
        *args, **kwargs: Arguments to pass to the function
        
    Returns:
        A Future representing the execution of the function
    
    Example:
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = []
            for i in range(3):
                child_context = root_context.create_child_context(f"thread_{i}")
                futures.append(
                    run_in_executor_with_context(executor, process_data, child_context, data[i])
                )
            for future in concurrent.futures.as_completed(futures):
                results.append(future.result())
    """
    def wrapper():
        # Set the context in the worker thread
        set_current_context(context)
        return func(*args, **kwargs)
    
    return executor.submit(wrapper)
