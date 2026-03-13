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
    """List available agents with optional filtering"""
    try:
        query = supabase_client.client.table("agent_catalog").select("*").eq("is_active", True)
        
        if category:
            # First get category ID from slug
            cat_res = supabase_client.client.table("agent_categories").select("id").eq("slug", category).single().execute()
            if cat_res.data:
                query = query.eq("category_id", cat_res.data["id"])
            else:
                return [] # Category not found means no agents
        
        if search:
            # Supabase text search (simple ilike for now)
            query = query.ilike("name", f"%{search}%")
            
        result = query.order("metadata->install_count", desc=True).execute()
        
        return result.data
    except Exception as e:
        logger.error(f"Failed to list agents: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/agents/{agent_id}", response_model=AgentDetail)
@limiter.limit(settings.RATE_LIMIT_DEFAULT)
async def get_agent_details(request: Request, agent_id: UUID):
    """Get full details for a specific agent"""
    try:
        result = supabase_client.client.table("agent_catalog")\
            .select("*")\
            .eq("id", str(agent_id))\
            .single()\
            .execute()
            
        if not result.data:
            raise HTTPException(status_code=404, detail="Agent not found")
            
        return result.data
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get agent details: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/categories", response_model=List[AgentCategory])
@limiter.limit(settings.RATE_LIMIT_DEFAULT)
async def list_categories(request: Request):
    """List all agent categories"""
    try:
        result = supabase_client.client.table("agent_categories").select("*").order("name").execute()
        return result.data
    except Exception as e:
        logger.error(f"Failed to list categories: {e}")
        raise HTTPException(status_code=500, detail=str(e))
