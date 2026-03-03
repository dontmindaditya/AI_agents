from typing import TypedDict, Annotated
import operator
from langgraph.graph import StateGraph, END
from schemas.state_schemas import FrontendAgentState
from subagents import (
    UIAnalyzerAgent,
    ComponentGeneratorAgent,
    StateManagerAgent,
    OptimizationAgent
)
from utils.output_formatter import print_info, print_success


class FrontendAgentGraph:
    """
    LangGraph workflow that orchestrates the frontend agent system.
    """
    
    def __init__(self):
        self.ui_analyzer = UIAnalyzerAgent()
        self.component_generator = ComponentGeneratorAgent()
        self.state_manager = StateManagerAgent()
        self.optimizer = OptimizationAgent()
        
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow"""
        
        # Create the graph
        workflow = StateGraph(FrontendAgentState)
        
        # Add nodes (agents)
        workflow.add_node("analyze_ui", self.ui_analyzer)
        workflow.add_node("generate_components", self.component_generator)
        workflow.add_node("add_state_management", self.state_manager)
        workflow.add_node("optimize_code", self.optimizer)
        
        # Define the workflow edges
        workflow.set_entry_point("analyze_ui")
        
        # Linear flow: analyze -> generate -> state -> optimize -> end
        workflow.add_edge("analyze_ui", "generate_components")
        workflow.add_edge("generate_components", "add_state_management")
        workflow.add_edge("add_state_management", "optimize_code")
        workflow.add_edge("optimize_code", END)
        
        return workflow.compile()
    
    def run(self, user_input: str, framework: str = "react") -> FrontendAgentState:
        """
        Run the frontend agent workflow.
        
        Args:
            user_input: User's description of the frontend they want
            framework: Target framework (react, vue, vanilla)
            
        Returns:
            Final state with generated code
        """
        print_info(f"Starting Frontend Agent Workflow...")
        print_info(f"Framework: {framework}")
        print_info(f"User Input: {user_input}\n")
        
        # Initialize state
        initial_state: FrontendAgentState = {
            "user_input": user_input,
            "framework": framework,
            "ui_analysis": None,
            "components": [],
            "ui_patterns": [],
            "generated_code": None,
            "component_structure": None,
            "state_pattern": None,
            "state_logic": None,
            "optimized_code": None,
            "optimization_notes": None,
            "is_valid": False,
            "validation_errors": [],
            "iteration_count": 0,
            "next_step": None,
            "is_complete": False,
            "messages": []
        }
        
        # Run the graph
        final_state = self.graph.invoke(initial_state)
        
        print_success("\n🎉 Frontend Agent Workflow Complete!")
        
        return final_state
    
    def get_graph_visualization(self) -> str:
        """Get a text visualization of the graph"""
        return """
Frontend Agent Graph:

    [Start]
       ↓
[UI Analyzer Agent]
       ↓
[Component Generator Agent]
       ↓
[State Manager Agent]
       ↓
[Optimization Agent]
       ↓
     [End]

Agent Responsibilities:
- UI Analyzer: Analyzes requirements, identifies components and patterns
- Component Generator: Creates actual component code
- State Manager: Adds state management logic
- Optimizer: Optimizes and validates the final code
        """


def create_frontend_graph() -> FrontendAgentGraph:
    """Factory function to create a new frontend agent graph"""
    return FrontendAgentGraph()