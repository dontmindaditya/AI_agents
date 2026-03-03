"""
Webby Backend - FastAPI Application
"""

import asyncio
from contextlib import asynccontextmanager
from typing import Dict

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field


from config import settings
from utils.logger import setup_logger
from pipeline.orchestrator import PipelineOrchestrator
from services.websocket_manager import WebSocketManager
from routers import marketplace, agent_management, agents

logger = setup_logger(__name__)
ws_manager = WebSocketManager()
orchestrator: PipelineOrchestrator = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager"""
    global orchestrator
    
    logger.info(f"🚀 Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    orchestrator = PipelineOrchestrator(ws_manager)
    app.state.orchestrator = orchestrator
    
    yield
    
    logger.info("👋 Shutting down...")
    await ws_manager.disconnect_all()


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan,
)

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
    project_id: str
    agent_type: str
    task_description: str
    context: Dict = Field(default_factory=dict)


class PipelineExecuteRequest(BaseModel):
    project_id: str
    project_name: str
    project_type: str
    framework: str
    description: str
    design_preferences: Dict = Field(default_factory=dict)
    additional_context: Dict = Field(default_factory=dict)


@app.get("/")
async def root():
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "healthy"
    }


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "active_connections": len(ws_manager.active_connections),
        "active_pipelines": orchestrator.get_active_pipeline_count() if orchestrator else 0
    }


@app.websocket("/ws/{project_id}")
async def websocket_endpoint(websocket: WebSocket, project_id: str):
    await ws_manager.connect(websocket, project_id)
    
    try:
        await ws_manager.send_personal_message(
            {"type": "connected", "data": {"project_id": project_id}},
            websocket
        )
        
        while True:
            try:
                data = await websocket.receive_json()
                if data.get("type") == "ping":
                    await ws_manager.send_personal_message(
                        {"type": "pong", "data": {}},
                        websocket
                    )
            except WebSocketDisconnect:
                break
            except Exception as e:
                logger.error(f"WebSocket error: {e}")
                break
    finally:
        ws_manager.disconnect(websocket, project_id)


@app.post("/api/pipeline/execute")
async def execute_pipeline(request: PipelineExecuteRequest, background_tasks: BackgroundTasks):
    try:
        logger.info(f"🎯 Starting pipeline: {request.project_id}")
        
        background_tasks.add_task(
            orchestrator.execute_pipeline,
            project_id=request.project_id,
            project_data={
                "name": request.project_name,
                "type": request.project_type,
                "framework": request.framework,
                "description": request.description,
                "design_preferences": request.design_preferences,
                "additional_context": request.additional_context
            }
        )
        
        return {
            "status": "started",
            "project_id": request.project_id,
            "message": "Pipeline started"
        }
    except Exception as e:
        logger.error(f"❌ Pipeline failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/pipeline/status/{project_id}")
async def get_pipeline_status(project_id: str):
    try:
        status = await orchestrator.get_pipeline_status(project_id)
        return status
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/pipeline/cancel/{project_id}")
async def cancel_pipeline(project_id: str):
    try:
        await orchestrator.cancel_pipeline(project_id)
        return {"status": "cancelled", "project_id": project_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/agents/execute")
async def execute_agent(request: ExecuteAgentRequest, background_tasks: BackgroundTasks):
    try:
        logger.info(f"🤖 Executing {request.agent_type}: {request.project_id}")
        
        background_tasks.add_task(
            orchestrator.execute_agent,
            project_id=request.project_id,
            agent_type=request.agent_type,
            task_description=request.task_description,
            context=request.context
        )
        
        return {
            "status": "started",
            "agent_type": request.agent_type
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


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