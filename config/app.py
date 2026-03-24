"""
Application Configuration

Settings for application-level configuration including name, version, server, and CORS.
"""

import os
from pathlib import Path
from typing import Optional, List
from pydantic_settings import BaseSettings


class AppSettings(BaseSettings):
    """Application-level settings."""
    
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
    
    class Config:
        env_file = _get_env_file()
        case_sensitive = True
        extra = "ignore"


class ServerSettings(BaseSettings):
    """Server-specific settings."""
    
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    WORKERS: int = 4
    
    class Config:
        env_file = _get_env_file()
        case_sensitive = True
        extra = "ignore"


class CorsSettings(BaseSettings):
    """CORS settings."""
    
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "https://webby.fairquanta.com",
    ]
    
    class Config:
        env_file = _get_env_file()
        case_sensitive = True
        extra = "ignore"


def _get_env_file() -> str:
    """Get the appropriate .env file path."""
    current_dir = Path(__file__).parent.parent
    parent_dir = current_dir.parent
    
    if (current_dir / ".env").exists():
        return str(current_dir / ".env")
    elif (parent_dir / ".env").exists():
        return str(parent_dir / ".env")
    return ".env"
