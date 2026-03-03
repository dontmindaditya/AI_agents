"""
Helper Utilities
"""
from typing import Any, Dict, List, Optional
import json
import hashlib
from datetime import datetime
import uuid


def generate_task_id() -> str:
    """Generate unique task ID"""
    return f"task_{uuid.uuid4().hex[:12]}"


def generate_session_id() -> str:
    """Generate unique session ID"""
    return f"session_{uuid.uuid4().hex[:16]}"


def hash_string(text: str) -> str:
    """
    Generate SHA256 hash of string
    
    Args:
        text: Input text
        
    Returns:
        Hexadecimal hash string
    """
    return hashlib.sha256(text.encode()).hexdigest()


def serialize_datetime(obj: Any) -> str:
    """
    Serialize datetime objects to ISO format
    
    Args:
        obj: Object to serialize
        
    Returns:
        ISO formatted string
    """
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")


def safe_json_dumps(data: Any, pretty: bool = False) -> str:
    """
    Safely serialize data to JSON
    
    Args:
        data: Data to serialize
        pretty: Whether to format prettily
        
    Returns:
        JSON string
    """
    try:
        if pretty:
            return json.dumps(data, indent=2, default=serialize_datetime)
        return json.dumps(data, default=serialize_datetime)
    except Exception as e:
        return json.dumps({"error": f"Serialization failed: {str(e)}"})


def safe_json_loads(json_str: str) -> Optional[Dict[Any, Any]]:
    """
    Safely parse JSON string
    
    Args:
        json_str: JSON string
        
    Returns:
        Parsed dictionary or None if failed
    """
    try:
        return json.loads(json_str)
    except json.JSONDecodeError:
        return None


def merge_dicts(*dicts: Dict[Any, Any]) -> Dict[Any, Any]:
    """
    Merge multiple dictionaries
    
    Args:
        *dicts: Dictionaries to merge
        
    Returns:
        Merged dictionary
    """
    result = {}
    for d in dicts:
        if d:
            result.update(d)
    return result


def flatten_dict(d: Dict[Any, Any], parent_key: str = '', sep: str = '_') -> Dict[str, Any]:
    """
    Flatten nested dictionary
    
    Args:
        d: Dictionary to flatten
        parent_key: Parent key prefix
        sep: Separator for nested keys
        
    Returns:
        Flattened dictionary
    """
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncate text to specified length
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add when truncated
        
    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def extract_error_message(error: Exception) -> str:
    """
    Extract clean error message from exception
    
    Args:
        error: Exception object
        
    Returns:
        Clean error message
    """
    error_msg = str(error)
    if not error_msg:
        error_msg = error.__class__.__name__
    return error_msg


def format_duration(seconds: float) -> str:
    """
    Format duration in human-readable format
    
    Args:
        seconds: Duration in seconds
        
    Returns:
        Formatted duration string
    """
    if seconds < 1:
        return f"{seconds * 1000:.0f}ms"
    elif seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}m"
    else:
        hours = seconds / 3600
        return f"{hours:.1f}h"


def chunk_list(lst: List[Any], chunk_size: int) -> List[List[Any]]:
    """
    Split list into chunks
    
    Args:
        lst: List to chunk
        chunk_size: Size of each chunk
        
    Returns:
        List of chunks
    """
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]


def get_timestamp() -> str:
    """Get current timestamp in ISO format"""
    return datetime.utcnow().isoformat()


def parse_bool(value: Any) -> bool:
    """
    Parse boolean from various types
    
    Args:
        value: Value to parse
        
    Returns:
        Boolean value
    """
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.lower() in ('true', '1', 'yes', 'on')
    return bool(value)