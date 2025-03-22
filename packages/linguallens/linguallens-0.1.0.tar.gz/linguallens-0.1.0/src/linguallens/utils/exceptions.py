class LingualLensError(Exception):
    """Base exception for all LingualLens errors."""
    pass


class ProviderNotFoundError(LingualLensError):
    """Raised when a provider is not found."""
    def __init__(self, provider_name: str, available_providers: list):
        self.provider_name = provider_name
        self.available_providers = available_providers
        message = f"Provider '{provider_name}' not found. Available providers: {', '.join(available_providers)}"
        super().__init__(message)


class ModelNotFoundError(LingualLensError):
    """Raised when a model is not found."""
    def __init__(self, model_name: str, provider_name: str, available_models: list):
        self.model_name = model_name
        self.provider_name = provider_name
        self.available_models = available_models
        message = f"Model '{model_name}' not found for provider '{provider_name}'. Available models: {', '.join(available_models)}"
        super().__init__(message)


class APIKeyError(LingualLensError):
    """Raised when there is an issue with API keys."""
    def __init__(self, provider_name: str, message: str = None):
        self.provider_name = provider_name
        default_message = f"API key for '{provider_name}' is not set or invalid"
        super().__init__(message or default_message)


class GenerationError(LingualLensError):
    """Raised when there is an error during text generation."""
    def __init__(self, provider_name: str, model_name: str, message: str = None):
        self.provider_name = provider_name
        self.model_name = model_name
        default_message = f"Error generating text with model '{model_name}' from provider '{provider_name}'"
        super().__init__(message or default_message)


class ConfigurationError(LingualLensError):
    """Raised when there is an error with configuration."""
    pass


class PackageNotFoundError(LingualLensError):
    """Raised when a required package is not found."""
    def __init__(self, package_name: str, provider_name: str):
        self.package_name = package_name
        self.provider_name = provider_name
        message = f"Required package '{package_name}' for provider '{provider_name}' not found. Please install it using pip."
        super().__init__(message) 