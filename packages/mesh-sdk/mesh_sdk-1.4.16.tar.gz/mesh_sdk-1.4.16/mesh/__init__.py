"""
Mesh API Client SDK

This package provides a simple, powerful interface to the Mesh API.
"""

import os
import sys
import logging
from typing import Dict, Any, Optional, List, Union

# Set up logging
if os.environ.get("DEBUG", "").lower() in ('true', '1', 'yes'):
    logging.basicConfig(level=logging.DEBUG)
else:
    logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mesh")

# Export client classes for advanced usage
from .client import MeshClient
from .zkp_client import MeshZKPClient
from .auto_refresh_client import AutoRefreshMeshClient

# Export model constants
from .models import OpenAI, Anthropic, Google, Provider, get_best_model, get_fastest_model, get_cheapest_model

# Export auth functions
from .auth import authenticate, clear_token, is_authenticated, get_device_code, poll_for_device_token

# Create a singleton client instance
_client = None

def _get_client() -> MeshClient:
    """Get or create a singleton client instance with automatic authentication
    
    Returns:
        MeshClient: An authenticated client with auto-refresh capabilities
    """
    global _client
    
    # Return existing client if available
    if _client is not None:
        return _client
    
    # Import here to avoid circular imports
    from .token_manager import get_token, is_token_valid
    from .auth import authenticate
    
    # Check for existing token
    token_data = get_token()
    
    # Authenticate if needed
    if not token_data or not is_token_valid(token_data):
        # Try to authenticate with backend
        try:
            # The authenticate function will automatically detect environment
            # and choose browser-based or device flow as appropriate
            token_data = authenticate()
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            token_data = None
            
        # Still no token? Raise exception
        if not token_data:
            raise RuntimeError("Authentication failed. Please try again by running 'mesh-auth' from the command line.")
    
    # Create client with token and auto-refresh enabled
    _client = MeshClient(auto_refresh=True)
    
    # The token will be loaded automatically in the client constructor,
    # but we set it explicitly to ensure it's using the latest token
    if token_data and "access_token" in token_data:
        _client.auth_token = token_data["access_token"]
    
    return _client

# =========================
# Simplified API Functions
# =========================

def chat(
    messages: Union[str, List[Dict[str, str]]],
    model: Optional[str] = None,
    temperature: Optional[float] = None,
    max_tokens: Optional[int] = None,
    thinking: Optional[bool] = None,
    provider: Optional[str] = None,
    image_path: Optional[Union[str, List[str]]] = None,
    **kwargs
) -> Union[str, Dict[str, Any]]:
    """Send a chat request to an AI model, optionally with images.
    
    This function allows for both text-only and multimodal (text + image) conversations
    with various AI models.
    
    Args:
        messages: Either a string message or a list of message objects with 'role' and 'content'
        model: Model name to use (e.g., "gpt-4o", "claude-3-7-sonnet-20250219")
        temperature: Temperature for generation (0.0-2.0)
        max_tokens: Maximum tokens to generate
        thinking: Whether to enable thinking/reasoning
        provider: Model provider ("openai", "anthropic", or "google")
        image_path: Path to an image file or list of image paths to include with the message
        **kwargs: Additional model parameters
    
    Returns:
        By default, returns a string containing just the response content.
        If using a custom MeshClient with return_content_only=False, returns the full response dict.
    
    Image Best Practices:
        - Image Size: Optimal image size is up to 1568px on long edge with no more than 1.15 megapixels
          for best performance. The SDK will automatically resize larger images if PIL is installed.
        - File Types: Supported formats are JPEG, PNG, GIF, and WebP.
        - Multiple Images: Up to 5 images can be included in a single request.
        - Model Selection: When using images, a vision-capable model will be automatically selected
          if not specified (OpenAI: gpt-4o, Claude: claude-3-7-sonnet-20250219, Google: gemini-2.0-flash-exp-image-generation).
    
    Vision Limitations:
        - People Identification: Models cannot identify specific people in images.
        - Accuracy: Models may have issues with low-quality, rotated, or small images.
        - Spatial Reasoning: Models have limited spatial reasoning abilities.
        - Counting: Models can give approximate counts but may not be precisely accurate.
        - Inappropriate Content: Models will not process inappropriate images.
        
    Examples:
        # Simple text chat
        response = mesh.chat("What's the capital of France?")
        
        # Chat with an image
        response = mesh.chat("What's in this image?", image_path="photo.jpg")
        
        # Chat with multiple images
        response = mesh.chat("Compare these images", image_path=["image1.jpg", "image2.jpg"])
        
        # Specify a vision-capable model
        response = mesh.chat("Describe this image", 
                            image_path="image.jpg", 
                            model="gpt-4o")
    """
    client = _get_client()
    
    # Convert string to proper message format if needed
    if isinstance(messages, str):
        # If it's a string, just pass it directly to client.chat()
        return client.chat(
            message=messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            thinking=thinking,
            provider=provider,
            image_path=image_path,
            **kwargs
        )
    else:
        # For message arrays, create proper format
        return client.chat(
            message=messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            thinking=thinking,
            provider=provider,
            image_path=image_path,
            **kwargs
        )

def complete(
    prompt: str, 
    model: Optional[str] = None, 
    temperature: Optional[float] = None,
    max_tokens: Optional[int] = None,
    thinking: Optional[bool] = None,
    provider: Optional[str] = None,
    **kwargs
) -> str:
    """
    Generate text completion from a prompt.
    
    Args:
        prompt: Text prompt for completion
        model: Model name to use (e.g., "gpt-4o", "claude-3-opus-20240229")
        temperature: Temperature for generation (0.0-2.0)
        max_tokens: Maximum tokens to generate
        thinking: Whether to enable thinking/reasoning
        provider: Model provider ("openai" or "anthropic")
        **kwargs: Additional model parameters
    
    Returns:
        String containing the generated text
    """
    messages = [{"role": "user", "content": prompt}]
    response = chat(
        messages=messages,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
        thinking=thinking,
        provider=provider,
        **kwargs
    )
    return response.get("choices", [{}])[0].get("message", {}).get("content", "")

def image(
    prompt: str,
    image_path: Optional[str] = None,
    model: Optional[str] = None,
    provider: Optional[str] = None,
    size: Optional[str] = None,
    n: Optional[int] = None,
    output_path: Optional[str] = None,
    quality: Optional[str] = None,
    response_format: Optional[str] = None,
    **kwargs
) -> Union[str, List[str], Dict[str, Any]]:
    """Generate or modify an image using AI.
    
    This function supports two main use cases:
    1. Generate a new image from a text prompt
    2. Modify an existing image based on a text prompt
    
    Examples:
        # Generate an image and get URL/base64
        image_data = mesh.image("A cat wearing sunglasses")
        
        # Generate and save to file
        image_path = mesh.image("A cat wearing sunglasses", output_path="cat.png")
        
        # Modify an existing image
        modified_image = mesh.image("Make the cat wear a hat", image_path="cat.jpg")
        
        # Generate with a specific provider
        openai_image = mesh.image("A futuristic cityscape", provider="openai")
        
        # Generate with Gemini 2.0 image generation
        gemini_image = mesh.image("3D rendered pig with wings and a top hat flying over a futuristic city", 
                                  provider="google", 
                                  model="gemini-2.0-flash-exp-image-generation")
    
    Args:
        prompt: Text description of the image to generate or modification to apply
        image_path: Path to an input image (if modifying an existing image)
        model: Model to use (e.g., "gemini-2.0-flash-exp-image-generation", "dall-e-3")
        provider: Provider to use ("google" or "openai")
        size: Size of the output image (e.g., "1024x1024")
        n: Number of images to generate
        output_path: Path to save the generated image(s)
        quality: Image quality (e.g., "standard", "hd")
        response_format: Format of the response ("url" or "b64_json")
        **kwargs: Additional parameters to pass to the provider API
        
    Returns:
        If output_path is specified, returns the output path(s).
        Otherwise, returns the URL(s) or base64 data of the generated image(s).
        
    Notes:
        - For Google's Gemini 2.0 image generation, the function automatically sets
          responseModalities to ["Text", "Image"] as required by the API.
        - Gemini 2.0 supports both image generation and image editing/modification.
        - The model can generate both interleaved text and images in a single response.
        - All generated images include a SynthID watermark.
    """
    client = _get_client()
    return client.image(
        prompt=prompt,
        image_path=image_path,
        model=model,
        provider=provider,
        size=size,
        n=n,
        output_path=output_path,
        quality=quality,
        response_format=response_format,
        **kwargs
    )

def store_key(key_name: str, key_value: str, user_id: str = None) -> Dict[str, Any]:
    """Store a key in the Mesh API
    
    Args:
        key_name: Name of the key to store
        key_value: Value of the key to store
        user_id: Optional User ID to associate with the key. If not provided, extracted from auth token.
        
    Returns:
        dict: Result of the operation
    """
    client = _get_client()
    return client.store_key(key_name=key_name, key_value=key_value, user_id=user_id)

def get_key(key_name: str, user_id: str = None) -> Optional[str]:
    """Get a key from the Mesh API
    
    Args:
        key_name: Name of the key to retrieve
        user_id: Optional User ID to retrieve key for. If not provided, extracted from auth token.
        
    Returns:
        Optional[str]: The key value if found, or None if not found
    """
    client = _get_client()
    return client.get_key(key_name=key_name, user_id=user_id)

def store_key_zkp(key_name: str, key_value: str, user_id: str = None) -> Dict[str, Any]:
    """Store a key using Zero-Knowledge Proofs
    
    Args:
        key_name: Name of the key to store
        key_value: Value of the key to store
        user_id: Optional User ID to associate with the key. If not provided, extracted from auth token.
        
    Returns:
        dict: Result of the operation
    """
    from .zkp_client import MeshZKPClient
    client = MeshZKPClient()
    
    # Transfer authentication from singleton client
    main_client = _get_client()
    client.auth_token = main_client.auth_token
    
    return client.store_key_zkp(key_name=key_name, key_value=key_value, user_id=user_id)

def verify_key(key_name: str, key_value: str, user_id: str = None) -> bool:
    """Verify a key using Zero-Knowledge Proofs
    
    Args:
        key_name: Name of the key to verify
        key_value: Value of the key to verify
        user_id: Optional User ID to verify key for. If not provided, extracted from auth token.
        
    Returns:
        bool: True if key verified successfully, False otherwise
    """
    from .zkp_client import MeshZKPClient
    client = MeshZKPClient()
    
    # Transfer authentication from singleton client
    main_client = _get_client()
    client.auth_token = main_client.auth_token
    
    result = client.verify_key(key_name=key_name, key_value=key_value, user_id=user_id)
    return result.get("verified", False)

def list_keys(user_id: str = None) -> List[str]:
    """List all keys stored for a user
    
    Args:
        user_id: Optional User ID to list keys for. If not provided, extracted from auth token.
        
    Returns:
        List[str]: A list of key names (without the user_id prefix)
    """
    client = _get_client()
    return client.list_keys(user_id=user_id)

# Set version
__version__ = "1.5.0"

# Export simplified API functions and client classes
__all__ = [
    # Simplified API functions
    'chat',
    'complete',
    'image',
    'store_key',
    'get_key',
    'store_key_zkp',
    'verify_key',
    'list_keys',
    
    # Client classes for advanced usage
    'MeshClient',
    'MeshZKPClient',
    'AutoRefreshMeshClient',
    
    # Auth utilities
    'authenticate',
    'clear_token',
    'is_authenticated',
    'get_device_code',
    'poll_for_device_token',
    
    # Model utilities
    'get_best_model',
    'get_fastest_model',
    'get_cheapest_model',
    
    # Provider and model constants
    'OpenAI',
    'Anthropic',
    'Google',
    'Provider'
]