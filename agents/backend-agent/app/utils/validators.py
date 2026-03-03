"""
Input Validation Utilities
"""
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, validator, Field
import re


class TaskInput(BaseModel):
    """Task input validation"""
    task: str = Field(..., min_length=1, max_length=5000)
    agent_type: Optional[str] = Field(None, pattern="^(api|database|validation|orchestrator)$")
    context: Dict[str, Any] = Field(default_factory=dict)
    
    @validator('task')
    def validate_task(cls, v):
        if not v.strip():
            raise ValueError("Task cannot be empty")
        return v.strip()


class WorkflowInput(BaseModel):
    """Workflow input validation"""
    workflow_type: str = Field(..., pattern="^(data_processing|api_workflow|custom)$")
    input_data: Dict[str, Any] = Field(default_factory=dict)
    config: Dict[str, Any] = Field(default_factory=dict)


class DatabaseQuery(BaseModel):
    """Database query validation"""
    table: str = Field(..., min_length=1, max_length=100)
    operation: str = Field(..., pattern="^(select|insert|update|delete)$")
    filters: Optional[Dict[str, Any]] = None
    data: Optional[Dict[str, Any]] = None
    
    @validator('table')
    def validate_table_name(cls, v):
        # Only allow alphanumeric and underscores
        if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', v):
            raise ValueError("Invalid table name")
        return v


class APIRequest(BaseModel):
    """API request validation"""
    method: str = Field(..., pattern="^(GET|POST|PUT|PATCH|DELETE)$")
    url: str = Field(..., min_length=1)
    headers: Optional[Dict[str, str]] = None
    params: Optional[Dict[str, Any]] = None
    body: Optional[Dict[str, Any]] = None
    
    @validator('url')
    def validate_url(cls, v):
        url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain
            r'localhost|'  # localhost
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # or IP
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE
        )
        if not url_pattern.match(v):
            raise ValueError("Invalid URL format")
        return v


def validate_json_structure(data: Any, schema: Dict[str, type]) -> bool:
    """
    Validate JSON data against a simple schema
    
    Args:
        data: Data to validate
        schema: Schema definition {key: expected_type}
        
    Returns:
        True if valid, False otherwise
    """
    if not isinstance(data, dict):
        return False
    
    for key, expected_type in schema.items():
        if key not in data:
            return False
        if not isinstance(data[key], expected_type):
            return False
    
    return True


def sanitize_input(text: str, max_length: int = 10000) -> str:
    """
    Sanitize user input
    
    Args:
        text: Input text
        max_length: Maximum allowed length
        
    Returns:
        Sanitized text
    """
    # Remove null bytes
    text = text.replace('\x00', '')
    
    # Trim to max length
    text = text[:max_length]
    
    # Strip leading/trailing whitespace
    text = text.strip()
    
    return text


def validate_sql_injection(query: str) -> bool:
    """
    Basic SQL injection detection
    
    Args:
        query: Query string to check
        
    Returns:
        True if safe, False if potential injection detected
    """
    dangerous_patterns = [
        r'(\bUNION\b.*\bSELECT\b)',
        r'(\bDROP\b.*\bTABLE\b)',
        r'(\bEXEC\b|\bEXECUTE\b)',
        r'(;.*--)',
        r'(\bOR\b.*=.*)',
        r'(\bAND\b.*=.*)',
    ]
    
    query_upper = query.upper()
    
    for pattern in dangerous_patterns:
        if re.search(pattern, query_upper, re.IGNORECASE):
            return False
    
    return True