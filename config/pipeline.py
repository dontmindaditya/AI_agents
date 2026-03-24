"""
Pipeline Configuration

Settings and stage definitions for the code generation pipeline.
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


class PipelineSettings(BaseSettings):
    """Pipeline behavior settings."""
    
    MAX_FILE_SIZE: int = 1024 * 1024
    MAX_FILES_PER_PROJECT: int = 100
    
    class Config:
        env_file = _get_env_file()
        case_sensitive = True
        extra = "ignore"


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
