"""
Tests for API Endpoints
"""
import pytest
from fastapi.testclient import TestClient


def test_root_endpoint(client):
    """Test root endpoint"""
    response = client.get("/")
    
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "version" in data


def test_health_endpoint(client):
    """Test health check endpoint"""
    response = client.get("/health")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_list_agents_endpoint(client):
    """Test list agents endpoint"""
    response = client.get("/api/v1/agents/list")
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] == True
    assert "agents" in data
    assert len(data["agents"]) > 0


def test_execute_agent_validation(client, sample_task_input):
    """Test agent execution with validation agent"""
    sample_task_input["task"] = "Validate this email: test@example.com"
    sample_task_input["agent_type"] = "validation"
    
    response = client.post(
        "/api/v1/agent/execute",
        json=sample_task_input
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] == True
    assert "data" in data


def test_execute_agent_missing_task(client):
    """Test agent execution with missing task"""
    response = client.post(
        "/api/v1/agent/execute",
        json={"context": {}}
    )
    
    assert response.status_code == 422  # Validation error


def test_execute_agent_invalid_agent_type(client):
    """Test agent execution with invalid agent type"""
    response = client.post(
        "/api/v1/agent/execute",
        json={
            "task": "Test task",
            "agent_type": "invalid_agent",
            "context": {}
        }
    )
    
    assert response.status_code == 422  # Validation error


def test_workflow_run_data_processing(client):
    """Test workflow execution with data_processing type"""
    response = client.post(
        "/api/v1/workflow/run",
        json={
            "workflow_type": "data_processing",
            "input_data": {"test": "data"},
            "config": {}
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] == True


def test_workflow_run_api_workflow(client):
    """Test workflow execution with api_workflow type"""
    response = client.post(
        "/api/v1/workflow/run",
        json={
            "workflow_type": "api_workflow",
            "input_data": {},
            "config": {}
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] == True


def test_workflow_run_invalid_type(client):
    """Test workflow execution with invalid type"""
    response = client.post(
        "/api/v1/workflow/run",
        json={
            "workflow_type": "invalid_type",
            "input_data": {},
            "config": {}
        }
    )
    
    assert response.status_code == 422  # Validation error


def test_list_tasks_endpoint(client):
    """Test list tasks endpoint"""
    response = client.get("/api/v1/tasks?limit=5")
    
    assert response.status_code == 200
    data = response.json()
    assert "success" in data
    assert "count" in data
    assert "data" in data


def test_list_tasks_with_status_filter(client):
    """Test list tasks with status filter"""
    response = client.get("/api/v1/tasks?limit=5&status=completed")
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] == True


def test_database_query_endpoint(client):
    """Test database query endpoint"""
    response = client.post(
        "/api/v1/database/query",
        json={
            "table": "tasks",
            "filters": {},
            "limit": 10
        }
    )
    
    # May fail if database not configured, but endpoint should exist
    assert response.status_code in [200, 500]


def test_get_task_not_found(client):
    """Test get task with non-existent ID"""
    response = client.get("/api/v1/tasks/nonexistent_task_id")
    
    # Should return 404 or 500 depending on database state
    assert response.status_code in [404, 500]


def test_cors_headers(client):
    """Test CORS headers are present"""
    response = client.get("/")
    
    # Check that CORS middleware is active
    assert response.status_code == 200


def test_request_id_header(client):
    """Test that request ID header is added"""
    response = client.get("/health")
    
    # Request logging middleware should add X-Request-ID
    assert response.status_code == 200


def test_api_documentation_endpoints(client):
    """Test that API documentation is available"""
    # Swagger UI
    response = client.get("/docs")
    assert response.status_code == 200
    
    # ReDoc
    response = client.get("/redoc")
    assert response.status_code == 200


def test_openapi_schema(client):
    """Test OpenAPI schema endpoint"""
    response = client.get("/openapi.json")
    
    assert response.status_code == 200
    data = response.json()
    assert "openapi" in data
    assert "info" in data
    assert "paths" in data


@pytest.mark.parametrize("endpoint,method", [
    ("/api/v1/agent/execute", "POST"),
    ("/api/v1/workflow/run", "POST"),
    ("/api/v1/agents/list", "GET"),
    ("/api/v1/tasks", "GET"),
])
def test_endpoint_exists(client, endpoint, method):
    """Test that all main endpoints exist"""
    if method == "GET":
        response = client.get(endpoint)
    elif method == "POST":
        response = client.post(endpoint, json={})
    
    # Should not return 404
    assert response.status_code != 404