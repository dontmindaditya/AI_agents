"""
LLM Provider abstraction layer supporting multiple providers
"""

from typing import Optional, Dict, Any
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.language_models.base import BaseLanguageModel
from config.settings import settings


class LLMProvider:
    """Factory class for creating LLM instances from different providers"""
    
    SUPPORTED_PROVIDERS = {
        "openai": {
            "class": ChatOpenAI,
            "default_model": "gpt-4-turbo-preview",
            "models": ["gpt-4-turbo-preview", "gpt-4", "gpt-3.5-turbo", "gpt-4o"]
        },
        "anthropic": {
            "class": ChatAnthropic,
            "default_model": "claude-3-opus-20240229",
            "models": ["claude-3-opus-20240229", "claude-3-sonnet-20240229", "claude-3-haiku-20240307"]
        },
        "google": {
            "class": ChatGoogleGenerativeAI,
            "default_model": "gemini-pro",
            "models": ["gemini-pro", "gemini-pro-vision"]
        }
    }
    
    @classmethod
    def create_llm(
        cls,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> BaseLanguageModel:
        """
        Create an LLM instance from the specified provider
        
        Args:
            provider: LLM provider name (openai, anthropic, google)
            model: Specific model to use
            temperature: Temperature for generation
            max_tokens: Maximum tokens to generate
            **kwargs: Additional provider-specific parameters
            
        Returns:
            Configured LLM instance
        """
        # Use defaults from settings if not provided
        provider = provider or settings.default_llm_provider
        temperature = temperature if temperature is not None else settings.temperature
        max_tokens = max_tokens or settings.max_tokens
        
        # Validate provider
        if provider not in cls.SUPPORTED_PROVIDERS:
            raise ValueError(
                f"Unsupported provider: {provider}. "
                f"Supported providers: {list(cls.SUPPORTED_PROVIDERS.keys())}"
            )
        
        provider_config = cls.SUPPORTED_PROVIDERS[provider]
        model = model or provider_config["default_model"]
        
        # Validate model for provider
        if model not in provider_config["models"]:
            print(f"Warning: Model '{model}' may not be supported by {provider}")
        
        # Get API key
        api_key = settings.get_api_key(provider)
        
        # Create LLM instance based on provider
        llm_class = provider_config["class"]
        
        if provider == "openai":
            return llm_class(
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
                openai_api_key=api_key,
                **kwargs
            )
        elif provider == "anthropic":
            return llm_class(
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
                anthropic_api_key=api_key,
                **kwargs
            )
        elif provider == "google":
            return llm_class(
                model=model,
                temperature=temperature,
                max_output_tokens=max_tokens,
                google_api_key=api_key,
                **kwargs
            )
        else:
            raise ValueError(f"Provider implementation not found: {provider}")
    
    @classmethod
    def get_available_models(cls, provider: str) -> list:
        """Get list of available models for a provider"""
        if provider not in cls.SUPPORTED_PROVIDERS:
            raise ValueError(f"Unsupported provider: {provider}")
        return cls.SUPPORTED_PROVIDERS[provider]["models"]
    
    @classmethod
    def get_supported_providers(cls) -> list:
        """Get list of all supported providers"""
        return list(cls.SUPPORTED_PROVIDERS.keys())


# Example usage functions
def create_default_llm() -> BaseLanguageModel:
    """Create LLM with default settings"""
    return LLMProvider.create_llm()


def create_discussion_llm() -> BaseLanguageModel:
    """Create LLM optimized for agent discussions"""
    return LLMProvider.create_llm(
        temperature=0.8,  # Higher creativity for discussions
        max_tokens=1500
    )


def create_instructor_llm() -> BaseLanguageModel:
    """Create LLM optimized for teaching"""
    return LLMProvider.create_llm(
        temperature=0.7,  # Balanced for teaching
        max_tokens=2000
    )


def create_syllabus_llm() -> BaseLanguageModel:
    """Create LLM optimized for syllabus generation"""
    return LLMProvider.create_llm(
        temperature=0.6,  # More focused for structured output
        max_tokens=3000
    )