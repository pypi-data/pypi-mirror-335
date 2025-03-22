# BotBrigade LLM Python SDK

## Overview
The **BotBrigade LLM Python SDK** provides an easy way to interact with the **BotBrigade LLM API** for text generation, model listing, and streaming responses. This SDK supports both **synchronous** and **asynchronous** operations using `httpx`.

## Installation
Ensure you have Python 3.7+ installed.

```bash
pip install botbrigade_llm
```

## Initialization
Import the `LLMClient` and create an instance with your API key:

```python
from botbrigade_llm import LLMClient

client = LLMClient(api_key="your_api_key")
```

Alternatively, you can set the API key as an environment variable:

```bash
export BBS_API_KEY="your_api_key"
```

And initialize the client without explicitly passing the key:

```python
client = LLMClient()
```

## Listing Available Models
The SDK allows you to retrieve a list of available LLM models.

### Synchronous
```python
models = client.list_models()
print(models)
```

### Asynchronous
```python
import asyncio

async def get_models():
    models = await client.alist_models()
    print(models)

asyncio.run(get_models())
```

## Generating Responses
The SDK supports both synchronous and asynchronous text generation.

### Message Structure

The API supports different message roles:
- `user`: The user's input message.
- `system`: A system-level instruction to guide the model's behavior.
- `assistant`: Previous responses from the assistant, used to provide conversation history.

Example:
```python
messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "How do I check if a string contains a substring in Python?"},
    {"role": "assistant", "content": "You can use the 'in' keyword in Python."}
]
```

### **Synchronous Response Generation**
```python
response = client.responses.create(
    model="claudia-1",
    messages=[{"role": "user", "content": "Tell me a joke"}],
    max_tokens=100,
    temperature=0.7,
)
print(response)
```

### **Asynchronous Response Generation**
```python
async def generate():
    response = await client.responses.acreate(
        model="claudia-1",
        messages=[{"role": "user", "content": "Tell me a joke"}],
        max_tokens=100,
        temperature=0.7,
    )
    print(response)

asyncio.run(generate())
```

### Non-Stream Response Format

All responses follow a standardized structure:

```json
{
  "id": "chatcmpl-1234567890",
  "object": "chat.completion",
  "created": 1710823456,
  "model": "claudia-1",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "Hello! How can I assist you today?",
        "refusal": null,
        "annotations": []
      },
      "logprobs": null,
      "finish_reason": "stop"
    }
  ]
}
```

## Streaming Responses
If `stream=True`, the response is streamed instead of returning a single object. The API returns data as Server-Sent Events (SSE).

### **Synchronous Streaming**
```python
for chunk in client.responses.create(
    model="claudia-1",
    messages=[{"role": "user", "content": "Tell me a story"}],
    stream=True
):
    print(chunk)
```

### **Asynchronous Streaming**
```python
async def stream_response():
    async for chunk in await client.responses.acreate(
        model="claudia-1",
        messages=[{"role": "user", "content": "Tell me a story"}],
        stream=True
    ):
        print(chunk)

asyncio.run(stream_response())
```

## Optional Payload Parameters
The SDK allows the following optional parameters for `create()` and `acreate()`:

| Parameter         | Type       | Description |
|------------------|-----------|-------------|
| `temperature`    | `float`   | Sampling temperature (higher values make output more random). Default: `1.0` |
| `max_tokens`     | `int`     | Maximum number of tokens in the response. Default: `None` (unlimited) |
| `top_p`         | `float`   | Nucleus sampling probability. Default: `1.0` |
| `frequency_penalty` | `float` | Penalizes repeated tokens. Default: `0.0` |
| `presence_penalty`  | `float` | Encourages new tokens. Default: `0.0` |
| `stream`        | `bool`    | Whether to stream responses. Default: `False` |

Example:
```python
response = client.responses.create(
    model="claudia-1",
    messages=[{"role": "user", "content": "Give me a summary of AI history."}],
    max_tokens=200,
    temperature=0.8,
    top_p=0.9,
    frequency_penalty=0.2,
    presence_penalty=0.1
)
print(response)
```

## Closing the Client
To properly close the HTTP connection, use:

### **Synchronous**
```python
client.close()
```

### **Asynchronous**
```python
asyncio.run(client.aclose())
```

## License
This SDK is licensed under **MIT License**.

## Support
For issues and contributions, please submit a GitHub issue or contact **BotBrigade Support**.

