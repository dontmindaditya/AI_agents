from typing import TypedDict, List, Optional, Literal
from typing_extensions import Annotated
import operator


class FrontendAgentState(TypedDict):
    """
    State schema for the frontend agent workflow.
    
    This state is passed between all agents in the graph.
    """
    # Input
    user_input: str
    framework: Literal["react", "vue", "vanilla"]
    
    # UI Analysis
    ui_analysis: Optional[str]
    components: List[str]
    ui_patterns: List[str]
    
    # Component Generation
    generated_code: Optional[str]
    component_structure: Optional[str]
    
    # State Management
    state_pattern: Optional[str]
    state_logic: Optional[str]
    
    # Optimization
    optimized_code: Optional[str]
    optimization_notes: Optional[str]
    
    # Validation
    is_valid: bool
    validation_errors: List[str]
    
    # Workflow Control
    iteration_count: Annotated[int, operator.add]
    next_step: Optional[str]
    is_complete: bool
    
    # Messages for tracking
    messages: Annotated[List[str], operator.add]


class AnalyzerOutput(TypedDict):
    """Output schema for UI Analyzer Agent"""
    ui_analysis: str
    components: List[str]
    ui_patterns: List[str]
    framework: str


class GeneratorOutput(TypedDict):
    """Output schema for Component Generator Agent"""
    generated_code: str
    component_structure: str


class StateManagerOutput(TypedDict):
    """Output schema for State Manager Agent"""
    state_pattern: str
    state_logic: str
    enhanced_code: str


class OptimizerOutput(TypedDict):
    """Output schema for Optimization Agent"""
    optimized_code: str
    optimization_notes: str
    is_valid: bool
    validation_errors: List[str]