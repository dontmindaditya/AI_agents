from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, Depends, Request
from uuid import UUID
from slowapi import Limiter
from slowapi.util import get_remote_address

from database.client import supabase_client
from app_models.marketplace import AgentSchema, AgentDetail, AgentCategory
from utils.logger import setup_logger
from config import settings

logger = setup_logger(__name__)

router = APIRouter(
    prefix="/api/marketplace",
    tags=["marketplace"]
)
limiter = Limiter(key_func=get_remote_address)


@router.get("/agents", response_model=List[AgentSchema])
@limiter.limit(settings.RATE_LIMIT_DEFAULT)
async def list_agents(
    request: Request,
    category: Optional[str] = Query(None, description="Filter by category slug"),
    search: Optional[str] = Query(None, description="Search query")
):
    """
    List available agents with optional filtering.
    
    Returns:
        List of active agents, optionally filtered by category and search query.
    """
    try:
        query = supabase_client.client.table("agent_catalog").select("*").eq("is_active", True)
        
        if category:
            cat_res = supabase_client.client.table("agent_categories").select("id").eq("slug", category).single().execute()
            if cat_res.data:
                query = query.eq("category_id", cat_res.data["id"])
            else:
                return []
        
        if search:
            query = query.ilike("name", f"%{search}%")
        
        result = query.order("metadata->install_count", desc=True).execute()
        
        return result.data
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to list agents: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve agents. Please try again later."
        )

@router.get("/agents/{agent_id}", response_model=AgentDetail)
@limiter.limit(settings.RATE_LIMIT_DEFAULT)
async def get_agent_details(request: Request, agent_id: UUID):
    """
    Get full details for a specific agent.
    
    Args:
        agent_id: UUID of the agent to retrieve.
        
    Returns:
        Detailed agent information including configuration.
        
    Raises:
        HTTPException 404: If agent is not found.
        HTTPException 500: If there's a server error.
    """
    try:
        result = supabase_client.client.table("agent_catalog")\
            .select("*")\
            .eq("id", str(agent_id))\
            .single()\
            .execute()
        
        if not result.data:
            raise HTTPException(
                status_code=404,
                detail=f"Agent with ID '{agent_id}' not found"
            )
            
        return result.data
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get agent details: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve agent details. Please try again later."
        )

@router.get("/categories", response_model=List[AgentCategory])
@limiter.limit(settings.RATE_LIMIT_DEFAULT)
async def list_categories(request: Request):
    """
    List all agent categories.
    
    Returns:
        List of all available agent categories.
        
    Raises:
        HTTPException 500: If there's a server error.
    """
    try:
        result = supabase_client.client.table("agent_categories").select("*").order("name").execute()
        return result.data
    except Exception as e:
        logger.error(f"Failed to list categories: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve categories. Please try again later."
        )
