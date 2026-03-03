from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
import os
from pathlib import Path


class Settings(BaseSettings):
    """Application settings loaded from environment variables or .env file"""

    # === API Keys (existing ones) ===
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    google_api_key: Optional[str] = None

    # === Model Configuration ===
    default_llm_provider: str = "openai"
    default_model: str = "gpt-4-turbo-preview"
    temperature: float = 0.7
    max_tokens: int = 2000

    # === Agent Configuration ===
    max_discussion_rounds: int = 5
    discussion_turn_limit: int = 10

    # === Logging ===
    log_level: str = "INFO"
    log_file: str = "edugpt.log"

    # === NEW: Allow extra fields from your large .env file ===
    # This prevents the "extra_forbidden" validation errors
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="allow",  # ← Critical line: accepts GROQ_API_KEY, GEMINI_API_KEY, SUPABASE keys, etc.
    )

    def validate_api_keys(self):
        """Validate that at least one API key is provided"""
        if not any([self.openai_api_key, self.anthropic_api_key, self.google_api_key]):
            raise ValueError("At least one LLM API key must be provided")

    def get_api_key(self, provider: str) -> str:
        """Get API key for specific provider"""
        key_map = {
            "openai": self.openai_api_key,
            "anthropic": self.anthropic_api_key,
            "google": self.google_api_key,
        }
        key = key_map.get(provider.lower())
        if not key:
            raise ValueError(f"API key for provider '{provider}' not found")
        return key


# Global settings instance (instantiated once)
settings = Settings()

# Optional: Run validation on startup (uncomment if you want strict check early)
# settings.validate_api_keys()