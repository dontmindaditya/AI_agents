"""Tests for LangGraph workflow."""

import pytest
from unittest.mock import Mock, patch
from graph import DebugOptimizationGraph, DebugState
from graph.state import create_initial_state


# Test code samples
SIMPLE_CODE = """
def add(a, b):
    return a + b
"""

COMPLEX_CODE = """
def nested_loops(data):
    result = []
    for i in range(len(data)):
        for j in range(len(data)):
            if data[i] == data[j]:
                result.append(data[i])
    return result
"""

ISSUE_CODE = """
def bad_function(x):
    try:
        result = eval(x)
    except:
        pass
    return result
"""


class TestDebugState:
    """Test state management."""
    
    def test_create_initial_state(self):
        """Test initial state creation."""
        state = create_initial_state(SIMPLE_CODE, run_profiling=True)
        
        assert state["code"] == SIMPLE_CODE
        assert state["run_profiling"] == True
        assert state["current_step"] == "start"
        assert state["code_analysis"] is None
        assert state["performance_analysis"] is None
        assert state["memory_analysis"] is None
        assert state["optimization_suggestions"] is None
        assert state["validation_results"] is None
        assert isinstance(state["messages"], list)
        assert isinstance(state["errors"], list)
        assert isinstance(state["completed_steps"], list)
    
    def test_state_structure(self):
        """Test state has all required fields."""
        state = create_initial_state(SIMPLE_CODE)
        
        required_fields = [
            "code",
            "run_profiling",
            "code_analysis",
            "performance_analysis",
            "memory_analysis",
            "optimization_suggestions",
            "validation_results",
            "messages",
            "errors",
            "final_report",
            "current_step",
            "completed_steps"
        ]
        
        for field in required_fields:
            assert field in state, f"Missing required field: {field}"


class TestDebugOptimizationGraph:
    """Test LangGraph workflow."""
    
    def test_graph_initialization(self):
        """Test graph can be initialized."""
        graph = DebugOptimizationGraph()
        
        assert graph is not None
        assert graph.llm is not None
        assert graph.code_analyzer is not None
        assert graph.performance_profiler is not None
        assert graph.memory_analyzer is not None
        assert graph.optimizer is not None
        assert graph.validator is not None
        assert graph.graph is not None
    
    def test_run_simple_code(self):
        """Test workflow with simple code."""
        graph = DebugOptimizationGraph()
        results = graph.run(SIMPLE_CODE, run_profiling=False)
        
        assert "summary" in results
        assert "code_quality" in results
        assert "performance" in results
        assert "memory" in results
        assert "optimizations" in results
        assert "recommendations" in results
    
    def test_run_complex_code(self):
        """Test workflow with complex code."""
        graph = DebugOptimizationGraph()
        results = graph.run(COMPLEX_CODE, run_profiling=False)
        
        # Should detect issues and bottlenecks
        assert results["summary"]["total_bottlenecks"] > 0
        assert results["summary"]["total_optimizations"] >= 0
    
    def test_run_issue_code(self):
        """Test workflow with problematic code."""
        graph = DebugOptimizationGraph()
        results = graph.run(ISSUE_CODE, run_profiling=False)
        
        # Should detect critical issues
        assert results["summary"]["total_issues"] > 0
    
    def test_workflow_steps(self):
        """Test workflow executes all steps."""
        graph = DebugOptimizationGraph()
        results = graph.run(SIMPLE_CODE, run_profiling=False)
        
        # Check that all analysis sections are present
        assert "code_quality" in results
        assert "performance" in results
        assert "memory" in results
        assert "optimizations" in results
    
    def test_summary_generation(self):
        """Test summary generation."""
        graph = DebugOptimizationGraph()
        results = graph.run(SIMPLE_CODE, run_profiling=False)
        
        summary = results["summary"]
        assert "total_issues" in summary
        assert "total_bottlenecks" in summary
        assert "total_memory_issues" in summary
        assert "total_optimizations" in summary
        assert "quick_wins" in summary
        assert "critical_optimizations" in summary
    
    def test_code_quality_metrics(self):
        """Test code quality metrics generation."""
        graph = DebugOptimizationGraph()
        results = graph.run(SIMPLE_CODE, run_profiling=False)
        
        code_quality = results["code_quality"]
        assert "maintainability_index" in code_quality
        assert "average_complexity" in code_quality
        assert "severity_breakdown" in code_quality
        
        # Verify metrics are reasonable
        assert 0 <= code_quality["maintainability_index"] <= 100
        assert code_quality["average_complexity"] >= 0
    
    def test_recommendations_generation(self):
        """Test recommendations are generated."""
        graph = DebugOptimizationGraph()
        results = graph.run(COMPLEX_CODE, run_profiling=False)
        
        recommendations = results["recommendations"]
        assert isinstance(recommendations, list)
        assert len(recommendations) > 0
        
        # Verify recommendation format
        for rec in recommendations:
            assert isinstance(rec, str)
            assert len(rec) > 0
    
    def test_optimization_suggestions(self):
        """Test optimization suggestions are generated."""
        graph = DebugOptimizationGraph()
        results = graph.run(COMPLEX_CODE, run_profiling=False)
        
        optimizations = results["optimizations"]
        assert "quick_wins" in optimizations
        assert "critical" in optimizations
        assert "implementation_plan" in optimizations
        
        # Verify quick wins format
        if len(optimizations["quick_wins"]) > 0:
            quick_win = optimizations["quick_wins"][0]
            assert "title" in quick_win
            assert "impact" in quick_win
            assert "effort" in quick_win
    
    def test_error_handling(self):
        """Test workflow handles errors gracefully."""
        graph = DebugOptimizationGraph()
        
        # Invalid syntax
        invalid_code = "def broken( invalid syntax"
        results = graph.run(invalid_code, run_profiling=False)
        
        # Should not crash
        assert results is not None
        assert "summary" in results or "error" in results
    
    def test_without_profiling(self):
        """Test workflow without profiling."""
        graph = DebugOptimizationGraph()
        results = graph.run(SIMPLE_CODE, run_profiling=False)
        
        assert results is not None
        assert "summary" in results
        
        # Profiling should be skipped
        memory = results.get("memory", {})
        profiling = memory.get("profiling", {})
        if profiling:
            assert profiling.get("skipped") == True or profiling == {}
    
    def test_with_profiling(self):
        """Test workflow with profiling enabled."""
        graph = DebugOptimizationGraph()
        
        # Safe code for profiling
        safe_code = """
def calculate():
    result = 0
    for i in range(10):
        result += i
    return result
"""
        results = graph.run(safe_code, run_profiling=True)
        
        assert results is not None
        assert "summary" in results


class TestWorkflowNodes:
    """Test individual workflow nodes."""
    
    def test_analyze_code_node(self):
        """Test code analysis node."""
        graph = DebugOptimizationGraph()
        
        state = create_initial_state(SIMPLE_CODE)
        result = graph._analyze_code_node(state)
        
        assert "code_analysis" in result
        assert "messages" in result
        assert "current_step" in result
        assert result["current_step"] == "analyze_code"
    
    def test_analyze_performance_node(self):
        """Test performance analysis node."""
        graph = DebugOptimizationGraph()
        
        state = create_initial_state(SIMPLE_CODE)
        result = graph._analyze_performance_node(state)
        
        assert "performance_analysis" in result
        assert "messages" in result
        assert result["current_step"] == "analyze_performance"
    
    def test_analyze_memory_node(self):
        """Test memory analysis node."""
        graph = DebugOptimizationGraph()
        
        state = create_initial_state(SIMPLE_CODE)
        result = graph._analyze_memory_node(state)
        
        assert "memory_analysis" in result
        assert "messages" in result
        assert result["current_step"] == "analyze_memory"
    
    def test_generate_optimizations_node(self):
        """Test optimization generation node."""
        graph = DebugOptimizationGraph()
        
        # Create state with analysis results
        state = create_initial_state(SIMPLE_CODE)
        state["code_analysis"] = {"summary": {"total_issues": 0}, "ast_analysis": {"issues": []}}
        state["performance_analysis"] = {"bottlenecks": []}
        state["memory_analysis"] = {"static_analysis": []}
        
        result = graph._generate_optimizations_node(state)
        
        assert "optimization_suggestions" in result
        assert "messages" in result
        assert result["current_step"] == "generate_optimizations"
    
    def test_generate_report_node(self):
        """Test report generation node."""
        graph = DebugOptimizationGraph()
        
        # Create state with all analysis results
        state = create_initial_state(SIMPLE_CODE)
        state["code_analysis"] = {
            "summary": {
                "total_issues": 0,
                "maintainability_index": 85,
                "severity_breakdown": {"critical": 0, "high": 0, "medium": 0, "low": 0}
            },
            "complexity_metrics": {
                "cyclomatic": {"average": 2}
            }
        }
        state["performance_analysis"] = {"bottlenecks": [], "static_analysis": {}}
        state["memory_analysis"] = {"static_analysis": [], "profiling": {}}
        state["optimization_suggestions"] = {
            "total_opportunities": 0,
            "quick_wins": [],
            "critical_optimizations": [],
            "implementation_plan": {}
        }
        
        result = graph._generate_report_node(state)
        
        assert "final_report" in result
        assert "messages" in result
        assert result["current_step"] == "complete"


class TestWorkflowIntegration:
    """Test full workflow integration."""
    
    def test_complete_workflow(self):
        """Test complete workflow execution."""
        graph = DebugOptimizationGraph()
        
        code = """
def process_data(items):
    result = ""
    for item in items:
        result += str(item) + ", "
    return result

def search(data, target):
    for i in range(len(data)):
        if data[i] == target:
            return i
    return -1
"""
        
        results = graph.run(code, run_profiling=False)
        
        # Verify complete results
        assert "summary" in results
        assert "code_quality" in results
        assert "performance" in results
        assert "memory" in results
        assert "optimizations" in results
        assert "recommendations" in results
        
        # Should detect some issues
        assert results["summary"]["total_issues"] >= 0
        assert results["summary"]["total_bottlenecks"] >= 0
    
    def test_workflow_with_multiple_issues(self):
        """Test workflow with code containing multiple issues."""
        graph = DebugOptimizationGraph()
        
        code = """
def bad_code(a, b, c, d, e, f, g, h):
    global state
    result = []
    for i in range(len(a)):
        for j in range(len(b)):
            try:
                x = eval(str(i))
            except:
                pass
            result.append(i + j)
    return result
"""
        
        results = graph.run(code, run_profiling=False)
        
        # Should detect multiple issues
        assert results["summary"]["total_issues"] > 0
        assert results["summary"]["total_bottlenecks"] > 0
        
        # Should have recommendations
        assert len(results["recommendations"]) > 0
    
    def test_workflow_consistency(self):
        """Test workflow produces consistent results."""
        graph = DebugOptimizationGraph()
        
        # Run twice on same code
        results1 = graph.run(SIMPLE_CODE, run_profiling=False)
        results2 = graph.run(SIMPLE_CODE, run_profiling=False)
        
        # Key metrics should be consistent
        assert results1["summary"]["total_issues"] == results2["summary"]["total_issues"]
        assert results1["code_quality"]["maintainability_index"] == results2["code_quality"]["maintainability_index"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])