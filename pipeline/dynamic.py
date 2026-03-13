import asyncio
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, field_validator
from agents.registry import agent_registry
from agents.base import BaseAgent

class PipelineStep(BaseModel):
    agent_id: str = Field(..., min_length=1, max_length=100)
    inputs: Dict[str, Any] = Field(default_factory=dict)
    output_key: Optional[str] = Field(None, max_length=100)
    
    @field_validator('agent_id')
    @classmethod
    def validate_agent_id(cls, v: str) -> str:
        if not v.strip():
            raise ValueError('agent_id cannot be empty')
        return v.strip()

class PipelineConfig(BaseModel):
    name: str = Field(default="Dynamic Pipeline", min_length=1, max_length=200)
    steps: List[PipelineStep] = Field(..., min_length=1, max_length=50)
    initial_context: Dict[str, Any] = Field(default_factory=dict)
    
    @field_validator('steps')
    @classmethod
    def validate_steps(cls, v: List[PipelineStep]) -> List[PipelineStep]:
        if not v:
            raise ValueError('steps cannot be empty')
        return v

class DynamicPipeline:
    """
    Executes a sequence of agents dynamically.
    """
    def __init__(self):
        pass

    async def run(self, config: PipelineConfig) -> Dict[str, Any]:
        """
        Run the pipeline based on the configuration.
        Returns the final context.
        """
        context = config.initial_context.copy()
        execution_trace = []

        print(f"🚀 Starting Dynamic Pipeline: {config.name}")

        for i, step in enumerate(config.steps):
            agent_id = step.agent_id
            print(f"▶️  Step {i+1}: {agent_id}")

            # 1. Resolve Agent
            agent_class = agent_registry.get_agent_class(agent_id)
            if not agent_class:
                error_msg = f"Agent '{agent_id}' not found in registry."
                print(f"❌ {error_msg}")
                raise ValueError(error_msg)
            
            # 2. Instantiate Agent
            # (We could pass some pipeline-level config here if needed)
            agent: BaseAgent = agent_class()

            # 3. Resolve Inputs
            # Inputs can be static (from step.inputs) or dynamic (from context)
            # Simple logic: start with step.inputs, overlay with context variables if needed?
            # For now, let's just use step.inputs + context as a whole
            run_inputs = step.inputs.copy()
            
            # 4. Run Agent
            try:
                result = await agent.run(run_inputs, context)
            except Exception as e:
                print(f"❌ Error running agent {agent_id}: {e}")
                raise e

            # 5. Update Context
            if step.output_key:
                context[step.output_key] = result
            
            # Store execution trace
            execution_trace.append({
                "step": i,
                "agent": agent_id,
                "inputs": run_inputs,
                "result": result
            })

        print(f"✅ Pipeline Completed")
        return {
            "context": context,
            "trace": execution_trace
        }
