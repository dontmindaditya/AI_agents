"""Performance metrics calculation utilities."""

import time
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional
import psutil
import tracemalloc


@dataclass
class ExecutionMetrics:
    """Metrics from code execution."""
    execution_time: float
    memory_used_mb: float
    peak_memory_mb: float
    cpu_percent: float
    success: bool
    error: Optional[str] = None


@dataclass
class ComplexityMetrics:
    """Code complexity metrics."""
    cyclomatic_complexity: int
    cognitive_complexity: int
    lines_of_code: int
    maintainability_index: float
    halstead_metrics: Dict[str, float]


class MetricsCalculator:
    """Calculate various performance and complexity metrics."""
    
    @staticmethod
    def measure_execution(
        func: Callable,
        *args,
        **kwargs
    ) -> ExecutionMetrics:
        """
        Measure execution time and memory usage.
        
        Args:
            func: Function to measure
            *args: Function arguments
            **kwargs: Function keyword arguments
            
        Returns:
            Execution metrics
        """
        # Start memory tracking
        tracemalloc.start()
        process = psutil.Process()
        
        # Get initial CPU usage
        process.cpu_percent()
        
        # Record start time
        start_time = time.perf_counter()
        
        success = True
        error = None
        
        try:
            # Execute function
            result = func(*args, **kwargs)
        except Exception as e:
            success = False
            error = str(e)
        
        # Record end time
        end_time = time.perf_counter()
        
        # Get memory usage
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        # Get CPU usage
        cpu_percent = process.cpu_percent()
        
        return ExecutionMetrics(
            execution_time=end_time - start_time,
            memory_used_mb=current / 1024 / 1024,
            peak_memory_mb=peak / 1024 / 1024,
            cpu_percent=cpu_percent,
            success=success,
            error=error
        )
    
    @staticmethod
    def calculate_time_complexity(
        measurements: List[tuple[int, float]]
    ) -> str:
        """
        Estimate time complexity from measurements.
        
        Args:
            measurements: List of (input_size, execution_time) tuples
            
        Returns:
            Estimated complexity (O(1), O(n), O(n^2), etc.)
        """
        if len(measurements) < 2:
            return "O(1)"
        
        # Sort by input size
        measurements = sorted(measurements)
        
        # Calculate ratios
        ratios = []
        for i in range(1, len(measurements)):
            n1, t1 = measurements[i-1]
            n2, t2 = measurements[i]
            
            if t1 > 0:
                time_ratio = t2 / t1
                size_ratio = n2 / n1
                ratios.append((size_ratio, time_ratio))
        
        if not ratios:
            return "O(1)"
        
        # Average time ratio relative to size ratio
        avg_ratio = sum(tr / sr for sr, tr in ratios) / len(ratios)
        
        # Classify complexity
        if avg_ratio < 1.2:
            return "O(1)"
        elif avg_ratio < 1.8:
            return "O(log n)"
        elif avg_ratio < 2.5:
            return "O(n)"
        elif avg_ratio < 4.0:
            return "O(n log n)"
        elif avg_ratio < 8.0:
            return "O(n^2)"
        else:
            return "O(2^n) or worse"
    
    @staticmethod
    def calculate_maintainability_index(
        lines_of_code: int,
        cyclomatic_complexity: int,
        halstead_volume: float
    ) -> float:
        """
        Calculate maintainability index.
        
        Formula: MI = 171 - 5.2 * ln(V) - 0.23 * G - 16.2 * ln(LOC)
        Where:
            V = Halstead Volume
            G = Cyclomatic Complexity
            LOC = Lines of Code
        
        Args:
            lines_of_code: Total lines of code
            cyclomatic_complexity: Cyclomatic complexity
            halstead_volume: Halstead volume metric
            
        Returns:
            Maintainability index (0-100)
        """
        import math
        
        if lines_of_code == 0 or halstead_volume == 0:
            return 100.0
        
        mi = (
            171
            - 5.2 * math.log(halstead_volume)
            - 0.23 * cyclomatic_complexity
            - 16.2 * math.log(lines_of_code)
        )
        
        # Normalize to 0-100 scale
        mi = max(0, min(100, mi * 100 / 171))
        
        return round(mi, 2)
    
    @staticmethod
    def calculate_halstead_metrics(
        operators: List[str],
        operands: List[str]
    ) -> Dict[str, float]:
        """
        Calculate Halstead complexity metrics.
        
        Args:
            operators: List of operators in code
            operands: List of operands in code
            
        Returns:
            Dictionary of Halstead metrics
        """
        import math
        
        n1 = len(set(operators))  # Unique operators
        n2 = len(set(operands))   # Unique operands
        N1 = len(operators)       # Total operators
        N2 = len(operands)        # Total operands
        
        if n1 == 0 or n2 == 0:
            return {
                "vocabulary": 0,
                "length": 0,
                "volume": 0,
                "difficulty": 0,
                "effort": 0,
                "time": 0,
                "bugs": 0
            }
        
        vocabulary = n1 + n2
        length = N1 + N2
        volume = length * math.log2(vocabulary) if vocabulary > 0 else 0
        difficulty = (n1 / 2) * (N2 / n2)
        effort = difficulty * volume
        time_seconds = effort / 18  # Stroud number
        bugs = volume / 3000
        
        return {
            "vocabulary": vocabulary,
            "length": length,
            "volume": round(volume, 2),
            "difficulty": round(difficulty, 2),
            "effort": round(effort, 2),
            "time": round(time_seconds, 2),
            "bugs": round(bugs, 4)
        }
    
    @staticmethod
    def compare_performance(
        baseline: ExecutionMetrics,
        optimized: ExecutionMetrics
    ) -> Dict[str, Any]:
        """
        Compare baseline vs optimized performance.
        
        Args:
            baseline: Baseline execution metrics
            optimized: Optimized execution metrics
            
        Returns:
            Performance comparison
        """
        if baseline.execution_time == 0:
            time_improvement = 0
        else:
            time_improvement = (
                (baseline.execution_time - optimized.execution_time)
                / baseline.execution_time
                * 100
            )
        
        if baseline.memory_used_mb == 0:
            memory_improvement = 0
        else:
            memory_improvement = (
                (baseline.memory_used_mb - optimized.memory_used_mb)
                / baseline.memory_used_mb
                * 100
            )
        
        return {
            "time_improvement_percent": round(time_improvement, 2),
            "memory_improvement_percent": round(memory_improvement, 2),
            "speedup_factor": round(
                baseline.execution_time / optimized.execution_time
                if optimized.execution_time > 0 else 0,
                2
            ),
            "is_faster": optimized.execution_time < baseline.execution_time,
            "is_memory_efficient": optimized.memory_used_mb < baseline.memory_used_mb
        }
    
    @staticmethod
    def calculate_big_o_score(complexity: str) -> int:
        """
        Convert Big-O notation to numeric score for ranking.
        
        Args:
            complexity: Big-O notation string
            
        Returns:
            Numeric score (lower is better)
        """
        complexity_scores = {
            "O(1)": 1,
            "O(log n)": 2,
            "O(n)": 3,
            "O(n log n)": 4,
            "O(n^2)": 5,
            "O(n^3)": 6,
            "O(2^n)": 7,
            "O(n!)": 8
        }
        
        for key, score in complexity_scores.items():
            if key in complexity:
                return score
        
        return 5  # Default to moderate complexity