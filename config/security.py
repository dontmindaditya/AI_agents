"""
Security Configuration

Settings for API keys, authentication, and rate limiting.
"""

from typing import Optional, Union, List
from pydantic import field_validator
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


class RateLimitSettings(BaseSettings):
    """Rate limiting configuration."""
    
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_DEFAULT: str = "100/minute"
    RATE_LIMIT_STORAGE_URL: Optional[str] = "memory://"
    RATE_LIMIT_PIPELINE: str = "10/minute"
    RATE_LIMIT_AGENTS: str = "30/minute"
    RATE_LIMIT_WS: str = "60/minute"
    RATE_LIMIT_HEALTH: str = "200/minute"
    
    class Config:
        env_file = _get_env_file()
        case_sensitive = True
        extra = "ignore"


class APIKeySettings(BaseSettings):
    """API key authentication settings."""
    
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


class SecuritySettings(BaseSettings):
    """Combined security settings."""
    
    API_KEY_ENABLED: bool = True
    API_KEYS: Union[List[str], str] = []
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_DEFAULT: str = "100/minute"
    RATE_LIMIT_STORAGE_URL: Optional[str] = "memory://"
    RATE_LIMIT_PIPELINE: str = "10/minute"
    RATE_LIMIT_AGENTS: str = "30/minute"
    RATE_LIMIT_WS: str = "60/minute"
    RATE_LIMIT_HEALTH: str = "200/minute"
    
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
