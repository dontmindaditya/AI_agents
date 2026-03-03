"""Configuration settings for Debug Optimization Agent."""

from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with environment variable support."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # LLM API Keys
    openai_api_key: str = Field(default="", description="OpenAI API key")
    anthropic_api_key: str = Field(default="", description="Anthropic API key")
    google_api_key: str = Field(default="", description="Google API key")
    groq_api_key: str = Field(default="", description="Groq API key")

    # Default LLM Provider
    default_llm_provider: Literal["openai", "anthropic", "google", "groq"] = Field(
        default="openai",
        description="Default LLM provider to use"
    )

    # Model Names
    openai_model: str = Field(
        default="gpt-4-turbo-preview",
        description="OpenAI model name"
    )
    anthropic_model: str = Field(
        default="claude-3-5-sonnet-20241022",
        description="Anthropic model name"
    )
    google_model: str = Field(
        default="gemini-pro",
        description="Google model name"
    )
    groq_model: str = Field(
        default="mixtral-8x7b-32768",
        description="Groq model name"
    )

    # Agent Configuration
    max_iterations: int = Field(
        default=10,
        description="Maximum iterations for agent execution"
    )
    temperature: float = Field(
        default=0.1,
        description="Temperature for LLM generation"
    )
    max_tokens: int = Field(
        default=4096,
        description="Maximum tokens for LLM response"
    )

    # Profiling Configuration
    profiling_timeout: int = Field(
        default=30,
        description="Timeout in seconds for profiling operations"
    )
    memory_limit_mb: int = Field(
        default=512,
        description="Memory limit in MB for code execution"
    )

    # Logging Configuration
    log_level: str = Field(
        default="INFO",
        description="Logging level"
    )
    log_file: str = Field(
        default="debug_agent.log",
        description="Log file path"
    )

    def get_llm_config(self, provider: str | None = None) -> dict:
        """Get LLM configuration for specified provider."""
        provider = provider or self.default_llm_provider

        configs = {
            "openai": {
                "api_key": self.openai_api_key,
                "model": self.openai_model,
                "temperature": self.temperature,
                "max_tokens": self.max_tokens,
            },
            "anthropic": {
                "api_key": self.anthropic_api_key,
                "model": self.anthropic_model,
                "temperature": self.temperature,
                "max_tokens": self.max_tokens,
            },
            "google": {
                "api_key": self.google_api_key,
                "model": self.google_model,
                "temperature": self.temperature,
                "max_tokens": self.max_tokens,
            },
            "groq": {
                "api_key": self.groq_api_key,
                "model": self.groq_model,
                "temperature": self.temperature,
                "max_tokens": self.max_tokens,
            }
        }

        return configs.get(provider, configs["openai"])


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()