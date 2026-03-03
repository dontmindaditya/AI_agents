from typing import Dict, Any, Optional
from agents.base import BaseAgent, AgentMetadata
from .agents.planner import PlannerAgent as LegacyPlannerAgent

class PlanningAgent(BaseAgent):
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.planner = LegacyPlannerAgent()

    @property
    def metadata(self) -> AgentMetadata:
        return AgentMetadata(
            name="Planning Agent",
            description="Analyzes requirements and creates a comprehensive project structure and task list.",
            version="1.0.0",
            author="Webby System",
            tags=["planning", "architecture", "strategy"],
            inputs={
                "type": "object",
                "properties": {
                    "question": {"type": "string", "description": "What do you want to build or plan?"},
                    "context": {"type": "string", "description": "Additional context or documentation"}
                },
                "required": ["question"]
            },
            outputs={
                "type": "object",
                "properties": {
                    "plan": {"type": "string", "description": "The generated project plan"}
                }
            }
        )

    async def run(self, inputs: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        question = inputs.get("question")
        user_context = inputs.get("context", "")
        
        # Merge pipeline context if valid
        if context and "additional_context" in context:
             user_context += f"\n{context['additional_context']}"

        result = self.planner.plan(question=question, context=user_context)
        
        return {
            "plan": result,
            "status": "completed"
        }
