"""
Standalone tests for validation models without full main.py dependencies.
"""
import pytest
from pydantic import BaseModel, ValidationError, Field
from typing import Optional, Dict, Any
import re


class ExecuteAgentRequest(BaseModel):
    """Request model for executing an agent."""
    project_id: str = Field(..., min_length=3, max_length=100, pattern=r'^[a-zA-Z0-9_-]+$')
    agent_type: str = Field(..., min_length=1, max_length=50)
    task_description: str = Field(..., min_length=1, max_length=5000)
    context: Optional[Dict[str, Any]] = None
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "project_id": "my-project-123",
                    "agent_type": "frontend",
                    "task_description": "Build a todo app",
                    "context": {"framework": "react"}
                }
            ]
        }
    }


class PipelineExecuteRequest(BaseModel):
    """Request model for executing a pipeline."""
    project_id: str = Field(..., min_length=3, max_length=100, pattern=r'^[a-zA-Z0-9_-]+$')
    prompt: str = Field(..., min_length=1, max_length=10000)
    settings: Optional[Dict[str, Any]] = None
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "project_id": "my-project-123",
                    "prompt": "Build a full-stack todo app",
                    "settings": {"verbose": True}
                }
            ]
        }
    }


class TestExecuteAgentRequest:
    """Tests for ExecuteAgentRequest validation."""

    def test_valid_request(self):
        """Test creating a valid ExecuteAgentRequest."""
        request = ExecuteAgentRequest(
            project_id="my-project-123",
            agent_type="frontend",
            task_description="Build a todo app",
            context={"framework": "react"}
        )
        
        assert request.project_id == "my-project-123"
        assert request.agent_type == "frontend"

    def test_invalid_project_id_characters(self):
        """Test that invalid project_id characters are rejected."""
        with pytest.raises(ValidationError):
            ExecuteAgentRequest(
                project_id="invalid project!",
                agent_type="frontend",
                task_description="Build a todo app"
            )

    def test_project_id_too_short(self):
        """Test that project_id shorter than 3 chars is rejected."""
        with pytest.raises(ValidationError):
            ExecuteAgentRequest(
                project_id="ab",
                agent_type="frontend",
                task_description="Build a todo app"
            )

    def test_project_id_too_long(self):
        """Test that project_id longer than 100 chars is rejected."""
        with pytest.raises(ValidationError):
            ExecuteAgentRequest(
                project_id="a" * 101,
                agent_type="frontend",
                task_description="Build a todo app"
            )

    def test_empty_task_description(self):
        """Test that empty task_description is rejected."""
        with pytest.raises(ValidationError):
            ExecuteAgentRequest(
                project_id="my-project",
                agent_type="frontend",
                task_description=""
            )

    def test_task_description_too_long(self):
        """Test that task_description longer than 5000 chars is rejected."""
        with pytest.raises(ValidationError):
            ExecuteAgentRequest(
                project_id="my-project",
                agent_type="frontend",
                task_description="a" * 5001
            )

    def test_valid_agent_types(self):
        """Test various valid agent types."""
        valid_types = ["frontend", "backend", "fullstack", "research", "planning"]
        
        for agent_type in valid_types:
            request = ExecuteAgentRequest(
                project_id="my-project",
                agent_type=agent_type,
                task_description="Build something"
            )
            assert request.agent_type == agent_type

    def test_optional_context(self):
        """Test that context is optional."""
        request = ExecuteAgentRequest(
            project_id="my-project",
            agent_type="frontend",
            task_description="Build something"
        )
        assert request.context is None


class TestPipelineExecuteRequest:
    """Tests for PipelineExecuteRequest validation."""

    def test_valid_request(self):
        """Test creating a valid PipelineExecuteRequest."""
        request = PipelineExecuteRequest(
            project_id="my-project-123",
            prompt="Build a full-stack todo app",
            settings={"verbose": True}
        )
        
        assert request.project_id == "my-project-123"
        assert request.prompt == "Build a full-stack todo app"
        assert request.settings == {"verbose": True}

    def test_invalid_project_id(self):
        """Test that invalid project_id is rejected."""
        with pytest.raises(ValidationError):
            PipelineExecuteRequest(
                project_id="invalid project!",
                prompt="Build something"
            )

    def test_empty_prompt(self):
        """Test that empty prompt is rejected."""
        with pytest.raises(ValidationError):
            PipelineExecuteRequest(
                project_id="my-project",
                prompt=""
            )

    def test_prompt_too_long(self):
        """Test that prompt longer than 10000 chars is rejected."""
        with pytest.raises(ValidationError):
            PipelineExecuteRequest(
                project_id="my-project",
                prompt="a" * 10001
            )

    def test_optional_settings(self):
        """Test that settings is optional."""
        request = PipelineExecuteRequest(
            project_id="my-project",
            prompt="Build something"
        )
        assert request.settings is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
