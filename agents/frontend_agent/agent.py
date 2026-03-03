import sys
import os
from typing import Dict, Any, Optional
from agents.base import BaseAgent, AgentMetadata

class FrontendAgent(BaseAgent):
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        # Hack to support legacy imports inside the frontend_agent package
        current_dir = os.path.dirname(__file__)
        if current_dir not in sys.path:
            sys.path.insert(0, current_dir)
            
        from .graph import create_frontend_graph, FrontendAgentGraph
        self.graph = create_frontend_graph()

    @property
    def metadata(self) -> AgentMetadata:
        return AgentMetadata(
            name="Frontend Agent",
            description="Generates production-ready frontend code (React, Vue, etc.) using a multi-agent workflow.",
            version="1.0.0",
            author="Webby System",
            tags=["frontend", "react", "ui", "code-generation"],
            inputs={
                "type": "object",
                "properties": {
                    "task_description": {"type": "string", "description": "Description of the UI to build"},
                    "framework": {"type": "string", "description": "Target framework (react, vue, vanilla)", "default": "react"}
                },
                "required": ["task_description"]
            },
            outputs={
                "type": "object",
                "properties": {
                    "code": {"type": "string", "description": "Generated code"},
                    "components": {"type": "array", "description": "List of generated components"}
                }
            }
        )

    async def run(self, inputs: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        task = inputs.get("task_description")
        framework = inputs.get("framework", "react")
        
        # Merge pipeline context if valid
        if context and "additional_context" in context:
             task += f"\nContext: {context['additional_context']}"

        result_state = self.graph.run(user_input=task, framework=framework)
        
        # Extract code safely
        generated_code = result_state.get("optimized_code") or result_state.get("generated_code")
        components = result_state.get("generated_components", [])
        
        return {
            "code": str(generated_code),
            "components": components,
            "report": result_state.get("validation_errors", []),
            "status": "completed"
        }
