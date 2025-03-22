# LingualLens

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)
[![Multi-Provider](https://img.shields.io/badge/multi--provider-OpenAI%20%7C%20Google%20%7C%20Anthropic%20%7C%20HF-blueviolet)]()

A unified interface for interacting with language models from multiple providers.

## Features

- **Multi-Provider Support**: Interact with models from OpenAI, Anthropic, Google, and HuggingFace through a single consistent API
- **Simple Interface**: Generate text, classify sentiment, and extract entities with just a few lines of code
- **Provider-Agnostic**: Switch between different providers and models without changing your code
- **Extensible**: Easy to add support for additional providers
- **Configurable**: Configure models and providers through code or configuration files

## Installation

```bash
# Basic installation
pip install linguallens

# With support for specific providers
pip install linguallens[openai]      # OpenAI support
pip install linguallens[anthropic]   # Anthropic support
pip install linguallens[google]      # Google support
pip install linguallens[huggingface] # HuggingFace support

# Full installation with all providers
pip install linguallens[all]
```

## Quick Start

```python
from linguallens import LingualLens

# Initialize with API keys for different providers
lens = LingualLens(
    openai_api_key="your-openai-key",
    anthropic_api_key="your-anthropic-key",
    google_api_key="your-google-key",
    default_provider="openai",
    default_model="gpt-3.5-turbo"
)

# Generate text with the default provider and model
response = lens.generate("Explain quantum computing in simple terms")
print(response)

# Use a different provider and model
response = lens.generate(
    "What are the ethical implications of AI?",
    provider="anthropic",
    model="claude-3-opus-20240229"
)
print(response)

# Analyze sentiment
sentiment = lens.classify_sentiment("I love this product! It works great.")
print(sentiment)  # {'score': 1.0, 'label': 'positive', ...}

# Extract entities
entities = lens.extract_entities("Contact us at support@example.com or visit https://example.com")
print(entities)  # [{'type': 'EMAIL', 'value': 'support@example.com', ...}, ...]
```

## Advanced Usage

### Configuration Files

LingualLens supports configuration through JSON or YAML files:

```python
lens = LingualLens(config_path="config.yaml")
```

Example `config.yaml`:
```yaml
providers:
  openai:
    api_key: "your-openai-key"
    models:
      gpt-4:
        max_tokens: 8192
        default_params:
          temperature: 0.7
          top_p: 1.0
  anthropic:
    api_key: "your-anthropic-key"
    models:
      claude-3-opus-20240229:
        max_tokens: 4096
        default_params:
          temperature: 0.5
```

### Working with Local Models

For HuggingFace models, you can choose between using the Inference API or local models:

```python
# Use a local model
response = lens.generate(
    "What is machine learning?",
    provider="huggingface",
    model="mistralai/Mistral-7B-Instruct-v0.2",
    use_api=False  # Use local model instead of API
)
```

## Adding a New Provider

LingualLens is designed to be easily extensible. To add a new provider:

1. Create a new class that inherits from `BaseProvider`
2. Implement the required methods: `generate`, `load_model`, and `available_models`
3. Register the provider with LingualLens

```python
from linguallens import BaseProvider, LingualLens

class MyCustomProvider(BaseProvider):
    def __init__(self, api_key=None):
        super().__init__(api_key)
        # Initialize your provider here
    
    def generate(self, prompt, model, max_tokens=100, temperature=0.7, top_p=1.0, 
                 stop_sequences=None, streaming=False):
        # Implement text generation
        return "Generated text"
    
    def load_model(self, model_name):
        # Load or get a reference to a model
        return model_proxy
    
    def available_models(self):
        # Return a list of available models
        return ["model1", "model2"]

# Register the provider
LingualLens.register_provider("my_provider", MyCustomProvider)

# Use the provider
lens = LingualLens(my_provider_api_key="your-key")
response = lens.generate("Hello", provider="my_provider", model="model1")
```

## License

MIT 