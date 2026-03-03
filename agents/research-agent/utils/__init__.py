"""
Utilities package for research agent
"""

from .helpers import (
    ensure_directories,
    save_report,
    print_header,
    print_success,
    print_error,
    print_info,
    print_markdown,
    validate_env_variables,
    truncate_text,
    get_file_size_mb
)

from .prompts import (
    RESEARCHER_ROLE,
    RESEARCHER_GOAL,
    RESEARCHER_BACKSTORY,
    ANALYZER_ROLE,
    ANALYZER_GOAL,
    ANALYZER_BACKSTORY,
    WRITER_ROLE,
    WRITER_GOAL,
    WRITER_BACKSTORY,
    RESEARCH_TASK_DESCRIPTION,
    ANALYSIS_TASK_DESCRIPTION,
    WRITING_TASK_DESCRIPTION,
    PDF_ANALYSIS_TASK_DESCRIPTION
)

__all__ = [
    'ensure_directories',
    'save_report',
    'print_header',
    'print_success',
    'print_error',
    'print_info',
    'print_markdown',
    'validate_env_variables',
    'truncate_text',
    'get_file_size_mb',
    'RESEARCHER_ROLE',
    'RESEARCHER_GOAL',
    'RESEARCHER_BACKSTORY',
    'ANALYZER_ROLE',
    'ANALYZER_GOAL',
    'ANALYZER_BACKSTORY',
    'WRITER_ROLE',
    'WRITER_GOAL',
    'WRITER_BACKSTORY',
    'RESEARCH_TASK_DESCRIPTION',
    'ANALYSIS_TASK_DESCRIPTION',
    'WRITING_TASK_DESCRIPTION',
    'PDF_ANALYSIS_TASK_DESCRIPTION'
]