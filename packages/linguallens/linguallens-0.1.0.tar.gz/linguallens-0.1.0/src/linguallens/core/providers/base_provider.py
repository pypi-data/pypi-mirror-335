from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Union, Any


class BaseProvider(ABC):
    """
    Abstract base class for all model providers.
    All provider implementations must inherit from this class.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the provider.
        
        Args:
            api_key: API key for the provider
        """
        self.api_key = api_key
    
    @abstractmethod
    def generate(
        self,
        prompt: str,
        model: str,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        top_p: float = 1.0,
        stop: Optional[Union[str, List[str]]] = None,
        stream: bool = False,
        **kwargs
    ) -> str:
        """
        Generate text using a model from this provider.
        
        Args:
            prompt: Input prompt
            model: Model name/identifier
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            top_p: Top-p sampling parameter
            stop: Stop sequences
            stream: Whether to stream the response
            **kwargs: Additional provider-specific parameters
            
        Returns:
            Generated text
        """
        pass
    
    @abstractmethod
    def load_model(self, model_name: str):
        """
        Load a model from this provider.
        
        Args:
            model_name: Name of the model to load
            
        Returns:
            Loaded model
        """
        pass
    
    @abstractmethod
    def available_models(self) -> List[str]:
        """
        Get available models from this provider.
        
        Returns:
            List of available model names/identifiers
        """
        pass
    
    def _validate_api_key(self) -> bool:
        """
        Validate that the API key is set.
        
        Returns:
            True if the API key is set, False otherwise
        """
        return self.api_key is not None and len(self.api_key) > 0 