"""Wrapper for memory profiling tools."""

import tracemalloc
import gc
from typing import Dict, Any, List

from tools.code_executor import CodeExecutor
from utils.logger import get_logger

logger = get_logger(__name__)


class MemoryProfilerWrapper:
    """Wrapper for memory profiling."""
    
    def __init__(self):
        """Initialize memory profiler wrapper."""
        self.executor = CodeExecutor()
    
    def profile(self, code: str) -> Dict[str, Any]:
        """
        Profile memory usage of code.
        
        Args:
            code: Python code to profile
            
        Returns:
            Memory profiling results
        """
        logger.info("Starting memory profiling")
        
        if not self.executor.is_safe(code):
            return {
                "error": "Code unsafe for profiling",
                "peak_memory_mb": 0
            }
        
        try:
            # Start memory tracking
            tracemalloc.start()
            gc.collect()  # Clean up before profiling
            
            # Get baseline
            baseline_snapshot = tracemalloc.take_snapshot()
            baseline_current, baseline_peak = tracemalloc.get_traced_memory()
            
            # Execute code
            globals_dict = {}
            try:
                exec(code, globals_dict)
            except Exception as e:
                logger.error(f"Execution error during profiling: {str(e)}")
                tracemalloc.stop()
                return {
                    "error": str(e),
                    "peak_memory_mb": 0
                }
            
            # Get memory usage after execution
            current_memory, peak_memory = tracemalloc.get_traced_memory()
            final_snapshot = tracemalloc.take_snapshot()
            
            # Stop tracking
            tracemalloc.stop()
            
            # Calculate memory increase
            memory_increase = current_memory - baseline_current
            peak_increase = peak_memory - baseline_peak
            
            # Get top memory allocations
            top_stats = self._get_top_allocations(final_snapshot)
            
            return {
                "current_memory_mb": round(current_memory / 1024 / 1024, 2),
                "peak_memory_mb": round(peak_memory / 1024 / 1024, 2),
                "memory_increase_mb": round(memory_increase / 1024 / 1024, 2),
                "peak_increase_mb": round(peak_increase / 1024 / 1024, 2),
                "top_allocations": top_stats,
                "baseline_mb": round(baseline_current / 1024 / 1024, 2)
            }
            
        except Exception as e:
            logger.error(f"Memory profiling failed: {str(e)}")
            if tracemalloc.is_tracing():
                tracemalloc.stop()
            return {
                "error": str(e),
                "peak_memory_mb": 0
            }
    
    def profile_function(
        self,
        code: str,
        function_name: str,
        *args,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Profile memory usage of a specific function.
        
        Args:
            code: Python code containing function
            function_name: Name of function to profile
            *args: Function arguments
            **kwargs: Function keyword arguments
            
        Returns:
            Memory profiling results
        """
        logger.info(f"Profiling memory for function: {function_name}")
        
        try:
            # Prepare code with function call
            full_code = f"{code}\n\n{function_name}(*{args}, **{kwargs})"
            
            return self.profile(full_code)
            
        except Exception as e:
            logger.error(f"Function memory profiling failed: {str(e)}")
            return {
                "error": str(e),
                "peak_memory_mb": 0
            }
    
    def compare_memory(
        self,
        code1: str,
        code2: str
    ) -> Dict[str, Any]:
        """
        Compare memory usage of two code versions.
        
        Args:
            code1: First code version
            code2: Second code version
            
        Returns:
            Memory comparison results
        """
        logger.info("Comparing memory usage")
        
        try:
            profile1 = self.profile(code1)
            profile2 = self.profile(code2)
            
            if "error" in profile1 or "error" in profile2:
                return {
                    "error": "Memory profiling failed",
                    "code1": profile1,
                    "code2": profile2
                }
            
            memory_diff = profile2["peak_memory_mb"] - profile1["peak_memory_mb"]
            improvement_percent = 0
            
            if profile1["peak_memory_mb"] > 0:
                improvement_percent = (memory_diff / profile1["peak_memory_mb"]) * 100
            
            return {
                "code1_peak_mb": profile1["peak_memory_mb"],
                "code2_peak_mb": profile2["peak_memory_mb"],
                "memory_difference_mb": round(memory_diff, 2),
                "code2_uses_less": memory_diff < 0,
                "improvement_percent": round(improvement_percent, 2),
                "details": {
                    "code1": profile1,
                    "code2": profile2
                }
            }
            
        except Exception as e:
            logger.error(f"Memory comparison failed: {str(e)}")
            return {
                "error": str(e)
            }
    
    def detect_memory_leaks(self, code: str, iterations: int = 10) -> Dict[str, Any]:
        """
        Detect potential memory leaks by running code multiple times.
        
        Args:
            code: Python code to test
            iterations: Number of iterations
            
        Returns:
            Memory leak detection results
        """
        logger.info(f"Detecting memory leaks ({iterations} iterations)")
        
        if not self.executor.is_safe(code):
            return {
                "error": "Code unsafe for leak detection",
                "leak_detected": False
            }
        
        try:
            memory_samples = []
            
            tracemalloc.start()
            
            for i in range(iterations):
                gc.collect()
                
                # Execute code
                self.executor.execute(code)
                
                # Sample memory
                current, peak = tracemalloc.get_traced_memory()
                memory_samples.append(current / 1024 / 1024)  # MB
            
            tracemalloc.stop()
            
            # Analyze trend
            first_half = sum(memory_samples[:len(memory_samples)//2]) / (len(memory_samples)//2)
            second_half = sum(memory_samples[len(memory_samples)//2:]) / (len(memory_samples)//2)
            
            increase = second_half - first_half
            leak_detected = increase > 1.0  # More than 1MB increase
            
            return {
                "leak_detected": leak_detected,
                "memory_increase_mb": round(increase, 2),
                "memory_samples": [round(m, 2) for m in memory_samples],
                "first_half_avg": round(first_half, 2),
                "second_half_avg": round(second_half, 2),
                "iterations": iterations
            }
            
        except Exception as e:
            logger.error(f"Memory leak detection failed: {str(e)}")
            if tracemalloc.is_tracing():
                tracemalloc.stop()
            return {
                "error": str(e),
                "leak_detected": False
            }
    
    def _get_top_allocations(
        self,
        snapshot: tracemalloc.Snapshot,
        limit: int = 10
    ) -> List[Dict]:
        """Get top memory allocations from snapshot."""
        try:
            top_stats = snapshot.statistics('lineno')
            
            allocations = []
            for stat in top_stats[:limit]:
                allocations.append({
                    "filename": stat.traceback.format()[0] if stat.traceback else "unknown",
                    "size_mb": round(stat.size / 1024 / 1024, 4),
                    "count": stat.count
                })
            
            return allocations
            
        except Exception as e:
            logger.error(f"Error getting allocations: {str(e)}")
            return []