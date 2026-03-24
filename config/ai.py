"""
AI Configuration

Settings for AI model providers and their configurations.
"""

from typing import Optional
from pydantic_settings import BaseSettings
from pathlib import Path


def _get_env_file() -> str:
    """Get the appropriate .env file path."""
    current_dir = Path(__file__).parent.parent
    parent_dir = current_dir.parent
    
    if (current_dir / ".env").exists():
        return str(current_dir / ".env")
    elif (parent_dir / ".env").exists():
        return str(parent_dir / ".env")
    return ".env"


class AIKeySettings(BaseSettings):
    """AI API key settings."""
    
    ANTHROPIC_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    GROQ_API_KEY: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None
    
    class Config:
        env_file = _get_env_file()
        case_sensitive = True
        extra = "ignore"


class AIModelSettings(BaseSettings):
    """AI model configuration settings."""
    
    CLAUDE_MODEL: str = "claude-sonnet-4-20250514"
    GPT_MODEL: str = "gpt-4o"
    GROQ_MODEL: str = "llama-3.1-70b-versatile"
    GEMINI_MODEL: str = "gemini-1.5-pro"
    
    class Config:
        env_file = _get_env_file()
        case_sensitive = True
        extra = "ignore"


AI_MODELS = {
    "claude": {
        "provider": "anthropic",
        "model": "claude-sonnet-4-20250514",
        "max_tokens": 4096,
        "temperature": 0.7,
        "use_cases": ["planning", "uiux", "analysis"]
    },
    "gpt4": {
        "provider": "openai",
        "model": "gpt-4o",
        "max_tokens": 4096,
        "temperature": 0.7,
        "use_cases": ["frontend", "backend", "generation"]
    },
    "groq": {
        "provider": "groq",
        "model": "llama-3.1-70b-versatile",
        "max_tokens": 2048,
        "temperature": 0.3,
        "use_cases": ["debugging", "validation"]
    },
    "gemini": {
        "provider": "google",
        "model": "gemini-1.5-pro",
        "max_tokens": 4096,
        "temperature": 0.7,
        "use_cases": ["research", "documentation"]
    }
}
