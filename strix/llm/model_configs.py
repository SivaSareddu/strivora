"""
Model-specific configurations including context window limits.
"""

# Model context window limits (in tokens)
MODEL_CONTEXT_LIMITS = {
    # OpenAI Models
    "openai/gpt-4o": 128_000,
    "openai/gpt-4o-mini": 128_000,
    "openai/gpt-4-turbo": 128_000,
    "openai/gpt-4": 8_192,
    "openai/gpt-3.5-turbo": 4_096,
    "openai/gpt-3.5-turbo-16k": 16_384,
    
    # Anthropic Models
    "anthropic/claude-3-5-sonnet-20241022": 200_000,
    "anthropic/claude-3-5-haiku-20241022": 200_000,
    "anthropic/claude-3-opus-20240229": 200_000,
    "anthropic/claude-3-sonnet-20240229": 200_000,
    "anthropic/claude-3-haiku-20240307": 200_000,
    
    # Google Models
    "google/gemini-1.5-pro": 1_000_000,
    "google/gemini-1.5-flash": 1_000_000,
    "google/gemini-2.0-flash-exp": 1_000_000,
    
    # Meta Models
    "meta-llama/llama-3.1-405b": 128_000,
    "meta-llama/llama-3.1-70b": 128_000,
    "meta-llama/llama-3.1-8b": 128_000,
    
    # Mistral Models
    "mistral/mistral-large": 32_000,
    "mistral/mistral-medium": 32_000,
    "mistral/mistral-small": 32_000,
    
    # Cohere Models
    "cohere/command-r-plus": 128_000,
    "cohere/command-r": 128_000,
    
    # Default fallback for unknown models
    "default": 30_000,
}


def get_model_context_limit(model_name: str) -> int:
    """
    Get the context window limit for a given model.
    
    Args:
        model_name: The model name (e.g., "openai/gpt-4o")
        
    Returns:
        The context window limit in tokens
    """
    # Check for exact match first
    if model_name in MODEL_CONTEXT_LIMITS:
        return MODEL_CONTEXT_LIMITS[model_name]
    
    # Check for partial matches (e.g., "gpt-4o" matches "openai/gpt-4o")
    model_lower = model_name.lower()
    for key, limit in MODEL_CONTEXT_LIMITS.items():
        if key.lower() in model_lower or model_lower in key.lower():
            return limit
    
    # Return default limit for unknown models
    return MODEL_CONTEXT_LIMITS["default"]


def get_safe_token_limit(model_name: str, safety_margin: float = 0.9) -> int:
    """
    Get a safe token limit for a model with a safety margin.
    
    Args:
        model_name: The model name
        safety_margin: Safety margin as a fraction (0.9 = 90% of max)
        
    Returns:
        Safe token limit accounting for safety margin
    """
    max_limit = get_model_context_limit(model_name)
    return int(max_limit * safety_margin)
