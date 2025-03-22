import logging
from typing import Dict, List, Optional, Union, Any

import openai
from openai import OpenAI

from .base_provider import BaseProvider
from ...utils.logging_utils import setup_logger

logger = setup_logger("linguallens.providers.openai")

class OpenAIProvider(BaseProvider):
    """
    Provider implementation for OpenAI models.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the OpenAI provider.
        
        Args:
            api_key: OpenAI API key
        """
        super().__init__(api_key)
        
        if not self._validate_api_key():
            logger.warning("OpenAI API key not provided. Some functionality may not work.")
        
        # Initialize the OpenAI client
        self.client = OpenAI(api_key=self.api_key)
        
        # Cache of available models
        self._models_cache = None
    
    def generate(
        self,
        prompt: str,
        model: str = "gpt-3.5-turbo",
        max_tokens: int = 1000,
        temperature: float = 0.7,
        top_p: float = 1.0,
        stop: Optional[Union[str, List[str]]] = None,
        stream: bool = False,
        system_message: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        Generate text using an OpenAI model.
        
        Args:
            prompt: Input prompt
            model: Model name (e.g., 'gpt-3.5-turbo', 'gpt-4')
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
            raise ValueError("OpenAI API key is required")
        
        logger.info(f"Generating with OpenAI model: {model}")
        
        try:
            # Prepare messages
            messages = []
            
            if system_message:
                messages.append({"role": "system", "content": system_message})
            
            messages.append({"role": "user", "content": prompt})
            
            # Make the API call
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p,
                stop=stop,
                stream=stream,
                **kwargs
            )
            
            if stream:
                # Handle streaming response
                collected_chunks = []
                collected_messages = []
                
                for chunk in response:
                    collected_chunks.append(chunk)
                    if chunk.choices and chunk.choices[0].delta.content:
                        content = chunk.choices[0].delta.content
                        collected_messages.append(content)
                
                return "".join(collected_messages)
            else:
                # Handle regular response
                return response.choices[0].message.content
        
        except Exception as e:
            logger.error(f"Error generating text with OpenAI: {str(e)}")
            raise
    
    def load_model(self, model_name: str):
        """
        Load an OpenAI model.
        Note: This doesn't actually load the model locally, as OpenAI models
        are accessed via API. This is mainly for compatibility with the interface.
        
        Args:
            model_name: Name of the model to load
            
        Returns:
            A proxy object representing the model
        """
        logger.info(f"Loading OpenAI model: {model_name}")
        
        class OpenAIModel:
            def __init__(self, provider, model_name):
                self.provider = provider
                self.model_name = model_name
            
            def generate(self, prompt, **kwargs):
                return self.provider.generate(prompt=prompt, model=self.model_name, **kwargs)
        
        return OpenAIModel(self, model_name)
    
    def available_models(self) -> List[str]:
        """
        Get list of available OpenAI models.
        
        Returns:
            List of available model names
        """
        if not self._validate_api_key():
            logger.warning("OpenAI API key not provided. Returning default models.")
            return [
                "gpt-3.5-turbo",
                "gpt-4",
                "gpt-4-turbo-preview",
                "gpt-4-vision-preview"
            ]
        
        if self._models_cache is None:
            try:
                models = self.client.models.list()
                self._models_cache = [model.id for model in models.data if "gpt" in model.id]
            except Exception as e:
                logger.error(f"Error fetching OpenAI models: {str(e)}")
                # Return default models if API call fails
                self._models_cache = [
                    "gpt-3.5-turbo",
                    "gpt-4",
                    "gpt-4-turbo-preview",
                    "gpt-4-vision-preview"
                ]
        
        return self._models_cache 