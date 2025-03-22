import logging
from typing import Dict, List, Optional, Union, Any

import anthropic
from anthropic import Anthropic

from .base_provider import BaseProvider
from ...utils.logging_utils import setup_logger

logger = setup_logger("linguallens.providers.anthropic")

class AnthropicProvider(BaseProvider):
    """
    Provider implementation for Anthropic Claude models.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Anthropic provider.
        
        Args:
            api_key: Anthropic API key
        """
        super().__init__(api_key)
        
        if not self._validate_api_key():
            logger.warning("Anthropic API key not provided. Some functionality may not work.")
        
        # Initialize the Anthropic client
        self.client = Anthropic(api_key=self.api_key)
        
        # Default models
        self.default_models = [
            "claude-3-opus-20240229",
            "claude-3-sonnet-20240229",
            "claude-3-haiku-20240307",
            "claude-2.1",
            "claude-2.0",
            "claude-instant-1.2"
        ]
    
    def generate(
        self,
        prompt: str,
        model: str = "claude-3-sonnet-20240229",
        max_tokens: int = 1000,
        temperature: float = 0.7,
        top_p: float = 1.0,
        stop: Optional[Union[str, List[str]]] = None,
        stream: bool = False,
        system_message: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        Generate text using an Anthropic model.
        
        Args:
            prompt: Input prompt
            model: Model name (e.g., 'claude-3-opus-20240229')
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
        if not self._validate_api_key():
            raise ValueError("Anthropic API key is required")
        
        logger.info(f"Generating with Anthropic model: {model}")
        
        try:
            # Prepare messages
            messages = [{"role": "user", "content": prompt}]
            
            # Make the API call
            response = self.client.messages.create(
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=messages,
                system=system_message,
                stream=stream,
                **kwargs
            )
            
            if stream:
                # Handle streaming response
                collected_message = ""
                
                for chunk in response:
                    if chunk.type == "content_block_delta" and chunk.delta.text:
                        collected_message += chunk.delta.text
                
                return collected_message
            else:
                # Handle regular response
                return response.content[0].text
        
        except Exception as e:
            logger.error(f"Error generating text with Anthropic: {str(e)}")
            raise
    
    def load_model(self, model_name: str):
        """
        Load an Anthropic model.
        Note: This doesn't actually load the model locally, as Anthropic models
        are accessed via API. This is mainly for compatibility with the interface.
        
        Args:
            model_name: Name of the model to load
            
        Returns:
            A proxy object representing the model
        """
        logger.info(f"Loading Anthropic model: {model_name}")
        
        class AnthropicModel:
            def __init__(self, provider, model_name):
                self.provider = provider
                self.model_name = model_name
            
            def generate(self, prompt, **kwargs):
                return self.provider.generate(prompt=prompt, model=self.model_name, **kwargs)
        
        return AnthropicModel(self, model_name)
    
    def available_models(self) -> List[str]:
        """
        Get list of available Anthropic models.
        
        Returns:
            List of available model names
        """
        # Anthropic doesn't have an API endpoint to list available models,
        # so we return the default list
        return self.default_models 