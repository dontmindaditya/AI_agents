"""
Agent Configuration

Settings and configurations for AI agents.
"""

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


class AgentSettings(BaseSettings):
    """Agent behavior settings."""
    
    MAX_AGENTS: int = 10
    AGENT_TIMEOUT: int = 300
    MAX_RETRIES: int = 3
    
    class Config:
        env_file = _get_env_file()
        case_sensitive = True
        extra = "ignore"


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
