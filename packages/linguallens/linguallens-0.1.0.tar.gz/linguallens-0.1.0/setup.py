from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="linguallens",
    version="0.1.0",
    author="LingualLens Team",
    author_email="info@linguallens.io",
    description="A unified interface for interacting with language models from multiple providers",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/linguallens/linguallens",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.28.0",
        "pyyaml>=6.0",
    ],
    extras_require={
        "openai": ["openai>=1.0.0"],
        "anthropic": ["anthropic>=0.5.0"],
        "google": ["google-generativeai>=0.2.0"],
        "huggingface": ["transformers>=4.30.0", "torch>=2.0.0"],
        "all": [
            "openai>=1.0.0",
            "anthropic>=0.5.0",
            "google-generativeai>=0.2.0",
            "transformers>=4.30.0",
            "torch>=2.0.0",
        ],
        "dev": [
            "pytest>=7.0.0",
            "black>=23.0.0",
            "isort>=5.10.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
    },
)