"""
LingualLens - A unified interface for interacting with language models from multiple providers.
"""

from .core import (
    LingualLens,
    BaseProvider,
    OpenAIProvider,
    AnthropicProvider,
    GoogleProvider,
    HuggingFaceProvider
)

from .utils import (
    ModelConfig,
    setup_logger,
    preprocess_prompt,
    extract_entities,
    analyze_sentiment,
    truncate_text,
    format_as_json,
    parse_json_safely,
    LingualLensError,
    ProviderNotFoundError,
    ModelNotFoundError,
    APIKeyError,
    GenerationError,
    ConfigurationError,
    PackageNotFoundError
)

__version__ = "0.1.0"

__all__ = [
    # Core
    'LingualLens',
    
    # Providers
    'BaseProvider',
    'OpenAIProvider',
    'AnthropicProvider',
    'GoogleProvider',
    'HuggingFaceProvider',
    
    # Utils
    'ModelConfig',
    'setup_logger',
    'preprocess_prompt',
    'extract_entities',
    'analyze_sentiment',
    'truncate_text',
    'format_as_json',
    'parse_json_safely',
    
    # Exceptions
    'LingualLensError',
    'ProviderNotFoundError',
    'ModelNotFoundError',
    'APIKeyError',
    'GenerationError',
    'ConfigurationError',
    'PackageNotFoundError'
] 