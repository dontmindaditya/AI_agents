"""
State Manager for LangGraph Workflows
"""
from typing import Any, Dict, List, Optional, TypedDict
from datetime import datetime

from app.utils.logger import setup_logger
from app.utils.helpers import generate_task_id

logger = setup_logger(__name__)


class WorkflowState(TypedDict):
    """State structure for workflows"""
    workflow_id: str
    current_step: str
    completed_steps: List[str]
    input_data: Dict[str, Any]
    intermediate_results: Dict[str, Any]
    final_output: Optional[Dict[str, Any]]
    errors: List[str]
    metadata: Dict[str, Any]


class StateManager:
    """Manage workflow state"""
    
    def __init__(self):
        self._states: Dict[str, WorkflowState] = {}
    
    def create_state(
        self,
        input_data: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ) -> WorkflowState:
        """
        Create a new workflow state
        
        Args:
            input_data: Initial input data
            metadata: Optional metadata
            
        Returns:
            New workflow state
        """
        workflow_id = generate_task_id()
        
        state: WorkflowState = {
            "workflow_id": workflow_id,
            "current_step": "start",
            "completed_steps": [],
            "input_data": input_data,
            "intermediate_results": {},
            "final_output": None,
            "errors": [],
            "metadata": metadata or {
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
        }
        
        self._states[workflow_id] = state
        logger.info(f"Created workflow state: {workflow_id}")
        
        return state
    
    def get_state(self, workflow_id: str) -> Optional[WorkflowState]:
        """Get workflow state by ID"""
        return self._states.get(workflow_id)
    
    def update_state(
        self,
        workflow_id: str,
        updates: Dict[str, Any]
    ) -> Optional[WorkflowState]:
        """
        Update workflow state
        
        Args:
            workflow_id: Workflow ID
            updates: State updates
            
        Returns:
            Updated state or None if not found
        """
        state = self._states.get(workflow_id)
        if not state:
            logger.warning(f"Workflow state not found: {workflow_id}")
            return None
        
        # Update state
        state.update(updates)
        state["metadata"]["updated_at"] = datetime.utcnow().isoformat()
        
        logger.info(f"Updated workflow state: {workflow_id}")
        return state
    
    def add_step_result(
        self,
        workflow_id: str,
        step_name: str,
        result: Any
    ) -> Optional[WorkflowState]:
        """
        Add result for a completed step
        
        Args:
            workflow_id: Workflow ID
            step_name: Name of completed step
            result: Step result
            
        Returns:
            Updated state or None if not found
        """
        state = self._states.get(workflow_id)
        if not state:
            return None
        
        # Add step to completed steps
        if step_name not in state["completed_steps"]:
            state["completed_steps"].append(step_name)
        
        # Store intermediate result
        state["intermediate_results"][step_name] = result
        
        # Update metadata
        state["metadata"]["updated_at"] = datetime.utcnow().isoformat()
        
        logger.info(f"Added result for step '{step_name}' in workflow {workflow_id}")
        return state
    
    def add_error(
        self,
        workflow_id: str,
        error: str
    ) -> Optional[WorkflowState]:
        """
        Add error to workflow state
        
        Args:
            workflow_id: Workflow ID
            error: Error message
            
        Returns:
            Updated state or None if not found
        """
        state = self._states.get(workflow_id)
        if not state:
            return None
        
        state["errors"].append(error)
        state["metadata"]["updated_at"] = datetime.utcnow().isoformat()
        
        logger.warning(f"Added error to workflow {workflow_id}: {error}")
        return state
    
    def set_final_output(
        self,
        workflow_id: str,
        output: Dict[str, Any]
    ) -> Optional[WorkflowState]:
        """
        Set final workflow output
        
        Args:
            workflow_id: Workflow ID
            output: Final output data
            
        Returns:
            Updated state or None if not found
        """
        state = self._states.get(workflow_id)
        if not state:
            return None
        
        state["final_output"] = output
        state["current_step"] = "completed"
        state["metadata"]["updated_at"] = datetime.utcnow().isoformat()
        state["metadata"]["completed_at"] = datetime.utcnow().isoformat()
        
        logger.info(f"Set final output for workflow {workflow_id}")
        return state
    
    def delete_state(self, workflow_id: str) -> bool:
        """Delete workflow state"""
        if workflow_id in self._states:
            del self._states[workflow_id]
            logger.info(f"Deleted workflow state: {workflow_id}")
            return True
        return False
    
    def list_states(self) -> List[str]:
        """Get list of all workflow IDs"""
        return list(self._states.keys())
    
    def clear_completed_states(self) -> int:
        """
        Clear all completed workflow states
        
        Returns:
            Number of states cleared
        """
        completed = [
            wf_id for wf_id, state in self._states.items()
            if state["current_step"] == "completed"
        ]
        
        for wf_id in completed:
            del self._states[wf_id]
        
        logger.info(f"Cleared {len(completed)} completed workflow states")
        return len(completed)


# Global instance
state_manager = StateManager()