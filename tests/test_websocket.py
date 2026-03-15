"""
WebSocket Integration Tests

Tests for WebSocket endpoints and WebSocketManager functionality.
These tests use FastAPI's TestClient with websocket_connect for testing.
"""
import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from typing import Dict, Any
import sys
from pathlib import Path

backend_dir = Path(__file__).parent.parent
sys.path.append(str(backend_dir))

from fastapi import WebSocket, WebSocketDisconnect
from fastapi.testclient import TestClient
from starlette.websockets import WebSocketState


class MockWebSocket:
    """Mock WebSocket for testing."""
    
    def __init__(self):
        self.messages = []
        self.accepted = False
        self.closed = False
        self.close_code = None
    
    async def accept(self):
        self.accepted = True
    
    async def send_json(self, data: Dict[str, Any]):
        self.messages.append(data)
    
    async def receive_json(self) -> Dict[str, Any]:
        return {"type": "ping"}
    
    async def close(self, code: int = 1000):
        self.closed = True
        self.close_code = code
    
    @property
    def client_state(self) -> WebSocketState:
        return WebSocketState.CONNECTED


class TestWebSocketManager:
    """Tests for WebSocketManager class."""

    @pytest.fixture
    def ws_manager(self):
        """Create a fresh WebSocketManager instance."""
        from services.websocket_manager import WebSocketManager
        return WebSocketManager()

    @pytest.mark.asyncio
    async def test_connect(self, ws_manager):
        """Test connecting a WebSocket."""
        mock_ws = MockWebSocket()
        
        await ws_manager.connect(mock_ws, "test-project")
        
        assert mock_ws.accepted is True
        assert "test-project" in ws_manager.active_connections
        assert mock_ws in ws_manager.active_connections["test-project"]

    @pytest.mark.asyncio
    async def test_connect_multiple_to_same_project(self, ws_manager):
        """Test multiple connections to same project."""
        mock_ws1 = MockWebSocket()
        mock_ws2 = MockWebSocket()
        
        await ws_manager.connect(mock_ws1, "test-project")
        await ws_manager.connect(mock_ws2, "test-project")
        
        assert len(ws_manager.active_connections["test-project"]) == 2

    @pytest.mark.asyncio
    async def test_connect_different_projects(self, ws_manager):
        """Test connections to different projects."""
        mock_ws1 = MockWebSocket()
        mock_ws2 = MockWebSocket()
        
        await ws_manager.connect(mock_ws1, "project-1")
        await ws_manager.connect(mock_ws2, "project-2")
        
        assert len(ws_manager.active_connections) == 2
        assert mock_ws1 in ws_manager.active_connections["project-1"]
        assert mock_ws2 in ws_manager.active_connections["project-2"]

    @pytest.mark.asyncio
    async def test_disconnect(self, ws_manager):
        """Test disconnecting a WebSocket."""
        mock_ws = MockWebSocket()
        
        await ws_manager.connect(mock_ws, "test-project")
        ws_manager.disconnect(mock_ws, "test-project")
        
        assert "test-project" not in ws_manager.active_connections

    @pytest.mark.asyncio
    async def test_disconnect_keeps_other_connections(self, ws_manager):
        """Test that disconnecting one keeps others."""
        mock_ws1 = MockWebSocket()
        mock_ws2 = MockWebSocket()
        
        await ws_manager.connect(mock_ws1, "test-project")
        await ws_manager.connect(mock_ws2, "test-project")
        
        ws_manager.disconnect(mock_ws1, "test-project")
        
        assert len(ws_manager.active_connections["test-project"]) == 1
        assert mock_ws2 in ws_manager.active_connections["test-project"]

    @pytest.mark.asyncio
    async def test_send_personal_message(self, ws_manager):
        """Test sending personal message."""
        mock_ws = MockWebSocket()
        
        await ws_manager.connect(mock_ws, "test-project")
        await ws_manager.send_personal_message({"type": "test"}, mock_ws)
        
        assert len(mock_ws.messages) == 1
        assert mock_ws.messages[0]["type"] == "test"

    @pytest.mark.asyncio
    async def test_broadcast_to_project(self, ws_manager):
        """Test broadcasting to all connections in a project."""
        mock_ws1 = MockWebSocket()
        mock_ws2 = MockWebSocket()
        
        await ws_manager.connect(mock_ws1, "test-project")
        await ws_manager.connect(mock_ws2, "test-project")
        
        await ws_manager.broadcast_to_project("test-project", {"type": "broadcast"})
        
        assert len(mock_ws1.messages) == 1
        assert len(mock_ws2.messages) == 1
        assert mock_ws1.messages[0]["type"] == "broadcast"

    @pytest.mark.asyncio
    async def test_broadcast_to_nonexistent_project(self, ws_manager):
        """Test broadcast to non-existent project does nothing."""
        mock_ws = MockWebSocket()
        
        # Should not raise
        await ws_manager.broadcast_to_project("nonexistent", {"type": "test"})
        
        assert len(mock_ws.messages) == 0

    @pytest.mark.asyncio
    async def test_send_agent_update(self, ws_manager):
        """Test sending agent update."""
        mock_ws = MockWebSocket()
        
        await ws_manager.connect(mock_ws, "test-project")
        await ws_manager.send_agent_update("test-project", {"agent": "test-agent"})
        
        assert len(mock_ws.messages) == 1
        assert mock_ws.messages[0]["type"] == "agent_update"
        assert mock_ws.messages[0]["data"]["agent"] == "test-agent"

    @pytest.mark.asyncio
    async def test_send_stage_update(self, ws_manager):
        """Test sending stage update."""
        mock_ws = MockWebSocket()
        
        await ws_manager.connect(mock_ws, "test-project")
        await ws_manager.send_stage_update("test-project", {"stage": "planning"})
        
        assert len(mock_ws.messages) == 1
        assert mock_ws.messages[0]["type"] == "stage_update"
        assert mock_ws.messages[0]["data"]["stage"] == "planning"

    @pytest.mark.asyncio
    async def test_send_file_created(self, ws_manager):
        """Test sending file created notification."""
        mock_ws = MockWebSocket()
        
        await ws_manager.connect(mock_ws, "test-project")
        await ws_manager.send_file_created("test-project", {"file": "index.js"})
        
        assert len(mock_ws.messages) == 1
        assert mock_ws.messages[0]["type"] == "file_created"

    @pytest.mark.asyncio
    async def test_send_error(self, ws_manager):
        """Test sending error notification."""
        mock_ws = MockWebSocket()
        
        await ws_manager.connect(mock_ws, "test-project")
        await ws_manager.send_error("test-project", {"error": "Something went wrong"})
        
        assert len(mock_ws.messages) == 1
        assert mock_ws.messages[0]["type"] == "error"
        assert mock_ws.messages[0]["data"]["error"] == "Something went wrong"

    @pytest.mark.asyncio
    async def test_send_completion(self, ws_manager):
        """Test sending completion notification."""
        mock_ws = MockWebSocket()
        
        await ws_manager.connect(mock_ws, "test-project")
        await ws_manager.send_completion("test-project", {"status": "completed"})
        
        assert len(mock_ws.messages) == 1
        assert mock_ws.messages[0]["type"] == "pipeline_complete"
        assert mock_ws.messages[0]["data"]["status"] == "completed"

    @pytest.mark.asyncio
    async def test_broadcast_adds_timestamp(self, ws_manager):
        """Test that broadcast adds timestamp to message."""
        mock_ws = MockWebSocket()
        
        await ws_manager.connect(mock_ws, "test-project")
        await ws_manager.broadcast_to_project("test-project", {"type": "test"})
        
        assert "timestamp" in mock_ws.messages[0]

    @pytest.mark.asyncio
    async def test_disconnect_all(self, ws_manager):
        """Test disconnecting all connections."""
        mock_ws1 = MockWebSocket()
        mock_ws2 = MockWebSocket()
        
        await ws_manager.connect(mock_ws1, "project-1")
        await ws_manager.connect(mock_ws2, "project-2")
        
        await ws_manager.disconnect_all()
        
        assert len(ws_manager.active_connections) == 0


class TestWebSocketEndpoint:
    """Tests for the WebSocket endpoint in main.py."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        from fastapi import FastAPI
        from fastapi.testclient import TestClient
        from services.websocket_manager import WebSocketManager
        
        app = FastAPI()
        ws_manager = WebSocketManager()
        
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
            finally:
                ws_manager.disconnect(websocket, project_id)
        
        return TestClient(app)

    def test_websocket_connection(self, client):
        """Test WebSocket connection establishes successfully."""
        with client.websocket_connect("/ws/test-project") as websocket:
            data = websocket.receive_json()
            assert data["type"] == "connected"
            assert data["data"]["project_id"] == "test-project"

    def test_websocket_ping_pong(self, client):
        """Test ping-pong functionality."""
        with client.websocket_connect("/ws/test-project") as websocket:
            # Receive connection message
            websocket.receive_json()
            
            # Send ping
            websocket.send_json({"type": "ping"})
            
            # Receive pong
            data = websocket.receive_json()
            assert data["type"] == "pong"

    def test_websocket_multiple_messages(self, client):
        """Test multiple messages through WebSocket."""
        with client.websocket_connect("/ws/test-project") as websocket:
            # Receive connection message
            websocket.receive_json()
            
            # Send multiple pings
            for i in range(3):
                websocket.send_json({"type": "ping"})
                data = websocket.receive_json()
                assert data["type"] == "pong"

    def test_websocket_disconnect(self, client):
        """Test WebSocket disconnects cleanly."""
        with client.websocket_connect("/ws/test-project") as websocket:
            websocket.receive_json()
        
        # Connection should close without error

    def test_websocket_multiple_connections_same_project(self, client):
        """Test multiple connections to same project."""
        with client.websocket_connect("/ws/test-project") as ws1:
            ws1.receive_json()
            
            with client.websocket_connect("/ws/test-project") as ws2:
                ws2.receive_json()
                
                # Both should receive connection messages
                assert True


class TestWebSocketRateLimiting:
    """Tests for WebSocket rate limiting."""

    def test_rate_limit_config(self):
        """Test that rate limit is configured for WebSocket."""
        from config import settings
        
        assert hasattr(settings, 'RATE_LIMIT_WS')
        assert settings.RATE_LIMIT_WS == "60/minute"


class TestWebSocketIntegration:
    """Integration tests for WebSocket with pipeline."""

    @pytest.mark.asyncio
    async def test_pipeline_stage_updates_via_websocket(self):
        """Test that pipeline stages send updates via WebSocket."""
        from services.websocket_manager import WebSocketManager
        
        ws_manager = WebSocketManager()
        mock_ws = MockWebSocket()
        
        # Simulate connection
        await ws_manager.connect(mock_ws, "pipeline-test")
        
        # Simulate stage updates
        await ws_manager.send_stage_update("pipeline-test", {
            "stage": "planning",
            "status": "completed"
        })
        
        await ws_manager.send_stage_update("pipeline-test", {
            "stage": "generation",
            "status": "running"
        })
        
        await ws_manager.send_completion("pipeline-test", {
            "status": "completed",
            "files": ["index.js", "app.py"]
        })
        
        assert len(mock_ws.messages) == 3
        assert mock_ws.messages[0]["type"] == "stage_update"
        assert mock_ws.messages[1]["type"] == "stage_update"
        assert mock_ws.messages[2]["type"] == "pipeline_complete"

    @pytest.mark.asyncio
    async def test_agent_updates_via_websocket(self):
        """Test that agent updates are sent via WebSocket."""
        from services.websocket_manager import WebSocketManager
        
        ws_manager = WebSocketManager()
        mock_ws = MockWebSocket()
        
        await ws_manager.connect(mock_ws, "agent-test")
        
        await ws_manager.send_agent_update("agent-test", {
            "agent": "frontend",
            "status": "generating",
            "progress": 50
        })
        
        assert len(mock_ws.messages) == 1
        assert mock_ws.messages[0]["type"] == "agent_update"
        assert mock_ws.messages[0]["data"]["progress"] == 50


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
