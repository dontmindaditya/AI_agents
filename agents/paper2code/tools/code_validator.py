"""
Code validation and syntax checking tools
"""
import ast
import sys
import subprocess
from typing import Dict, List, Tuple, Optional
from pathlib import Path
import tempfile
from utils.logger import logger


class CodeValidator:
    """Validate and check code syntax and quality"""
    
    def __init__(self, language: str = "python"):
        """
        Initialize code validator
        
        Args:
            language: Programming language (python, javascript, etc.)
        """
        self.language = language.lower()
        self.errors = []
        self.warnings = []
        
    def validate_python(self, code: str) -> Dict:
        """
        Validate Python code
        
        Args:
            code: Python code string
            
        Returns:
            Validation result dictionary
        """
        result = {
            "valid": False,
            "errors": [],
            "warnings": [],
            "syntax_valid": False,
            "ast_tree": None
        }
        
        # Check syntax using ast
        try:
            tree = ast.parse(code)
            result["syntax_valid"] = True
            result["ast_tree"] = tree
            logger.info("✓ Python syntax is valid")
        except SyntaxError as e:
            result["errors"].append({
                "type": "SyntaxError",
                "message": str(e),
                "line": e.lineno,
                "offset": e.offset
            })
            logger.error(f"✗ Syntax error at line {e.lineno}: {e.msg}")
            return result
        
        # Check for common issues
        warnings = self._check_python_issues(code, tree)
        result["warnings"].extend(warnings)
        
        # Run pylint if available
        pylint_result = self._run_pylint(code)
        if pylint_result:
            result["warnings"].extend(pylint_result)
        
        result["valid"] = result["syntax_valid"] and len(result["errors"]) == 0
        
        return result
    
    def _check_python_issues(self, code: str, tree: ast.AST) -> List[Dict]:
        """Check for common Python code issues"""
        warnings = []
        
        # Check for undefined variables (basic check)
        defined_vars = set()
        used_vars = set()
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Name):
                if isinstance(node.ctx, ast.Store):
                    defined_vars.add(node.id)
                elif isinstance(node.ctx, ast.Load):
                    used_vars.add(node.id)
        
        # Check for unused imports
        imported_names = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    name = alias.asname if alias.asname else alias.name
                    imported_names.add(name)
            elif isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    name = alias.asname if alias.asname else alias.name
                    imported_names.add(name)
        
        unused_imports = imported_names - used_vars
        if unused_imports:
            warnings.append({
                "type": "UnusedImport",
                "message": f"Unused imports: {', '.join(unused_imports)}",
                "severity": "low"
            })
        
        # Check for too complex functions
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                complexity = self._calculate_complexity(node)
                if complexity > 10:
                    warnings.append({
                        "type": "Complexity",
                        "message": f"Function '{node.name}' has high complexity: {complexity}",
                        "severity": "medium",
                        "line": node.lineno
                    })
        
        return warnings
    
    def _calculate_complexity(self, node: ast.FunctionDef) -> int:
        """Calculate cyclomatic complexity"""
        complexity = 1
        
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
        
        return complexity
    
    def _run_pylint(self, code: str) -> Optional[List[Dict]]:
        """Run pylint on code"""
        try:
            # Create temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(code)
                temp_path = f.name
            
            # Run pylint
            result = subprocess.run(
                ['pylint', temp_path, '--output-format=json'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            # Clean up
            Path(temp_path).unlink()
            
            if result.returncode != 0:
                import json
                try:
                    pylint_output = json.loads(result.stdout)
                    return [{
                        "type": item.get("type", "unknown"),
                        "message": item.get("message", ""),
                        "line": item.get("line", 0),
                        "severity": "medium"
                    } for item in pylint_output]
                except:
                    pass
        
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        
        return None
    
    def validate_javascript(self, code: str) -> Dict:
        """
        Validate JavaScript code (basic validation)
        
        Args:
            code: JavaScript code string
            
        Returns:
            Validation result dictionary
        """
        result = {
            "valid": False,
            "errors": [],
            "warnings": [],
            "syntax_valid": False
        }
        
        # Basic syntax checks
        # Check for balanced braces
        if code.count('{') != code.count('}'):
            result["errors"].append({
                "type": "SyntaxError",
                "message": "Unbalanced braces"
            })
        
        # Check for balanced parentheses
        if code.count('(') != code.count(')'):
            result["errors"].append({
                "type": "SyntaxError",
                "message": "Unbalanced parentheses"
            })
        
        # Check for balanced brackets
        if code.count('[') != code.count(']'):
            result["errors"].append({
                "type": "SyntaxError",
                "message": "Unbalanced brackets"
            })
        
        result["syntax_valid"] = len(result["errors"]) == 0
        result["valid"] = result["syntax_valid"]
        
        return result
    
    def validate(self, code: str, language: Optional[str] = None) -> Dict:
        """
        Validate code based on language
        
        Args:
            code: Code string
            language: Programming language (optional, uses instance language if not provided)
            
        Returns:
            Validation result dictionary
        """
        lang = (language or self.language).lower()
        
        if lang == "python":
            return self.validate_python(code)
        elif lang in ["javascript", "typescript", "js", "ts"]:
            return self.validate_javascript(code)
        else:
            return {
                "valid": True,
                "errors": [],
                "warnings": [{
                    "type": "UnsupportedLanguage",
                    "message": f"Validation not implemented for {lang}",
                    "severity": "low"
                }],
                "syntax_valid": True
            }
    
    def check_imports(self, code: str, language: str = "python") -> List[str]:
        """
        Extract required imports/dependencies from code
        
        Args:
            code: Code string
            language: Programming language
            
        Returns:
            List of required imports
        """
        imports = []
        
        if language == "python":
            try:
                tree = ast.parse(code)
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            imports.append(alias.name.split('.')[0])
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            imports.append(node.module.split('.')[0])
            except:
                pass
        
        elif language in ["javascript", "typescript"]:
            # Extract from require() and import statements
            import re
            import_patterns = [
                r'require\([\'"]([^\'"]+)[\'"]\)',
                r'import\s+.*\s+from\s+[\'"]([^\'"]+)[\'"]',
            ]
            for pattern in import_patterns:
                matches = re.findall(pattern, code)
                imports.extend(matches)
        
        return list(set(imports))
    
    def estimate_quality_score(self, code: str, language: str = "python") -> float:
        """
        Estimate code quality score (0-100)
        
        Args:
            code: Code string
            language: Programming language
            
        Returns:
            Quality score
        """
        score = 100.0
        
        validation = self.validate(code, language)
        
        # Deduct for errors
        score -= len(validation.get("errors", [])) * 20
        
        # Deduct for warnings
        score -= len(validation.get("warnings", [])) * 5
        
        # Check code length (too short or too long)
        lines = code.split('\n')
        if len(lines) < 5:
            score -= 10
        elif len(lines) > 500:
            score -= 5
        
        # Check for documentation
        if language == "python":
            if '"""' not in code and "'''" not in code:
                score -= 10
        
        # Check for comments
        comment_ratio = self._calculate_comment_ratio(code, language)
        if comment_ratio < 0.05:  # Less than 5% comments
            score -= 10
        
        return max(0.0, min(100.0, score))
    
    def _calculate_comment_ratio(self, code: str, language: str) -> float:
        """Calculate ratio of comment lines to total lines"""
        lines = code.split('\n')
        comment_lines = 0
        
        if language == "python":
            for line in lines:
                stripped = line.strip()
                if stripped.startswith('#') or '"""' in stripped or "'''" in stripped:
                    comment_lines += 1
        
        elif language in ["javascript", "typescript"]:
            for line in lines:
                stripped = line.strip()
                if stripped.startswith('//') or stripped.startswith('/*'):
                    comment_lines += 1
        
        return comment_lines / max(len(lines), 1)


def validate_code(code: str, language: str = "python") -> Dict:
    """
    Convenience function to validate code
    
    Args:
        code: Code string
        language: Programming language
        
    Returns:
        Validation result
    """
    validator = CodeValidator(language)
    return validator.validate(code)