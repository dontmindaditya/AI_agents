"""
WebSocket Manager

This module provides WebSocket connection management for real-time communication
between the server and clients. It supports:
- Multiple concurrent connections per project
- Broadcasting messages to all clients in a project
- Thread-safe connection handling with asyncio locks
- Various message types (agent updates, stage updates, file creation, errors, completion)

Usage:
    from services.websocket_manager import WebSocketManager
    
    ws_manager = WebSocketManager()
    
    # In FastAPI websocket endpoint
    @app.websocket("/ws/{project_id}")
    async def websocket_endpoint(websocket: WebSocket, project_id: str):
        await ws_manager.connect(websocket, project_id)
        try:
            while True:
                data = await websocket.receive_json()
        finally:
            ws_manager.disconnect(websocket, project_id)
    
    # Send updates to clients
    await ws_manager.send_stage_update(project_id, {"stage": "planning", "status": "completed"})
    await ws_manager.send_completion(project_id, {"status": "completed", "files": [...]})
"""

import asyncio
from typing import Dict, Set, Any
from datetime import datetime
from fastapi import WebSocket
from utils.logger import setup_logger

logger = setup_logger(__name__)


class WebSocketManager:
    """
    Manages WebSocket connections for real-time project updates.
    
    This class handles WebSocket connections organized by project_id,
    allowing broadcasting to specific projects. It uses asyncio locks
    for thread-safe operations.
    
    Attributes:
        active_connections: Dictionary mapping project_id to set of WebSocket connections
        _lock: Asyncio lock for thread-safe operations
    
    Example:
        >>> manager = WebSocketManager()
        >>> await manager.connect(websocket, "project-1")
        >>> await manager.send_stage_update("project-1", {"stage": "generation"})
        >>> manager.disconnect(websocket, "project-1")
    """
    
    def __init__(self):
        """
        Initialize the WebSocket manager.
        """
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        self._lock = asyncio.Lock()
    
    async def connect(self, websocket: WebSocket, project_id: str) -> None:
        """
        Accept and register a new WebSocket connection.
        
        Args:
            websocket: The WebSocket connection to register
            project_id: Unique identifier for the project room
        """
        await websocket.accept()
        
        async with self._lock:
            if project_id not in self.active_connections:
                self.active_connections[project_id] = set()
            self.active_connections[project_id].add(websocket)
        
        logger.info(f"WebSocket connected: {project_id}")
    
    def disconnect(self, websocket: WebSocket, project_id: str):
        """Disconnect WebSocket"""
        if project_id in self.active_connections:
            self.active_connections[project_id].discard(websocket)
            if not self.active_connections[project_id]:
                del self.active_connections[project_id]
        logger.info(f"❌ WebSocket disconnected: {project_id}")
    
    async def send_personal_message(self, message: Dict[str, Any], websocket: WebSocket):
        """Send to specific WebSocket"""
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.error(f"Failed to send message: {e}")
    
    async def broadcast_to_project(self, project_id: str, message: Dict[str, Any]):
        """Broadcast to all project connections"""
        if project_id not in self.active_connections:
            return
        
        message["timestamp"] = datetime.utcnow().isoformat()
        disconnected = set()
        
        for websocket in self.active_connections[project_id]:
            try:
                await websocket.send_json(message)
            except Exception as e:
                logger.error(f"Broadcast failed: {e}")
                disconnected.add(websocket)
        
        if disconnected:
            async with self._lock:
                self.active_connections[project_id] -= disconnected
    
    async def send_agent_update(self, project_id: str, agent_data: Dict[str, Any]):
        """Send agent update"""
        await self.broadcast_to_project(project_id, {
            "type": "agent_update",
            "data": agent_data
        })
    
    async def send_stage_update(self, project_id: str, stage_data: Dict[str, Any]):
        """Send stage update"""
        await self.broadcast_to_project(project_id, {
            "type": "stage_update",
            "data": stage_data
        })
    
    async def send_file_created(self, project_id: str, file_data: Dict[str, Any]):
        """Send file creation"""
        await self.broadcast_to_project(project_id, {
            "type": "file_created",
            "data": file_data
        })
    
    async def send_error(self, project_id: str, error_data: Dict[str, Any]):
        """Send error"""
        await self.broadcast_to_project(project_id, {
            "type": "error",
            "data": error_data
        })
    
    async def send_completion(self, project_id: str, completion_data: Dict[str, Any]):
        """Send completion"""
        await self.broadcast_to_project(project_id, {
            "type": "pipeline_complete",
            "data": completion_data
        })
    
    async def disconnect_all(self):
        """Disconnect all"""
        for project_id in list(self.active_connections.keys()):
            for websocket in list(self.active_connections[project_id]):
                try:
                    await websocket.close()
                except:
                    pass
        self.active_connections.clear()