"""
Test Configuration
"""
import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from main import app


@pytest.fixture
def client():
    """FastAPI test client"""
    return TestClient(app)


@pytest.fixture
def sample_task_input():
    """Sample task input for testing"""
    return {
        "task": "Test task description",
        "agent_type": "validation",
        "context": {"test": True}
    }


@pytest.fixture
def sample_workflow_input():
    """Sample workflow input for testing"""
    return {
        "workflow_type": "data_processing",
        "input_data": {"test": "data"},
        "config": {}
    }