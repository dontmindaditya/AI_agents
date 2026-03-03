"""
Configuration settings for UI/UX Agent
"""
from pydantic_settings import BaseSettings
from typing import Literal
from pathlib import Path
import os
from dotenv import load_dotenv

# Load environment variables from multiple sources
# Priority: .env > .env.local > environment variables
load_dotenv(".env.local", override=False)  # Load .env.local first (lower priority)
load_dotenv(override=True)  # Load .env second (higher priority)


class Settings(BaseSettings):
    """Application settings"""
    
    # API Keys
    openai_api_key: str = ""
    anthropic_api_key: str = ""
    
    # LLM Configuration
    default_llm_provider: Literal["openai", "anthropic"] = "openai"
    openai_model: str = "gpt-4-turbo-preview"
    anthropic_model: str = "claude-3-5-sonnet-20241022"
    
    # Agent Configuration
    max_iterations: int = 10
    agent_temperature: float = 0.7
    agent_verbose: bool = True
    
    # Image Processing
    max_image_size: int = 5242880  # 5MB
    supported_image_formats: str = "jpg,jpeg,png,webp"
    
    # Output Configuration
    output_code_format: Literal["react", "html", "vue"] = "react"
    output_directory: Path = Path("./outputs")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
    
    def get_supported_formats(self) -> list[str]:
        """Get list of supported image formats"""
        return self.supported_image_formats.split(",")
    
    def ensure_output_directory(self):
        """Create output directory if it doesn't exist"""
        self.output_directory.mkdir(parents=True, exist_ok=True)


# Global settings instance
settings = Settings()