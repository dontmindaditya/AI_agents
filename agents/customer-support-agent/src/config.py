"""
Configuration management for the Customer Support Agent.
Handles environment variables and API key setup.
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from typing import Optional

class Config:
    """Configuration class for managing environment variables and settings."""
    
    def __init__(self):
        """Initialize configuration by loading environment variables."""
        root_dir = Path(__file__).parent.parent.parent
        load_dotenv(root_dir / ".env")
        self._validate_config()
    
    @property
    def openai_api_key(self) -> str:
        """Get OpenAI API key from environment."""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError(
                "OPENAI_API_KEY not found in environment variables. "
                "Please set it in your .env file."
            )
        return api_key
    
    @property
    def openai_model(self) -> str:
        """Get OpenAI model name from environment or use default."""
        return os.getenv("OPENAI_MODEL", "gpt-4")
    
    @property
    def temperature(self) -> float:
        """Get temperature setting for LLM from environment or use default."""
        return float(os.getenv("TEMPERATURE", "0"))
    
    def _validate_config(self) -> None:
        """Validate that required configuration is present."""
        if not os.getenv("OPENAI_API_KEY"):
            print(
                "Warning: OPENAI_API_KEY not found in environment variables.\n"
                "Please create a .env file with your OpenAI API key.\n"
                "Example: OPENAI_API_KEY=your_api_key_here"
            )
    
    def setup_environment(self) -> None:
        """Set up environment variables for the application."""
        os.environ["OPENAI_API_KEY"] = self.openai_api_key

# Create a global config instance
config = Config()

def get_config() -> Config:
    """Get the global configuration instance."""
    return config