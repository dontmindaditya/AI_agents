"""
Configuration management for Webby Backend
"""

import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings from environment variables"""
    
    # Application
    APP_NAME: str = "Webby Backend"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "production"
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    WORKERS: int = 4
    
    # CORS
    CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "https://webby.fairquanta.com",
    ]
    
    # Supabase
    SUPABASE_URL: Optional[str] = None
    SUPABASE_KEY: Optional[str] = None
    SUPABASE_SERVICE_KEY: Optional[str] = None
    NEXT_PUBLIC_SUPABASE_URL: Optional[str] = None
    NEXT_PUBLIC_SUPABASE_ANON_KEY: Optional[str] = None
    
    # AI Model API Keys
    ANTHROPIC_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    GROQ_API_KEY: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None
    
    # AI Model Settings
    CLAUDE_MODEL: str = "claude-sonnet-4-20250514"
    GPT_MODEL: str = "gpt-4o"
    GROQ_MODEL: str = "llama-3.1-70b-versatile"
    GEMINI_MODEL: str = "gemini-1.5-pro"
    
    # Agent Settings
    MAX_AGENTS: int = 10
    AGENT_TIMEOUT: int = 300
    MAX_RETRIES: int = 3
    
    # WebSocket Settings
    WS_HEARTBEAT_INTERVAL: int = 30
    WS_MESSAGE_MAX_SIZE: int = 10 * 1024 * 1024
    
    # Code Generation Settings
    MAX_FILE_SIZE: int = 1024 * 1024
    MAX_FILES_PER_PROJECT: int = 100
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    
    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_DEFAULT: str = "100/minute"
    RATE_LIMIT_STORAGE_URL: Optional[str] = "memory://"
    
    # Rate limits per endpoint
    RATE_LIMIT_PIPELINE: str = "10/minute"
    RATE_LIMIT_AGENTS: str = "30/minute"
    RATE_LIMIT_WS: str = "60/minute"
    RATE_LIMIT_HEALTH: str = "200/minute"
    
    # API Key Authentication
    API_KEY_ENABLED: bool = True
    API_KEYS: list[str] = []  # List of valid API keys
    
    class Config:
        # Check both backend/.env and parent directory .env
        current_dir = Path(__file__).parent
        parent_dir = current_dir.parent
        
        # Try backend/.env first, then ../.env
        if (current_dir / ".env").exists():
            env_file = str(current_dir / ".env")
        elif (parent_dir / ".env").exists():
            env_file = str(parent_dir / ".env")
        else:
            env_file = ".env"
        
        case_sensitive = True
        extra = "ignore"  # CRITICAL: Ignore frontend variables


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


settings = get_settings()


# AI Model Configuration
AI_MODELS = {
    "claude": {
        "provider": "anthropic",
        "model": settings.CLAUDE_MODEL,
        "max_tokens": 4096,
        "temperature": 0.7,
        "use_cases": ["planning", "uiux", "analysis"]
    },
    "gpt4": {
        "provider": "openai",
        "model": settings.GPT_MODEL,
        "max_tokens": 4096,
        "temperature": 0.7,
        "use_cases": ["frontend", "backend", "generation"]
    },
    "groq": {
        "provider": "groq",
        "model": settings.GROQ_MODEL,
        "max_tokens": 2048,
        "temperature": 0.3,
        "use_cases": ["debugging", "validation"]
    },
    "gemini": {
        "provider": "google",
        "model": settings.GEMINI_MODEL,
        "max_tokens": 4096,
        "temperature": 0.7,
        "use_cases": ["research", "documentation"]
    }
}


# Agent Configuration
AGENT_CONFIGS = {
    "planner": {
        "role": "Project Planning Specialist",
        "goal": "Create comprehensive project structure and task allocation",
        "model": "claude",
        "max_iterations": 3,
        "allow_delegation": True,
    },
    "research": {
        "role": "Technical Research Specialist",
        "goal": "Conduct in-depth technical research",
        "model": "gemini",
        "max_iterations": 5,
        "allow_delegation": False,
    },
    "uiux": {
        "role": "UI/UX Design Specialist",
        "goal": "Create beautiful, accessible user interfaces",
        "model": "claude",
        "max_iterations": 4,
        "allow_delegation": False,
    },
    "frontend": {
        "role": "Frontend Development Specialist",
        "goal": "Generate production-ready React/Next.js components",
        "model": "gpt4",
        "max_iterations": 5,
        "allow_delegation": False,
    },
    "backend": {
        "role": "Backend Development Specialist",
        "goal": "Create robust API routes and database schemas",
        "model": "gpt4",
        "max_iterations": 5,
        "allow_delegation": False,
    },
    "debugger": {
        "role": "Code Quality & Debugging Specialist",
        "goal": "Identify and fix errors",
        "model": "groq",
        "max_iterations": 3,
        "allow_delegation": False,
    }
}


# Pipeline Stage Configuration
PIPELINE_STAGES = {
    "planning": {
        "order": 1,
        "name": "Planning & Architecture",
        "agents": ["planner"],
        "required": True,
        "estimated_duration": 120,
    },
    "research": {
        "order": 2,
        "name": "Technical Research",
        "agents": ["research"],
        "required": False,
        "estimated_duration": 180,
    },
    "analysis": {
        "order": 3,
        "name": "Requirements Analysis",
        "agents": ["planner"],
        "required": True,
        "estimated_duration": 90,
    },
    "design": {
        "order": 4,
        "name": "UI/UX Design",
        "agents": ["uiux"],
        "required": True,
        "estimated_duration": 150,
    },
    "generation": {
        "order": 5,
        "name": "Code Generation",
        "agents": ["frontend", "backend"],
        "required": True,
        "estimated_duration": 300,
    },
    "integration": {
        "order": 6,
        "name": "Agent Integration",
        "agents": [],
        "required": True,
        "estimated_duration": 30,
    },
    "testing": {
        "order": 7,
        "name": "Testing & Debugging",
        "agents": ["debugger"],
        "required": True,
        "estimated_duration": 120,
    }
}