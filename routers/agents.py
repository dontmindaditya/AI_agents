"""
API endpoint to list and run all available agents
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends, Request
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, field_validator
from slowapi import Limiter
from slowapi.util import get_remote_address
from agents.registry import agent_registry
from utils.auth import get_current_user, require_role, verify_api_key
from config import settings

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)


class AgentRunRequest(BaseModel):
    inputs: Dict[str, Any] = Field(..., min_length=1)
    context: Optional[Dict[str, Any]] = None
    
    @field_validator('inputs')
    @classmethod
    def validate_inputs(cls, v: Dict) -> Dict:
        if not isinstance(v, dict):
            raise ValueError('inputs must be a dictionary')
        if len(v) > 100:
            raise ValueError('inputs cannot have more than 100 keys')
        return v
    
    @field_validator('context')
    @classmethod
    def validate_context(cls, v: Optional[Dict]) -> Optional[Dict]:
        if v is not None and not isinstance(v, dict):
            raise ValueError('context must be a dictionary')
        return v


@router.get("/agents/list", response_model=List[Dict[str, Any]])
@limiter.limit(settings.RATE_LIMIT_DEFAULT)
async def list_available_agents(
    request: Request,
    user: dict = Depends(verify_api_key)
):
    """
    Get all available agents from the registry
    This auto-discovers agents from the agents directory
    """
    return agent_registry.get_all_agents()

@router.get("/agents/{agent_id}")
@limiter.limit(settings.RATE_LIMIT_DEFAULT)
async def get_agent_details(
    request: Request,
    agent_id: str,
    user: dict = Depends(verify_api_key)
):
    """Get details for a specific agent"""
    agent = agent_registry.get_agent_metadata(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent

@router.post("/agents/{agent_id}/run")
@limiter.limit(settings.RATE_LIMIT_AGENTS)
async def run_agent(
    request: Request,
    agent_id: str, 
    agent_request: AgentRunRequest,
    user: dict = Depends(verify_api_key)
):
    """Execute a specific agent"""
    agent_class = agent_registry.get_agent_class(agent_id)
    if not agent_class:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    try:
        # Instantiate agent
        agent = agent_class()
        
        # Validate inputs (optional, based on metadata)
        # agent.validate_inputs(agent_request.inputs)
        
        # Run agent
        result = await agent.run(agent_request.inputs, agent_request.context)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Pipeline Execution
from pipeline.dynamic import DynamicPipeline, PipelineConfig

@router.post("/pipelines/run")
@limiter.limit(settings.RATE_LIMIT_PIPELINE)
async def run_pipeline(
    request: Request,
    config: PipelineConfig,
    user: dict = Depends(verify_api_key)
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

