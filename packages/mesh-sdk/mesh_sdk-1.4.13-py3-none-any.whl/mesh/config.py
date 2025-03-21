"""
Mesh SDK Configuration

This module provides default configuration settings for the Mesh SDK.
Users can override these settings by setting environment variables.
"""

import os
from typing import Dict, Any, Optional

# Default configuration
DEFAULT_CONFIG = {
    # API Configuration
    "MESH_API_URL": "https://mesh-abh5.onrender.com",
    
    # SDK Configuration
    "DEBUG": "false",
    "AUTO_REFRESH": "true",
    
    # Model Configuration
    "DEFAULT_OPENAI_MODEL": "gpt-4o",
    "DEFAULT_ANTHROPIC_MODEL": "claude-3-7-sonnet-20250219",
    "DEFAULT_PROVIDER": "openai",
    
    # Thinking Configuration
    "THINKING_ENABLED": "false",
    "DEFAULT_THINKING_BUDGET": "4000",  # Default thinking budget in tokens
    "DEFAULT_THINKING_MAX_TOKENS": "16000",  # Default max_tokens when thinking is enabled
    
    # Model Override Configuration
    "DEFAULT_OPENAI_MODEL_OVERRIDE": "",  # Empty means use DEFAULT_OPENAI_MODEL
    "DEFAULT_ANTHROPIC_MODEL_OVERRIDE": "",  # Empty means use DEFAULT_ANTHROPIC_MODEL
}

def get_config(key: str, default: Optional[str] = None) -> str:
    """
    Get a configuration value from environment variables or default config.
    
    Args:
        key: The configuration key to get
        default: Default value if not found in environment or default config
        
    Returns:
        str: The configuration value
    """
    # First check environment variables
    value = os.environ.get(key)
    
    # Then check default config
    if value is None:
        value = DEFAULT_CONFIG.get(key, default)
    
    return value

def get_all_config() -> Dict[str, str]:
    """
    Get all configuration values.
    
    Returns:
        Dict[str, str]: All configuration values
    """
    config = {}
    
    # Start with default config
    for key, value in DEFAULT_CONFIG.items():
        config[key] = value
    
    # Override with environment variables
    for key in DEFAULT_CONFIG.keys():
        env_value = os.environ.get(key)
        if env_value is not None:
            config[key] = env_value
    
    return config

def is_debug_enabled() -> bool:
    """
    Check if debug mode is enabled.
    
    Returns:
        bool: True if debug mode is enabled
    """
    debug = get_config("DEBUG", "false").lower()
    return debug in ("true", "1", "yes", "y")

def is_auto_refresh_enabled() -> bool:
    """
    Check if auto refresh is enabled.
    
    Returns:
        bool: True if auto refresh is enabled
    """
    auto_refresh = get_config("AUTO_REFRESH", "true").lower()
    return auto_refresh in ("true", "1", "yes", "y")

def is_thinking_enabled() -> bool:
    """
    Check if thinking is enabled by default.
    
    Returns:
        bool: True if thinking is enabled by default
    """
    thinking_enabled = get_config("THINKING_ENABLED", "false").lower()
    return thinking_enabled in ("true", "1", "yes", "y")

def get_default_thinking_budget() -> int:
    """
    Get the default thinking budget in tokens.
    
    Returns:
        int: Default thinking budget in tokens
    """
    return int(get_config("DEFAULT_THINKING_BUDGET", "4000"))

def get_default_thinking_max_tokens() -> int:
    """
    Get the default max_tokens when thinking is enabled.
    
    Returns:
        int: Default max_tokens when thinking is enabled
    """
    return int(get_config("DEFAULT_THINKING_MAX_TOKENS", "16000"))

def get_default_model(provider: str) -> str:
    """
    Get the default model for a specific provider.
    
    Args:
        provider: The provider name (e.g., "openai", "anthropic")
        
    Returns:
        str: The default model for the specified provider
    """
    provider = provider.lower()
    
    if provider == "openai":
        return get_config("DEFAULT_OPENAI_MODEL")
    elif provider == "anthropic":
        return get_config("DEFAULT_ANTHROPIC_MODEL")
    else:
        # Fallback to OpenAI's default if provider unknown
        return get_config("DEFAULT_OPENAI_MODEL")

def get_default_model_with_override(provider: str) -> str:
    """
    Get the default model for a provider, considering any overrides.
    
    Args:
        provider: The provider name (e.g., "openai", "anthropic")
        
    Returns:
        str: The default model for the specified provider
    """
    provider = provider.lower()
    
    if provider == "openai":
        override = get_config("DEFAULT_OPENAI_MODEL_OVERRIDE", "")
        return override if override else get_config("DEFAULT_OPENAI_MODEL")
    elif provider == "anthropic":
        override = get_config("DEFAULT_ANTHROPIC_MODEL_OVERRIDE", "")
        return override if override else get_config("DEFAULT_ANTHROPIC_MODEL")
    else:
        # Fallback to OpenAI's default if provider unknown
        return get_config("DEFAULT_OPENAI_MODEL")

def get_default_provider() -> str:
    """
    Get the default provider for AI models.
    
    Returns:
        str: The default provider (e.g., "openai", "anthropic")
    """
    return get_config("DEFAULT_PROVIDER", "openai")

def get_auth_config_endpoint() -> str:
    """
    Get the endpoint for fetching Auth0 configuration from the backend.
    
    Returns:
        str: The endpoint URL
    """
    base_url = get_config("MESH_API_URL")
    return f"{base_url}/auth/config"

def get_auth_url_endpoint() -> str:
    """
    Get the endpoint for generating Auth0 authorization URL.
    
    Returns:
        str: The endpoint URL
    """
    base_url = get_config("MESH_API_URL")
    return f"{base_url}/auth/get-auth-url"

def get_token_exchange_endpoint() -> str:
    """
    Get the endpoint for exchanging auth code for tokens.
    
    Returns:
        str: The endpoint URL
    """
    base_url = get_config("MESH_API_URL")
    return f"{base_url}/auth/exchange-token"

def get_token_refresh_endpoint():
    """
    Return the backend token refresh endpoint URL.
    
    Returns:
        str: The endpoint URL
    """
    base_url = get_config("MESH_API_URL")
    return f"{base_url}/auth/refresh-token"

def get_token_validate_endpoint():
    """
    Return the backend token validation endpoint URL.
    
    Returns:
        str: The endpoint URL
    """
    base_url = get_config("MESH_API_URL")
    return f"{base_url}/auth/validate"