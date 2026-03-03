"""Safe code execution sandbox."""

import ast
import sys
import io
import signal
from contextlib import contextmanager
from typing import Dict, Any, Optional
import time

from config.settings import get_settings
from utils.logger import get_logger

logger = get_logger(__name__)


class TimeoutException(Exception):
    """Exception raised when execution times out."""
    pass


def timeout_handler(signum, frame):
    """Handle timeout signal."""
    raise TimeoutException("Code execution timed out")


class CodeExecutor:
    """Safe code execution with timeout and resource limits."""
    
    # Dangerous operations that should be blocked
    DANGEROUS_OPERATIONS = {
        'eval', 'exec', 'compile', '__import__',
        'open', 'file', 'input', 'raw_input',
        'os', 'sys', 'subprocess', 'importlib',
        'socket', 'urllib', 'requests', 'httplib'
    }
    
    def __init__(self):
        """Initialize code executor."""
        self.settings = get_settings()
        self.timeout = self.settings.profiling_timeout
    
    def is_safe(self, code: str) -> bool:
        """
        Check if code is safe to execute.
        
        Args:
            code: Python code to check
            
        Returns:
            True if code appears safe, False otherwise
        """
        try:
            tree = ast.parse(code)
            
            for node in ast.walk(tree):
                # Check for dangerous function calls
                if isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Name):
                        if node.func.id in self.DANGEROUS_OPERATIONS:
                            logger.warning(f"Dangerous operation detected: {node.func.id}")
                            return False
                
                # Check for import statements
                if isinstance(node, (ast.Import, ast.ImportFrom)):
                    module_name = None
                    if isinstance(node, ast.Import):
                        module_name = node.names[0].name
                    elif isinstance(node, ast.ImportFrom):
                        module_name = node.module
                    
                    if module_name and any(dangerous in module_name for dangerous in self.DANGEROUS_OPERATIONS):
                        logger.warning(f"Dangerous import detected: {module_name}")
                        return False
            
            return True
            
        except SyntaxError:
            logger.error("Syntax error in code")
            return False
        except Exception as e:
            logger.error(f"Safety check failed: {str(e)}")
            return False
    
    def execute(self, code: str, globals_dict: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Execute code safely.
        
        Args:
            code: Python code to execute
            globals_dict: Global variables (optional)
            
        Returns:
            Execution results
        """
        if not self.is_safe(code):
            return {
                "success": False,
                "error": "Code contains unsafe operations",
                "output": "",
                "execution_time": 0
            }
        
        return self.execute_with_timeout(code, globals_dict, self.timeout)
    
    def execute_with_timeout(
        self,
        code: str,
        globals_dict: Optional[Dict] = None,
        timeout: int = 30
    ) -> Dict[str, Any]:
        """
        Execute code with timeout.
        
        Args:
            code: Python code to execute
            globals_dict: Global variables
            timeout: Timeout in seconds
            
        Returns:
            Execution results
        """
        if globals_dict is None:
            globals_dict = {}
        
        # Capture stdout
        old_stdout = sys.stdout
        sys.stdout = captured_output = io.StringIO()
        
        start_time = time.time()
        success = False
        error = None
        
        try:
            # Set up timeout (Unix only)
            if hasattr(signal, 'SIGALRM'):
                signal.signal(signal.SIGALRM, timeout_handler)
                signal.alarm(timeout)
            
            # Execute code
            exec(code, globals_dict)
            success = True
            
        except TimeoutException:
            error = f"Execution timed out after {timeout} seconds"
            logger.warning(error)
        except Exception as e:
            error = str(e)
            logger.error(f"Execution error: {error}")
        finally:
            # Cancel timeout
            if hasattr(signal, 'SIGALRM'):
                signal.alarm(0)
            
            # Restore stdout
            sys.stdout = old_stdout
        
        execution_time = time.time() - start_time
        output = captured_output.getvalue()
        
        return {
            "success": success,
            "error": error,
            "output": output,
            "execution_time": execution_time,
            "globals": {k: str(v) for k, v in globals_dict.items() if not k.startswith('__')}
        }
    
    def execute_function(
        self,
        code: str,
        function_name: str,
        *args,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Execute a specific function from code.
        
        Args:
            code: Python code containing the function
            function_name: Name of function to execute
            *args: Function arguments
            **kwargs: Function keyword arguments
            
        Returns:
            Execution results
        """
        if not self.is_safe(code):
            return {
                "success": False,
                "error": "Code contains unsafe operations",
                "result": None
            }
        
        globals_dict = {}
        
        try:
            # Execute code to define function
            exec(code, globals_dict)
            
            # Check if function exists
            if function_name not in globals_dict:
                return {
                    "success": False,
                    "error": f"Function '{function_name}' not found",
                    "result": None
                }
            
            # Call function
            func = globals_dict[function_name]
            result = func(*args, **kwargs)
            
            return {
                "success": True,
                "error": None,
                "result": result
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "result": None
            }
    
    @contextmanager
    def safe_execution_context(self):
        """Context manager for safe execution."""
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        
        sys.stdout = io.StringIO()
        sys.stderr = io.StringIO()
        
        try:
            yield
        finally:
            sys.stdout = old_stdout
            sys.stderr = old_stderr