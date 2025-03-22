import os
from typing import Dict, List, Optional, Union, Any
import logging

# Provider-specific clients
import openai
import anthropic
try:
    import google.generativeai as genai
except ImportError:
    genai = None

from ..utils.logging_utils import setup_logger
from ..utils.config import ModelConfig
from .providers.openai_provider import OpenAIProvider
from .providers.anthropic_provider import AnthropicProvider
from .providers.huggingface_provider import HuggingFaceProvider
from .providers.google_provider import GoogleProvider
from .providers.base_provider import BaseProvider

logger = setup_logger("linguallens")

class LingualLens:
    """
    Main class for LingualLens - a multi-provider framework for large language models.
    Provides a unified interface for interacting with models from different providers.
    """
    
    def __init__(
        self,
        openai_api_key: Optional[str] = None,
        anthropic_api_key: Optional[str] = None,
        hf_api_key: Optional[str] = None,
        google_api_key: Optional[str] = None,
        api_key: Optional[str] = None,  # Generic API key
        default_provider: str = "openai",
        default_model: Optional[str] = None,
        log_level: str = "INFO",
        config_path: Optional[str] = None
    ):
        """
        Initialize LingualLens with API keys for different providers.
        
        Args:
            openai_api_key: API key for OpenAI
            anthropic_api_key: API key for Anthropic
            hf_api_key: API key for HuggingFace
            google_api_key: API key for Google AI
            api_key: Generic API key (used if provider-specific key not provided)
            default_provider: Default provider to use if not specified
            default_model: Default model to use if not specified
            log_level: Logging level
            config_path: Path to configuration file
        """
        # Set up logging
        logging.getLogger("linguallens").setLevel(getattr(logging, log_level))
        
        # Load API keys from environment if not provided
        self.openai_api_key = openai_api_key or os.getenv("OPENAI_API_KEY") or api_key
        self.anthropic_api_key = anthropic_api_key or os.getenv("ANTHROPIC_API_KEY") or api_key
        self.hf_api_key = hf_api_key or os.getenv("HF_API_KEY") or os.getenv("HUGGINGFACE_API_KEY") or api_key
        self.google_api_key = google_api_key or os.getenv("GOOGLE_API_KEY") or api_key
        
        # Load configuration
        self.config = ModelConfig(config_path)
        
        # Set default provider and model
        self.default_provider = default_provider
        self.default_model = default_model or self._get_default_model(default_provider)
        
        # Initialize provider instances
        self.providers: Dict[str, BaseProvider] = {}
        self._initialize_providers()
        
        logger.info(f"LingualLens initialized with default provider: {default_provider}")
    
    def _initialize_providers(self) -> None:
        """Initialize all available providers based on API keys."""
        if self.openai_api_key:
            self.providers["openai"] = OpenAIProvider(api_key=self.openai_api_key)
            logger.info("OpenAI provider initialized")
        
        if self.anthropic_api_key:
            self.providers["anthropic"] = AnthropicProvider(api_key=self.anthropic_api_key)
            logger.info("Anthropic provider initialized")
        
        if self.hf_api_key:
            self.providers["huggingface"] = HuggingFaceProvider(api_key=self.hf_api_key)
            logger.info("HuggingFace provider initialized")
        
        if self.google_api_key and genai:
            self.providers["google"] = GoogleProvider(api_key=self.google_api_key)
            logger.info("Google provider initialized")
    
    def _get_default_model(self, provider: str) -> str:
        """Get the default model for a provider."""
        provider_defaults = {
            "openai": "gpt-3.5-turbo",
            "anthropic": "claude-3-sonnet-20240229",
            "huggingface": "mistralai/Mistral-7B-Instruct-v0.2",
            "google": "gemini-pro"
        }
        return provider_defaults.get(provider, "gpt-3.5-turbo")
    
    def _resolve_provider_and_model(
        self, provider: Optional[str] = None, model: Optional[str] = None
    ) -> tuple:
        """Resolve the provider and model to use."""
        if not provider:
            provider = self.default_provider
        
        if provider not in self.providers:
            available = ", ".join(self.providers.keys())
            raise ValueError(
                f"Provider '{provider}' not initialized. Available providers: {available}"
            )
        
        # If model is not specified, use default for the provider
        if not model:
            model = self._get_default_model(provider)
        
        return provider, model
    
    def generate(
        self,
        prompt: str,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        top_p: float = 1.0,
        stop: Optional[Union[str, List[str]]] = None,
        stream: bool = False,
        **kwargs
    ) -> str:
        """
        Generate text using the specified provider and model.
        
        Args:
            prompt: The input prompt
            provider: Provider to use (openai, anthropic, huggingface, google)
            model: Model to use
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            top_p: Top-p sampling parameter
            stop: Stop sequences
            stream: Whether to stream the response
            **kwargs: Additional provider-specific parameters
            
        Returns:
            Generated text
        """
        provider, model = self._resolve_provider_and_model(provider, model)
        logger.info(f"Generating with {provider}/{model}")
        
        return self.providers[provider].generate(
            prompt=prompt,
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p,
            stop=stop,
            stream=stream,
            **kwargs
        )
    
    def classify_sentiment(
        self, 
        text: str, 
        provider: Optional[str] = None,
        model: Optional[str] = None
    ) -> str:
        """
        Classify the sentiment of text.
        
        Args:
            text: Text to classify
            provider: Provider to use
            model: Model to use
            
        Returns:
            Sentiment classification (positive, negative, neutral)
        """
        prompt = f"Classify the sentiment of the following text as positive, negative, or neutral:\n\n{text}"
        response = self.generate(prompt, provider=provider, model=model)
        
        # Extract sentiment from response
        if "positive" in response.lower():
            return "positive"
        elif "negative" in response.lower():
            return "negative"
        else:
            return "neutral"
    
    def extract_entities(
        self, 
        text: str, 
        provider: Optional[str] = None,
        model: Optional[str] = None
    ) -> List[Dict[str, str]]:
        """
        Extract named entities from text.
        
        Args:
            text: Text to analyze
            provider: Provider to use
            model: Model to use
            
        Returns:
            List of entities with type and value
        """
        prompt = f"Extract named entities from the following text. Format the output as a list of JSON objects with 'type' and 'value' fields:\n\n{text}"
        response = self.generate(prompt, provider=provider, model=model)
        
        try:
            import json
            # Try to parse entities from response
            if "[" in response and "]" in response:
                entities_str = response[response.find("["):response.rfind("]")+1]
                return json.loads(entities_str)
            return []
        except Exception as e:
            logger.error(f"Error parsing entities: {e}")
            return []
    
    def load_model(self, model_name: str, provider: Optional[str] = None):
        """
        Load a pre-trained model.
        
        Args:
            model_name: Name of the model to load
            provider: Provider to use
            
        Returns:
            Loaded model
        """
        if not provider:
            # Try to determine provider from model name
            if model_name.startswith("gpt"):
                provider = "openai"
            elif model_name.startswith("claude"):
                provider = "anthropic"
            elif "gemini" in model_name:
                provider = "google"
            else:
                provider = "huggingface"
        
        provider, _ = self._resolve_provider_and_model(provider, model_name)
        return self.providers[provider].load_model(model_name)
    
    def analyze_feature_importance(self, model, X, y):
        """
        Analyze feature importance for a model.
        
        Args:
            model: The model to analyze
            X: Features
            y: Target
            
        Returns:
            Feature importance scores
        """
        from ..explainers import FeatureImportanceAnalyzer
        analyzer = FeatureImportanceAnalyzer()
        return analyzer.analyze(model, X, y)
    
    def available_providers(self) -> List[str]:
        """Get list of available providers."""
        return list(self.providers.keys())
    
    def available_models(self, provider: Optional[str] = None) -> Dict[str, List[str]]:
        """
        Get available models for providers.
        
        Args:
            provider: If specified, only return models for this provider
            
        Returns:
            Dictionary of provider -> list of models
        """
        if provider:
            if provider not in self.providers:
                raise ValueError(f"Provider {provider} not available")
            return {provider: self.providers[provider].available_models()}
        
        return {p: self.providers[p].available_models() for p in self.providers} 