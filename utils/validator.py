"""Input validation utilities"""

import re
from typing import Optional


def validate_project_name(name: str) -> tuple[bool, Optional[str]]:
    """Validate project name"""
    if not name or len(name) < 3:
        return False, "Project name must be at least 3 characters"
    
    if len(name) > 100:
        return False, "Project name must be less than 100 characters"
    
    if not re.match(r'^[a-zA-Z0-9\s\-_]+$', name):
        return False, "Project name can only contain letters, numbers, spaces, hyphens and underscores"
    
    return True, None


def validate_project_type(project_type: str) -> tuple[bool, Optional[str]]:
    """Validate project type"""
    valid_types = ["website", "webapp", "dashboard", "saas", "api", "ecommerce", "blog", "portfolio"]
    
    if project_type not in valid_types:
        return False, f"Invalid project type. Must be one of: {', '.join(valid_types)}"
    
    return True, None


def validate_framework(framework: str) -> tuple[bool, Optional[str]]:
    """Validate framework"""
    valid_frameworks = ["nextjs", "react", "vue", "angular", "svelte"]
    
    if framework not in valid_frameworks:
        return False, f"Invalid framework. Must be one of: {', '.join(valid_frameworks)}"
    
    return True, None


def validate_file_path(path: str) -> tuple[bool, Optional[str]]:
    """Validate file path"""
    # Check for path traversal
    if ".." in path:
        return False, "Path cannot contain '..'"
    
    # Check for absolute paths
    if path.startswith("/"):
        return False, "Path cannot be absolute"
    
    # Check length
    if len(path) > 500:
        return False, "Path too long"
    
    return True, None


def validate_code_length(code: str, max_length: int = 50000) -> tuple[bool, Optional[str]]:
    """Validate code length"""
    if len(code) > max_length:
        return False, f"Code exceeds maximum length of {max_length} characters"
    
    return True, None