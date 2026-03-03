"""Performance profiler agent for runtime analysis."""

from typing import Dict, Any, List
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.language_models import BaseChatModel

from algorithms.bottleneck_analyzer import BottleneckAnalyzer
from tools.profiler_wrapper import ProfilerWrapper
from tools.code_executor import CodeExecutor
from models.llm_provider import LLMFactory
from utils.logger import AgentLogger
from prompts.analyzer_prompts import PROFILER_SYSTEM_PROMPT, PROFILER_USER_PROMPT


class PerformanceProfilerAgent:
    """Agent for performance profiling and bottleneck detection."""
    
    def __init__(self, llm: BaseChatModel = None):
        """
        Initialize performance profiler agent.
        
        Args:
            llm: Language model to use
        """
        self.llm = llm or LLMFactory.create_analyzer_llm()
        self.logger = AgentLogger("PerformanceProfiler")
        self.profiler = ProfilerWrapper()
        self.executor = CodeExecutor()
    
    def analyze(self, code: str, run_profiling: bool = True) -> Dict[str, Any]:
        """
        Analyze code for performance issues.
        
        Args:
            code: Python code to analyze
            run_profiling: Whether to run actual profiling (default: True)
            
        Returns:
            Performance analysis results
        """
        self.logger.info("Starting performance analysis")
        
        try:
            # Static bottleneck detection (always runs)
            bottlenecks = self._detect_bottlenecks(code)
            
            results = {
                "bottlenecks": bottlenecks,
                "static_analysis": self._analyze_bottlenecks(bottlenecks),
            }
            
            # Runtime profiling (optional, may be disabled for unsafe code)
            if run_profiling:
                profiling_results = self._run_profiling(code)
                results["profiling"] = profiling_results
            else:
                results["profiling"] = {
                    "skipped": True,
                    "reason": "Profiling disabled for safety"
                }
            
            # Get LLM insights
            llm_insights = self._get_llm_insights(code, results)
            results["llm_insights"] = llm_insights
            
            self.logger.info(f"Performance analysis complete: {len(bottlenecks)} bottlenecks found")
            
            return results
            
        except Exception as e:
            self.logger.error(f"Performance analysis failed: {str(e)}")
            return {
                "error": str(e),
                "bottlenecks": [],
                "profiling": {},
                "llm_insights": ""
            }
    
    def _detect_bottlenecks(self, code: str) -> List:
        """Detect performance bottlenecks using static analysis."""
        self.logger.debug("Detecting bottlenecks")
        
        try:
            analyzer = BottleneckAnalyzer(code)
            return analyzer.analyze()
        except Exception as e:
            self.logger.error(f"Bottleneck detection failed: {str(e)}")
            return []
    
    def _run_profiling(self, code: str) -> Dict[str, Any]:
        """Run actual code profiling."""
        self.logger.debug("Running code profiling")
        
        try:
            # Check if code is safe to execute
            if not self.executor.is_safe(code):
                self.logger.warning("Code deemed unsafe for execution")
                return {
                    "skipped": True,
                    "reason": "Code contains potentially unsafe operations"
                }
            
            # Run with profiling
            cpu_profile = self.profiler.profile_cpu(code)
            memory_profile = self.profiler.profile_memory(code)
            
            return {
                "cpu": cpu_profile,
                "memory": memory_profile,
                "execution_successful": True
            }
            
        except Exception as e:
            self.logger.error(f"Profiling failed: {str(e)}")
            return {
                "error": str(e),
                "execution_successful": False
            }
    
    def _analyze_bottlenecks(self, bottlenecks: List) -> Dict[str, Any]:
        """Analyze detected bottlenecks."""
        if not bottlenecks:
            return {
                "total": 0,
                "by_severity": {},
                "by_type": {},
                "top_priority": []
            }
        
        # Count by severity
        by_severity = {}
        for b in bottlenecks:
            severity = b.severity
            by_severity[severity] = by_severity.get(severity, 0) + 1
        
        # Count by type
        by_type = {}
        for b in bottlenecks:
            btype = b.type
            by_type[btype] = by_type.get(btype, 0) + 1
        
        # Get top priority (critical and high severity)
        top_priority = [
            b for b in bottlenecks
            if b.severity in ["critical", "high"]
        ]
        
        return {
            "total": len(bottlenecks),
            "by_severity": by_severity,
            "by_type": by_type,
            "top_priority": top_priority[:5]  # Top 5
        }
    
    def _get_llm_insights(self, code: str, analysis_results: Dict) -> str:
        """Get LLM insights about performance."""
        self.logger.debug("Getting LLM performance insights")
        
        try:
            bottlenecks = analysis_results.get("bottlenecks", [])[:5]
            static_analysis = analysis_results.get("static_analysis", {})
            
            user_message = PROFILER_USER_PROMPT.format(
                code=code[:1000],
                total_bottlenecks=static_analysis.get("total", 0),
                critical_count=static_analysis.get("by_severity", {}).get("critical", 0),
                high_count=static_analysis.get("by_severity", {}).get("high", 0),
                bottleneck_summary=self._format_bottlenecks(bottlenecks)
            )
            
            messages = [
                SystemMessage(content=PROFILER_SYSTEM_PROMPT),
                HumanMessage(content=user_message)
            ]
            
            response = self.llm.invoke(messages)
            return response.content
            
        except Exception as e:
            self.logger.error(f"LLM insights failed: {str(e)}")
            return "Performance insights unavailable"
    
    def _format_bottlenecks(self, bottlenecks: List) -> str:
        """Format bottlenecks for LLM prompt."""
        if not bottlenecks:
            return "No significant bottlenecks detected"
        
        formatted = []
        for b in bottlenecks:
            formatted.append(
                f"- {b.type} (Line {b.line_number}): {b.description}\n"
                f"  Impact: {b.impact}\n"
                f"  Suggestion: {b.optimization_suggestion}"
            )
        return "\n\n".join(formatted)
    
    def get_optimization_priorities(self, analysis_results: Dict) -> List[Dict]:
        """Get prioritized list of performance optimizations."""
        bottlenecks = analysis_results.get("bottlenecks", [])
        
        # Sort by severity score
        severity_scores = {
            "critical": 4,
            "high": 3,
            "medium": 2,
            "low": 1
        }
        
        sorted_bottlenecks = sorted(
            bottlenecks,
            key=lambda b: severity_scores.get(b.severity, 0),
            reverse=True
        )
        
        priorities = []
        for b in sorted_bottlenecks[:10]:  # Top 10
            priorities.append({
                "line": b.line_number,
                "type": b.type,
                "severity": b.severity,
                "description": b.description,
                "impact": b.impact,
                "suggestion": b.optimization_suggestion,
                "estimated_improvement": b.estimated_improvement
            })
        
        return priorities