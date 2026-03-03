"""State management for debug optimization workflow."""

from typing import TypedDict, List, Dict, Any, Optional
from typing_extensions import Annotated
import operator


class DebugState(TypedDict):
    """State for debug optimization workflow."""
    
    # Input
    code: str
    run_profiling: bool
    
    # Analysis results
    code_analysis: Optional[Dict[str, Any]]
    performance_analysis: Optional[Dict[str, Any]]
    memory_analysis: Optional[Dict[str, Any]]
    
    # Optimization results
    optimization_suggestions: Optional[Dict[str, Any]]
    
    # Validation results
    validation_results: Optional[List[Dict[str, Any]]]
    
    # Accumulated messages (for agent communication)
    messages: Annotated[List[str], operator.add]
    
    # Errors
    errors: Annotated[List[str], operator.add]
    
    # Final results
    final_report: Optional[Dict[str, Any]]
    
    # Control flow
    current_step: str
    completed_steps: Annotated[List[str], operator.add]


def create_initial_state(code: str, run_profiling: bool = True) -> DebugState:
    """
    Create initial state for workflow.
    
    Args:
        code: Python code to analyze
        run_profiling: Whether to run profiling
        
    Returns:
        Initial workflow state
    """
    return DebugState(
        code=code,
        run_profiling=run_profiling,
        code_analysis=None,
        performance_analysis=None,
        memory_analysis=None,
        optimization_suggestions=None,
        validation_results=None,
        messages=[],
        errors=[],
        final_report=None,
        current_step="start",
        completed_steps=[]
    )