from .client import TelaClient, Canvas, file, files
from .folder_watcher import watch_folder, run_canvas_on_folder_update
from .utils import split_pdf, count_pdf_pages
from .__version__ import __version__
from .hooks import (
    TelaHooks, tela_hook, HookName,
    CacheHitHook, CacheMissHook, RequestStartHook, RequestErrorHook, RequestSuccessHook,
    BatchStartHook, BatchItemStartHook, BatchItemEndHook, BatchEndHook,
    CanvasRunStartHook, MissingInputHook, CanvasAttemptHook, CanvasRetryHook,
    CanvasRunSuccessHook, CanvasRunFailureHook
)

__all__ = [
    'TelaClient', 'Canvas', 'file', 'files', 
    'watch_folder', 'run_canvas_on_folder_update', 
    'split_pdf', 'count_pdf_pages', 
    'TelaHooks', 'tela_hook', 'HookName',
    'CacheHitHook', 'CacheMissHook', 'RequestStartHook', 'RequestErrorHook', 'RequestSuccessHook',
    'BatchStartHook', 'BatchItemStartHook', 'BatchItemEndHook', 'BatchEndHook',
    'CanvasRunStartHook', 'MissingInputHook', 'CanvasAttemptHook', 'CanvasRetryHook',
    'CanvasRunSuccessHook', 'CanvasRunFailureHook',
    '__version__'
]

# Add __version__ attribute to the client
TelaClient.__version__ = __version__
