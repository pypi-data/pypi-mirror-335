"""
Lifecycle hooks for the Tela client.

This module defines types and decorators for lifecycle hooks.
"""

from typing import Any, Callable, Dict, Optional, Protocol, TypedDict, Union, cast, Literal


# Hook function signatures as Protocol classes for IDE support

class CacheHitHook(Protocol):
    """Called when a cached response is found for a canvas request.
    Return False to ignore the cache and force a new request."""
    def __call__(self, canvas_id: str, **kwargs: Any) -> Optional[bool]: ...

class CacheMissHook(Protocol):
    """Called when no cached response is found for a canvas request."""
    def __call__(self, canvas_id: str, **kwargs: Any) -> Any: ...

class RequestStartHook(Protocol):
    """Called when a request to the API begins."""
    def __call__(self, canvas_id: str, **kwargs: Any) -> Any: ...

class RequestErrorHook(Protocol):
    """Called when a request to the API fails."""
    def __call__(self, error: Any, status_code: Optional[int] = None, 
                 error_type: Optional[str] = None, **kwargs: Any) -> Any: ...

class RequestSuccessHook(Protocol):
    """Called when a request to the API succeeds."""
    def __call__(self, canvas_id: str, response: Dict[str, Any], **kwargs: Any) -> Any: ...

class BatchStartHook(Protocol):
    """Called when a batch execution begins."""
    def __call__(self, inputs_count: int, **kwargs: Any) -> Any: ...

class BatchItemStartHook(Protocol):
    """Called when processing a batch item begins."""
    def __call__(self, index: int, input: Dict[str, Any], **kwargs: Any) -> Any: ...

class BatchItemEndHook(Protocol):
    """Called when processing a batch item completes."""
    def __call__(self, index: int, input: Dict[str, Any], result: Any, **kwargs: Any) -> Any: ...

class BatchEndHook(Protocol):
    """Called when a batch execution completes."""
    def __call__(self, results_count: int, **kwargs: Any) -> Any: ...

class CanvasRunStartHook(Protocol):
    """Called when a canvas run begins."""
    def __call__(self, canvas_id: str, kwargs: Dict[str, Any], **extra_kwargs: Any) -> Any: ...

class MissingInputHook(Protocol):
    """Called when expected input is missing."""
    def __call__(self, canvas_id: str, missing_input: str, **kwargs: Any) -> Any: ...

class CanvasAttemptHook(Protocol):
    """Called when attempting to execute a canvas."""
    def __call__(self, canvas_id: str, attempt: int, max_attempts: int, **kwargs: Any) -> Any: ...

class CanvasRetryHook(Protocol):
    """Called when a canvas execution is retried."""
    def __call__(self, canvas_id: str, attempt: int, max_attempts: int, **kwargs: Any) -> Any: ...

class CanvasRunSuccessHook(Protocol):
    """Called when a canvas run succeeds."""
    def __call__(self, canvas_id: str, content_type: str, **kwargs: Any) -> Any: ...

class CanvasRunFailureHook(Protocol):
    """Called when all canvas run attempts fail."""
    def __call__(self, canvas_id: str, attempts: int, **kwargs: Any) -> Any: ...


# Valid hook names for autocomplete
HookName = Literal[
    'on_cache_hit', 'on_cache_miss',
    'on_request_start', 'on_request_error', 'on_request_success',
    'on_batch_start', 'on_batch_item_start', 'on_batch_item_end', 'on_batch_end',
    'on_canvas_run_start', 'on_missing_input', 'on_canvas_attempt', 'on_canvas_retry',
    'on_canvas_run_success', 'on_canvas_run_failure'
]

# Type for all hooks collection
class TelaHooks(TypedDict, total=False):
    """Dictionary of lifecycle hooks"""
    on_cache_hit: CacheHitHook
    on_cache_miss: CacheMissHook
    on_request_start: RequestStartHook
    on_request_error: RequestErrorHook
    on_request_success: RequestSuccessHook
    on_batch_start: BatchStartHook
    on_batch_item_start: BatchItemStartHook
    on_batch_item_end: BatchItemEndHook
    on_batch_end: BatchEndHook
    on_canvas_run_start: CanvasRunStartHook
    on_missing_input: MissingInputHook
    on_canvas_attempt: CanvasAttemptHook
    on_canvas_retry: CanvasRetryHook
    on_canvas_run_success: CanvasRunSuccessHook
    on_canvas_run_failure: CanvasRunFailureHook

# Mapping of hook names to function type (for IDE support)
HOOK_TYPES = {
    'on_cache_hit': CacheHitHook,
    'on_cache_miss': CacheMissHook,
    'on_request_start': RequestStartHook,
    'on_request_error': RequestErrorHook,
    'on_request_success': RequestSuccessHook,
    'on_batch_start': BatchStartHook,
    'on_batch_item_start': BatchItemStartHook,
    'on_batch_item_end': BatchItemEndHook,
    'on_batch_end': BatchEndHook,
    'on_canvas_run_start': CanvasRunStartHook,
    'on_missing_input': MissingInputHook,
    'on_canvas_attempt': CanvasAttemptHook,
    'on_canvas_retry': CanvasRetryHook,
    'on_canvas_run_success': CanvasRunSuccessHook,
    'on_canvas_run_failure': CanvasRunFailureHook
}

# Simple decorator that marks a function as a hook
def tela_hook(hook_name: HookName) -> Callable[[Callable], Callable]:
    """
    Decorator that marks a function as a Tela lifecycle hook.
    
    Args:
        hook_name: The name of the hook (IDE will show all available options)
        
    Returns:
        The decorated function with a _hook_name attribute
        
    Example:
        ```python
        @tela_hook('on_request_start')
        def log_request(canvas_id, **kwargs):
            print(f"Request started for {canvas_id}")
            
        client.add_hook(log_request)
        ```
    """
    def decorator(func: Callable) -> Callable:
        # Add hook_name as attribute to the function
        setattr(func, '_hook_name', hook_name)
        return func
        
    return decorator

# Empty hooks dictionary for default initialization
EMPTY_HOOKS: TelaHooks = {}

# Helper to validate hook names
def _validate_hook_name(hook_name: str) -> None:
    """Validate that a hook name is valid"""
    if hook_name not in HOOK_TYPES:
        raise ValueError(
            f"Unknown hook name: {hook_name}. " 
            f"Valid hook names are: {', '.join(HOOK_TYPES.keys())}"
        )