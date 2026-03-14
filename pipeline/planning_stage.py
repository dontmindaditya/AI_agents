"""
Planning Stage

This stage creates a comprehensive project plan and structure based on the project description.
It uses the PlanningAdapter to invoke the planning agent which generates:
- Project structure (folders, files)
- Task breakdown
- Technical specifications

The planning stage is the first stage in the pipeline and must complete before
analysis begins.

Usage:
    stage = PlanningStage(ws_manager)
    result = await stage.execute("project-123", {"project_data": {...}})
"""

from typing import Dict, Any
from pipeline.adapters import PlanningAdapter
from utils.logger import setup_logger

logger = setup_logger(__name__)


class PlanningStage:
    """
    Planning stage that creates project structure and task allocation.
    
    This stage analyzes the project description and creates a comprehensive
    plan including file structure, dependencies, and implementation tasks.
    
    Attributes:
        ws_manager: WebSocket manager for real-time updates
        adapter: PlanningAdapter instance for invoking the planning agent
    """
    
    def __init__(self, websocket_manager: WebSocketManager):
        """
        Initialize the planning stage.
        
        Args:
            websocket_manager: WebSocket manager for sending updates
        """
        self.ws_manager = websocket_manager
        self.adapter = PlanningAdapter()
    
    async def execute(self, project_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the planning stage for a project.
        
        Args:
            project_id: Unique project identifier
            context: Pipeline context containing:
                - project_data: Project configuration dictionary
                    - description: Project description
                    - type: Project type
                    - framework: Target framework
                    
        Returns:
            Dictionary containing:
                - plan: Generated project plan
                - status: Stage completion status
                
        Raises:
            Exception: If planning fails
        """
        try:
            project_data = context["project_data"]
            description = project_data.get("description", "website")
            
            # Use adapter to call user's planning_agent
            plan = self.adapter.create_plan(description, project_data)
            
            context["plan"] = plan
            context["project_structure"] = plan.get("project_structure", {})
            
            logger.info(f"Planning completed for: {description}")
            
            return {"plan": plan, "status": "completed"}
            
        except Exception as e:
            logger.error(f"Planning failed: {e}")
            raise