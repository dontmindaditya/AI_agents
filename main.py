"""
AgentHub - FastAPI Application
"""

import asyncio
from contextlib import asynccontextmanager
from typing import Dict

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, BackgroundTasks, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, field_validator
from pydantic import model_validator
import re
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from pydantic import ValidationError


from config import settings
from utils.logger import setup_logger
from utils.auth import get_current_user, verify_api_key
from pipeline.orchestrator import PipelineOrchestrator
from services.websocket_manager import WebSocketManager
from routers import marketplace, agent_management, agents
from dependencies import init_services, get_ws_manager, get_orchestrator, get_optional_orchestrator

logger = setup_logger(__name__)
ws_manager = WebSocketManager()
orchestrator: PipelineOrchestrator = None

limiter = Limiter(key_func=get_remote_address)


def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={
            "detail": "Your limit is exceeded. Please wait for sometime before making another request.",
            "retry_after": exc.detail,
            "message": "Rate limit exceeded"
        }
    )


def validation_exception_handler(request: Request, exc: ValidationError):
    errors = []
    for error in exc.errors():
        errors.append({
            "field": ".".join(str(loc) for loc in error["loc"]),
            "message": error["msg"],
            "type": error["type"]
        })
    return JSONResponse(
        status_code=422,
        content={
            "detail": "Validation error",
            "errors": errors,
            "message": "Please check your input and try again."
        }
    )


def generic_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions"""
    error_id = id(exc)
    logger.error(f"Unhandled exception {error_id}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "error_id": str(error_id),
            "message": "An unexpected error occurred. Please try again later."
        }
    )


def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "message": getattr(exc, "msg", "HTTP error occurred")
        }
    )


def value_error_handler(request: Request, exc: ValueError):
    """Handle ValueError exceptions"""
    return JSONResponse(
        status_code=400,
        content={
            "detail": str(exc),
            "message": "Invalid input value"
        }
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager - initializes and cleans up services."""
    global orchestrator
    
    logger.info(f"🚀 Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    orchestrator = PipelineOrchestrator(ws_manager)
    app.state.orchestrator = orchestrator
    
    init_services(ws_manager, orchestrator)
    logger.info("Services initialized via dependency injection")
    
    yield
    
    logger.info("👋 Shutting down...")
    await ws_manager.disconnect_all()


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)
app.add_exception_handler(ValidationError, validation_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(ValueError, value_error_handler)
app.add_exception_handler(Exception, generic_exception_handler)

app.include_router(marketplace.router)
app.include_router(agent_management.router)
app.include_router(agents.router, prefix="/api", tags=["agents"])

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ExecuteAgentRequest(BaseModel):
    project_id: str = Field(..., min_length=1, max_length=100, pattern=r"^[a-zA-Z0-9_-]+$")
    agent_type: str = Field(..., min_length=1, max_length=50)
    task_description: str = Field(..., min_length=1, max_length=5000)
    context: Dict = Field(default_factory=dict)
    
    @field_validator('project_id')
    @classmethod
    def validate_project_id(cls, v: str) -> str:
        if not re.match(r"^[a-zA-Z0-9_-]+$", v):
            raise ValueError('project_id must contain only alphanumeric characters, hyphens, and underscores')
        return v
    
    @field_validator('agent_type')
    @classmethod
    def validate_agent_type(cls, v: str) -> str:
        allowed_agents = ['frontend', 'backend', 'planner', 'research', 'uiux', 'debugger', 'paper2code']
        if v.lower() not in allowed_agents:
            raise ValueError(f'agent_type must be one of: {", ".join(allowed_agents)}')
        return v.lower()
    
    @field_validator('context')
    @classmethod
    def validate_context(cls, v: Dict) -> Dict:
        if not isinstance(v, dict):
            raise ValueError('context must be a dictionary')
        return v


class PipelineExecuteRequest(BaseModel):
    project_id: str = Field(..., min_length=1, max_length=100, pattern=r"^[a-zA-Z0-9_-]+$")
    project_name: str = Field(..., min_length=1, max_length=200)
    project_type: str = Field(..., min_length=1, max_length=50)
    framework: str = Field(..., min_length=1, max_length=50)
    description: str = Field(..., min_length=1, max_length=10000)
    design_preferences: Dict = Field(default_factory=dict)
    additional_context: Dict = Field(default_factory=dict)
    
    @field_validator('project_id')
    @classmethod
    def validate_project_id(cls, v: str) -> str:
        if not re.match(r"^[a-zA-Z0-9_-]+$", v):
            raise ValueError('project_id must contain only alphanumeric characters, hyphens, and underscores')
        return v
    
    @field_validator('project_name')
    @classmethod
    def validate_project_name(cls, v: str) -> str:
        if len(v.strip()) < 1:
            raise ValueError('project_name cannot be empty or whitespace only')
        return v.strip()
    
    @field_validator('project_type')
    @classmethod
    def validate_project_type(cls, v: str) -> str:
        allowed_types = ['web', 'mobile', 'desktop', 'api', 'fullstack', 'library']
        if v.lower() not in allowed_types:
            raise ValueError(f'project_type must be one of: {", ".join(allowed_types)}')
        return v.lower()
    
    @field_validator('framework')
    @classmethod
    def validate_framework(cls, v: str) -> str:
        allowed_frameworks = ['react', 'vue', 'angular', 'nextjs', 'django', 'fastapi', 'flask', 'express', 'spring']
        if v.lower() not in allowed_frameworks:
            raise ValueError(f'framework must be one of: {", ".join(allowed_frameworks)}')
        return v.lower()
    
    @field_validator('design_preferences', 'additional_context')
    @classmethod
    def validate_dict_fields(cls, v: Dict) -> Dict:
        if not isinstance(v, dict):
            raise ValueError('design_preferences and additional_context must be dictionaries')
        return v


@app.get("/")
@limiter.limit(settings.RATE_LIMIT_DEFAULT)
async def root(request: Request):
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "healthy"
    }


@app.get("/health")
@limiter.limit(settings.RATE_LIMIT_HEALTH)
async def health(
    request: Request,
    ws_mgr = Depends(get_ws_manager),
    orch = Depends(get_optional_orchestrator)
):
    return {
        "status": "healthy",
        "active_connections": len(ws_mgr.active_connections),
        "active_pipelines": orch.get_active_pipeline_count() if orch else 0
    }


@app.websocket("/ws/{project_id}")
@limiter.limit(settings.RATE_LIMIT_WS)
async def websocket_endpoint(
    websocket: WebSocket,
    project_id: str,
    ws_mgr = Depends(get_ws_manager)
):
    await ws_mgr.connect(websocket, project_id)
    
    try:
        await ws_mgr.send_personal_message(
            {"type": "connected", "data": {"project_id": project_id}},
            websocket
        )
        
        while True:
            try:
                data = await websocket.receive_json()
                if data.get("type") == "ping":
                    await ws_mgr.send_personal_message(
                        {"type": "pong", "data": {}},
                        websocket
                    )
            except WebSocketDisconnect:
                break
            except Exception as e:
                logger.error(f"WebSocket error: {e}")
                break
    finally:
        ws_mgr.disconnect(websocket, project_id)


@app.post("/api/pipeline/execute")
@limiter.limit(settings.RATE_LIMIT_PIPELINE)
async def execute_pipeline(
    request: Request,
    pipeline_request: PipelineExecuteRequest, 
    background_tasks: BackgroundTasks,
    user: dict = Depends(get_current_user),
    orch = Depends(get_orchestrator)
):
    """
    Execute a pipeline for project generation.
    
    Args:
        pipeline_request: Pipeline configuration including project details.
        
    Returns:
        Status message indicating pipeline has started.
    """
    try:
        logger.info(f"Starting pipeline: {pipeline_request.project_id}")
        
        background_tasks.add_task(
            orch.execute_pipeline,
            project_id=pipeline_request.project_id,
            project_data={
                "name": pipeline_request.project_name,
                "type": pipeline_request.project_type,
                "framework": pipeline_request.framework,
                "description": pipeline_request.description,
                "design_preferences": pipeline_request.design_preferences,
                "additional_context": pipeline_request.additional_context
            }
        )
        
        return {
            "status": "started",
            "project_id": pipeline_request.project_id,
            "message": "Pipeline started successfully"
        }
    except ValueError as e:
        logger.error(f"Pipeline validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Pipeline execution error: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to start pipeline. Please try again later."
        )


@app.get("/api/pipeline/status/{project_id}")
@limiter.limit(settings.RATE_LIMIT_PIPELINE)
async def get_pipeline_status(
    request: Request,
    project_id: str,
    user: dict = Depends(get_current_user)
):
    """
    Get the status of a pipeline.
    
    Args:
        project_id: ID of the project to check status for.
        
    Returns:
        Pipeline status information.
    """
    try:
        status = await orchestrator.get_pipeline_status(project_id)
        return status
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to get pipeline status: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve pipeline status. Please try again later."
        )


@app.post("/api/pipeline/cancel/{project_id}")
@limiter.limit(settings.RATE_LIMIT_PIPELINE)
async def cancel_pipeline(
    request: Request,
    project_id: str,
    user: dict = Depends(get_current_user)
):
    """
    Cancel a running pipeline.
    
    Args:
        project_id: ID of the project to cancel.
        
    Returns:
        Cancellation confirmation.
    """
    try:
        await orchestrator.cancel_pipeline(project_id)
        return {"status": "cancelled", "project_id": project_id, "message": "Pipeline cancelled successfully"}
    except Exception as e:
        logger.error(f"Failed to cancel pipeline: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to cancel pipeline. Please try again later."
        )


@app.post("/api/agents/execute")
@limiter.limit(settings.RATE_LIMIT_AGENTS)
async def execute_agent(
    request: Request,
    agent_request: ExecuteAgentRequest, 
    background_tasks: BackgroundTasks,
    user: dict = Depends(verify_api_key)
):
    """
    Execute a single agent.
    
    Args:
        agent_request: Agent execution request including agent type and task description.
        
    Returns:
        Status message indicating agent execution has started.
    """
    try:
        logger.info(f"Executing agent: {agent_request.agent_type} for project: {agent_request.project_id}")
        
        background_tasks.add_task(
            orchestrator.execute_agent,
            project_id=agent_request.project_id,
            agent_type=agent_request.agent_type,
            task_description=agent_request.task_description,
            context=agent_request.context
        )
        
        return {
            "status": "started",
            "agent_type": agent_request.agent_type,
            "project_id": agent_request.project_id,
            "message": f"Agent '{agent_request.agent_type}' started successfully"
        }
    except ValueError as e:
        logger.error(f"Agent validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Agent execution error: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to execute agent. Please try again later."
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        workers=settings.WORKERS if not settings.DEBUG else 1,
        log_level=settings.LOG_LEVEL.lower()
    )