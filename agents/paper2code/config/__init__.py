"""Configuration package for Paper2Code Agent System"""
from .settings import (
    settings,
    Settings,
    PAPER_ANALYZER_PROMPT,
    ALGORITHM_DESIGNER_PROMPT,
    CODE_GENERATOR_PROMPT,
    CODE_REVIEWER_PROMPT,
    TOOL_DESCRIPTIONS
)

__all__ = [
    'settings',
    'Settings',
    'PAPER_ANALYZER_PROMPT',
    'ALGORITHM_DESIGNER_PROMPT',
    'CODE_GENERATOR_PROMPT',
    'CODE_REVIEWER_PROMPT',
    'TOOL_DESCRIPTIONS'
]