from typing import Dict, Any, List  # ← Added List here
from langgraph.graph import StateGraph, END
from langchain_core.language_models import BaseChatModel

from graph.state import DebugState, create_initial_state
from agents import (
    CodeAnalyzerAgent,
    PerformanceProfilerAgent,
    MemoryAnalyzerAgent,
    OptimizationSuggesterAgent,
    ValidatorAgent
)
from models.llm_provider import get_llm
from utils.logger import get_logger

logger = get_logger(__name__)


class DebugOptimizationGraph:
    """LangGraph workflow for debug and optimization."""

    def __init__(self, llm: BaseChatModel = None):
        """
        Initialize debug optimization graph.

        Args:
            llm: Language model to use (optional)
        """
        self.llm = llm or get_llm()

        # Initialize agents
        self.code_analyzer = CodeAnalyzerAgent(self.llm)
        self.performance_profiler = PerformanceProfilerAgent(self.llm)
        self.memory_analyzer = MemoryAnalyzerAgent(self.llm)
        self.optimizer = OptimizationSuggesterAgent(self.llm)
        self.validator = ValidatorAgent(self.llm)  # Note: not used yet, but kept for future

        # Build graph
        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow."""
        workflow = StateGraph(DebugState)

        # Add nodes
        workflow.add_node("analyze_code", self._analyze_code_node)
        workflow.add_node("analyze_performance", self._analyze_performance_node)
        workflow.add_node("analyze_memory", self._analyze_memory_node)
        workflow.add_node("generate_optimizations", self._generate_optimizations_node)
        workflow.add_node("generate_report", self._generate_report_node)

        # Set entry point
        workflow.set_entry_point("analyze_code")

        # Add edges (linear flow)
        workflow.add_edge("analyze_code", "analyze_performance")
        workflow.add_edge("analyze_performance", "analyze_memory")
        workflow.add_edge("analyze_memory", "generate_optimizations")
        workflow.add_edge("generate_optimizations", "generate_report")
        workflow.add_edge("generate_report", END)

        return workflow.compile()

    def _analyze_code_node(self, state: DebugState) -> Dict[str, Any]:
        """Code analysis node."""
        logger.info("Running code analysis node")

        try:
            analysis_results = self.code_analyzer.analyze(state["code"])

            return {
                "code_analysis": analysis_results,
                "messages": state.get("messages", []) + [
                    f"Code analysis complete: {len(analysis_results.get('ast_analysis', {}).get('issues', []))} issues found"
                ],
                "current_step": "analyze_code",
                "completed_steps": (state.get("completed_steps", []) + ["analyze_code"]),
            }
        except Exception as e:
            logger.error(f"Code analysis node failed: {str(e)}")
            return {
                "errors": state.get("errors", []) + [f"Code analysis failed: {str(e)}"],
                "code_analysis": {},
                "current_step": "analyze_code",
                "completed_steps": (state.get("completed_steps", []) + ["analyze_code"]),
            }

    def _analyze_performance_node(self, state: DebugState) -> Dict[str, Any]:
        """Performance analysis node."""
        logger.info("Running performance analysis node")

        try:
            performance_results = self.performance_profiler.analyze(
                state["code"],
                run_profiling=state.get("run_profiling", True)
            )

            bottleneck_count = len(performance_results.get("bottlenecks", []))

            return {
                "performance_analysis": performance_results,
                "messages": state.get("messages", []) + [
                    f"Performance analysis complete: {bottleneck_count} bottlenecks found"
                ],
                "current_step": "analyze_performance",
                "completed_steps": (state.get("completed_steps", []) + ["analyze_performance"]),
            }
        except Exception as e:
            logger.error(f"Performance analysis node failed: {str(e)}")
            return {
                "errors": state.get("errors", []) + [f"Performance analysis failed: {str(e)}"],
                "performance_analysis": {},
                "current_step": "analyze_performance",
                "completed_steps": (state.get("completed_steps", []) + ["analyze_performance"]),
            }

    def _analyze_memory_node(self, state: DebugState) -> Dict[str, Any]:
        """Memory analysis node."""
        logger.info("Running memory analysis node")

        try:
            memory_results = self.memory_analyzer.analyze(
                state["code"],
                run_profiling=state.get("run_profiling", True)
            )

            issue_count = len(memory_results.get("static_analysis", []))

            return {
                "memory_analysis": memory_results,
                "messages": state.get("messages", []) + [
                    f"Memory analysis complete: {issue_count} memory issues found"
                ],
                "current_step": "analyze_memory",
                "completed_steps": (state.get("completed_steps", []) + ["analyze_memory"]),
            }
        except Exception as e:
            logger.error(f"Memory analysis node failed: {str(e)}")
            return {
                "errors": state.get("errors", []) + [f"Memory analysis failed: {str(e)}"],
                "memory_analysis": {},
                "current_step": "analyze_memory",
                "completed_steps": (state.get("completed_steps", []) + ["analyze_memory"]),
            }

    def _generate_optimizations_node(self, state: DebugState) -> Dict[str, Any]:
        """Generate optimization suggestions node."""
        logger.info("Running optimization generation node")

        try:
            optimization_results = self.optimizer.suggest(
                state["code"],
                state.get("code_analysis", {}),
                state.get("performance_analysis", {}),
                state.get("memory_analysis", {})
            )

            opportunity_count = optimization_results.get("total_opportunities", 0)

            return {
                "optimization_suggestions": optimization_results,
                "messages": state.get("messages", []) + [
                    f"Generated {opportunity_count} optimization suggestions"
                ],
                "current_step": "generate_optimizations",
                "completed_steps": (state.get("completed_steps", []) + ["generate_optimizations"]),
            }
        except Exception as e:
            logger.error(f"Optimization generation node failed: {str(e)}")
            return {
                "errors": state.get("errors", []) + [f"Optimization generation failed: {str(e)}"],
                "optimization_suggestions": {},
                "current_step": "generate_optimizations",
                "completed_steps": (state.get("completed_steps", []) + ["generate_optimizations"]),
            }

    def _generate_report_node(self, state: DebugState) -> Dict[str, Any]:
        """Generate final report node."""
        logger.info("Generating final report")

        try:
            code_analysis = state.get("code_analysis", {})
            performance_analysis = state.get("performance_analysis", {})
            memory_analysis = state.get("memory_analysis", {})
            optimizations = state.get("optimization_suggestions", {})

            report = {
                "summary": {
                    "total_issues": code_analysis.get("summary", {}).get("total_issues", 0),
                    "total_bottlenecks": len(performance_analysis.get("bottlenecks", [])),
                    "total_memory_issues": len(memory_analysis.get("static_analysis", [])),
                    "total_optimizations": optimizations.get("total_opportunities", 0),
                    "quick_wins": len(optimizations.get("quick_wins", [])),
                    "critical_optimizations": len(optimizations.get("critical_optimizations", [])),
                },
                "code_quality": {
                    "maintainability_index": code_analysis.get("summary", {}).get("maintainability_index", 0),
                    "average_complexity": code_analysis.get("complexity_metrics", {}).get("cyclomatic", {}).get("average", 0),
                    "severity_breakdown": code_analysis.get("summary", {}).get("severity_breakdown", {}),
                },
                "performance": {
                    "bottlenecks": performance_analysis.get("static_analysis", {}),
                    "top_bottlenecks": [
                        {
                            "type": b.type if hasattr(b, "type") else "unknown",
                            "line": b.line_number if hasattr(b, "line_number") else 0,
                            "severity": b.severity if hasattr(b, "severity") else "info",
                            "description": b.description if hasattr(b, "description") else str(b),
                        }
                        for b in performance_analysis.get("bottlenecks", [])[:5]
                    ],
                },
                "memory": {
                    "issues": memory_analysis.get("static_analysis", [])[:5],
                    "profiling": memory_analysis.get("profiling", {}),
                },
                "optimizations": {
                    "quick_wins": optimizations.get("quick_wins", [])[:5],
                    "critical": optimizations.get("critical_optimizations", [])[:5],
                    "implementation_plan": optimizations.get("implementation_plan", {}),
                },
                "recommendations": self._generate_recommendations(
                    code_analysis, performance_analysis, memory_analysis, optimizations
                ),
                "workflow_messages": state.get("messages", []),
                "errors": state.get("errors", []),
            }

            return {
                "final_report": report,
                "messages": state.get("messages", []) + ["Final report generated"],
                "current_step": "complete",
                "completed_steps": (state.get("completed_steps", []) + ["generate_report"]),
            }

        except Exception as e:
            logger.error(f"Report generation failed: {str(e)}")
            return {
                "errors": state.get("errors", []) + [f"Report generation failed: {str(e)}"],
                "final_report": {},
                "current_step": "complete",
                "completed_steps": (state.get("completed_steps", []) + ["generate_report"]),
            }

    def _generate_recommendations(
        self,
        code_analysis: Dict,
        performance_analysis: Dict,
        memory_analysis: Dict,
        optimizations: Dict
    ) -> List[str]:
        """Generate top-level recommendations."""
        recommendations = []

        # Code quality
        maintainability = code_analysis.get("summary", {}).get("maintainability_index", 100)
        if maintainability < 50:
            recommendations.append("🔴 Critical: Code maintainability is very low. Refactoring is strongly recommended.")
        elif maintainability < 70:
            recommendations.append("🟡 Warning: Code maintainability could be improved significantly.")

        # Performance critical bottlenecks
        critical_bottlenecks = len([
            b for b in performance_analysis.get("bottlenecks", [])
            if getattr(b, "severity", "").lower() == "critical"
        ])
        if critical_bottlenecks > 0:
            recommendations.append(f"🔴 Critical: {critical_bottlenecks} critical performance bottlenecks detected.")

        # Quick wins
        quick_wins = len(optimizations.get("quick_wins", []))
        if quick_wins > 0:
            recommendations.append(f"✅ Good news: {quick_wins} quick-win optimizations available (high impact, low effort).")

        # Memory issues
        memory_issues = len(memory_analysis.get("static_analysis", []))
        if memory_issues > 5:
            recommendations.append(f"🟡 Memory: {memory_issues} potential memory issues detected.")

        if not recommendations:
            recommendations.append("✅ Code looks good! No critical issues detected.")

        return recommendations

    def run(self, code: str, run_profiling: bool = True) -> Dict[str, Any]:
        """
        Run the complete debug optimization workflow.

        Args:
            code: Python code to analyze
            run_profiling: Whether to run actual profiling

        Returns:
            Final analysis report
        """
        logger.info("Starting debug optimization workflow")

        try:
            initial_state = create_initial_state(code, run_profiling)
            final_state = self.graph.invoke(initial_state)

            logger.info("Workflow completed successfully")
            return final_state.get("final_report", {})

        except Exception as e:
            logger.error(f"Workflow failed: {str(e)}")
            return {
                "error": str(e),
                "summary": {},
                "recommendations": [f"Workflow failed: {str(e)}"],
            }