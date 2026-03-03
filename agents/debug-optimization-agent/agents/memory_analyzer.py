"""Memory analyzer agent for memory usage analysis."""

from typing import Dict, Any, List
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.language_models import BaseChatModel

from tools.memory_profiler_wrapper import MemoryProfilerWrapper
from tools.code_executor import CodeExecutor
from models.llm_provider import LLMFactory
from utils.logger import AgentLogger
from prompts.analyzer_prompts import MEMORY_SYSTEM_PROMPT, MEMORY_USER_PROMPT


class MemoryAnalyzerAgent:
    """Agent for memory usage analysis and leak detection."""
    
    def __init__(self, llm: BaseChatModel = None):
        """
        Initialize memory analyzer agent.
        
        Args:
            llm: Language model to use
        """
        self.llm = llm or LLMFactory.create_analyzer_llm()
        self.logger = AgentLogger("MemoryAnalyzer")
        self.memory_profiler = MemoryProfilerWrapper()
        self.executor = CodeExecutor()
    
    def analyze(self, code: str, run_profiling: bool = True) -> Dict[str, Any]:
        """
        Analyze code for memory issues.
        
        Args:
            code: Python code to analyze
            run_profiling: Whether to run actual profiling
            
        Returns:
            Memory analysis results
        """
        self.logger.info("Starting memory analysis")
        
        try:
            # Static analysis for memory issues
            static_issues = self._detect_static_memory_issues(code)
            
            results = {
                "static_analysis": static_issues,
            }
            
            # Runtime memory profiling
            if run_profiling:
                profiling_results = self._run_memory_profiling(code)
                results["profiling"] = profiling_results
            else:
                results["profiling"] = {
                    "skipped": True,
                    "reason": "Profiling disabled"
                }
            
            # Get LLM insights
            llm_insights = self._get_llm_insights(code, results)
            results["llm_insights"] = llm_insights
            
            self.logger.info("Memory analysis complete")
            
            return results
            
        except Exception as e:
            self.logger.error(f"Memory analysis failed: {str(e)}")
            return {
                "error": str(e),
                "static_analysis": [],
                "profiling": {},
                "llm_insights": ""
            }
    
    def _detect_static_memory_issues(self, code: str) -> List[Dict]:
        """Detect potential memory issues through static analysis."""
        self.logger.debug("Detecting static memory issues")
        
        issues = []
        lines = code.split('\n')
        
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            
            # Check for large data structures
            if 'range(' in stripped:
                # Check for large ranges
                import re
                matches = re.findall(r'range\((\d+)\)', stripped)
                for match in matches:
                    size = int(match)
                    if size > 10000:
                        issues.append({
                            "line": i,
                            "type": "large_range",
                            "severity": "medium",
                            "description": f"Large range({size}) may consume significant memory",
                            "suggestion": "Consider using generator or iterator pattern"
                        })
            
            # Check for list comprehensions with large inputs
            if '[' in stripped and 'for' in stripped and 'in' in stripped:
                if 'range(' in stripped:
                    issues.append({
                        "line": i,
                        "type": "list_comprehension",
                        "severity": "low",
                        "description": "List comprehension with range - consider generator",
                        "suggestion": "Use generator expression () instead of [] for large datasets"
                    })
            
            # Check for global variables (potential memory leaks)
            if stripped.startswith('global '):
                issues.append({
                    "line": i,
                    "type": "global_variable",
                    "severity": "medium",
                    "description": "Global variable usage detected",
                    "suggestion": "Minimize global state to prevent memory leaks"
                })
            
            # Check for file operations without explicit close
            if 'open(' in stripped and 'with' not in stripped:
                issues.append({
                    "line": i,
                    "type": "resource_leak",
                    "severity": "high",
                    "description": "File opened without context manager",
                    "suggestion": "Use 'with open()' to ensure proper resource cleanup"
                })
        
        return issues
    
    def _run_memory_profiling(self, code: str) -> Dict[str, Any]:
        """Run actual memory profiling."""
        self.logger.debug("Running memory profiling")
        
        try:
            # Check if code is safe
            if not self.executor.is_safe(code):
                return {
                    "skipped": True,
                    "reason": "Code unsafe for execution"
                }
            
            # Profile memory
            profile_result = self.memory_profiler.profile(code)
            
            return {
                "peak_memory_mb": profile_result.get("peak_memory_mb", 0),
                "memory_increase_mb": profile_result.get("memory_increase_mb", 0),
                "line_by_line": profile_result.get("line_by_line", []),
                "execution_successful": True
            }
            
        except Exception as e:
            self.logger.error(f"Memory profiling failed: {str(e)}")
            return {
                "error": str(e),
                "execution_successful": False
            }
    
    def _get_llm_insights(self, code: str, analysis_results: Dict) -> str:
        """Get LLM insights about memory usage."""
        self.logger.debug("Getting LLM memory insights")
        
        try:
            static_issues = analysis_results.get("static_analysis", [])
            profiling = analysis_results.get("profiling", {})
            
            peak_memory = profiling.get("peak_memory_mb", "N/A")
            
            user_message = MEMORY_USER_PROMPT.format(
                code=code[:1000],
                total_issues=len(static_issues),
                peak_memory=peak_memory,
                issue_summary=self._format_issues(static_issues[:5])
            )
            
            messages = [
                SystemMessage(content=MEMORY_SYSTEM_PROMPT),
                HumanMessage(content=user_message)
            ]
            
            response = self.llm.invoke(messages)
            return response.content
            
        except Exception as e:
            self.logger.error(f"LLM insights failed: {str(e)}")
            return "Memory insights unavailable"
    
    def _format_issues(self, issues: List[Dict]) -> str:
        """Format memory issues for LLM prompt."""
        if not issues:
            return "No significant memory issues detected"
        
        formatted = []
        for issue in issues:
            formatted.append(
                f"- Line {issue['line']}: {issue['type']}\n"
                f"  {issue['description']}\n"
                f"  Suggestion: {issue['suggestion']}"
            )
        return "\n\n".join(formatted)
    
    def get_memory_recommendations(self, analysis_results: Dict) -> List[Dict]:
        """Get memory optimization recommendations."""
        issues = analysis_results.get("static_analysis", [])
        
        recommendations = []
        for issue in issues:
            if issue["severity"] in ["high", "critical"]:
                recommendations.append({
                    "line": issue["line"],
                    "type": issue["type"],
                    "severity": issue["severity"],
                    "recommendation": issue["suggestion"]
                })
        
        return recommendations