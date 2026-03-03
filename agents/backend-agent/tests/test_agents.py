"""
Tests for Agent Functionality
"""
import pytest
from app.agents.api_agent import api_agent
from app.agents.database_agent import database_agent
from app.agents.validation_agent import validation_agent
from app.agents.orchestrator import orchestrator


@pytest.mark.asyncio
async def test_validation_agent_email():
    """Test validation agent with email validation"""
    result = await validation_agent.execute(
        task="Validate this email: test@example.com",
        context={}
    )
    
    assert result is not None
    assert "task_id" in result
    assert result["agent"] == "Validation Agent"


@pytest.mark.asyncio
async def test_validation_agent_url():
    """Test validation agent with URL validation"""
    result = await validation_agent.execute(
        task="Validate this URL: https://example.com",
        context={}
    )
    
    assert result is not None
    assert "task_id" in result


@pytest.mark.asyncio
async def test_api_agent():
    """Test API agent with simple request"""
    result = await api_agent.execute(
        task="Check if the API endpoint https://httpbin.org/status/200 is accessible",
        context={}
    )
    
    assert result is not None
    assert "task_id" in result
    assert result["agent"] == "API Agent"


@pytest.mark.asyncio
async def test_database_agent():
    """Test database agent with query"""
    result = await database_agent.execute(
        task="Get schema information for tasks table",
        context={"table": "tasks"}
    )
    
    assert result is not None
    assert "task_id" in result
    assert result["agent"] == "Database Agent"


@pytest.mark.asyncio
async def test_orchestrator_auto_select():
    """Test orchestrator automatic agent selection"""
    result = await orchestrator.execute_task(
        task="Validate this JSON: {\"name\": \"test\"}",
        agent_type=None  # Let orchestrator decide
    )
    
    assert result is not None
    assert "task_id" in result
    assert "delegated_to" in result


@pytest.mark.asyncio
async def test_orchestrator_explicit_agent():
    """Test orchestrator with explicit agent selection"""
    result = await orchestrator.execute_task(
        task="Query database for information",
        agent_type="database"
    )
    
    assert result is not None
    assert result["delegated_to"] == "database"


@pytest.mark.asyncio
async def test_orchestrator_workflow():
    """Test orchestrator multi-step workflow"""
    steps = [
        {"agent_type": "validation", "task": "Validate input data"},
        {"agent_type": "database", "task": "Query database"},
        {"agent_type": "validation", "task": "Format results"}
    ]
    
    result = await orchestrator.execute_workflow(steps)
    
    assert result is not None
    assert "workflow_id" in result
    assert result["success"] == True
    assert len(result["results"]) == 3


def test_agent_determination():
    """Test orchestrator agent type determination"""
    # API-related task
    agent_type = orchestrator._determine_agent_type("Make an API request to fetch data")
    assert agent_type == "api"
    
    # Database-related task
    agent_type = orchestrator._determine_agent_type("Query the users table")
    assert agent_type == "database"
    
    # Validation-related task
    agent_type = orchestrator._determine_agent_type("Validate this email address")
    assert agent_type == "validation"