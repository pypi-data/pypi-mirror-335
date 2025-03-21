# Mesh SDK for Python

A simple Python SDK for talking to AI models (like GPT-4, Claude, and Gemini) with just a few lines of code.

## Installation

```bash
pip install mesh-sdk
```

## Why Use Mesh?

- **Super Simple**: Just one line of code to chat with AI
- **Works with Everything**: OpenAI, Anthropic, and Google models
- **Vision Support**: Send images to AI models easily
- **Secure**: Safely store your API keys

## Quick Start - Talk to AI

```python
import mesh

# Ask a question - that's it!
response = mesh.chat("What is the capital of France?")
print(response)

# Send an image
response = mesh.chat("What's in this image?", images="photo.jpg")
print(response)

# Use a specific model
response = mesh.chat("Tell me a joke", model="gpt-4o")
print(response)
```

## Store and Get Keys

```python
# Save an API key securely
mesh.store_key("openai_key", "sk-abcdef123456")

# Get a saved key
key = mesh.get_key("openai_key")

# List all your keys
all_keys = mesh.list_keys()
```

## Text Completion

```python
# Complete some text
response = mesh.complete("Once upon a time")
print(response)

# Use a specific model for completion
response = mesh.complete("The recipe includes", model="claude-3-7-opus")
```

## Vision (Send Images to AI)

```python
# Ask about an image
response = mesh.chat("What's in this image?", images="photo.jpg")
print(response)

# Send multiple images
response = mesh.chat("Compare these two images", 
                    images=["image1.jpg", "image2.jpg"])
```

## Popular AI Models

```python
# OpenAI models
mesh.chat("Hello", model="gpt-4o")          # Latest and best
mesh.chat("Hello", model="gpt-4-turbo")    # Fast and powerful

# Anthropic models
mesh.chat("Hello", model="claude-3-7-sonnet")  # Balanced option
mesh.chat("Hello", model="claude-3-7-opus")    # Most powerful

# Google models
mesh.chat("Hello", model="gemini-2.0-pro")    # Powerful
mesh.chat("Hello", model="gemini-2.0-flash")  # Fast response
```

## Simple Configuration

Set these environment variables to customize Mesh:

```bash
# Set your API URL (if not using the default cloud service)
export MESH_API_URL="http://your-server-url.com"

# Enable debug mode to see what's happening
export DEBUG=true
```

## Advanced Usage

If you need more advanced features, check our super simple guides:

### Using a Direct Client

```python
# Import the client directly (alternative to top-level functions)
from mesh import MeshClient

# Create a client
client = MeshClient()

# Use the client
response = client.chat("Hello world")
print(response)
```

### All Available Models

- **OpenAI:** `gpt-4o`, `gpt-4-turbo`, `gpt-4`, `gpt-3.5-turbo`
- **Anthropic:** `claude-3-7-opus`, `claude-3-7-sonnet`, `claude-3-7-haiku`
- **Google:** `gemini-2.0-pro`, `gemini-2.0-flash`, `gemini-pro-vision`

### Need Help?

If you have questions:

- Email: support@meshsdk.io
- GitHub: https://github.com/meshsdk/mesh-python/issues

## Common Issues and Solutions

### "I can't connect to the API"
- Make sure you're connected to the internet
- Check if you need to set `MESH_API_URL` to your own server

### "I get authentication errors"
- Run `mesh-auth` from your command line to log in again

### "My AI responses are weird or cut off"
- Try a different model (e.g., `model="gpt-4o"` or `model="claude-3-7-opus"`) 
- Make sure your API keys are valid

## License

This project is licensed under the MIT License.


# MESH_API_URL - Base server URL
# OPENAI_API_KEY - OpenAI API key
# ANTHROPIC_API_KEY - Anthropic API key
# DEFAULT_PROVIDER - Default AI provider
# DEFAULT_MODEL - Default model to use

# Set default model for a provider
client.set_default_model("openai", "gpt-4")
client.set_default_model("anthropic", "claude-3-7-sonnet-20250219")

# Reset to original defaults
client.reset_default_models()
```

## API Reference

For complete API documentation, please refer to the docstrings in the code.

## Chat Functionality

The SDK provides a simple interface to chat with AI models:

```python
# Chat with default model
response = client.chat("Hello, world!")

# Chat with specific model
response = client.chat("Hello, world!", model="gpt-4o", provider="openai")

# Enable thinking mode (Claude 3.7 Sonnet only)
response = client.chat("Solve this complex problem...", model="claude-3-7-sonnet-20250219", thinking=True)

# Get raw API response
response = client.chat("Hello, world!", original_response=True)
```

### Automatic User Registration

The SDK automatically ensures that the user is registered in the database before sending chat requests. This is necessary because the chat endpoints require the user to exist in the database. The registration process happens transparently when you make your first chat request:

```python
# The first chat request will automatically register the user if needed
response = client.chat("Hello, world!")
```

If the user registration fails, the SDK will return an error with troubleshooting steps:

```python
{
    "success": False,
    "error": "Failed to register user. Chat requires user registration.",
    "troubleshooting": [
        "Try calling the auth profile endpoint directly first",
        "Verify your authentication token is valid",
        "Check that the server URL is correct"
    ]
}
```

### Helper Methods

The SDK also provides helper methods for common chat scenarios:

```python
# Chat with GPT-4o
response = client.chat_with_gpt4o("Hello, world!")

# Chat with Claude
response = client.chat_with_claude("Hello, world!")

# Chat with the best model for a provider
response = client.chat_with_best_model("Hello, world!", provider="openai")

# Chat with the fastest model for a provider
response = client.chat_with_fastest_model("Hello, world!", provider="anthropic")

# Chat with the cheapest model for a provider
response = client.chat_with_cheapest_model("Hello, world!")
```

### Using Claude Models

The Mesh SDK supports Anthropic's Claude models and provides several ways to use them:

```python
from mesh import MeshClient

client = MeshClient()

# Method 1: Use the built-in helper method (recommended)
response = client.chat_with_claude("Write a haiku about programming")

# Specify Claude version
response = client.chat_with_claude("Write a haiku about programming", version="3.7")  # Use Claude 3.7
response = client.chat_with_claude("Write a haiku about programming", version="3")    # Use Claude 3 Opus

# Method 2: Specify the provider and model explicitly
response = client.chat(
    message="Write a haiku about programming",
    model="claude-3-7-sonnet-20250219",
    provider="anthropic"
)

# Method 3: Use a model alias (which maps to a specific version)
response = client.chat(
    message="Write a haiku about programming",
    model="claude-37"  # Aliased to claude-3-7-sonnet-20250219
)
```

#### Claude Model Aliases

The SDK provides several aliases for Claude models to make them easier to use:

| Alias           | Maps to                     | Description              |
|-----------------|----------------------------|--------------------------|
| `claude`        | claude-3-5-sonnet-20241022 | Latest stable Claude     |
| `claude-37`     | claude-3-7-sonnet-20250219 | Claude 3.7 Sonnet        |
| `claude-35`     | claude-3-5-sonnet-20241022 | Claude 3.5 Sonnet        |
| `claude-35-haiku` | claude-3-5-haiku-20241022 | Claude 3.5 Haiku        |
| `claude-3`      | claude-3-opus-20240229    | Claude 3 Opus            |
| `claude-opus`   | claude-3-opus-20240229    | Claude 3 Opus            |
| `claude-sonnet` | claude-3-sonnet-20240229  | Claude 3 Sonnet          |
| `claude-haiku`  | claude-3-haiku-20240307   | Claude 3 Haiku           |

> **Note:** When using the `claude` alias directly, it's mapped to a specific version of Claude (currently Claude 3.5 Sonnet) for stability. This may not be the absolute latest Claude model. For the most reliable way to use specific Claude versions:
> - Use `chat_with_claude(message, version="3.7")` to explicitly select the version
> - Or specify the full model ID with `model="claude-3-7-sonnet-20250219"` 