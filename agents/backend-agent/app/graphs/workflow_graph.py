"""
Workflow Graph - LangGraph Implementation
"""
from typing import Dict, Any, List, Optional, Literal
from typing_extensions import TypedDict
from langgraph.graph import Graph, StateGraph, END

from app.agents.api_agent import api_agent
from app.agents.database_agent import database_agent
from app.agents.validation_agent import validation_agent
from app.graphs.state_manager import WorkflowState, state_manager
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


class WorkflowGraph:
    """LangGraph workflow for multi-agent coordination"""
    
    def __init__(self):
        self.graph = self._create_graph()
    
    def _create_graph(self) -> StateGraph:
        """Create workflow graph"""
        # Define the graph
        workflow = StateGraph(WorkflowState)
        
        # Add nodes
        workflow.add_node("validate_input", self._validate_input_node)
        workflow.add_node("process_api", self._process_api_node)
        workflow.add_node("process_database", self._process_database_node)
        workflow.add_node("format_output", self._format_output_node)
        
        # Add edges
        workflow.set_entry_point("validate_input")
        workflow.add_edge("validate_input", "process_api")
        workflow.add_edge("process_api", "process_database")
        workflow.add_edge("process_database", "format_output")
        workflow.add_edge("format_output", END)
        
        return workflow.compile()
    
    async def _validate_input_node(self, state: WorkflowState) -> WorkflowState:
        """Validate input node"""
        logger.info("Executing validate_input node")
        
        try:
            # Use validation agent
            result = await validation_agent.execute(
                task="Validate the input data structure and format",
                context=state.get("input_data")
            )
            
            # Update state
            state["current_step"] = "validate_input"
            state["completed_steps"].append("validate_input")
            state["intermediate_results"]["validation"] = result
            
            if not result.get("success"):
                state["errors"].append("Input validation failed")
        except Exception as e:
            logger.error(f"Validation node failed: {e}")
            state["errors"].append(str(e))
        
        return state
    
    async def _process_api_node(self, state: WorkflowState) -> WorkflowState:
        """Process API node"""
        logger.info("Executing process_api node")
        
        try:
            # Use API agent
            api_task = state.get("input_data", {}).get("api_task", "Fetch data from API")
            result = await api_agent.execute(
                task=api_task,
                context=state.get("intermediate_results", {})
            )
            
            # Update state
            state["current_step"] = "process_api"
            state["completed_steps"].append("process_api")
            state["intermediate_results"]["api_result"] = result
            
            if not result.get("success"):
                state["errors"].append("API processing failed")
        except Exception as e:
            logger.error(f"API node failed: {e}")
            state["errors"].append(str(e))
        
        return state
    
    async def _process_database_node(self, state: WorkflowState) -> WorkflowState:
        """Process database node"""
        logger.info("Executing process_database node")
        
        try:
            # Use database agent
            db_task = state.get("input_data", {}).get("db_task", "Store data in database")
            result = await database_agent.execute(
                task=db_task,
                context=state.get("intermediate_results", {})
            )
            
            # Update state
            state["current_step"] = "process_database"
            state["completed_steps"].append("process_database")
            state["intermediate_results"]["database_result"] = result
            
            if not result.get("success"):
                state["errors"].append("Database processing failed")
        except Exception as e:
            logger.error(f"Database node failed: {e}")
            state["errors"].append(str(e))
        
        return state
    
    async def _format_output_node(self, state: WorkflowState) -> WorkflowState:
        """Format output node"""
        logger.info("Executing format_output node")
        
        try:
            # Use validation agent for formatting
            result = await validation_agent.execute(
                task="Format the processed results into a clear output",
                context=state.get("intermediate_results", {})
            )
            
            # Update state
            state["current_step"] = "format_output"
            state["completed_steps"].append("format_output")
            state["final_output"] = result
        except Exception as e:
            logger.error(f"Format output node failed: {e}")
            state["errors"].append(str(e))
        
        return state
    
    async def execute(self, input_data: Dict[str, Any]) -> WorkflowState:
        """
        Execute workflow
        
        Args:
            input_data: Input data for workflow
            
        Returns:
            Final workflow state
        """
        try:
            # Create initial state
            initial_state = state_manager.create_state(input_data)
            
            logger.info(f"Starting workflow: {initial_state['workflow_id']}")
            
            # Execute graph
            final_state = await self.graph.ainvoke(initial_state)
            
            logger.info(f"Workflow completed: {initial_state['workflow_id']}")
            
            return final_state
        except Exception as e:
            logger.error(f"Workflow execution failed: {e}")
            raise


class ConditionalWorkflowGraph:
    """Workflow graph with conditional routing"""
    
    def __init__(self):
        self.graph = self._create_conditional_graph()
    
    def _create_conditional_graph(self) -> StateGraph:
        """Create conditional workflow graph"""
        workflow = StateGraph(WorkflowState)
        
        # Add nodes
        workflow.add_node("start", self._start_node)
        workflow.add_node("validate", self._validate_node)
        workflow.add_node("api_path", self._api_path_node)
        workflow.add_node("database_path", self._database_path_node)
        workflow.add_node("end", self._end_node)
        
        # Add conditional edges
        workflow.set_entry_point("start")
        workflow.add_edge("start", "validate")
        workflow.add_conditional_edges(
            "validate",
            self._route_decision,
            {
                "api": "api_path",
                "database": "database_path",
                "end": "end"
            }
        )
        workflow.add_edge("api_path", "end")
        workflow.add_edge("database_path", "end")
        workflow.add_edge("end", END)
        
        return workflow.compile()
    
    async def _start_node(self, state: WorkflowState) -> WorkflowState:
        """Start node"""
        logger.info("Workflow started")
        state["current_step"] = "start"
        state["completed_steps"].append("start")
        return state
    
    async def _validate_node(self, state: WorkflowState) -> WorkflowState:
        """Validation node"""
        logger.info("Validating input")
        result = await validation_agent.execute(
            "Validate input data",
            state.get("input_data")
        )
        state["current_step"] = "validate"
        state["completed_steps"].append("validate")
        state["intermediate_results"]["validation"] = result
        return state
    
    async def _api_path_node(self, state: WorkflowState) -> WorkflowState:
        """API path node"""
        logger.info("Taking API path")
        result = await api_agent.execute(
            "Execute API operation",
            state.get("input_data")
        )
        state["current_step"] = "api_path"
        state["completed_steps"].append("api_path")
        state["intermediate_results"]["api_result"] = result
        return state
    
    async def _database_path_node(self, state: WorkflowState) -> WorkflowState:
        """Database path node"""
        logger.info("Taking database path")
        result = await database_agent.execute(
            "Execute database operation",
            state.get("input_data")
        )
        state["current_step"] = "database_path"
        state["completed_steps"].append("database_path")
        state["intermediate_results"]["database_result"] = result
        return state
    
    async def _end_node(self, state: WorkflowState) -> WorkflowState:
        """End node"""
        logger.info("Workflow ending")
        state["current_step"] = "end"
        state["completed_steps"].append("end")
        state["final_output"] = state.get("intermediate_results", {})
        return state
    
    def _route_decision(self, state: WorkflowState) -> Literal["api", "database", "end"]:
        """
        Decide which path to take based on state
        
        Args:
            state: Current workflow state
            
        Returns:
            Next node to execute
        """
        # Check for errors
        if state.get("errors"):
            return "end"
        
        # Check input data for routing hints
        input_data = state.get("input_data", {})
        
        if "api" in str(input_data).lower():
            return "api"
        elif "database" in str(input_data).lower() or "db" in str(input_data).lower():
            return "database"
        else:
            return "end"
    
    async def execute(self, input_data: Dict[str, Any]) -> WorkflowState:
        """
        Execute conditional workflow
        
        Args:
            input_data: Input data
            
        Returns:
            Final state
        """
        try:
            initial_state = state_manager.create_state(input_data)
            logger.info(f"Starting conditional workflow: {initial_state['workflow_id']}")
            
            final_state = await self.graph.ainvoke(initial_state)
            
            logger.info(f"Conditional workflow completed: {initial_state['workflow_id']}")
            return final_state
        except Exception as e:
            logger.error(f"Conditional workflow failed: {e}")
            raise


# Global instances
workflow_graph = WorkflowGraph()
conditional_workflow_graph = ConditionalWorkflowGraph()