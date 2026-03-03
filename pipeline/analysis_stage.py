"""Analysis Stage"""

import sys
import os
from typing import Dict, Any

# Add uiux-agent to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'agents', 'uiux-agent'))

from utils.logger import get_logger

logger = get_logger(__name__)


class AnalysisStage:
    """Analysis stage"""
    
    def __init__(self, websocket_manager):
        self.ws_manager = websocket_manager
    
    async def execute(self, project_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute analysis"""
        try:
            project_data = context["project_data"]
            
            # For now, create a basic design system
            # In the future, integrate with real uiux-agent
            design_system = {
                "colors": {
                    "primary": "#3b82f6",
                    "secondary": "#8b5cf6",
                    "background": "#ffffff",
                    "text": "#1f2937"
                },
                "typography": {
                    "fontFamily": "Inter, sans-serif",
                    "headingSize": "2rem",
                    "bodySize": "1rem"
                },
                "spacing": {
                    "unit": "0.25rem"
                }
            }
            
            # Analyze components
            components = self._analyze_components(context.get("plan", {}))
            
            context["design_system"] = design_system
            context["components"] = components
            
            return {
                "design_system": design_system,
                "components": components
            }
            
        except Exception as e:
            logger.error(f"Analysis failed: {e}")
            raise
    
    def _analyze_components(self, plan: Dict[str, Any]) -> list:
        """Analyze components"""
        components = ["Layout", "Header", "Footer"]
        
        task_breakdown = plan.get("task_breakdown", [])
        for task in task_breakdown:
            task_desc = task.get("task", "").lower()
            if "hero" in task_desc:
                components.append("Hero")
            if "card" in task_desc:
                components.append("Card")
            if "button" in task_desc:
                components.append("Button")
        
        return list(set(components))