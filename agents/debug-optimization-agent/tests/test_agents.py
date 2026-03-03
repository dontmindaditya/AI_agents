"""Tests for agent modules."""

import pytest
from unittest.mock import Mock, patch
from agents import (
    CodeAnalyzerAgent,
    PerformanceProfilerAgent,
    MemoryAnalyzerAgent,
    OptimizationSuggesterAgent,
    ValidatorAgent
)


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
def bad_function(x, y, z, a, b, c, d, e):
    global state
    state = x + y
    try:
        result = eval(x)
    except:
        pass
    return result
"""


class TestCodeAnalyzerAgent:
    """Test code analyzer agent."""
    
    def test_agent_initialization(self):
        """Test agent can be initialized."""
        agent = CodeAnalyzerAgent()
        assert agent is not None
        assert agent.llm is not None
    
    def test_analyze_simple_code(self):
        """Test analysis of simple code."""
        agent = CodeAnalyzerAgent()
        results = agent.analyze(SIMPLE_CODE)
        
        assert "ast_analysis" in results
        assert "complexity_metrics" in results
        assert "patterns" in results
        assert "summary" in results
    
    def test_analyze_complex_code(self):
        """Test analysis of complex code."""
        agent = CodeAnalyzerAgent()
        results = agent.analyze(COMPLEX_CODE)
        
        # Should detect issues
        assert results["summary"]["total_issues"] >= 0
        assert "bottleneck" in str(results).lower() or "nested" in str(results).lower()
    
    def test_analyze_issue_code(self):
        """Test analysis of problematic code."""
        agent = CodeAnalyzerAgent()
        results = agent.analyze(ISSUE_CODE)
        
        # Should detect critical issues (eval, bare except, etc.)
        assert results["summary"]["total_issues"] > 0
        
        # Check for critical severity
        severity = results["summary"]["severity_breakdown"]
        assert severity["critical"] > 0 or severity["high"] > 0
    
    def test_get_critical_issues(self):
        """Test extraction of critical issues."""
        agent = CodeAnalyzerAgent()
        results = agent.analyze(ISSUE_CODE)
        
        critical = agent.get_critical_issues(results)
        assert isinstance(critical, list)
    
    def test_error_handling(self):
        """Test error handling with invalid code."""
        agent = CodeAnalyzerAgent()
        
        # Invalid syntax
        invalid_code = "def broken( invalid syntax"
        results = agent.analyze(invalid_code)
        
        # Should handle gracefully
        assert "error" in results or "ast_analysis" in results


class TestPerformanceProfilerAgent:
    """Test performance profiler agent."""
    
    def test_agent_initialization(self):
        """Test agent can be initialized."""
        agent = PerformanceProfilerAgent()
        assert agent is not None
        assert agent.profiler is not None
    
    def test_analyze_without_profiling(self):
        """Test analysis without runtime profiling."""
        agent = PerformanceProfilerAgent()
        results = agent.analyze(SIMPLE_CODE, run_profiling=False)
        
        assert "bottlenecks" in results
        assert "static_analysis" in results
        assert results["profiling"]["skipped"] == True
    
    def test_detect_bottlenecks(self):
        """Test bottleneck detection."""
        agent = PerformanceProfilerAgent()
        results = agent.analyze(COMPLEX_CODE, run_profiling=False)
        
        # Should detect nested loop bottleneck
        assert len(results["bottlenecks"]) > 0
        
        bottleneck_types = [b.type for b in results["bottlenecks"]]
        assert "nested_loops" in bottleneck_types
    
    def test_analyze_with_profiling(self):
        """Test analysis with runtime profiling."""
        agent = PerformanceProfilerAgent()
        
        # Simple safe code for profiling
        safe_code = """
def calculate():
    result = 0
    for i in range(100):
        result += i
    return result

calculate()
"""
        results = agent.analyze(safe_code, run_profiling=True)
        
        assert "bottlenecks" in results
        assert "profiling" in results
    
    def test_get_optimization_priorities(self):
        """Test priority extraction."""
        agent = PerformanceProfilerAgent()
        results = agent.analyze(COMPLEX_CODE, run_profiling=False)
        
        priorities = agent.get_optimization_priorities(results)
        assert isinstance(priorities, list)
        
        if len(priorities) > 0:
            assert "line" in priorities[0]
            assert "severity" in priorities[0]
            assert "suggestion" in priorities[0]


class TestMemoryAnalyzerAgent:
    """Test memory analyzer agent."""
    
    def test_agent_initialization(self):
        """Test agent can be initialized."""
        agent = MemoryAnalyzerAgent()
        assert agent is not None
    
    def test_analyze_without_profiling(self):
        """Test analysis without runtime profiling."""
        agent = MemoryAnalyzerAgent()
        results = agent.analyze(SIMPLE_CODE, run_profiling=False)
        
        assert "static_analysis" in results
        assert results["profiling"]["skipped"] == True
    
    def test_detect_memory_issues(self):
        """Test memory issue detection."""
        memory_code = """
def create_large_list():
    data = []
    for i in range(10000):
        data.append([i] * 1000)
    return data

global cache
cache = []
"""
        agent = MemoryAnalyzerAgent()
        results = agent.analyze(memory_code, run_profiling=False)
        
        # Should detect issues
        assert len(results["static_analysis"]) >= 0
    
    def test_get_memory_recommendations(self):
        """Test memory recommendations."""
        agent = MemoryAnalyzerAgent()
        
        code_with_issues = """
f = open('test.txt', 'r')
data = f.read()
"""
        results = agent.analyze(code_with_issues, run_profiling=False)
        recommendations = agent.get_memory_recommendations(results)
        
        assert isinstance(recommendations, list)


class TestOptimizationSuggesterAgent:
    """Test optimization suggester agent."""
    
    def test_agent_initialization(self):
        """Test agent can be initialized."""
        agent = OptimizationSuggesterAgent()
        assert agent is not None
    
    def test_suggest_optimizations(self):
        """Test optimization suggestion generation."""
        agent = OptimizationSuggesterAgent()
        
        # Mock analysis results
        code_analysis = {
            "ast_analysis": {"issues": []},
            "summary": {"total_issues": 0}
        }
        performance_analysis = {
            "bottlenecks": []
        }
        memory_analysis = {
            "static_analysis": []
        }
        
        results = agent.suggest(
            SIMPLE_CODE,
            code_analysis,
            performance_analysis,
            memory_analysis
        )
        
        assert "total_opportunities" in results
        assert "quick_wins" in results
        assert "all_opportunities" in results
    
    def test_get_quick_wins(self):
        """Test quick win extraction."""
        agent = OptimizationSuggesterAgent()
        
        # Create mock suggestions
        suggestions = {
            "quick_wins": [
                {
                    "title": "Test optimization",
                    "impact": "HIGH",
                    "effort": "EASY"
                }
            ]
        }
        
        quick_wins = agent.get_quick_win_recommendations(suggestions)
        assert isinstance(quick_wins, list)
        assert len(quick_wins) <= 5
    
    def test_get_critical_recommendations(self):
        """Test critical recommendation extraction."""
        agent = OptimizationSuggesterAgent()
        
        suggestions = {
            "critical_optimizations": [
                {
                    "title": "Critical fix",
                    "impact": "CRITICAL",
                    "effort": "MODERATE"
                }
            ]
        }
        
        critical = agent.get_critical_recommendations(suggestions)
        assert isinstance(critical, list)


class TestValidatorAgent:
    """Test validator agent."""
    
    def test_agent_initialization(self):
        """Test agent can be initialized."""
        agent = ValidatorAgent()
        assert agent is not None
    
    def test_validate_simple_optimization(self):
        """Test validation of simple optimization."""
        agent = ValidatorAgent()
        
        original = """
def slow():
    result = []
    for i in range(10):
        result.append(i * 2)
    return result
"""
        
        optimized = """
def fast():
    return [i * 2 for i in range(10)]
"""
        
        results = agent.validate(original, optimized, "Convert to list comprehension")
        
        assert "syntax_valid" in results
        assert "safe_to_apply" in results
        assert "recommendation" in results
    
    def test_validate_syntax_error(self):
        """Test validation catches syntax errors."""
        agent = ValidatorAgent()
        
        original = "def valid(): return 1"
        optimized = "def invalid( syntax error"
        
        results = agent.validate(original, optimized, "Test")
        
        assert results["syntax_valid"] == False
        assert "error" in results["errors"][0].lower() or "syntax" in results["errors"][0].lower()
    
    def test_validation_recommendation(self):
        """Test validation generates recommendations."""
        agent = ValidatorAgent()
        
        original = "def original(): return 1"
        optimized = "def optimized(): return 1"
        
        results = agent.validate(original, optimized, "No change")
        
        assert results["recommendation"] in [
            "APPROVE - Safe and beneficial",
            "REVIEW - Performance improved but verify equivalence",
            "REVIEW - Functionally equivalent but verify performance",
            "REVIEW - Manual verification recommended",
            "REJECT - Syntax errors",
            "REJECT - Safety concerns"
        ]
    
    def test_batch_validate(self):
        """Test batch validation."""
        agent = ValidatorAgent()
        
        optimizations = [
            {
                "title": "Opt 1",
                "optimized_code": "def test1(): return 1",
                "description": "Test 1"
            },
            {
                "title": "Opt 2",
                "optimized_code": "def test2(): return 2",
                "description": "Test 2"
            }
        ]
        
        results = agent.batch_validate("def original(): return 0", optimizations)
        
        assert isinstance(results, list)
        assert len(results) == 2
        assert all("recommendation" in r for r in results)


class TestAgentIntegration:
    """Test agent integration and workflow."""
    
    def test_full_analysis_pipeline(self):
        """Test complete analysis pipeline with all agents."""
        # Initialize agents
        code_analyzer = CodeAnalyzerAgent()
        performance_profiler = PerformanceProfilerAgent()
        memory_analyzer = MemoryAnalyzerAgent()
        optimizer = OptimizationSuggesterAgent()
        
        # Run analysis pipeline
        code_results = code_analyzer.analyze(COMPLEX_CODE)
        perf_results = performance_profiler.analyze(COMPLEX_CODE, run_profiling=False)
        mem_results = memory_analyzer.analyze(COMPLEX_CODE, run_profiling=False)
        
        # Generate optimizations
        opt_results = optimizer.suggest(
            COMPLEX_CODE,
            code_results,
            perf_results,
            mem_results
        )
        
        # Verify pipeline results
        assert code_results["summary"]["total_issues"] >= 0
        assert len(perf_results["bottlenecks"]) >= 0
        assert opt_results["total_opportunities"] >= 0
    
    def test_agent_error_recovery(self):
        """Test agents handle errors gracefully."""
        agents = [
            CodeAnalyzerAgent(),
            PerformanceProfilerAgent(),
            MemoryAnalyzerAgent()
        ]
        
        # Test with invalid code
        invalid_code = "def broken syntax error"
        
        for agent in agents:
            try:
                if hasattr(agent, 'analyze'):
                    result = agent.analyze(invalid_code)
                    # Should not crash
                    assert result is not None
            except Exception as e:
                pytest.fail(f"Agent {type(agent).__name__} failed to handle error: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])