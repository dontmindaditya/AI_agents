"""Planning Stage"""

from typing import Dict, Any
from pipeline.adapters import PlanningAdapter
from utils.logger import get_logger

logger = get_logger(__name__)


class PlanningStage:
    """Planning stage"""
    
    def __init__(self, websocket_manager):
        self.ws_manager = websocket_manager
        self.adapter = PlanningAdapter()
    
    async def execute(self, project_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute planning"""
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