"""
Configuration Module

Modular configuration system for AgentHub.
Each config file contains settings for a specific domain.

Usage:
    from config import settings
    
    # Access all settings
    settings.APP_NAME
    settings.ANTHROPIC_API_KEY
    settings.RATE_LIMIT_PIPELINE
"""

from functools import lru_cache
from typing import Optional, List, Union
from pydantic import field_validator
from pydantic_settings import BaseSettings
from pathlib import Path


def _get_env_file() -> str:
    """Get the appropriate .env file path."""
    current_dir = Path(__file__).parent
    parent_dir = current_dir.parent
    
    if (current_dir / ".env").exists():
        return str(current_dir / ".env")
    elif (parent_dir / ".env").exists():
        return str(parent_dir / ".env")
    return ".env"


class Settings(BaseSettings):
    """
    Main settings class combining all configuration domains.
    
    This class provides a unified interface to all settings while
    internally organizing them by domain.
    """
    
    APP_NAME: str = "AgentHub"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "production"
    
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    WORKERS: int = 4
    
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "https://webby.fairquanta.com",
    ]
    
    SUPABASE_URL: Optional[str] = None
    SUPABASE_KEY: Optional[str] = None
    SUPABASE_SERVICE_KEY: Optional[str] = None
    NEXT_PUBLIC_SUPABASE_URL: Optional[str] = None
    NEXT_PUBLIC_SUPABASE_ANON_KEY: Optional[str] = None
    
    ANTHROPIC_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    GROQ_API_KEY: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None
    
    CLAUDE_MODEL: str = "claude-sonnet-4-20250514"
    GPT_MODEL: str = "gpt-4o"
    GROQ_MODEL: str = "llama-3.1-70b-versatile"
    GEMINI_MODEL: str = "gemini-1.5-pro"
    
    MAX_AGENTS: int = 10
    AGENT_TIMEOUT: int = 300
    MAX_RETRIES: int = 3
    
    WS_HEARTBEAT_INTERVAL: int = 30
    WS_MESSAGE_MAX_SIZE: int = 10 * 1024 * 1024
    
    MAX_FILE_SIZE: int = 1024 * 1024
    MAX_FILES_PER_PROJECT: int = 100
    
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_DEFAULT: str = "100/minute"
    RATE_LIMIT_STORAGE_URL: Optional[str] = "memory://"
    RATE_LIMIT_PIPELINE: str = "10/minute"
    RATE_LIMIT_AGENTS: str = "30/minute"
    RATE_LIMIT_WS: str = "60/minute"
    RATE_LIMIT_HEALTH: str = "200/minute"
    
    API_KEY_ENABLED: bool = True
    API_KEYS: Union[List[str], str] = []
    
    @field_validator('API_KEYS', mode='before')
    @classmethod
    def parse_api_keys(cls, v):
        """Parse API_KEYS from string or list."""
        if isinstance(v, str):
            if v.startswith('['):
                import json
                return json.loads(v)
            return [k.strip() for k in v.split(',') if k.strip()]
        return v
    
    class Config:
        env_file = _get_env_file()
        case_sensitive = True
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings()


from .ai import AI_MODELS
from .agents import AGENT_CONFIGS
from .pipeline import PIPELINE_STAGES

__all__ = [
    "settings",
    "get_settings",
    "Settings",
    "AI_MODELS",
    "AGENT_CONFIGS",
    "PIPELINE_STAGES",
]
