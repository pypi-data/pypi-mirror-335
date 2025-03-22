import logging
import os
from typing import Dict, List, Optional, Union, Any

try:
    import torch
    from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
    HF_AVAILABLE = True
except ImportError:
    HF_AVAILABLE = False

from .base_provider import BaseProvider
from ...utils.logging_utils import setup_logger

logger = setup_logger("linguallens.providers.huggingface")

class HuggingFaceProvider(BaseProvider):
    """
    Provider implementation for HuggingFace models.
    Supports both local models and HuggingFace Inference API.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the HuggingFace provider.
        
        Args:
            api_key: HuggingFace API key
        """
        super().__init__(api_key)
        
        if not HF_AVAILABLE:
            logger.error("HuggingFace transformers package not available. Please install it using 'pip install transformers torch'")
        
        # Cache of loaded models
        self.model_cache = {}
        
        # Default models
        self.default_models = [
            "mistralai/Mistral-7B-Instruct-v0.2",
            "meta-llama/Llama-2-7b-chat-hf",
            "google/flan-t5-xxl",
            "EleutherAI/gpt-j-6b",
            "EleutherAI/pythia-6.9b",
            "bigscience/bloom-7b1"
        ]
    
    def generate(
        self,
        prompt: str,
        model: str = "mistralai/Mistral-7B-Instruct-v0.2",
        max_tokens: int = 1000,
        temperature: float = 0.7,
        top_p: float = 1.0,
        stop: Optional[Union[str, List[str]]] = None,
        stream: bool = False,
        use_api: bool = False,
        system_message: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        Generate text using a HuggingFace model.
        
        Args:
            prompt: Input prompt
            model: Model name (e.g., 'mistralai/Mistral-7B-Instruct-v0.2')
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            top_p: Top-p sampling parameter
            stop: Stop sequences
            stream: Whether to stream the response (not supported for local models)
            use_api: Whether to use the HuggingFace Inference API
            system_message: Optional system message
            **kwargs: Additional model-specific parameters
            
        Returns:
            Generated text
        """
        if not HF_AVAILABLE:
            raise ImportError("HuggingFace transformers package not available")
        
        logger.info(f"Generating with HuggingFace model: {model}")
        
        if use_api:
            return self._generate_with_api(
                prompt=prompt,
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p,
                stop=stop,
                system_message=system_message,
                **kwargs
            )
        else:
            return self._generate_with_local_model(
                prompt=prompt,
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p,
                stop=stop,
                system_message=system_message,
                **kwargs
            )
    
    def _generate_with_api(
        self,
        prompt: str,
        model: str,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        top_p: float = 1.0,
        stop: Optional[Union[str, List[str]]] = None,
        system_message: Optional[str] = None,
        **kwargs
    ) -> str:
        """Generate text using the HuggingFace Inference API."""
        if not self._validate_api_key():
            raise ValueError("HuggingFace API key is required for API inference")
        
        try:
            from huggingface_hub import InferenceClient
            
            client = InferenceClient(token=self.api_key)
            
            # Format the prompt with system message if provided
            formatted_prompt = prompt
            if system_message:
                formatted_prompt = f"{system_message}\n\n{prompt}"
            
            params = {
                "max_new_tokens": max_tokens,
                "temperature": temperature,
                "top_p": top_p
            }
            
            if stop:
                params["stop_sequences"] = stop if isinstance(stop, list) else [stop]
            
            # Add any other parameters
            params.update(kwargs)
            
            # Make the API call
            response = client.text_generation(
                formatted_prompt,
                model=model,
                **params
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Error generating text with HuggingFace API: {str(e)}")
            raise
    
    def _generate_with_local_model(
        self,
        prompt: str,
        model: str,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        top_p: float = 1.0,
        stop: Optional[Union[str, List[str]]] = None,
        system_message: Optional[str] = None,
        **kwargs
    ) -> str:
        """Generate text using a local HuggingFace model."""
        try:
            # Format the prompt with system message if provided
            formatted_prompt = prompt
            if system_message:
                formatted_prompt = f"{system_message}\n\n{prompt}"
            
            # Load or get the model from cache
            generator = self._get_or_load_model(model)
            
            # Set up generation parameters
            gen_kwargs = {
                "max_new_tokens": max_tokens,
                "temperature": temperature,
                "top_p": top_p,
                "do_sample": temperature > 0,
                "pad_token_id": 50256  # Default for GPT models
            }
            
            if stop:
                gen_kwargs["eos_token_id"] = stop
            
            # Add any other parameters
            gen_kwargs.update(kwargs)
            
            # Generate
            result = generator(formatted_prompt, **gen_kwargs)
            
            if isinstance(result, list) and len(result) > 0:
                if isinstance(result[0], dict) and "generated_text" in result[0]:
                    text = result[0]["generated_text"]
                    # Remove the input prompt from the output
                    if text.startswith(formatted_prompt):
                        text = text[len(formatted_prompt):].strip()
                    return text
                return str(result[0])
            
            return str(result)
        
        except Exception as e:
            logger.error(f"Error generating text with local HuggingFace model: {str(e)}")
            raise
    
    def _get_or_load_model(self, model_name: str):
        """Get a model from cache or load it."""
        if model_name in self.model_cache:
            return self.model_cache[model_name]
        
        generator = pipeline(
            "text-generation",
            model=model_name,
            device=0 if torch.cuda.is_available() else -1,
            token=self.api_key
        )
        
        self.model_cache[model_name] = generator
        return generator
    
    def load_model(self, model_name: str):
        """
        Load a HuggingFace model.
        
        Args:
            model_name: Name of the model to load
            
        Returns:
            Loaded model
        """
        if not HF_AVAILABLE:
            raise ImportError("HuggingFace transformers package not available")
        
        logger.info(f"Loading HuggingFace model: {model_name}")
        
        generator = self._get_or_load_model(model_name)
        
        class HuggingFaceModel:
            def __init__(self, provider, model_name, generator):
                self.provider = provider
                self.model_name = model_name
                self.generator = generator
            
            def generate(self, prompt, **kwargs):
                return self.provider.generate(prompt=prompt, model=self.model_name, **kwargs)
            
            def get_pipeline(self):
                return self.generator
        
        return HuggingFaceModel(self, model_name, generator)
    
    def available_models(self) -> List[str]:
        """
        Get list of available HuggingFace models.
        This is just a subset of popular models as HuggingFace has thousands of models.
        
        Returns:
            List of available model names
        """
        return self.default_models 