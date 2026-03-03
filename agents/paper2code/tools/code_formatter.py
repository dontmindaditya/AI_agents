"""
Code formatting tools
"""
import subprocess
import tempfile
from pathlib import Path
from typing import Optional
from utils.logger import logger


class CodeFormatter:
    """Format code according to language standards"""
    
    def __init__(self, language: str = "python"):
        """
        Initialize code formatter
        
        Args:
            language: Programming language
        """
        self.language = language.lower()
    
    def format_python(self, code: str, line_length: int = 88) -> str:
        """
        Format Python code using Black
        
        Args:
            code: Python code string
            line_length: Maximum line length
            
        Returns:
            Formatted code string
        """
        try:
            import black
            
            mode = black.Mode(
                line_length=line_length,
                string_normalization=True,
                is_pyi=False,
            )
            
            formatted = black.format_str(code, mode=mode)
            logger.info("✓ Code formatted with Black")
            return formatted
        
        except ImportError:
            logger.warning("Black not installed, using autopep8")
            return self._format_with_autopep8(code)
        
        except Exception as e:
            logger.error(f"Error formatting with Black: {str(e)}")
            return code
    
    def _format_with_autopep8(self, code: str) -> str:
        """Format Python code using autopep8"""
        try:
            import autopep8
            
            formatted = autopep8.fix_code(
                code,
                options={'aggressive': 1}
            )
            logger.info("✓ Code formatted with autopep8")
            return formatted
        
        except ImportError:
            logger.warning("autopep8 not installed, returning original code")
            return code
        
        except Exception as e:
            logger.error(f"Error formatting with autopep8: {str(e)}")
            return code
    
    def format_javascript(self, code: str) -> str:
        """
        Format JavaScript code using Prettier (if available)
        
        Args:
            code: JavaScript code string
            
        Returns:
            Formatted code string
        """
        try:
            # Create temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as f:
                f.write(code)
                temp_path = f.name
            
            # Run prettier
            result = subprocess.run(
                ['prettier', '--write', temp_path],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            # Read formatted code
            formatted_code = Path(temp_path).read_text()
            
            # Clean up
            Path(temp_path).unlink()
            
            logger.info("✓ Code formatted with Prettier")
            return formatted_code
        
        except (subprocess.TimeoutExpired, FileNotFoundError):
            logger.warning("Prettier not available, returning original code")
            return code
        
        except Exception as e:
            logger.error(f"Error formatting JavaScript: {str(e)}")
            return code
    
    def format(self, code: str, language: Optional[str] = None) -> str:
        """
        Format code based on language
        
        Args:
            code: Code string
            language: Programming language (optional)
            
        Returns:
            Formatted code string
        """
        lang = (language or self.language).lower()
        
        if lang == "python":
            return self.format_python(code)
        elif lang in ["javascript", "typescript", "js", "ts"]:
            return self.format_javascript(code)
        else:
            logger.info(f"No formatter available for {lang}")
            return code
    
    def add_docstrings(self, code: str, language: str = "python") -> str:
        """
        Add basic docstrings to functions/classes without them
        
        Args:
            code: Code string
            language: Programming language
            
        Returns:
            Code with added docstrings
        """
        if language != "python":
            return code
        
        import ast
        import re
        
        try:
            tree = ast.parse(code)
            lines = code.split('\n')
            
            # Find functions/classes without docstrings
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                    # Check if has docstring
                    has_docstring = (
                        node.body and
                        isinstance(node.body[0], ast.Expr) and
                        isinstance(node.body[0].value, ast.Constant)
                    )
                    
                    if not has_docstring:
                        # Add placeholder docstring
                        indent = self._get_indent(lines[node.lineno - 1])
                        docstring = f'{indent}    """TODO: Add docstring"""\n'
                        
                        # Insert after function/class definition
                        lines.insert(node.lineno, docstring)
            
            return '\n'.join(lines)
        
        except Exception as e:
            logger.error(f"Error adding docstrings: {str(e)}")
            return code
    
    def _get_indent(self, line: str) -> str:
        """Get indentation from line"""
        return line[:len(line) - len(line.lstrip())]
    
    def add_type_hints(self, code: str) -> str:
        """
        Add basic type hints to Python functions (placeholder)
        
        Args:
            code: Python code string
            
        Returns:
            Code with type hints
        """
        # This is a simplified version
        # In production, you'd use tools like MonkeyType or Pyre
        logger.info("Type hint addition is a placeholder - manual review recommended")
        return code
    
    def organize_imports(self, code: str, language: str = "python") -> str:
        """
        Organize and sort imports
        
        Args:
            code: Code string
            language: Programming language
            
        Returns:
            Code with organized imports
        """
        if language == "python":
            try:
                import isort
                
                sorted_code = isort.code(code)
                logger.info("✓ Imports organized with isort")
                return sorted_code
            
            except ImportError:
                logger.warning("isort not installed")
                return code
            
            except Exception as e:
                logger.error(f"Error organizing imports: {str(e)}")
                return code
        
        return code


def format_code(code: str, language: str = "python") -> str:
    """
    Convenience function to format code
    
    Args:
        code: Code string
        language: Programming language
        
    Returns:
        Formatted code
    """
    formatter = CodeFormatter(language)
    return formatter.format(code, language)