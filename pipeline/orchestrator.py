"""
Pipeline Orchestrator

This module is the main coordinator for executing multi-stage AI pipelines.
It orchestrates the flow between planning, analysis, generation, and integration stages,
providing real-time updates via WebSocket connections.

Pipeline Stages:
    1. Planning - Creates project structure and task allocation
    2. Analysis - Analyzes requirements and design
    3. Generation - Generates frontend/backend code
    4. Integration - Integrates agents and finalizes project

Usage:
    from pipeline.orchestrator import PipelineOrchestrator
    from services.websocket_manager import WebSocketManager
    
    ws_manager = WebSocketManager()
    orchestrator = PipelineOrchestrator(ws_manager)
    
    # Execute a full pipeline
    await orchestrator.execute_pipeline(
        project_id="my-project",
        project_data={"name": "Todo App", "framework": "react"}
    )
    
    # Get status
    status = await orchestrator.get_pipeline_status("my-project")
"""

import asyncio
from typing import Dict, Any, Optional
from datetime import datetime
from pipeline.planning_stage import PlanningStage
from pipeline.analysis_stage import AnalysisStage
from pipeline.generation_stage import GenerationStage
from pipeline.integration_stage import IntegrationStage
from utils.logger import setup_logger

logger = setup_logger(__name__)


class PipelineOrchestrator:
    """
    Main pipeline coordinator that manages the execution of multi-stage AI pipelines.
    
    This class coordinates the flow between different pipeline stages and maintains
    the state of all active pipelines. It also provides real-time updates via
    WebSocket connections.
    
    Attributes:
        ws_manager: WebSocket manager for real-time updates
        active_pipelines: Dictionary of running pipelines by project_id
        stages: Dictionary of pipeline stage instances
    
    Example:
        >>> orchestrator = PipelineOrchestrator(ws_manager)
        >>> await orchestrator.execute_pipeline("project-1", {"name": "My App"})
    """
    
    def __init__(self, websocket_manager: WebSocketManager):
        """
        Initialize the pipeline orchestrator.
        
        Args:
            websocket_manager: WebSocket manager instance for real-time communication
        """
        self.ws_manager: WebSocketManager = websocket_manager
        self.active_pipelines: Dict[str, Dict[str, Any]] = {}
        
        self.stages = {
            "planning": PlanningStage(websocket_manager),
            "analysis": AnalysisStage(websocket_manager),
            "generation": GenerationStage(websocket_manager),
            "integration": IntegrationStage(websocket_manager),
        }
        
        logger.info("Pipeline Orchestrator initialized")
    
    async def execute_pipeline(self, project_id: str, project_data: Dict[str, Any]) -> None:
        """
        Execute full pipeline for a project.
        
        Args:
            project_id: Unique identifier for the project
            project_data: Dictionary containing project configuration
                - name: Project name
                - type: Project type (web, mobile, etc.)
                - framework: Target framework
                - description: Project description
                
        Raises:
            Exception: If any stage fails, the pipeline stops and logs the error
        """
        try:
            logger.info(f"🚀 Starting pipeline: {project_id}")
            
            self.active_pipelines[project_id] = {
                "status": "running",
                "current_stage": "planning",
                "stages": {},
                "started_at": datetime.utcnow().isoformat(),
                "project_data": project_data
            }
            
            context = {"project_data": project_data}
            
            # Execute stages
            await self._execute_stage(project_id, "planning", context)
            await self._execute_stage(project_id, "analysis", context)
            await self._execute_stage(project_id, "design", context)
            await self._execute_stage(project_id, "generation", context)
            await self._execute_stage(project_id, "integration", context)
            
            # Complete
            self.active_pipelines[project_id]["status"] = "completed"
            self.active_pipelines[project_id]["completed_at"] = datetime.utcnow().isoformat()
            self.active_pipelines[project_id]["files"] = context.get("all_files", [])
            
            await self.ws_manager.send_completion(project_id, {
                "status": "completed",
                "message": "Generation complete!",
                "files": context.get("all_files", [])
            })
            
            logger.info(f"✅ Pipeline completed: {project_id}")
            
        except Exception as e:
            logger.error(f"❌ Pipeline failed: {e}")
            
            if project_id in self.active_pipelines:
                self.active_pipelines[project_id]["status"] = "failed"
                self.active_pipelines[project_id]["error"] = str(e)
            
            await self.ws_manager.send_error(project_id, {"error": str(e)})
            raise
    
    async def _execute_stage(self, project_id: str, stage_name: str, context: Dict[str, Any]):
        """Execute single stage"""
        try:
            stage_config = PIPELINE_STAGES[stage_name]
            stage = self.stages[stage_name]
            
            logger.info(f"▶️  Executing {stage_name}: {project_id}")
            
            self.active_pipelines[project_id]["current_stage"] = stage_name
            self.active_pipelines[project_id]["stages"][stage_name] = {
                "status": "running",
                "started_at": datetime.utcnow().isoformat()
            }
            
            await self.ws_manager.send_stage_update(project_id, {
                "stage": stage_name,
                "status": "running",
                "message": stage_config["name"]
            })
            
            result = await stage.execute(project_id, context)
            context[f"{stage_name}_result"] = result
            
            self.active_pipelines[project_id]["stages"][stage_name]["status"] = "completed"
            
            await self.ws_manager.send_stage_update(project_id, {
                "stage": stage_name,
                "status": "completed",
                "result": result
            })
            
            logger.info(f"✅ {stage_name} completed: {project_id}")
            
        except Exception as e:
            logger.error(f"❌ {stage_name} failed: {e}")
            if project_id in self.active_pipelines:
                self.active_pipelines[project_id]["stages"][stage_name]["status"] = "failed"
            raise
    
    async def execute_agent(
        self,
        project_id: str,
        agent_type: str,
        task_description: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute single agent"""
        from agents.registry import agent_registry
        
        agent_class = agent_registry.get_agent_class(agent_type)
        if not agent_class:
            raise ValueError(f"Unknown agent: {agent_type}")
        
        agent = agent_class()
        return await agent.run(
            inputs={"task": task_description, **context},
            context=context
        )
    
    async def get_pipeline_status(self, project_id: str) -> Dict[str, Any]:
        """Get pipeline status"""
        if project_id not in self.active_pipelines:
            raise ValueError(f"Pipeline not found: {project_id}")
        return self.active_pipelines[project_id]
    
    async def cancel_pipeline(self, project_id: str):
        """Cancel pipeline"""
        if project_id in self.active_pipelines:
            self.active_pipelines[project_id]["status"] = "cancelled"
            await self.ws_manager.send_stage_update(project_id, {
                "status": "cancelled"
            })
    
    def get_active_pipeline_count(self) -> int:
        """Get active count"""
        return len([p for p in self.active_pipelines.values() if p["status"] == "running"])