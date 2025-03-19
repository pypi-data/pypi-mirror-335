# Poridhi Cloud Python SDK

## Overview

The Poridhi Cloud Python SDK provides a comprehensive interface for interacting with the Poridhi Cloud infrastructure. It supports machine provisioning, worker allocation, resource monitoring, and model inference.

## Features

- Machine Provisioning
- Worker Allocation
- Resource Monitoring
- Model Inference (Streaming & WebSocket)
- Easy-to-use Python Interface

## Installation

```bash
pip install poridhi-cloud
```

## Quick Start

### Initializing the Client

```python
from poridhi_cloud import PoridihCloud

# Initialize with default settings
client = PoridihCloud()

# Or specify a custom base URL
client = PoridihCloud(base_url='http://your-cloud-endpoint')
```

### Launching a Machine

```python
# Launch a machine with 4 CPUs, 16GB RAM, and 1 NVIDIA GPU
machine = client.launch_machine(
    cpu=4,
    memory=8192,  # Memory in MB
    gpu='nvidia-tesla-t4',
    gpu_count=1
)
print(machine)
```

### Allocating a Worker

```python
# Allocate a worker with specific resources
worker = client.allocate_worker(
    cpu=2,
    memory=2096,
    gpu='nvidia-tesla-t4',
    gpu_count=1,
    image='',
    port=11434,
    machine_id=""
)
print(worker)
```

### Streaming Text Generation

#### HTTP Streaming
```python
# Stream text generation
for token in client.stream_generate(
    worker_id='your-worker-id', 
    model='llama3', 
    prompt='Tell me a story'
):
    print(token, end='')
```

#### WebSocket Streaming
```python
# WebSocket-based generation with callbacks
generator = (
    client.websocket_generate(
        worker_id='your-worker-id', 
        model='llama3', 
        prompt='Tell me a story'
    )
    .on_token(lambda token: print(token, end=''))
    .on_status(print)
    .on_error(print)
)

# Start generation
generator.start()
```

### Listing Resources

```python
# List all machines
machines = client.list_machines()
print(machines)

# List machine resources
resources = client.list_machine_resources()
print(resources)
```

## Configuration

### Environment Variables

- `PORIDHI_CLOUD_URL`: Base URL for the Poridhi Cloud API
- `PORIDHI_CLOUD_API_KEY`: API key for authentication

### Initialization Options

```python
client = PoridihCloud(
    base_url='http://your-server-url',
    api_key='your-optional-api-key'
)
```

## Error Handling

```python
from poridhi_cloud import PoridihCloudError

try:
    worker = client.allocate_worker(...)
except PoridihCloudError as e:
    print(f"Cloud Error: {e}")
```

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request

## License

MIT License

## Support

For issues and support, please open a GitHub issue in the repository.