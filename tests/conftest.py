"""Pytest configuration and fixtures for AgentHub tests."""
import sys
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

import os
import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from typing import Dict, Any
from uuid import uuid4
from datetime import datetime

# Set test environment variables before importing app modules
os.environ.setdefault("APP_NAME", "AgentHub Test")
os.environ.setdefault("LOG_LEVEL", "ERROR")
os.environ.setdefault("LOG_FORMAT", "text")
os.environ.setdefault("API_KEY_ENABLED", "true")
os.environ.setdefault("API_KEYS", "test-key-1,test-key-2")
os.environ.setdefault("SUPABASE_URL", "https://test.supabase.co")
os.environ.setdefault("SUPABASE_KEY", "test-key")
os.environ.setdefault("SUPABASE_SERVICE_KEY", "test-service-key")


# ============================================================================
# Fixtures: Mock Objects
# ============================================================================

@pytest.fixture
def mock_settings():
    """Mock settings for testing."""
    with patch('utils.auth.settings') as mock:
        mock.API_KEY_ENABLED = True
        mock.API_KEYS = ["test-key-1", "test-key-2"]
        mock.APP_NAME = "AgentHub Test"
        mock.LOG_LEVEL = "ERROR"
        mock.LOG_FORMAT = "text"
        yield mock


@pytest.fixture
def mock_supabase_client():
    """Mock Supabase client."""
    with patch('database.client.supabase_client') as mock:
        # Mock table returns
        mock.client = MagicMock()
        mock.service_client = MagicMock()
        
        # Mock table chain
        mock.client.table.return_value.select.return_value.eq.return_value.execute.return_value = MagicMock(
            data=[]
        )
        mock.client.table.return_value.insert.return_value.execute.return_value = MagicMock(
            data=[{"id": str(uuid4())}]
        )
        
        yield mock


@pytest.fixture
def mock_websocket_manager():
    """Mock WebSocket manager."""
    manager = MagicMock()
    manager.connect = AsyncMock()
    manager.disconnect = MagicMock()
    manager.send_personal_message = AsyncMock()
    manager.broadcast_to_project = AsyncMock()
    manager.active_connections = {}
    return manager


@pytest.fixture
def mock_orchestrator():
    """Mock PipelineOrchestrator."""
    orchestrator = MagicMock()
    orchestrator.execute_pipeline = AsyncMock()
    orchestrator.execute_agent = AsyncMock()
    orchestrator.get_pipeline_status = AsyncMock(return_value={
        "status": "completed",
        "project_id": "test-project"
    })
    orchestrator.cancel_pipeline = AsyncMock()
    orchestrator.active_pipelines = {}
    orchestrator.get_active_pipeline_count = MagicMock(return_value=0)
    return orchestrator


# ============================================================================
# Fixtures: Request/Response Models
# ============================================================================

@pytest.fixture
def sample_agent_request() -> Dict[str, Any]:
    """Sample agent execution request data."""
    return {
        "project_id": "test-project-123",
        "agent_type": "frontend",
        "task_description": "Build a simple todo app with React",
        "context": {"framework": "react"}
    }


@pytest.fixture
def sample_pipeline_request() -> Dict[str, Any]:
    """Sample pipeline execution request data."""
    return {
        "project_id": "test-project-456",
        "project_name": "My Test App",
        "project_type": "web",
        "framework": "react",
        "description": "A simple test application",
        "design_preferences": {"theme": "dark"},
        "additional_context": {}
    }


@pytest.fixture
def sample_user() -> Dict[str, Any]:
    """Sample authenticated user data."""
    return {
        "id": str(uuid4()),
        "email": "test@example.com",
        "role": "developer"
    }


@pytest.fixture
def sample_agent_metadata() -> Dict[str, Any]:
    """Sample agent metadata."""
    return {
        "id": "text_processor",
        "name": "Text Processor",
        "description": "Processes text with various operations",
        "version": "1.0.0",
        "author": "AgentHub",
        "tags": ["text", "utility"],
        "inputs": {
            "type": "object",
            "properties": {
                "text": {"type": "string"},
                "operation": {"type": "string", "enum": ["uppercase", "lowercase", "count_words"]}
            }
        },
        "outputs": {
            "type": "object",
            "properties": {
                "result": {"type": "string"}
            }
        }
    }


@pytest.fixture
def sample_pipeline_status() -> Dict[str, Any]:
    """Sample pipeline status response."""
    return {
        "status": "running",
        "project_id": "test-project",
        "current_stage": "generation",
        "stages": {
            "planning": {"status": "completed", "started_at": datetime.utcnow().isoformat()},
            "analysis": {"status": "completed", "started_at": datetime.utcnow().isoformat()},
            "generation": {"status": "running", "started_at": datetime.utcnow().isoformat()}
        },
        "started_at": datetime.utcnow().isoformat(),
        "project_data": {
            "name": "Test App",
            "type": "web",
            "framework": "react"
        }
    }


# ============================================================================
# Fixtures: Test Clients
# ============================================================================

@pytest.fixture
def api_client():
    """Create a test API client."""
    from fastapi.testclient import TestClient
    from main import app
    return TestClient(app)


@pytest.fixture
def auth_headers() -> Dict[str, str]:
    """Headers with valid API key."""
    return {"X-API-Key": "test-key-1"}


@pytest.fixture
def auth_headers_invalid() -> Dict[str, str]:
    """Headers with invalid API key."""
    return {"X-API-Key": "invalid-key"}


# ============================================================================
# Fixtures: Mock AI Responses
# ============================================================================

@pytest.fixture
def mock_ai_response() -> Dict[str, Any]:
    """Mock AI agent response."""
    return {
        "result": "Generated code here",
        "success": True,
        "files": [
            {"path": "src/App.tsx", "content": "// Code content"}
        ]
    }


@pytest.fixture
def mock_llm_response() -> str:
    """Mock LLM text response."""
    return """This is a mock AI response for testing purposes."""


# ============================================================================
# Fixtures: Database Records
# ============================================================================

@pytest.fixture
def sample_agent_record() -> Dict[str, Any]:
    """Sample agent database record."""
    return {
        "id": str(uuid4()),
        "name": "Frontend Agent",
        "slug": "frontend-agent",
        "description": "Generates React code",
        "detailed_description": "A comprehensive frontend code generator",
        "pricing_tier": "free",
        "category_id": str(uuid4()),
        "is_active": True,
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
        "metadata": {"installs": 100}
    }


@pytest.fixture
def sample_category_record() -> Dict[str, Any]:
    """Sample category database record."""
    return {
        "id": str(uuid4()),
        "name": "Frontend",
        "slug": "frontend",
        "description": "Frontend development agents"
    }


# ============================================================================
# Fixtures: Async Support
# ============================================================================

@pytest.fixture
def anyio_backend():
    """AnyIO backend for async tests."""
    return "asyncio"


# ============================================================================
# Configuration
# ============================================================================

def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line("markers", "unit: Unit tests")
    config.addinivalue_line("markers", "integration: Integration tests")
    config.addinivalue_line("markers", "slow: Slow running tests")
    config.addinivalue_line("markers", "asyncio: Async tests")


def pytest_collection_modifyitems(config, items):
    """Add markers to tests based on their names."""
    for item in items:
        if "test_agent_system" in item.nodeid or "test_pipeline" in item.nodeid:
            item.add_marker("integration")
        else:
            item.add_marker("unit")
