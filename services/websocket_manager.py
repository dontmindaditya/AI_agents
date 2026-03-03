"""WebSocket Manager"""

import asyncio
from typing import Dict, Set, Any
from datetime import datetime
from fastapi import WebSocket
from utils.logger import get_logger

logger = get_logger(__name__)


class WebSocketManager:
    """Manages WebSocket connections"""
    
    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        self._lock = asyncio.Lock()
    
    async def connect(self, websocket: WebSocket, project_id: str):
        """Connect WebSocket"""
        await websocket.accept()
        
        async with self._lock:
            if project_id not in self.active_connections:
                self.active_connections[project_id] = set()
            self.active_connections[project_id].add(websocket)
        
        logger.info(f"✅ WebSocket connected: {project_id}")
    
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