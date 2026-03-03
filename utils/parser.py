"""Code parsing utilities"""

import re
import json
from typing import Dict, Any, Optional


def extract_json_from_text(text: str) -> Optional[Dict[str, Any]]:
    """Extract JSON from text with markdown or other formatting"""
    try:
        # Try direct parse first
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    
    # Try to find JSON in markdown code blocks
    json_pattern = r'```(?:json)?\s*(\{.*?\})\s*```'
    matches = re.findall(json_pattern, text, re.DOTALL)
    
    if matches:
        try:
            return json.loads(matches[0])
        except json.JSONDecodeError:
            pass
    
    # Try to find JSON between braces
    if '{' in text and '}' in text:
        start = text.index('{')
        end = text.rindex('}') + 1
        try:
            return json.loads(text[start:end])
        except json.JSONDecodeError:
            pass
    
    return None


def clean_code_block(code: str) -> str:
    """Remove markdown code block formatting"""
    if "```" in code:
        code = code.split("```")[1]
        if code.startswith(("typescript", "tsx", "jsx", "javascript", "python")):
            code = code.split("\n", 1)[1]
    
    return code.strip()


def extract_imports(code: str) -> list[str]:
    """Extract import statements from code"""
    import_pattern = r'^import .+$'
    return re.findall(import_pattern, code, re.MULTILINE)


def extract_exports(code: str) -> list[str]:
    """Extract export statements from code"""
    export_pattern = r'^export .+$'
    return re.findall(export_pattern, code, re.MULTILINE)