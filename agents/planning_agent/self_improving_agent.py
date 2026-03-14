"""
Self-Improving Planning Agent

This agent uses AutoResearch to autonomously improve its planning capabilities.
It can run experiments on the planning logic and iterate to find better strategies.
"""

import os
import sys
from typing import Dict, Any, Optional
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from agents.base import BaseAgent, AgentMetadata
from agents.mixins import SelfImprovementMixin


class SelfImprovingPlannerAgent(BaseAgent, SelfImprovementMixin):
    """
    A planning agent that can autonomously improve itself.
    
    This agent uses the AutoResearch system to run experiments,
    evaluate planning strategies, and iterate for better performance.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.init_self_improvement()
        
        # Initialize the actual planner
        try:
            from agents.planning_agent.agent import PlanningAgent as LegacyPlannerAgent
            self.planner = LegacyPlannerAgent()
        except ImportError:
            self.planner = None
    
    @property
    def metadata(self) -> AgentMetadata:
        return AgentMetadata(
            name="Self-Improving Planner",
            description="An intelligent planning agent that can autonomously improve itself through experiments.",
            version="1.0.0",
            author="AgentHub",
            tags=["planning", "autonomous", "self-improvement", "strategy"],
            inputs={
                "type": "object",
                "properties": {
                    "task_description": {"type": "string", "description": "Description of what to plan"},
                    "auto_improve": {"type": "boolean", "description": "Enable autonomous improvement", "default": False},
                    "improvement_iterations": {"type": "integer", "description": "Max improvement iterations", "default": 3}
                },
                "required": ["task_description"]
            },
            outputs={
                "type": "object",
                "properties": {
                    "plan": {"type": "object", "description": "Generated plan"},
                    "improvement_results": {"type": "object", "description": "Self-improvement results if enabled"}
                }
            }
        )
    
    async def run(self, inputs: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute the planning agent.
        
        Args:
            inputs: Task description and options
            context: Optional context
                - auto_improve: Whether to run self-improvement
                - improvement_iterations: Max iterations for improvement
        """
        task = inputs.get("task_description", "")
        auto_improve = inputs.get("auto_improve", False)
        max_iterations = inputs.get("improvement_iterations", 3)
        
        # Run normal planning first
        if self.planner:
            plan_output = self.planner.plan(question=task, context=str(context or {}))
            plan = {
                "raw_output": plan_output,
                "project_structure": {},
                "description": task
            }
        else:
            plan = {
                "raw_output": f"Planning for: {task}\n\n[Planner not available - using fallback]",
                "project_structure": {},
                "description": task
            }
        
        result = {
            "plan": plan,
            "status": "completed"
        }
        
        # Run self-improvement if enabled
        if auto_improve:
            improvement_result = await self.improve(
                experiment_description=f"Improve planning for: {task[:50]}",
                max_iterations=max_iterations
            )
            result["improvement_results"] = improvement_result
            
            if improvement_result.get("improved"):
                result["plan"]["improved"] = True
                result["plan"]["improvement"] = improvement_result
        
        return result
    
    async def improve(
        self,
        metric_target: Optional[Dict[str, float]] = None,
        experiment_description: str = "",
        max_iterations: int = 5
    ) -> Dict[str, Any]:
        """Run self-improvement experiments."""
        return await super().improve(metric_target, experiment_description, max_iterations)
    
    def validate_inputs(self, inputs: Dict[str, Any]) -> bool:
        """Validate inputs."""
        return "task_description" in inputs
