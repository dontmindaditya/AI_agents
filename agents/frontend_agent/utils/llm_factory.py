from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chat_models.base import BaseChatModel
from config.settings import (
    LLM_PROVIDER,
    LLM_MODEL,
    LLM_TEMPERATURE,
    OPENAI_API_KEY,
    ANTHROPIC_API_KEY,
    GOOGLE_API_KEY
)


def create_llm(temperature: float = None) -> BaseChatModel:
    """
    Factory function to create LLM based on provider configuration.
    
    Args:
        temperature: Optional temperature override
        
    Returns:
        BaseChatModel instance
    """
    temp = temperature if temperature is not None else LLM_TEMPERATURE
    
    if LLM_PROVIDER == "openai":
        return ChatOpenAI(
            model=LLM_MODEL,
            temperature=temp,
            api_key=OPENAI_API_KEY
        )
    
    elif LLM_PROVIDER == "anthropic":
        return ChatAnthropic(
            model=LLM_MODEL,
            temperature=temp,
            api_key=ANTHROPIC_API_KEY
        )
    
    elif LLM_PROVIDER == "google":
        return ChatGoogleGenerativeAI(
            model=LLM_MODEL,
            temperature=temp,
            google_api_key=GOOGLE_API_KEY
        )
    
    else:
        raise ValueError(f"Unsupported LLM provider: {LLM_PROVIDER}")


def create_analyzer_llm() -> BaseChatModel:
    """Create LLM optimized for analysis tasks"""
    return create_llm(temperature=0.3)


def create_generator_llm() -> BaseChatModel:
    """Create LLM optimized for code generation"""
    return create_llm(temperature=0.7)


def create_optimizer_llm() -> BaseChatModel:
    """Create LLM optimized for optimization tasks"""
    return create_llm(temperature=0.4)