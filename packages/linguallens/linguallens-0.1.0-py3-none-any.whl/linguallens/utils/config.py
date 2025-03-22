import os
import json
import yaml
from typing import Dict, Optional, Any, List

class ModelConfig:
    """
    Configuration class for models and providers.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize model configuration.
        
        Args:
            config_path: Path to configuration file (JSON or YAML)
        """
        self.config: Dict[str, Any] = {
            "providers": {
                "openai": {
                    "models": {
                        "gpt-3.5-turbo": {
                            "max_tokens": 4096,
                            "default_params": {
                                "temperature": 0.7,
                                "top_p": 1.0
                            }
                        },
                        "gpt-4": {
                            "max_tokens": 8192,
                            "default_params": {
                                "temperature": 0.7,
                                "top_p": 1.0
                            }
                        }
                    }
                },
                "anthropic": {
                    "models": {
                        "claude-3-opus-20240229": {
                            "max_tokens": 4096,
                            "default_params": {
                                "temperature": 0.7,
                                "top_p": 1.0
                            }
                        },
                        "claude-3-sonnet-20240229": {
                            "max_tokens": 4096,
                            "default_params": {
                                "temperature": 0.7,
                                "top_p": 1.0
                            }
                        }
                    }
                },
                "huggingface": {
                    "models": {
                        "mistralai/Mistral-7B-Instruct-v0.2": {
                            "max_tokens": 2048,
                            "default_params": {
                                "temperature": 0.7,
                                "top_p": 1.0
                            }
                        }
                    }
                },
                "google": {
                    "models": {
                        "gemini-pro": {
                            "max_tokens": 2048,
                            "default_params": {
                                "temperature": 0.7,
                                "top_p": 1.0
                            }
                        }
                    }
                }
            }
        }
        
        if config_path:
            self.load_config(config_path)
    
    def load_config(self, config_path: str) -> None:
        """
        Load configuration from a file.
        
        Args:
            config_path: Path to configuration file
        """
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
        try:
            if config_path.endswith(".json"):
                with open(config_path, "r") as f:
                    loaded_config = json.load(f)
            elif config_path.endswith((".yaml", ".yml")):
                with open(config_path, "r") as f:
                    loaded_config = yaml.safe_load(f)
            else:
                raise ValueError("Configuration file must be JSON or YAML")
            
            # Merge loaded config with default config
            self._merge_configs(self.config, loaded_config)
        
        except Exception as e:
            raise ValueError(f"Error loading configuration: {str(e)}")
    
    def _merge_configs(self, base: Dict[str, Any], override: Dict[str, Any]) -> None:
        """
        Merge two configurations, with override taking precedence.
        
        Args:
            base: Base configuration
            override: Configuration to override with
        """
        for key, value in override.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._merge_configs(base[key], value)
            else:
                base[key] = value
    
    def get_model_config(self, provider: str, model: str) -> Dict[str, Any]:
        """
        Get configuration for a specific model.
        
        Args:
            provider: Provider name
            model: Model name
            
        Returns:
            Model configuration
        """
        if (
            provider in self.config["providers"] and
            "models" in self.config["providers"][provider] and
            model in self.config["providers"][provider]["models"]
        ):
            return self.config["providers"][provider]["models"][model]
        
        # Return empty config if not found
        return {"max_tokens": 1000, "default_params": {}}
    
    def get_provider_config(self, provider: str) -> Dict[str, Any]:
        """
        Get configuration for a specific provider.
        
        Args:
            provider: Provider name
            
        Returns:
            Provider configuration
        """
        if provider in self.config["providers"]:
            return self.config["providers"][provider]
        
        # Return empty config if not found
        return {"models": {}}
    
    def get_all_models(self, provider: Optional[str] = None) -> List[str]:
        """
        Get all models for a provider or for all providers.
        
        Args:
            provider: Provider name (if None, get for all providers)
            
        Returns:
            List of model names
        """
        if provider:
            if provider in self.config["providers"] and "models" in self.config["providers"][provider]:
                return list(self.config["providers"][provider]["models"].keys())
            return []
        
        # Get all models from all providers
        all_models = []
        for provider_name, provider_config in self.config["providers"].items():
            if "models" in provider_config:
                all_models.extend(provider_config["models"].keys())
        
        return all_models 