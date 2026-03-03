"""
Validation Tools for Agents
"""
from typing import Any, Dict, Optional
from langchain.tools import BaseTool
import re
import json

from app.utils.logger import setup_logger
from app.utils.validators import (
    validate_json_structure,
    validate_sql_injection,
    sanitize_input
)

logger = setup_logger(__name__)


class JSONValidatorTool(BaseTool):
    """Tool for validating JSON data"""
    
    name: str = "json_validator"
    description: str = """
    Validate JSON data structure and format.
    Input should be a JSON string to validate.
    Returns validation result with success status and any error messages.
    """
    
    def _run(self, json_str: str) -> Dict[str, Any]:
        """Validate JSON string"""
        try:
            # Try to parse JSON
            data = json.loads(json_str)
            
            return {
                "success": True,
                "valid": True,
                "message": "JSON is valid",
                "parsed_data": data
            }
        except json.JSONDecodeError as e:
            return {
                "success": True,
                "valid": False,
                "error": str(e),
                "message": "Invalid JSON format"
            }
        except Exception as e:
            logger.error(f"JSON validation failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _arun(self, json_str: str) -> Dict[str, Any]:
        """Async wrapper for JSON validation"""
        return self._run(json_str)


class EmailValidatorTool(BaseTool):
    """Tool for validating email addresses"""
    
    name: str = "email_validator"
    description: str = """
    Validate email address format.
    Input should be an email address string.
    Returns validation result.
    """
    
    def _run(self, email: str) -> Dict[str, Any]:
        """Validate email address"""
        try:
            # Basic email regex pattern
            pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            
            is_valid = bool(re.match(pattern, email))
            
            return {
                "success": True,
                "valid": is_valid,
                "email": email,
                "message": "Valid email" if is_valid else "Invalid email format"
            }
        except Exception as e:
            logger.error(f"Email validation failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _arun(self, email: str) -> Dict[str, Any]:
        """Async wrapper for email validation"""
        return self._run(email)


class URLValidatorTool(BaseTool):
    """Tool for validating URLs"""
    
    name: str = "url_validator"
    description: str = """
    Validate URL format.
    Input should be a URL string.
    Returns validation result.
    """
    
    def _run(self, url: str) -> Dict[str, Any]:
        """Validate URL"""
        try:
            # URL regex pattern
            pattern = re.compile(
                r'^https?://'  # http:// or https://
                r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain
                r'localhost|'  # localhost
                r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # or IP
                r'(?::\d+)?'  # optional port
                r'(?:/?|[/?]\S+)$', re.IGNORECASE
            )
            
            is_valid = bool(pattern.match(url))
            
            return {
                "success": True,
                "valid": is_valid,
                "url": url,
                "message": "Valid URL" if is_valid else "Invalid URL format"
            }
        except Exception as e:
            logger.error(f"URL validation failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _arun(self, url: str) -> Dict[str, Any]:
        """Async wrapper for URL validation"""
        return self._run(url)


class DataSanitizerTool(BaseTool):
    """Tool for sanitizing input data"""
    
    name: str = "data_sanitizer"
    description: str = """
    Sanitize and clean input data to remove potentially harmful content.
    Input should be a string to sanitize.
    Returns sanitized data.
    """
    
    def _run(self, text: str, max_length: int = 10000) -> Dict[str, Any]:
        """Sanitize input text"""
        try:
            sanitized = sanitize_input(text, max_length)
            
            return {
                "success": True,
                "original_length": len(text),
                "sanitized_length": len(sanitized),
                "sanitized_data": sanitized,
                "was_modified": text != sanitized
            }
        except Exception as e:
            logger.error(f"Data sanitization failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _arun(self, text: str, max_length: int = 10000) -> Dict[str, Any]:
        """Async wrapper for data sanitization"""
        return self._run(text, max_length)


class SQLInjectionDetectorTool(BaseTool):
    """Tool for detecting SQL injection attempts"""
    
    name: str = "sql_injection_detector"
    description: str = """
    Detect potential SQL injection patterns in input.
    Input should be a string to check for SQL injection.
    Returns detection result.
    """
    
    def _run(self, query: str) -> Dict[str, Any]:
        """Detect SQL injection"""
        try:
            is_safe = validate_sql_injection(query)
            
            return {
                "success": True,
                "safe": is_safe,
                "message": "Input appears safe" if is_safe else "Potential SQL injection detected",
                "severity": "low" if is_safe else "high"
            }
        except Exception as e:
            logger.error(f"SQL injection detection failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _arun(self, query: str) -> Dict[str, Any]:
        """Async wrapper for SQL injection detection"""
        return self._run(query)


class DataTypeValidatorTool(BaseTool):
    """Tool for validating data types"""
    
    name: str = "data_type_validator"
    description: str = """
    Validate if data matches expected type.
    Input should be a JSON with 'value' and 'expected_type' (string, number, boolean, array, object).
    Returns validation result.
    """
    
    def _run(self, value: Any, expected_type: str) -> Dict[str, Any]:
        """Validate data type"""
        try:
            type_map = {
                'string': str,
                'number': (int, float),
                'boolean': bool,
                'array': list,
                'object': dict,
                'null': type(None)
            }
            
            expected = type_map.get(expected_type.lower())
            if not expected:
                return {
                    "success": False,
                    "error": f"Unknown expected type: {expected_type}"
                }
            
            is_valid = isinstance(value, expected)
            actual_type = type(value).__name__
            
            return {
                "success": True,
                "valid": is_valid,
                "expected_type": expected_type,
                "actual_type": actual_type,
                "message": f"Type matches" if is_valid else f"Type mismatch: expected {expected_type}, got {actual_type}"
            }
        except Exception as e:
            logger.error(f"Data type validation failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _arun(self, value: Any, expected_type: str) -> Dict[str, Any]:
        """Async wrapper for data type validation"""
        return self._run(value, expected_type)


# Tool instances
json_validator_tool = JSONValidatorTool()
email_validator_tool = EmailValidatorTool()
url_validator_tool = URLValidatorTool()
data_sanitizer_tool = DataSanitizerTool()
sql_injection_detector_tool = SQLInjectionDetectorTool()
data_type_validator_tool = DataTypeValidatorTool()

# Export all validation tools
validation_tools = [
    json_validator_tool,
    email_validator_tool,
    url_validator_tool,
    data_sanitizer_tool,
    sql_injection_detector_tool,
    data_type_validator_tool
]