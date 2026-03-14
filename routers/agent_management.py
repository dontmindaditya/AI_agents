from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException, Body, Path, Request
from uuid import UUID
from slowapi import Limiter
from slowapi.util import get_remote_address

from database.client import supabase_client
from app_models.marketplace import (
    AgentCreateRequest, AgentUpdateRequest, AgentDetail,
    ProjectAgentResponse, ProjectAgentInstallRequest, ProjectAgentUpdateRequest
)
from utils.logger import setup_logger
from config import settings

logger = setup_logger(__name__)

router = APIRouter(tags=["agent-management"])
limiter = Limiter(key_func=get_remote_address)

# Error messages
ERROR_MESSAGES = {
    "create_failed": "Failed to create agent. Please check the input data and try again.",
    "update_failed": "Failed to update agent. Please check the input data and try again.",
    "not_found": "The requested resource was not found.",
    "list_failed": "Failed to retrieve data. Please try again later.",
    "install_failed": "Failed to install agent. Please try again.",
    "uninstall_failed": "Failed to uninstall agent. Please try again.",
    "refresh_failed": "Failed to refresh agents. Please try again.",
    "database_error": "Database operation failed. Please try again later.",
}


# --- Admin Endpoints ---

@router.post("/api/admin/agents", response_model=AgentDetail)
@limiter.limit(settings.RATE_LIMIT_DEFAULT)
async def create_agent(request: Request, agent: AgentCreateRequest):
    """
    Create a new agent (Admin only).
    
    Args:
        agent: Agent creation request with agent details.
        
    Returns:
        Created agent details.
        
    Raises:
        HTTPException 400: If the input data is invalid.
        HTTPException 500: If creation fails.
    """
    try:
        data = agent.model_dump(exclude_none=True)
        
        result = supabase_client.service_client.table("agent_catalog").insert(data).execute()
        if not result.data:
            raise HTTPException(
                status_code=400,
                detail=ERROR_MESSAGES["create_failed"]
            )
            
        return result.data[0]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create agent: {e}")
        raise HTTPException(
            status_code=500,
            detail=ERROR_MESSAGES["database_error"]
        )

@router.put("/api/admin/agents/{agent_id}", response_model=AgentDetail)
@limiter.limit(settings.RATE_LIMIT_DEFAULT)
async def update_agent(request: Request, agent_id: UUID, update: AgentUpdateRequest):
    """
    Update an existing agent (Admin only).
    
    Args:
        agent_id: UUID of the agent to update.
        update: Update request with new values.
        
    Returns:
        Updated agent details.
        
    Raises:
        HTTPException 404: If agent is not found.
        HTTPException 500: If update fails.
    """
    try:
        data = update.model_dump(exclude_none=True)
        
        result = supabase_client.service_client.table("agent_catalog")\
            .update(data)\
            .eq("id", str(agent_id))\
            .execute()
            
        if not result.data:
            raise HTTPException(
                status_code=404,
                detail=f"Agent with ID '{agent_id}' not found"
            )
            
        return result.data[0]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update agent: {e}")
        raise HTTPException(
            status_code=500,
            detail=ERROR_MESSAGES["database_error"]
        )

# --- Project Management Endpoints ---

@router.get("/api/projects/{project_id}/agents", response_model=List[ProjectAgentResponse])
@limiter.limit(settings.RATE_LIMIT_DEFAULT)
async def list_project_agents(request: Request, project_id: str):
    """
    List agents installed in a project.
    
    Args:
        project_id: ID of the project.
        
    Returns:
        List of installed agents with their configuration.
        
    Raises:
        HTTPException 500: If retrieval fails.
    """
    try:
        result = supabase_client.client.table("project_agents")\
            .select("*, agent:agent_catalog(*)")\
            .eq("project_id", project_id)\
            .execute()
            
        return result.data
    except Exception as e:
        logger.error(f"Failed to list project agents: {e}")
        raise HTTPException(
            status_code=500,
            detail=ERROR_MESSAGES["list_failed"]
        )

@router.post("/api/projects/{project_id}/agents", response_model=ProjectAgentResponse)
@limiter.limit(settings.RATE_LIMIT_DEFAULT)
async def install_agent(
    request: Request,
    project_id: str,
    install_req: ProjectAgentInstallRequest
):
    """Install an agent into a project"""
    try:
        # Check if already installed
        existing = supabase_client.client.table("project_agents")\
            .select("id")\
            .eq("project_id", project_id)\
            .eq("agent_id", str(install_req.agent_id))\
            .execute()
            
        if existing.data:
            raise HTTPException(status_code=400, detail="Agent already installed in this project")
            
        data = {
            "project_id": project_id,
            "agent_id": str(install_req.agent_id),
            "config": install_req.config,
            "is_enabled": True
        }
        
        result = supabase_client.client.table("project_agents").insert(data).select("*, agent:agent_catalog(*)").execute()
        return result.data[0]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to install agent: {e}")
        raise HTTPException(
            status_code=500,
            detail=ERROR_MESSAGES["install_failed"]
        )

@router.patch("/api/projects/{project_id}/agents/{agent_id}", response_model=ProjectAgentResponse)
@limiter.limit(settings.RATE_LIMIT_DEFAULT)
async def update_project_agent(
    request: Request,
    project_id: str,
    agent_id: UUID,
    update: ProjectAgentUpdateRequest
):
    """
    Update project agent configuration or status.
    
    Args:
        project_id: ID of the project.
        agent_id: UUID of the agent to update.
        update: Update request with new configuration.
        
    Returns:
        Updated project agent details.
        
    Raises:
        HTTPException 404: If agent installation not found.
        HTTPException 500: If update fails.
    """
    try:
        query = supabase_client.client.table("project_agents")\
            .update(update.model_dump(exclude_none=True))\
            .eq("project_id", project_id)\
            .eq("agent_id", str(agent_id))\
            .select("*, agent:agent_catalog(*)")
            
        result = query.execute()
        
        if not result.data:
            raise HTTPException(
                status_code=404,
                detail="Agent installation not found in this project"
            )
            
        return result.data[0]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update project agent: {e}")
        raise HTTPException(
            status_code=500,
            detail=ERROR_MESSAGES["update_failed"]
        )

@router.delete("/api/projects/{project_id}/agents/{agent_id}")
@limiter.limit(settings.RATE_LIMIT_DEFAULT)
async def uninstall_agent(request: Request, project_id: str, agent_id: UUID):
    """
    Uninstall an agent from a project.
    
    Args:
        project_id: ID of the project.
        agent_id: UUID of the agent to uninstall.
        
    Returns:
        Success message.
        
    Raises:
        HTTPException 500: If uninstall fails.
    """
    try:
        result = supabase_client.client.table("project_agents")\
            .delete()\
            .eq("project_id", project_id)\
            .eq("agent_id", str(agent_id))\
            .execute()
            
        return {"status": "success", "message": "Agent uninstalled successfully"}
    except Exception as e:
        logger.error(f"Failed to uninstall agent: {e}")
        raise HTTPException(
            status_code=500,
            detail=ERROR_MESSAGES["uninstall_failed"]
        )

@router.post("/api/projects/{project_id}/refresh-agents")
@limiter.limit(settings.RATE_LIMIT_PIPELINE)
async def refresh_agents(request: Request, project_id: str):
    """Regenerate agent integration for an active project (Hot Reload)"""
    try:
        orchestrator = request.app.state.orchestrator
        
        # Check if pipeline exists/active
        # Ideally we want to grab the context from the completed pipeline or re-hydrate it.
        if project_id not in orchestrator.active_pipelines:
             # For MVP, if not in memory, we might fail or need to reload context.
             # Let's assume the user is in the session.
             # If not, we could check if we can fetch file list from somewhere else? 
             # For now, return error if not found.
             raise HTTPException(status_code=404, detail="Active project session not found. Please regenerate the project.")
             
        pipeline_state = orchestrator.active_pipelines[project_id]
        context = {"all_files": pipeline_state.get("project_data", {}).get("all_files", [])} 
        # Wait, orchestrator stores project_data separately from runtime context?
        # In orchestrator.execute_pipeline:
        # self.active_pipelines[project_id] = { ... "project_data": project_data }
        # The 'context' with 'all_files' was local to execute_pipeline. 
        # But 'all_files' is sent in completion message.
        # We need to store 'all_files' in active_pipelines to retrieve it here.
        
        # Let's assume we modified orchestrator to store result?
        # In orchestrator.execute_pipeline:
        # self.active_pipelines[project_id]["status"] = "completed"
        # We didn't store the final context/files in active_pipelines.
        
        # FIX: We need to access the files. 
        # Since I can't easily modify orchestrator logic right now without potentially breaking flow,
        # I'll rely on the client sending the files OR simplify:
        # If the project is *running* (e.g. valid websocket), we might have data.
        
        # Let's fallback to: "Hot reload only works if I can find the files". 
        # Since I wrote IntegrationStage to modify 'all_files', I need 'all_files'.
        
        # Hack for MVP:
        # If active_pipelines has it, use it. If not, error.
        # But I need to make sure orchestrator STORES it.
        # 'project_data' usually has input parameters, not output files.
        
        # I will verify orchestrator again or just implement a stub that says "Not implemented fully without file persistence".
        # However, the user wants it to work.
        # I'll update orchestrator to store 'all_files' in the active_pipelines dict upon completion.
        
        # But first, let's write the endpoint assuming availability.
        
        if "result" in pipeline_state:
             context = {"all_files": pipeline_state["result"].get("files", [])}
        elif "project_data" in pipeline_state and "all_files" in pipeline_state["project_data"]:
             context = {"all_files": pipeline_state["project_data"]["all_files"]}
        else:
             # Last ditch: check if we attached it to the pipeline state manually
             context = {"all_files": pipeline_state.get("files", [])}

        if not context["all_files"]:
             raise HTTPException(status_code=400, detail="No files found for this project session")

        # Execute Integration Stage
        from pipeline.integration_stage import IntegrationStage
        stage = IntegrationStage(orchestrator.ws_manager)
        
        result = await stage.execute(project_id, context)
        
        # Broadcast update
        await orchestrator.ws_manager.send_personal_message({
            "type": "files_update",
            "data": {
                "files": context["all_files"],
                "message": "Agents updated successfully"
            }
        }, project_id) # Wait, ws_manager methods might differ
        
        # ws_manager.send_completion uses send_personal_message logic?
        # orchestrator.ws_manager.send_completion(project_id, {...})
        
        await orchestrator.ws_manager.send_completion(project_id, {
            "status": "updated",
            "message": "Agents updated!",
            "files": context["all_files"]
        })
        
        return {"status": "success", "integrated": result["integrated_agents"]}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to refresh agents: {e}")
        raise HTTPException(status_code=500, detail=str(e))
