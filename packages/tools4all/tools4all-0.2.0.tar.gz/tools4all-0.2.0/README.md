# Tools4All

A drop-in replacement for the Ollama Python library that adds function calling capabilities to LLMs that don't natively support them.

## 🎯 Goal

Tools4All attempts to enables function calling to non capable Ollama served LLMs. It works by:

1. Extending ollama.Client and overriding the chat method
2. Detecting if the LLM is capable of function calling
3. Injecting tool descriptions into the system prompt if the LLM is not capable of function calling
4. Parsing the LLM's response to extract tool calls and inject them into ollama.ChatResponse
5. Parsing role "tool" message items to extract tool results

This approach allows function calling with models that lack native tool support.

## Installation

```bash
pip install tools4all
```

Use as you would use ollama python library

### 📦 Dependencies

- `ollama`: Python client for Ollama
- `pydantic`: Data validation and settings management
- `rich`: For pretty printing (optional)

## Basic Usage

```python
from tools4all import Client

# Actual function that may be called
def get_weather(location):
    # Your implementation here
    return f"The weather in {location} is sunny."

# Define the tool description
tool = {
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "Get the current weather",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "The city and state, e.g., San Francisco, CA"
                }
            },
            "required": ["location"]
        }
    }
}

# Create a Tools4All client
client = Client(host='http://127.0.0.1:11434')

# Process a user prompt
prompt = "What's the weather like in San Francisco?"
model = "myllm:latest" # set the ollama model to use

client.chat(
    messages=[
        {"role": "user", "content": prompt}
    ],
    tools=[tool],
    model=model
)
```

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgements

- [Ollama](https://github.com/ollama/ollama) for providing the LLM backend
- [Pydantic](https://github.com/pydantic/pydantic) for data validation
