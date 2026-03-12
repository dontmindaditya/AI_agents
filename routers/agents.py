"""
API endpoint to list and run all available agents
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from agents.registry import agent_registry
from utils.auth import get_current_user, require_role

router = APIRouter()

class AgentRunRequest(BaseModel):
    inputs: Dict[str, Any]
    context: Optional[Dict[str, Any]] = None

@router.get("/agents/list", response_model=List[Dict[str, Any]])
async def list_available_agents(
    user: dict = Depends(get_current_user)
):
    """
    Get all available agents from the registry
    This auto-discovers agents from the agents directory
    """
    return agent_registry.get_all_agents()

@router.get("/agents/{agent_id}")
async def get_agent_details(
    agent_id: str,
    user: dict = Depends(get_current_user)
):
    """Get details for a specific agent"""
    agent = agent_registry.get_agent_metadata(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent

@router.post("/agents/{agent_id}/run")
async def run_agent(
    agent_id: str, 
    request: AgentRunRequest,
    user: dict = Depends(get_current_user)
):
    """Execute a specific agent"""
    agent_class = agent_registry.get_agent_class(agent_id)
    if not agent_class:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    try:
        # Instantiate agent
        agent = agent_class()
        
        # Validate inputs (optional, based on metadata)
        # agent.validate_inputs(request.inputs)
        
        # Run agent
        result = await agent.run(request.inputs, request.context)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Pipeline Execution
from pipeline.dynamic import DynamicPipeline, PipelineConfig

@router.post("/pipelines/run")
async def run_pipeline(
    config: PipelineConfig,
    user: dict = Depends(get_current_user)
):
    """
    Execute a dynamic pipeline of agents.
    """
    try:
        pipeline = DynamicPipeline()
        result = await pipeline.run(config)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

