"""
Adapter for Planning Agent
Bridges pipeline to user's planning_agent implementation
"""
import sys
import os
from typing import Dict, Any, Optional

# Add planning_agent directory to path
planning_agent_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'agents', 'planning_agent')
sys.path.insert(0, planning_agent_dir)

# Now import from the agents subdirectory within planning_agent
try:
    from agents.planner import PlannerAgent as RealPlannerAgent
    PLANNER_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import PlannerAgent: {e}")
    PLANNER_AVAILABLE = False
    RealPlannerAgent = None


class PlanningAdapter:
    """Adapter for planning_agent"""
    
    def __init__(self):
        if PLANNER_AVAILABLE:
            self.agent = RealPlannerAgent()
        else:
            self.agent = None
    
    def create_plan(self, description: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Create project plan"""
        if not self.agent:
            # Fallback if agent not available
            return {
                "raw_output": f"Project plan for: {description}\n\n[Planning agent not available - using fallback]",
                "project_structure": {},
                "description": description
            }
        
        question = f"Create a detailed project plan for: {description}"
        context_str = str(context) if context else ""
        
        plan_output = self.agent.plan(question=question, context=context_str)
        
        return {
            "raw_output": plan_output,
            "project_structure": {},
            "description": description
        }
