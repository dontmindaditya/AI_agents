"""Static analysis tools wrapper."""

import subprocess
import tempfile
import os
from typing import Dict, Any, List
from pathlib import Path

from utils.logger import get_logger

logger = get_logger(__name__)


class StaticAnalyzer:
    """Wrapper for static analysis tools (pylint, flake8, mypy)."""
    
    def __init__(self):
        """Initialize static analyzer."""
        self.tools_available = self._check_tools()
    
    def _check_tools(self) -> Dict[str, bool]:
        """Check which static analysis tools are available."""
        tools = {}
        
        for tool in ['pylint', 'flake8', 'mypy']:
            try:
                result = subprocess.run(
                    [tool, '--version'],
                    capture_output=True,
                    timeout=5
                )
                tools[tool] = result.returncode == 0
            except Exception:
                tools[tool] = False
        
        return tools
    
    def analyze(self, code: str) -> Dict[str, Any]:
        """
        Run all available static analysis tools.
        
        Args:
            code: Python code to analyze
            
        Returns:
            Analysis results from all tools
        """
        logger.info("Running static analysis")
        
        results = {}
        
        if self.tools_available.get('pylint', False):
            results['pylint'] = self.run_pylint(code)
        
        if self.tools_available.get('flake8', False):
            results['flake8'] = self.run_flake8(code)
        
        if self.tools_available.get('mypy', False):
            results['mypy'] = self.run_mypy(code)
        
        # Combine results
        results['summary'] = self._generate_summary(results)
        
        return results
    
    def run_pylint(self, code: str) -> Dict[str, Any]:
        """
        Run pylint on code.
        
        Args:
            code: Python code to analyze
            
        Returns:
            Pylint results
        """
        logger.debug("Running pylint")
        
        try:
            # Write code to temporary file
            with tempfile.NamedTemporaryFile(
                mode='w',
                suffix='.py',
                delete=False
            ) as f:
                f.write(code)
                temp_file = f.name
            
            try:
                # Run pylint
                result = subprocess.run(
                    ['pylint', temp_file, '--output-format=json'],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                # Parse JSON output
                import json
                if result.stdout:
                    messages = json.loads(result.stdout)
                else:
                    messages = []
                
                # Calculate score (10 - (errors + warnings) * 0.1)
                score = 10.0
                for msg in messages:
                    if msg.get('type') in ['error', 'fatal']:
                        score -= 0.5
                    elif msg.get('type') == 'warning':
                        score -= 0.2
                    elif msg.get('type') in ['convention', 'refactor']:
                        score -= 0.1
                
                score = max(0, score)
                
                return {
                    "tool": "pylint",
                    "score": round(score, 2),
                    "messages": messages,
                    "total_issues": len(messages),
                    "errors": len([m for m in messages if m.get('type') in ['error', 'fatal']]),
                    "warnings": len([m for m in messages if m.get('type') == 'warning']),
                    "conventions": len([m for m in messages if m.get('type') == 'convention'])
                }
                
            finally:
                # Clean up temp file
                os.unlink(temp_file)
                
        except subprocess.TimeoutExpired:
            return {"error": "Pylint timed out", "tool": "pylint"}
        except Exception as e:
            logger.error(f"Pylint failed: {str(e)}")
            return {"error": str(e), "tool": "pylint"}
    
    def run_flake8(self, code: str) -> Dict[str, Any]:
        """
        Run flake8 on code.
        
        Args:
            code: Python code to analyze
            
        Returns:
            Flake8 results
        """
        logger.debug("Running flake8")
        
        try:
            with tempfile.NamedTemporaryFile(
                mode='w',
                suffix='.py',
                delete=False
            ) as f:
                f.write(code)
                temp_file = f.name
            
            try:
                result = subprocess.run(
                    ['flake8', temp_file, '--format=json'],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                # Parse output
                messages = []
                if result.stdout:
                    import json
                    try:
                        data = json.loads(result.stdout)
                        messages = data.get(temp_file, [])
                    except json.JSONDecodeError:
                        # Fallback to text parsing
                        for line in result.stdout.split('\n'):
                            if line.strip():
                                messages.append({"message": line})
                
                return {
                    "tool": "flake8",
                    "messages": messages,
                    "total_issues": len(messages),
                    "passed": len(messages) == 0
                }
                
            finally:
                os.unlink(temp_file)
                
        except subprocess.TimeoutExpired:
            return {"error": "Flake8 timed out", "tool": "flake8"}
        except Exception as e:
            logger.error(f"Flake8 failed: {str(e)}")
            return {"error": str(e), "tool": "flake8"}
    
    def run_mypy(self, code: str) -> Dict[str, Any]:
        """
        Run mypy type checking on code.
        
        Args:
            code: Python code to analyze
            
        Returns:
            Mypy results
        """
        logger.debug("Running mypy")
        
        try:
            with tempfile.NamedTemporaryFile(
                mode='w',
                suffix='.py',
                delete=False
            ) as f:
                f.write(code)
                temp_file = f.name
            
            try:
                result = subprocess.run(
                    ['mypy', temp_file, '--no-error-summary'],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                # Parse output
                messages = []
                if result.stdout:
                    for line in result.stdout.split('\n'):
                        if line.strip() and ':' in line:
                            messages.append({"message": line.strip()})
                
                return {
                    "tool": "mypy",
                    "messages": messages,
                    "total_issues": len(messages),
                    "passed": len(messages) == 0
                }
                
            finally:
                os.unlink(temp_file)
                
        except subprocess.TimeoutExpired:
            return {"error": "Mypy timed out", "tool": "mypy"}
        except Exception as e:
            logger.error(f"Mypy failed: {str(e)}")
            return {"error": str(e), "tool": "mypy"}
    
    def _generate_summary(self, results: Dict) -> Dict[str, Any]:
        """Generate summary of all static analysis results."""
        total_issues = 0
        tools_run = 0
        tools_passed = 0
        
        for tool, result in results.items():
            if tool == 'summary':
                continue
            
            if 'error' not in result:
                tools_run += 1
                total_issues += result.get('total_issues', 0)
                
                if result.get('passed', False) or result.get('total_issues', 0) == 0:
                    tools_passed += 1
        
        return {
            "total_issues": total_issues,
            "tools_run": tools_run,
            "tools_passed": tools_passed,
            "all_passed": tools_passed == tools_run if tools_run > 0 else False,
            "tools_available": self.tools_available
        }
    
    def get_recommendations(self, analysis_results: Dict) -> List[str]:
        """
        Get recommendations based on static analysis.
        
        Args:
            analysis_results: Results from analyze()
            
        Returns:
            List of recommendations
        """
        recommendations = []
        
        pylint_result = analysis_results.get('pylint', {})
        if pylint_result.get('score', 10) < 7:
            recommendations.append(
                f"Pylint score is {pylint_result.get('score', 'N/A')}/10. "
                "Consider addressing pylint warnings."
            )
        
        flake8_result = analysis_results.get('flake8', {})
        if flake8_result.get('total_issues', 0) > 0:
            recommendations.append(
                f"Flake8 found {flake8_result.get('total_issues')} style issues. "
                "Review and fix PEP 8 violations."
            )
        
        mypy_result = analysis_results.get('mypy', {})
        if mypy_result.get('total_issues', 0) > 0:
            recommendations.append(
                f"Mypy found {mypy_result.get('total_issues')} type issues. "
                "Add type hints and fix type errors."
            )
        
        return recommendations if recommendations else ["Code looks good! No major issues detected."]