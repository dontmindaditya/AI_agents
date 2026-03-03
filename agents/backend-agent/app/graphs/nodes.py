"""
Reusable Graph Nodes
"""
from typing import Dict, Any, Callable
from app.graphs.state_manager import WorkflowState
from app.agents.api_agent import api_agent
from app.agents.database_agent import database_agent
from app.agents.validation_agent import validation_agent
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


class GraphNodes:
    """Collection of reusable graph nodes"""
    
    @staticmethod
    async def input_validation_node(state: WorkflowState) -> WorkflowState:
        """
        Validate input data
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated state
        """
        logger.info("Executing input validation node")
        
        try:
            input_data = state.get("input_data", {})
            
            # Use validation agent
            result = await validation_agent.execute(
                task=f"Validate this input data: {input_data}",
                context={"input_data": input_data}
            )
            
            # Update state
            state["intermediate_results"]["input_validation"] = result
            state["completed_steps"].append("input_validation")
            
            if not result.get("success"):
                state["errors"].append("Input validation failed")
                logger.warning("Input validation failed")
        except Exception as e:
            error_msg = f"Input validation node error: {str(e)}"
            logger.error(error_msg)
            state["errors"].append(error_msg)
        
        return state
    
    @staticmethod
    async def api_call_node(state: WorkflowState) -> WorkflowState:
        """
        Make API call
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated state
        """
        logger.info("Executing API call node")
        
        try:
            input_data = state.get("input_data", {})
            api_config = input_data.get("api_config", {})
            
            task = api_config.get("task", "Make API request")
            
            # Use API agent
            result = await api_agent.execute(
                task=task,
                context=api_config
            )
            
            # Update state
            state["intermediate_results"]["api_response"] = result
            state["completed_steps"].append("api_call")
            
            if not result.get("success"):
                state["errors"].append("API call failed")
                logger.warning("API call failed")
        except Exception as e:
            error_msg = f"API call node error: {str(e)}"
            logger.error(error_msg)
            state["errors"].append(error_msg)
        
        return state
    
    @staticmethod
    async def database_query_node(state: WorkflowState) -> WorkflowState:
        """
        Execute database query
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated state
        """
        logger.info("Executing database query node")
        
        try:
            input_data = state.get("input_data", {})
            db_config = input_data.get("db_config", {})
            
            task = db_config.get("task", "Query database")
            
            # Use database agent
            result = await database_agent.execute(
                task=task,
                context=db_config
            )
            
            # Update state
            state["intermediate_results"]["database_result"] = result
            state["completed_steps"].append("database_query")
            
            if not result.get("success"):
                state["errors"].append("Database query failed")
                logger.warning("Database query failed")
        except Exception as e:
            error_msg = f"Database query node error: {str(e)}"
            logger.error(error_msg)
            state["errors"].append(error_msg)
        
        return state
    
    @staticmethod
    async def data_transformation_node(state: WorkflowState) -> WorkflowState:
        """
        Transform data
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated state
        """
        logger.info("Executing data transformation node")
        
        try:
            intermediate_results = state.get("intermediate_results", {})
            
            # Use validation agent for transformation
            result = await validation_agent.execute(
                task="Transform and format the data appropriately",
                context={"data": intermediate_results}
            )
            
            # Update state
            state["intermediate_results"]["transformed_data"] = result
            state["completed_steps"].append("data_transformation")
            
            if not result.get("success"):
                state["errors"].append("Data transformation failed")
                logger.warning("Data transformation failed")
        except Exception as e:
            error_msg = f"Data transformation node error: {str(e)}"
            logger.error(error_msg)
            state["errors"].append(error_msg)
        
        return state
    
    @staticmethod
    async def error_handling_node(state: WorkflowState) -> WorkflowState:
        """
        Handle errors
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated state
        """
        logger.info("Executing error handling node")
        
        try:
            errors = state.get("errors", [])
            
            if errors:
                error_summary = {
                    "error_count": len(errors),
                    "errors": errors,
                    "recommendation": "Review errors and retry with corrected input"
                }
                
                state["final_output"] = {
                    "success": False,
                    "error_summary": error_summary
                }
                logger.warning(f"Workflow completed with {len(errors)} errors")
            else:
                logger.info("No errors found")
            
            state["completed_steps"].append("error_handling")
        except Exception as e:
            error_msg = f"Error handling node error: {str(e)}"
            logger.error(error_msg)
            state["errors"].append(error_msg)
        
        return state
    
    @staticmethod
    async def output_formatting_node(state: WorkflowState) -> WorkflowState:
        """
        Format final output
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated state
        """
        logger.info("Executing output formatting node")
        
        try:
            intermediate_results = state.get("intermediate_results", {})
            errors = state.get("errors", [])
            
            # Create formatted output
            output = {
                "success": len(errors) == 0,
                "workflow_id": state.get("workflow_id"),
                "steps_completed": state.get("completed_steps", []),
                "results": intermediate_results,
                "errors": errors if errors else None
            }
            
            state["final_output"] = output
            state["completed_steps"].append("output_formatting")
            
            logger.info("Output formatted successfully")
        except Exception as e:
            error_msg = f"Output formatting node error: {str(e)}"
            logger.error(error_msg)
            state["errors"].append(error_msg)
        
        return state
    
    @staticmethod
    async def logging_node(state: WorkflowState) -> WorkflowState:
        """
        Log workflow progress
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated state
        """
        logger.info("Executing logging node")
        
        try:
            workflow_id = state.get("workflow_id")
            current_step = state.get("current_step")
            completed_steps = state.get("completed_steps", [])
            errors = state.get("errors", [])
            
            log_entry = {
                "workflow_id": workflow_id,
                "current_step": current_step,
                "steps_completed": len(completed_steps),
                "error_count": len(errors),
                "timestamp": state.get("metadata", {}).get("updated_at")
            }
            
            logger.info(f"Workflow progress: {log_entry}")
            
            state["completed_steps"].append("logging")
        except Exception as e:
            logger.error(f"Logging node error: {str(e)}")
        
        return state
    
    @staticmethod
    def create_custom_node(
        name: str,
        handler: Callable[[WorkflowState], WorkflowState]
    ) -> Callable[[WorkflowState], WorkflowState]:
        """
        Create a custom node with a handler function
        
        Args:
            name: Node name
            handler: Handler function
            
        Returns:
            Node function
        """
        async def custom_node(state: WorkflowState) -> WorkflowState:
            logger.info(f"Executing custom node: {name}")
            
            try:
                result = await handler(state)
                result["completed_steps"].append(name)
                return result
            except Exception as e:
                error_msg = f"Custom node {name} error: {str(e)}"
                logger.error(error_msg)
                state["errors"].append(error_msg)
                return state
        
        return custom_node


# Export node functions
nodes = GraphNodes()