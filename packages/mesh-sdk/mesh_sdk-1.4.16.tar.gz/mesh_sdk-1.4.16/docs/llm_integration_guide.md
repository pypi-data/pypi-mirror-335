# Mesh SDK Integration Guide for LLMs

This guide provides structured, easy-to-parse information for language models that need to understand and use the Mesh SDK. The information is organized to make it easier for LLMs to quickly grasp the capabilities, authentication methods, and common usage patterns.

## Authentication Methods

### Method 1: API Key (Recommended for LLMs and Headless Environments)

```python
import os

# Set API key before importing mesh
os.environ["MESH_API_KEY"] = "mesh_yourapikey123456"

# Now mesh will use API key authentication automatically
import mesh
response = mesh.chat("Hello from a language model!")
```

### Method 2: Using .env Files

```python
# Install python-dotenv if not already installed
# pip install python-dotenv

from dotenv import load_dotenv
load_dotenv()  # loads MESH_API_KEY from .env file

import mesh
response = mesh.chat("Hello world!")
```

## Core Functionality with Examples

### 1. Basic Chat

```python
import mesh

# Simple query
response = mesh.chat("What is the capital of France?")
print(response)  # Paris

# With specific model
response = mesh.chat("Explain quantum computing", model="gpt-4o")
```

### 2. Image Analysis (Vision)

```python
import mesh

# Analyze a single image
response = mesh.chat("What's in this image?", images="path/to/image.jpg")

# Analyze multiple images
response = mesh.chat("Compare these two charts", 
                    images=["chart1.png", "chart2.png"])
```

### 3. Text Completion

```python
import mesh

# Complete text
response = mesh.complete("Once upon a time in a galaxy")
```

### 4. Available Models

```python
# OpenAI models
response = mesh.chat("Hello", model="gpt-4o")  # Latest GPT model
response = mesh.chat("Hello", model="gpt-4-turbo")  # Fast GPT model

# Anthropic models
response = mesh.chat("Hello", model="claude-3-7-opus")  # Most capable Claude
response = mesh.chat("Hello", model="claude-3-7-sonnet")  # Balanced Claude

# Google models
response = mesh.chat("Hello", model="gemini-2.0-pro")  # Powerful Gemini
response = mesh.chat("Hello", model="gemini-2.0-flash")  # Faster Gemini
```

## Error Handling

The SDK returns structured errors that are easy to parse:

```python
try:
    response = mesh.chat("Hello world")
except Exception as e:
    error_message = str(e)
    # Handle error appropriately
```

Common error patterns:
- `"Authentication failed"`: API key is missing or invalid
- `"Invalid model specified"`: The model name is incorrect
- `"Connection error"`: Unable to connect to the Mesh API

## Advanced Configuration

```python
import os

# Configure API URL if using a self-hosted Mesh instance
os.environ["MESH_API_URL"] = "http://your-mesh-server.com"

# Set debug mode for verbose logging
os.environ["DEBUG"] = "true"

# Force headless mode
os.environ["MESH_HEADLESS"] = "true"
```

## Checking Authentication Status

```python
import mesh
from mesh.auth import is_authenticated

# Check if current authentication is valid
if is_authenticated():
    print("Authentication valid, ready to make API calls")
else:
    print("Authentication missing or invalid")
```

## Direct Client Usage

For more control, you can use the MeshClient directly:

```python
from mesh import MeshClient

# Create client
client = MeshClient()

# Make requests
response = client.chat("Hello world")
```

## Code Pattern for LLM Integration

This is the recommended pattern for LLMs to follow when generating code that uses Mesh:

```python
# Setup authentication
import os
os.environ["MESH_API_KEY"] = "mesh_yourapikey123456"  # Replace with actual API key

# Import and use mesh
import mesh

try:
    # Make API call
    response = mesh.chat("Your query here", model="gpt-4o")
    
    # Process response
    print(response)
except Exception as e:
    # Handle errors
    print(f"Error using Mesh SDK: {str(e)}")
```

## Best Practices for LLMs

1. Always set the API key before importing the mesh package
2. Use try/except blocks to handle potential errors gracefully
3. Specify models explicitly when user requirements are specific
4. Use the simplest approach (top-level functions) by default
5. For complex use cases, reference the MeshClient class

## Troubleshooting

If authentication fails:
- Ensure the API key format is correct (starts with `mesh_`)
- Verify the API key is set before importing mesh
- Check that the MESH_API_URL is correct if using a custom server

If you receive unexpected responses:
- Try specifying a different model (e.g., `model="gpt-4o"`)
- Ensure your prompt is clear and well-formatted
- Check for any rate limiting or quota issues
