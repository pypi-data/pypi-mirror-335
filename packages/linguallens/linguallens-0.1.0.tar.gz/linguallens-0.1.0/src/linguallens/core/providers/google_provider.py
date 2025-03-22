import logging
from typing import Dict, List, Optional, Union, Any

try:
    import google.generativeai as genai
    GOOGLE_AVAILABLE = True
except ImportError:
    GOOGLE_AVAILABLE = False

from .base_provider import BaseProvider
from ...utils.logging_utils import setup_logger

logger = setup_logger("linguallens.providers.google")

class GoogleProvider(BaseProvider):
    """
    Provider implementation for Google models (Gemini).
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Google provider.
        
        Args:
            api_key: Google API key
        """
        super().__init__(api_key)
        
        if not GOOGLE_AVAILABLE:
            logger.error("Google GenerativeAI package not available. Please install it using 'pip install google-generativeai'")
            return
        
        if not self._validate_api_key():
            logger.warning("Google API key not provided. Some functionality may not work.")
            return
        
        # Initialize the Google client
        genai.configure(api_key=self.api_key)
        
        # Default models
        self.default_models = [
            "gemini-pro",
            "gemini-pro-vision",
            "gemini-ultra"
        ]
        
        # Cache of available models
        self._models_cache = None
    
    def generate(
        self,
        prompt: str,
        model: str = "gemini-pro",
        max_tokens: int = 1000,
        temperature: float = 0.7,
        top_p: float = 1.0,
        stop: Optional[Union[str, List[str]]] = None,
        stream: bool = False,
        system_message: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        Generate text using a Google model.
        
        Args:
            prompt: Input prompt
            model: Model name (e.g., 'gemini-pro')
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            top_p: Top-p sampling parameter
            stop: Stop sequences
            stream: Whether to stream the response
            system_message: Optional system message
            **kwargs: Additional model-specific parameters
            
        Returns:
            Generated text
        """
        if not GOOGLE_AVAILABLE:
            raise ImportError("Google GenerativeAI package not available")
        
        if not self._validate_api_key():
            raise ValueError("Google API key is required")
        
        logger.info(f"Generating with Google model: {model}")
        
        try:
            # Initialize the model
            google_model = genai.GenerativeModel(
                model_name=model,
                generation_config={
                    "max_output_tokens": max_tokens,
                    "temperature": temperature,
                    "top_p": top_p,
                    "stop_sequences": stop if stop else []
                }
            )
            
            # Prepare content
            content = []
            
            if system_message:
                content.append({"role": "system", "parts": [system_message]})
            
            content.append({"role": "user", "parts": [prompt]})
            
            # Make the API call
            if len(content) > 1:
                # Use chat endpoint if system message is provided
                response = google_model.generate_content(
                    content,
                    stream=stream,
                    **kwargs
                )
            else:
                # Use regular endpoint for simple prompts
                response = google_model.generate_content(
                    prompt,
                    stream=stream,
                    **kwargs
                )
            
            if stream:
                # Handle streaming response
                collected_text = ""
                
                for chunk in response:
                    if chunk.text:
                        collected_text += chunk.text
                
                return collected_text
            else:
                # Handle regular response
                return response.text
        
        except Exception as e:
            logger.error(f"Error generating text with Google: {str(e)}")
            raise
    
    def load_model(self, model_name: str):
        """
        Load a Google model.
        Note: This doesn't actually load the model locally, as Google models
        are accessed via API. This is mainly for compatibility with the interface.
        
        Args:
            model_name: Name of the model to load
            
        Returns:
            A proxy object representing the model
        """
        if not GOOGLE_AVAILABLE:
            raise ImportError("Google GenerativeAI package not available")
        
        logger.info(f"Loading Google model: {model_name}")
        
        class GoogleModel:
            def __init__(self, provider, model_name):
                self.provider = provider
                self.model_name = model_name
            
            def generate(self, prompt, **kwargs):
                return self.provider.generate(prompt=prompt, model=self.model_name, **kwargs)
        
        return GoogleModel(self, model_name)
    
    def available_models(self) -> List[str]:
        """
        Get list of available Google models.
        
        Returns:
            List of available model names
        """
        if not GOOGLE_AVAILABLE:
            logger.warning("Google GenerativeAI package not available")
            return []
        
        if not self._validate_api_key():
            logger.warning("Google API key not provided. Returning default models.")
            return self.default_models
        
        if self._models_cache is None:
            try:
                # Currently, Google doesn't provide a dedicated API to list models
                # So we use the default list
                self._models_cache = self.default_models
            except Exception as e:
                logger.error(f"Error fetching Google models: {str(e)}")
                self._models_cache = self.default_models
        
        return self._models_cache 