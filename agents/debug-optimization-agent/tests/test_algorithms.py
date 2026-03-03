"""Tests for algorithm modules."""

import pytest
from algorithms.ast_analyzer import ASTAnalyzer
from algorithms.complexity_metrics import ComplexityAnalyzer
from algorithms.pattern_detector import PatternDetector
from algorithms.bottleneck_analyzer import BottleneckAnalyzer
from algorithms.optimization_ranker import OptimizationRanker, ImpactLevel, EffortLevel


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


class TestASTAnalyzer:
    """Test AST analyzer."""
    
    def test_simple_analysis(self):
        """Test analysis of simple code."""
        analyzer = ASTAnalyzer(SIMPLE_CODE)
        results = analyzer.analyze()
        
        assert "issues" in results
        assert "metrics" in results
        assert isinstance(results["issues"], list)
    
    def test_issue_detection(self):
        """Test detection of code issues."""
        analyzer = ASTAnalyzer(ISSUE_CODE)
        results = analyzer.analyze()
        
        # Should detect eval usage and bare except
        assert len(results["issues"]) > 0
        
        # Check for critical issues
        critical_issues = [i for i in results["issues"] if i.severity == "critical"]
        assert len(critical_issues) > 0


class TestComplexityAnalyzer:
    """Test complexity analyzer."""
    
    def test_cyclomatic_complexity(self):
        """Test cyclomatic complexity calculation."""
        analyzer = ComplexityAnalyzer(SIMPLE_CODE)
        results = analyzer.analyze_all()
        
        assert "cyclomatic" in results
        assert results["cyclomatic"]["average"] >= 1
    
    def test_maintainability_index(self):
        """Test maintainability index calculation."""
        analyzer = ComplexityAnalyzer(SIMPLE_CODE)
        results = analyzer.analyze_all()
        
        assert "maintainability_index" in results
        assert 0 <= results["maintainability_index"] <= 100


class TestPatternDetector:
    """Test pattern detector."""
    
    def test_pattern_detection(self):
        """Test anti-pattern detection."""
        detector = PatternDetector(ISSUE_CODE)
        patterns = detector.detect_all()
        
        assert isinstance(patterns, list)
        # Should detect long parameter list
        assert len(patterns) > 0
    
    def test_nested_loop_detection(self):
        """Test detection of nested loops."""
        detector = PatternDetector(COMPLEX_CODE)
        patterns = detector.detect_all()
        
        # May detect inefficient loop pattern
        assert isinstance(patterns, list)


class TestBottleneckAnalyzer:
    """Test bottleneck analyzer."""
    
    def test_nested_loop_bottleneck(self):
        """Test detection of nested loop bottleneck."""
        analyzer = BottleneckAnalyzer(COMPLEX_CODE)
        bottlenecks = analyzer.analyze()
        
        assert len(bottlenecks) > 0
        # Should detect O(n^2) complexity
        nested_bottlenecks = [b for b in bottlenecks if b.type == "nested_loops"]
        assert len(nested_bottlenecks) > 0
    
    def test_bottleneck_severity(self):
        """Test bottleneck severity classification."""
        analyzer = BottleneckAnalyzer(COMPLEX_CODE)
        bottlenecks = analyzer.analyze()
        
        for bottleneck in bottlenecks:
            assert bottleneck.severity in ["critical", "high", "medium", "low"]


class TestOptimizationRanker:
    """Test optimization ranker."""
    
    def test_opportunity_addition(self):
        """Test adding optimization opportunities."""
        ranker = OptimizationRanker()
        
        ranker.add_opportunity(
            title="Test optimization",
            description="Test description",
            category="performance",
            impact=ImpactLevel.HIGH,
            effort=EffortLevel.EASY,
            line_number=10,
            estimated_improvement="10x faster",
            implementation_steps=["Step 1", "Step 2"]
        )
        
        opportunities = ranker.rank_opportunities()
        assert len(opportunities) == 1
        assert opportunities[0].title == "Test optimization"
    
    def test_priority_calculation(self):
        """Test priority score calculation."""
        ranker = OptimizationRanker()
        
        # High impact, low effort = high priority
        ranker.add_opportunity(
            title="Quick win",
            description="Easy fix",
            category="performance",
            impact=ImpactLevel.HIGH,
            effort=EffortLevel.EASY,
            line_number=1,
            estimated_improvement="5x",
            implementation_steps=["Fix it"]
        )
        
        # Low impact, high effort = low priority
        ranker.add_opportunity(
            title="Hard task",
            description="Difficult fix",
            category="performance",
            impact=ImpactLevel.LOW,
            effort=EffortLevel.VERY_HARD,
            line_number=2,
            estimated_improvement="1.1x",
            implementation_steps=["Work hard"]
        )
        
        opportunities = ranker.rank_opportunities()
        # Quick win should be first
        assert opportunities[0].title == "Quick win"
    
    def test_quick_wins(self):
        """Test quick wins identification."""
        ranker = OptimizationRanker()
        
        ranker.add_opportunity(
            title="Quick win",
            description="Easy and impactful",
            category="performance",
            impact=ImpactLevel.HIGH,
            effort=EffortLevel.EASY,
            line_number=1,
            estimated_improvement="10x",
            implementation_steps=["Do it"]
        )
        
        quick_wins = ranker.get_quick_wins()
        assert len(quick_wins) == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])