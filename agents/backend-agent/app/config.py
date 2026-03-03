"""
Configuration and Settings Management
"""
from pydantic_settings import BaseSettings
from typing import List, Optional
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings"""
    
    # API Keys - At least one LLM provider required
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    GROQ_API_KEY: Optional[str] = None
    GOOGLE_API_KEY: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None  # Alias for Google API Key
    
    # Supabase Configuration - Optional for basic usage
    SUPABASE_URL: Optional[str] = None
    SUPABASE_KEY: Optional[str] = None
    SUPABASE_SERVICE_KEY: Optional[str] = None
    NEXT_PUBLIC_SUPABASE_URL: Optional[str] = None  # Alternative naming
    NEXT_PUBLIC_SUPABASE_ANON_KEY: Optional[str] = None  # Alternative naming
    SUPABASE_SERVICE_ROLE_KEY: Optional[str] = None  # Alternative naming
    
    # Application Settings
    APP_NAME: str = "Backend Agent System"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"
    
    # Server Configuration
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    RELOAD: bool = True
    
    # LLM Configuration
    DEFAULT_LLM_PROVIDER: str = "openai"
    DEFAULT_MODEL: str = "gpt-4-turbo-preview"
    TEMPERATURE: float = 0.7
    MAX_TOKENS: int = 2000
    
    # Agent Configuration
    MAX_ITERATIONS: int = 10
    AGENT_TIMEOUT: int = 300
    
    # Memory Configuration
    ENABLE_MEMORY: bool = True
    MEMORY_TYPE: str = "conversation_buffer"
    MAX_MEMORY_SIZE: int = 10
    
    # CORS Configuration
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # Ignore extra fields in .env file
    
    def validate_llm_providers(self) -> bool:
        """Check if at least one LLM provider is configured"""
        # Use GEMINI_API_KEY as fallback for GOOGLE_API_KEY
        if self.GEMINI_API_KEY and not self.GOOGLE_API_KEY:
            self.GOOGLE_API_KEY = self.GEMINI_API_KEY
        
        return any([
            self.OPENAI_API_KEY,
            self.ANTHROPIC_API_KEY,
            self.GROQ_API_KEY,
            self.GOOGLE_API_KEY,
            self.GEMINI_API_KEY
        ])
    
    def validate_database(self) -> bool:
        """Check if database is configured"""
        # Use alternative naming if primary not set
        if self.NEXT_PUBLIC_SUPABASE_URL and not self.SUPABASE_URL:
            self.SUPABASE_URL = self.NEXT_PUBLIC_SUPABASE_URL
        
        if self.NEXT_PUBLIC_SUPABASE_ANON_KEY and not self.SUPABASE_KEY:
            self.SUPABASE_KEY = self.NEXT_PUBLIC_SUPABASE_ANON_KEY
        
        if self.SUPABASE_SERVICE_ROLE_KEY and not self.SUPABASE_SERVICE_KEY:
            self.SUPABASE_SERVICE_KEY = self.SUPABASE_SERVICE_ROLE_KEY
        
        return bool(self.SUPABASE_URL and self.SUPABASE_KEY)


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


# Global settings instance
settings = get_settings()