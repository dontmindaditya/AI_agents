import json

def get_optimizer_prompt(code: any, framework: str) -> str:
    """Get the prompt for code optimization"""
    
    # Ensure code is a string for the prompt
    if isinstance(code, (dict, list)):
        code_str = json.dumps(code, indent=2)
    else:
        code_str = str(code)

    return f"""You are a Frontend Performance Expert specializing in {framework}.

Current Code:
{code_str}
Perform a comprehensive optimization analysis and improve the code:

1. **Performance Optimization**
   - Identify and fix performance bottlenecks
   - Implement lazy loading where appropriate
   - Optimize re-renders/reactivity
   - Add memoization where beneficial

2. **Code Quality**
   - Remove code duplication
   - Improve naming conventions
   - Follow framework best practices

Format your response as JSON:
{{
    "optimized_code": "complete optimized code string",
    "optimization_notes": "detailed notes on optimizations",
    "is_valid": true,
    "validation_errors": [],
    "recommendations": "additional recommendations"
}}
"""

def get_validation_prompt(code: any, framework: str) -> str:
    code_str = json.dumps(code, indent=2) if isinstance(code, (dict, list)) else str(code)
    return f"""Validate the following {framework} code:

{code_str}

Check for syntax and logic errors. Return a report."""

def get_security_check_prompt(code: any) -> str:
    code_str = json.dumps(code, indent=2) if isinstance(code, (dict, list)) else str(code)
    return f"""Perform a security audit on this frontend code:

{code_str}

Check for XSS and sensitive data exposure."""