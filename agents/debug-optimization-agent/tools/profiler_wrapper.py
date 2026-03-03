"""Wrapper for CPU profiling tools."""

import cProfile
import pstats
import io
from typing import Dict, Any, List
import time

from tools.code_executor import CodeExecutor
from utils.logger import get_logger

logger = get_logger(__name__)


class ProfilerWrapper:
    """Wrapper for cProfile and performance profiling."""
    
    def __init__(self):
        """Initialize profiler wrapper."""
        self.executor = CodeExecutor()
    
    def profile_cpu(self, code: str) -> Dict[str, Any]:
        """
        Profile CPU usage of code.
        
        Args:
            code: Python code to profile
            
        Returns:
            Profiling results
        """
        logger.info("Starting CPU profiling")
        
        if not self.executor.is_safe(code):
            return {
                "error": "Code unsafe for profiling",
                "stats": []
            }
        
        try:
            # Create profiler
            profiler = cProfile.Profile()
            
            # Profile code execution
            globals_dict = {}
            profiler.enable()
            
            try:
                exec(code, globals_dict)
            except Exception as e:
                logger.error(f"Execution error during profiling: {str(e)}")
                return {
                    "error": str(e),
                    "stats": []
                }
            finally:
                profiler.disable()
            
            # Get statistics
            stats = self._format_stats(profiler)
            
            return {
                "stats": stats,
                "total_calls": stats[0]["ncalls"] if stats else 0,
                "total_time": stats[0]["tottime"] if stats else 0
            }
            
        except Exception as e:
            logger.error(f"Profiling failed: {str(e)}")
            return {
                "error": str(e),
                "stats": []
            }
    
    def profile_function(
        self,
        code: str,
        function_name: str,
        *args,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Profile a specific function.
        
        Args:
            code: Python code containing function
            function_name: Name of function to profile
            *args: Function arguments
            **kwargs: Function keyword arguments
            
        Returns:
            Profiling results
        """
        logger.info(f"Profiling function: {function_name}")
        
        try:
            # Prepare code with function call
            full_code = f"{code}\n\n{function_name}(*{args}, **{kwargs})"
            
            return self.profile_cpu(full_code)
            
        except Exception as e:
            logger.error(f"Function profiling failed: {str(e)}")
            return {
                "error": str(e),
                "stats": []
            }
    
    def profile_lines(self, code: str) -> Dict[str, Any]:
        """
        Profile code line by line.
        
        Note: This is a simplified version. For full line profiling,
        use line_profiler package separately.
        
        Args:
            code: Python code to profile
            
        Returns:
            Line profiling results
        """
        logger.info("Line profiling (simplified)")
        
        # This is a placeholder - full line profiling requires
        # line_profiler package and decorated functions
        
        lines = code.split('\n')
        line_stats = []
        
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            if stripped and not stripped.startswith('#'):
                line_stats.append({
                    "line_number": i,
                    "code": line,
                    "note": "Full line profiling requires line_profiler package"
                })
        
        return {
            "lines": line_stats,
            "note": "This is simplified line profiling. Use line_profiler for detailed results."
        }
    
    def benchmark(
        self,
        code: str,
        iterations: int = 100
    ) -> Dict[str, Any]:
        """
        Benchmark code execution.
        
        Args:
            code: Python code to benchmark
            iterations: Number of iterations
            
        Returns:
            Benchmark results
        """
        logger.info(f"Benchmarking code ({iterations} iterations)")
        
        if not self.executor.is_safe(code):
            return {
                "error": "Code unsafe for benchmarking",
                "times": []
            }
        
        times = []
        
        try:
            for _ in range(iterations):
                start = time.perf_counter()
                self.executor.execute(code)
                end = time.perf_counter()
                times.append(end - start)
            
            avg_time = sum(times) / len(times)
            min_time = min(times)
            max_time = max(times)
            
            return {
                "iterations": iterations,
                "average_time": avg_time,
                "min_time": min_time,
                "max_time": max_time,
                "total_time": sum(times),
                "times": times
            }
            
        except Exception as e:
            logger.error(f"Benchmarking failed: {str(e)}")
            return {
                "error": str(e),
                "times": []
            }
    
    def compare_performance(
        self,
        code1: str,
        code2: str,
        iterations: int = 100
    ) -> Dict[str, Any]:
        """
        Compare performance of two code versions.
        
        Args:
            code1: First code version
            code2: Second code version
            iterations: Number of iterations
            
        Returns:
            Comparison results
        """
        logger.info("Comparing code performance")
        
        try:
            bench1 = self.benchmark(code1, iterations)
            bench2 = self.benchmark(code2, iterations)
            
            if "error" in bench1 or "error" in bench2:
                return {
                    "error": "Benchmarking failed",
                    "code1": bench1,
                    "code2": bench2
                }
            
            speedup = bench1["average_time"] / bench2["average_time"] if bench2["average_time"] > 0 else 0
            
            return {
                "code1": bench1,
                "code2": bench2,
                "speedup_factor": round(speedup, 2),
                "code2_is_faster": bench2["average_time"] < bench1["average_time"],
                "time_difference": bench1["average_time"] - bench2["average_time"],
                "improvement_percent": round(
                    ((bench1["average_time"] - bench2["average_time"]) / bench1["average_time"] * 100),
                    2
                ) if bench1["average_time"] > 0 else 0
            }
            
        except Exception as e:
            logger.error(f"Performance comparison failed: {str(e)}")
            return {
                "error": str(e)
            }
    
    def _format_stats(self, profiler: cProfile.Profile) -> List[Dict]:
        """Format profiler statistics."""
        try:
            # Get stats
            string_io = io.StringIO()
            stats = pstats.Stats(profiler, stream=string_io)
            stats.sort_stats('cumulative')
            
            # Parse stats
            formatted_stats = []
            
            for func, (cc, nc, tt, ct, callers) in stats.stats.items():
                filename, line, func_name = func
                
                formatted_stats.append({
                    "function": func_name,
                    "filename": filename,
                    "line": line,
                    "ncalls": nc,
                    "tottime": round(tt, 6),
                    "cumtime": round(ct, 6),
                    "percall_tot": round(tt / nc, 6) if nc > 0 else 0,
                    "percall_cum": round(ct / nc, 6) if nc > 0 else 0
                })
            
            # Sort by cumulative time
            formatted_stats.sort(key=lambda x: x["cumtime"], reverse=True)
            
            return formatted_stats[:20]  # Top 20 functions
            
        except Exception as e:
            logger.error(f"Error formatting stats: {str(e)}")
            return []