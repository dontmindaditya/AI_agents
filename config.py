"""
Configuration Module - Backward Compatibility

This file re-exports from the modular config package.
For new code, import directly from config package.
"""

from config import (
    settings,
    get_settings,
    Settings,
    AI_MODELS,
    AGENT_CONFIGS,
    PIPELINE_STAGES,
)

__all__ = [
    "settings",
    "get_settings", 
    "Settings",
    "AI_MODELS",
    "AGENT_CONFIGS",
    "PIPELINE_STAGES",
]
