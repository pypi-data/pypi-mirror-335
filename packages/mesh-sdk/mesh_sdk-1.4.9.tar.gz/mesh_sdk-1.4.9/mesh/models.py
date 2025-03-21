"""
Model configuration and constants for Mesh SDK.

This module provides constants and helper functions for working with AI models
from various providers.
"""

from typing import Dict, Any, List, Optional

# OpenAI Models
class OpenAI:
    """Constants for OpenAI models"""
    # GPT-4o models
    GPT_4O = "gpt-4o"
    GPT_4O_MINI = "gpt-4o-mini"
    
    # O1 models
    O1 = "o1"
    O1_MINI = "o1-mini"
    
    # GPT-4 Turbo and GPT-4
    GPT_4_TURBO = "gpt-4-turbo"
    GPT_4 = "gpt-4"
    
    # GPT-3.5 Turbo
    GPT_3_5_TURBO = "gpt-3.5-turbo"
    
    # Image generation models
    DALL_E_3 = "dall-e-3"
    DALL_E_2 = "dall-e-2"
    
    # Default model
    DEFAULT = GPT_4O

# Anthropic Models
class Anthropic:
    """Constants for Anthropic models"""
    # Claude 3.7 models
    CLAUDE_3_7_SONNET = "claude-3-7-sonnet-20250219"
    
    # Claude 3.5 models
    CLAUDE_3_5_SONNET_V2 = "claude-3-5-sonnet-20241022"
    CLAUDE_3_5_SONNET = "claude-3-5-sonnet-20240620"
    CLAUDE_3_5_HAIKU = "claude-3-5-haiku-20241022"
    
    # Claude 3 models
    CLAUDE_3_OPUS = "claude-3-opus-20240229"
    CLAUDE_3_SONNET = "claude-3-sonnet-20240229"
    CLAUDE_3_HAIKU = "claude-3-haiku-20240307"
    
    # Default model
    DEFAULT = CLAUDE_3_7_SONNET

# Google Models
class Google:
    """Constants for Google Gemini models"""
    # Gemini 2.0 models
    GEMINI_2_0_PRO = "gemini-2.0-pro"
    GEMINI_2_0_FLASH = "gemini-2.0-flash"
    GEMINI_2_0_FLASH_THINKING = "gemini-2.0-flash-thinking-exp"
    GEMINI_2_0_PRO_VISION = "gemini-2.0-pro-vision"
    GEMINI_2_0_FLASH_EXP_IMAGE = "gemini-2.0-flash-exp-image-generation"
    
    # Gemini 1.5 models
    GEMINI_1_5_PRO = "gemini-1.5-pro"
    GEMINI_1_5_FLASH = "gemini-1.5-flash"
    
    # Imagen models
    IMAGEN_3 = "imagen-3.0-generate-002"
    
    # Default model
    DEFAULT = GEMINI_2_0_PRO

# Provider constants
class Provider:
    """Constants for AI model providers"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"

# Model aliases for easier reference
MODEL_ALIASES = {
    # OpenAI aliases
    "gpt4": "gpt-4",
    "gpt4o": "gpt-4o",
    "gpt4.5": "gpt-4.5-preview",
    "gpt45": "gpt-4.5-preview",
    "gpt3": "gpt-3.5-turbo",
    "gpt35": "gpt-3.5-turbo",
    "gpt3.5": "gpt-3.5-turbo",
    "gpt4omni": "gpt-4o",
    
    # Claude 3.7 aliases
    "claude": "claude-3-7-sonnet-20250219",  # Default to latest Claude
    "claude37": "claude-3-7-sonnet-20250219",
    "claude37sonnet": "claude-3-7-sonnet-20250219",
    "claude37s": "claude-3-7-sonnet-20250219",
    "claude3.7": "claude-3-7-sonnet-20250219",
    "claude-37": "claude-3-7-sonnet-20250219",
    "claude-3-7": "claude-3-7-sonnet-20250219",
    "claude-3.7": "claude-3-7-sonnet-20250219",
    "claude-3.7-sonnet": "claude-3-7-sonnet-20250219",
    
    # Claude 3.5 aliases
    "claude35": "claude-3-5-sonnet-20241022",
    "claude35sonnet": "claude-3-5-sonnet-20241022",
    "claude35s": "claude-3-5-sonnet-20241022",
    "claude3.5": "claude-3-5-sonnet-20241022",
    
    # Claude 3.5 Haiku aliases
    "claude35haiku": "claude-3-5-haiku-20241022",
    "claude35h": "claude-3-5-haiku-20241022",
    
    # Claude 3 Opus aliases
    "claude3opus": "claude-3-opus-20240229",
    "claudeopus": "claude-3-opus-20240229",
    
    # Claude 3 Sonnet aliases
    "claude3sonnet": "claude-3-sonnet-20240229",
    "claude3s": "claude-3-sonnet-20240229",
    
    # Claude 3 Haiku aliases
    "claude3haiku": "claude-3-haiku-20240307",
    "claude3h": "claude-3-haiku-20240307",
    
    # Google Gemini aliases - restored to original 2.0 mappings
    "gemini": "gemini-2.0-pro",
    "gemini2": "gemini-2.0-pro",
    "gemini20": "gemini-2.0-pro",
    "gemini2.0": "gemini-2.0-pro",
    "gemini2pro": "gemini-2.0-pro",
    "gemini2.0pro": "gemini-2.0-pro",
    "gemini-pro": "gemini-2.0-pro",
    
    # Flash model aliases
    "gemini2flash": "gemini-2.0-flash",
    "gemini2.0flash": "gemini-2.0-flash",
    "gemini-flash": "gemini-2.0-flash",
    "geminiflash": "gemini-2.0-flash",
    
    # Thinking models
    "geminithinking": "gemini-2.0-flash-thinking-exp",
    "gemini-thinking": "gemini-2.0-flash-thinking-exp",
    "gemini2thinking": "gemini-2.0-flash-thinking-exp",
    "gemini-flash-thinking": "gemini-2.0-flash-thinking-exp",
    
    "gemini1.5": "gemini-1.5-pro",
    "gemini15": "gemini-1.5-pro",
    "gemini1.5pro": "gemini-1.5-pro",
    "gemini15pro": "gemini-1.5-pro",
    
    "gemini1.5flash": "gemini-1.5-flash",
    "gemini15flash": "gemini-1.5-flash",
}

# Provider-specific model mappings
PROVIDER_MODELS = {
    "openai": {
        # GPT-4.5 models
        "gpt-4.5-preview": "gpt-4.5-preview",
        
        # GPT-4o models
        "gpt-4o": "gpt-4o",
        "gpt-4o-mini": "gpt-4o-mini",
        
        # O1 models
        "o1": "o1",
        "o1-mini": "o1-mini",
        
        # GPT-4 Turbo and GPT-4
        "gpt-4-turbo": "gpt-4-turbo",
        "gpt-4": "gpt-4",
        
        # GPT-3.5 Turbo
        "gpt-3.5-turbo": "gpt-3.5-turbo",
    },
    "anthropic": {
        # Claude 3.7 models
        "claude-3-7-sonnet-20250219": "claude-3-7-sonnet-20250219",
        
        # Claude 3.5 models
        "claude-3-5-sonnet-20241022": "claude-3-5-sonnet-20241022",
        "claude-3-5-haiku-20241022": "claude-3-5-haiku-20241022",
        
        # Claude 3 models
        "claude-3-opus-20240229": "claude-3-opus-20240229",
        "claude-3-sonnet-20240229": "claude-3-sonnet-20240229",
        "claude-3-haiku-20240307": "claude-3-haiku-20240307",
    },
    "google": {
        # Gemini 2.0 models
        "gemini-2.0-pro": "gemini-2.0-pro",
        "gemini-2.0-flash": "gemini-2.0-flash",
        "gemini-2.0-flash-thinking-exp": "gemini-2.0-flash-thinking-exp",
        "gemini-2.0-pro-vision": "gemini-2.0-pro-vision",
        
        # Gemini 1.5 models
        "gemini-1.5-pro": "gemini-1.5-pro",
        "gemini-1.5-flash": "gemini-1.5-flash",
        
        # Common aliases
        "gemini": "gemini-2.0-pro",
        "gemini-pro": "gemini-2.0-pro",
        "gemini-flash": "gemini-2.0-flash",
    }
}

def normalize_model_name(model_name: str) -> str:
    """
    Normalize a model name to its canonical form.
    
    Args:
        model_name: A model name or alias
        
    Returns:
        str: The canonical model name
    """
    # Check if it's a direct alias
    if model_name.lower() in MODEL_ALIASES:
        return MODEL_ALIASES[model_name.lower()]
    
    # Otherwise return as is
    return model_name

def get_provider_for_model(model_name: str) -> str:
    """
    Determine the provider for a given model.
    
    Args:
        model_name: The model name
        
    Returns:
        str: The provider name ("openai", "anthropic", "google", or "openai" as default)
    """
    # First check for direct name patterns in the original model name before normalization
    # This ensures that even aliases like "gemini" are properly matched
    model_lower = model_name.lower()
    
    # Check if it's a Google model by name pattern (before normalization)
    if "gemini" in model_lower:
        return "google"
        
    # Check if it's a Claude model by name pattern (before normalization)
    if "claude" in model_lower or "anthropic" in model_lower:
        return "anthropic"
    
    # Now normalize the model name (resolves aliases)
    model = normalize_model_name(model_name)
    model_lower = model.lower()
    
    # Check directly in the provider models dictionary
    for provider, models in PROVIDER_MODELS.items():
        if model in models:
            return provider
    
    # Check by name patterns again on the normalized name
    # Check if it's a Claude model by name pattern
    if "claude" in model_lower or "anthropic" in model_lower:
        return "anthropic"
    
    # Check if it's a Google model by name pattern
    if "gemini" in model_lower:
        return "google"
        
    # Default to OpenAI for all other models
    return "openai"

def get_best_model(provider: Optional[str] = None) -> str:
    """
    Get the best available model.
    
    Args:
        provider: Optional provider to constrain the choice
        
    Returns:
        str: The best model
    """
    if provider:
        provider = provider.lower()
        if provider == "openai":
            return OpenAI.GPT_4O
        elif provider == "anthropic":
            return Anthropic.CLAUDE_3_7_SONNET
        elif provider == "google":
            return Google.GEMINI_2_0_PRO
    
    # Default to the best overall model
    return Anthropic.CLAUDE_3_7_SONNET

def get_fastest_model(provider: Optional[str] = None) -> str:
    """
    Get the fastest available model.
    
    Args:
        provider: Optional provider to constrain the choice
        
    Returns:
        str: The fastest model
    """
    if provider:
        provider = provider.lower()
        if provider == "openai":
            return OpenAI.GPT_4O_MINI
        elif provider == "anthropic":
            return Anthropic.CLAUDE_3_5_HAIKU
        elif provider == "google":
            return Google.GEMINI_2_0_FLASH
    
    # Default to the fastest overall model
    return OpenAI.GPT_4O_MINI

def get_cheapest_model(provider: Optional[str] = None) -> str:
    """
    Get the cheapest available model.
    
    Args:
        provider: Optional provider to constrain the choice
        
    Returns:
        str: The cheapest model
    """
    if provider:
        provider = provider.lower()
        if provider == "openai":
            return OpenAI.GPT_3_5_TURBO
        elif provider == "anthropic":
            return Anthropic.CLAUDE_3_5_HAIKU
        elif provider == "google":
            return Google.GEMINI_1_5_FLASH
    
    # Default to the cheapest overall model
    return OpenAI.GPT_3_5_TURBO

def get_default_provider() -> str:
    """
    Get the default provider name.
    
    Returns:
        str: The default provider name
    """
    return Provider.OPENAI