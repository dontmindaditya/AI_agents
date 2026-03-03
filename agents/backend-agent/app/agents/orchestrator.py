"""
Orchestrator Agent - Coordinates multiple agents
"""
from typing import Any, Dict, Optional
from app.agents.api_agent import api_agent
from app.agents.database_agent import database_agent
from app.agents.validation_agent import validation_agent
from app.utils.logger import setup_logger
from app.utils.helpers import generate_task_id

logger = setup_logger(__name__)


class OrchestratorAgent:
    """Agent that coordinates other specialized agents"""
    
    def __init__(self):
        self.agents = {
            "api": api_agent,
            "database": database_agent,
            "validation": validation_agent
        }
    
    async def execute_task(
        self,
        task: str,
        agent_type: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute a task using the appropriate agent
        
        Args:
            task: Task description
            agent_type: Specific agent to use (api, database, validation)
            context: Optional context data
            
        Returns:
            Execution result
        """
        try:
            task_id = generate_task_id()
            logger.info(f"Orchestrator executing task: {task_id}")
            
            # If no specific agent type, determine from task
            if not agent_type:
                agent_type = self._determine_agent_type(task)
            
            # Get the appropriate agent
            agent = self.agents.get(agent_type)
            if not agent:
                return {
                    "task_id": task_id,
                    "success": False,
                    "error": f"Unknown agent type: {agent_type}"
                }
            
            # Execute the task
            result = await agent.execute(task, context)
            
            return {
                "task_id": task_id,
                "orchestrator": "main",
                "delegated_to": agent_type,
                "result": result
            }
        except Exception as e:
            logger.error(f"Orchestrator failed: {e}")
            return {
                "task_id": task_id,
                "success": False,
                "error": str(e)
            }
    
    def _determine_agent_type(self, task: str) -> str:
        """
        Determine which agent should handle the task
        
        Args:
            task: Task description
            
        Returns:
            Agent type (api, database, validation)
        """
        task_lower = task.lower()
        
        # Check for API-related keywords
        api_keywords = ['api', 'request', 'http', 'get', 'post', 'put', 'delete', 'endpoint', 'rest']
        if any(keyword in task_lower for keyword in api_keywords):
            return "api"
        
        # Check for database-related keywords
        db_keywords = ['database', 'query', 'insert', 'update', 'delete', 'table', 'record', 'select', 'sql']
        if any(keyword in task_lower for keyword in db_keywords):
            return "database"
        
        # Check for validation-related keywords
        validation_keywords = ['validate', 'check', 'verify', 'sanitize', 'format', 'clean', 'analyze']
        if any(keyword in task_lower for keyword in validation_keywords):
            return "validation"
        
        # Default to validation for general tasks
        return "validation"
    
    async def execute_workflow(
        self,
        steps: list[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Execute a multi-step workflow
        
        Args:
            steps: List of steps, each with 'agent_type' and 'task'
            
        Returns:
            Workflow execution result
        """
        try:
            workflow_id = generate_task_id()
            logger.info(f"Orchestrator executing workflow: {workflow_id}")
            
            results = []
            context = {}
            
            for i, step in enumerate(steps):
                agent_type = step.get("agent_type")
                task = step.get("task")
                
                if not agent_type or not task:
                    logger.warning(f"Invalid step {i}: missing agent_type or task")
                    continue
                
                # Execute step
                result = await self.execute_task(task, agent_type, context)
                results.append({
                    "step": i + 1,
                    "agent_type": agent_type,
                    "task": task,
                    "result": result
                })
                
                # Update context with result for next step
                if result.get("success"):
                    context[f"step_{i + 1}_result"] = result.get("result", {})
            
            return {
                "workflow_id": workflow_id,
                "success": True,
                "steps_completed": len(results),
                "results": results
            }
        except Exception as e:
            logger.error(f"Workflow execution failed: {e}")
            return {
                "workflow_id": workflow_id,
                "success": False,
                "error": str(e)
            }


# Global instance
orchestrator = OrchestratorAgent()