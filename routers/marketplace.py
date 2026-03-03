from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, Depends
from uuid import UUID

from database.client import supabase_client
from app_models.marketplace import AgentSchema, AgentDetail, AgentCategory
from utils.logger import setup_logger

logger = setup_logger(__name__)

router = APIRouter(
    prefix="/api/marketplace",
    tags=["marketplace"]
)

@router.get("/agents", response_model=List[AgentSchema])
async def list_agents(
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
async def get_agent_details(agent_id: UUID):
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
async def list_categories():
    """List all agent categories"""
    try:
        result = supabase_client.client.table("agent_categories").select("*").order("name").execute()
        return result.data
    except Exception as e:
        logger.error(f"Failed to list categories: {e}")
        raise HTTPException(status_code=500, detail=str(e))
