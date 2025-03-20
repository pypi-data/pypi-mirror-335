# Tela Client

A Python client library for interacting with the Tela API.

## Installation

You can install the Tela Client using pip:

```
pip install git+https://github.com/yourusername/tela-client.git
```

## Usage

Here's a basic example of how to use the Tela Client:

```python
from tela_client import TelaClient, file

TELA_API_KEY = "Your API KEY"
tela_client = TelaClient(TELA_API_KEY)

canvas_id = "your-canvas-id"
canvas = tela_client.new_canvas(canvas_id, expected_input=['document'])

FILE_NAME = "./your_document.pdf"
result = canvas.run(document=file(FILE_NAME))
print(result)
```

## Lifecycle Hooks

You can hook into the client's lifecycle to add custom logging, monitoring, or other functionality.

```python
from tela_client import TelaClient, tela_hook, file
import logging

# Step 1: Define hooks with @tela_hook decorator
@tela_hook('on_request_start')
def log_start(canvas_id, **kwargs):
    logging.info(f"Starting request for canvas {canvas_id}")

@tela_hook('on_cache_hit') 
def handle_cache(canvas_id, **kwargs):
    logging.info(f"Cache hit for canvas {canvas_id}")
    return True  # True to use cache, False to ignore cache

@tela_hook('on_request_success')
def log_success(canvas_id, response, **kwargs):
    logging.info(f"Request successful for canvas {canvas_id}")

# Step 2: Create client and add hooks
client = TelaClient(TELA_API_KEY)
client.add_hook(log_start)
client.add_hook(handle_cache)
client.add_hook(log_success)

# Step 3: Use client as normal - hooks run automatically
canvas = client.new_canvas(canvas_id)
result = canvas.run(document=file("./document.pdf"))
```

### Available Hooks

| Hook Name | Description | Parameters | Return Value |
|-----------|-------------|------------|-------------|
| `on_cache_hit` | Called when a cached response is found | `canvas_id` | Return `False` to ignore cache |
| `on_cache_miss` | Called when no cached response is found | `canvas_id` | Ignored |
| `on_request_start` | Called before making API request | `canvas_id` | Ignored |
| `on_request_error` | Called when an API request fails | `error`, `status_code` (optional), `error_type` (optional) | Ignored |
| `on_request_success` | Called when an API request succeeds | `canvas_id`, `response` | Ignored |
| `on_batch_start` | Called when a batch execution begins | `inputs_count` | Ignored |
| `on_batch_item_start` | Called when processing a batch item begins | `index`, `input` | Ignored |
| `on_batch_item_end` | Called when a batch item completes | `index`, `input`, `result` | Ignored |
| `on_batch_end` | Called when a batch execution completes | `results_count` | Ignored |
| `on_canvas_run_start` | Called when a canvas run begins | `canvas_id`, `kwargs` | Ignored |
| `on_missing_input` | Called when expected input is missing | `canvas_id`, `missing_input` | Ignored |
| `on_canvas_attempt` | Called for each canvas execution attempt | `canvas_id`, `attempt`, `max_attempts` | Ignored |
| `on_canvas_retry` | Called when a canvas execution is retried | `canvas_id`, `attempt`, `max_attempts` | Ignored |
| `on_canvas_run_success` | Called when a canvas run succeeds | `canvas_id`, `content_type` | Ignored |
| `on_canvas_run_failure` | Called when all canvas run attempts fail | `canvas_id`, `attempts` | Ignored |

For a complete example, see `examples/simple_hooks.py`.

## License