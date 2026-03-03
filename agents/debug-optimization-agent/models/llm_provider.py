"""Multi-provider LLM configuration with fallback support."""

from typing import Optional, Literal
from langchain_core.language_models import BaseChatModel
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq

from config.settings import get_settings
from utils.logger import get_logger

logger = get_logger(__name__)


class LLMProvider:
    """Multi-provider LLM with automatic fallback."""
    
    def __init__(
        self,
        provider: Optional[Literal["openai", "anthropic", "google", "groq"]] = None,
        fallback_providers: Optional[list[str]] = None
    ):
        """
        Initialize LLM provider with fallback support.
        
        Args:
            provider: Primary LLM provider
            fallback_providers: List of fallback providers
        """
        self.settings = get_settings()
        self.provider = provider or self.settings.default_llm_provider
        self.fallback_providers = fallback_providers or ["openai", "anthropic", "google", "groq"]
        
        # Remove primary provider from fallbacks
        if self.provider in self.fallback_providers:
            self.fallback_providers.remove(self.provider)
        
        self.llm: Optional[BaseChatModel] = None
        self.current_provider = self.provider
    
    def get_llm(self, force_provider: Optional[str] = None) -> BaseChatModel:
        """
        Get LLM instance with fallback support.
        
        Args:
            force_provider: Force specific provider
            
        Returns:
            LLM instance
        """
        provider = force_provider or self.provider
        
        try:
            llm = self._create_llm(provider)
            logger.info(f"Using LLM provider: {provider}")
            self.current_provider = provider
            return llm
        except Exception as e:
            logger.warning(f"Failed to initialize {provider}: {e}")
            
            # Try fallback providers
            for fallback in self.fallback_providers:
                try:
                    llm = self._create_llm(fallback)
                    logger.info(f"Falling back to: {fallback}")
                    self.current_provider = fallback
                    return llm
                except Exception as fallback_error:
                    logger.warning(f"Failed to initialize {fallback}: {fallback_error}")
                    continue
            
            # If all providers fail, raise error
            raise RuntimeError("All LLM providers failed to initialize")
    
    def _create_llm(self, provider: str) -> BaseChatModel:
        """
        Create LLM instance for specific provider.
        
        Args:
            provider: Provider name
            
        Returns:
            LLM instance
        """
        config = self.settings.get_llm_config(provider)
        
        if provider == "openai":
            if not config["api_key"]:
                raise ValueError("OpenAI API key not configured")
            
            return ChatOpenAI(
                model=config["model"],
                temperature=config["temperature"],
                max_tokens=config["max_tokens"],
                api_key=config["api_key"]
            )
        
        elif provider == "anthropic":
            if not config["api_key"]:
                raise ValueError("Anthropic API key not configured")
            
            return ChatAnthropic(
                model=config["model"],
                temperature=config["temperature"],
                max_tokens=config["max_tokens"],
                anthropic_api_key=config["api_key"]
            )
        
        elif provider == "google":
            if not config["api_key"]:
                raise ValueError("Google API key not configured")
            
            return ChatGoogleGenerativeAI(
                model=config["model"],
                temperature=config["temperature"],
                max_tokens=config["max_tokens"],
                google_api_key=config["api_key"]
            )
        
        elif provider == "groq":
            if not config["api_key"]:
                raise ValueError("Groq API key not configured")
            
            return ChatGroq(
                model=config["model"],
                temperature=config["temperature"],
                max_tokens=config["max_tokens"],
                groq_api_key=config["api_key"]
            )
        
        else:
            raise ValueError(f"Unsupported provider: {provider}")
    
    def switch_provider(self, provider: str) -> BaseChatModel:
        """
        Switch to different provider.
        
        Args:
            provider: New provider name
            
        Returns:
            New LLM instance
        """
        self.provider = provider
        return self.get_llm()


def get_llm(
    provider: Optional[str] = None,
    temperature: Optional[float] = None,
    max_tokens: Optional[int] = None
) -> BaseChatModel:
    """
    Convenience function to get LLM instance.
    
    Args:
        provider: LLM provider
        temperature: Temperature override
        max_tokens: Max tokens override
        
    Returns:
        LLM instance
    """
    settings = get_settings()
    provider = provider or settings.default_llm_provider
    
    config = settings.get_llm_config(provider)
    
    # Override config if provided
    if temperature is not None:
        config["temperature"] = temperature
    if max_tokens is not None:
        config["max_tokens"] = max_tokens
    
    llm_provider = LLMProvider(provider=provider)
    return llm_provider.get_llm()


class LLMFactory:
    """Factory for creating specialized LLM instances."""
    
    @staticmethod
    def create_analyzer_llm() -> BaseChatModel:
        """Create LLM optimized for code analysis."""
        return get_llm(temperature=0.0, max_tokens=4096)
    
    @staticmethod
    def create_optimizer_llm() -> BaseChatModel:
        """Create LLM optimized for generating optimizations."""
        return get_llm(temperature=0.1, max_tokens=8192)
    
    @staticmethod
    def create_validator_llm() -> BaseChatModel:
        """Create LLM optimized for validation."""
        return get_llm(temperature=0.0, max_tokens=2048)
    
    @staticmethod
    def create_creative_llm() -> BaseChatModel:
        """Create LLM with higher temperature for creative solutions."""
        return get_llm(temperature=0.3, max_tokens=4096)