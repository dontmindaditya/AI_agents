"""
Database Configuration

Settings for database connections and caching.
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


class DatabaseSettings(BaseSettings):
    """Database connection settings."""
    
    SUPABASE_URL: Optional[str] = None
    SUPABASE_KEY: Optional[str] = None
    SUPABASE_SERVICE_KEY: Optional[str] = None
    NEXT_PUBLIC_SUPABASE_URL: Optional[str] = None
    NEXT_PUBLIC_SUPABASE_ANON_KEY: Optional[str] = None
    DATABASE_URL: Optional[str] = None
    
    class Config:
        env_file = _get_env_file()
        case_sensitive = True
        extra = "ignore"


class WebSocketSettings(BaseSettings):
    """WebSocket configuration."""
    
    WS_HEARTBEAT_INTERVAL: int = 30
    WS_MESSAGE_MAX_SIZE: int = 10 * 1024 * 1024
    
    class Config:
        env_file = _get_env_file()
        case_sensitive = True
        extra = "ignore"


class LoggingSettings(BaseSettings):
    """Logging configuration."""
    
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    
    class Config:
        env_file = _get_env_file()
        case_sensitive = True
        extra = "ignore"
