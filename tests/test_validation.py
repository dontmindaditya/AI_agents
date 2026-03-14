"""
Test suite for input validation models.
"""
import sys
from pathlib import Path

backend_dir = Path(__file__).parent.parent
sys.path.append(str(backend_dir))

import pytest
from pydantic import ValidationError
from main import ExecuteAgentRequest, PipelineExecuteRequest


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
        """Test that invalid characters in project_id are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            ExecuteAgentRequest(
                project_id="my project!",  # Invalid: contains space and special char
                agent_type="frontend",
                task_description="Build a todo app"
            )
        
        assert "project_id" in str(exc_info.value)

    def test_invalid_agent_type(self):
        """Test that invalid agent_type is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            ExecuteAgentRequest(
                project_id="valid-project",
                agent_type="invalid_agent",  # Not in allowed list
                task_description="Build a todo app"
            )
        
        assert "agent_type" in str(exc_info.value)

    def test_valid_agent_types(self):
        """Test that all valid agent types are accepted."""
        valid_types = ["frontend", "backend", "planner", "research", "uiux", "debugger", "paper2code"]
        
        for agent_type in valid_types:
            request = ExecuteAgentRequest(
                project_id="test-project",
                agent_type=agent_type,
                task_description="Test task"
            )
            assert request.agent_type == agent_type

    def test_empty_task_description(self):
        """Test that empty task_description is rejected."""
        with pytest.raises(ValidationError):
            ExecuteAgentRequest(
                project_id="test-project",
                agent_type="frontend",
                task_description=""  # Empty
            )

    def test_task_description_too_long(self):
        """Test that overly long task_description is rejected."""
        with pytest.raises(ValidationError):
            ExecuteAgentRequest(
                project_id="test-project",
                agent_type="frontend",
                task_description="x" * 5001  # Exceeds max length
            )


class TestPipelineExecuteRequest:
    """Tests for PipelineExecuteRequest validation."""

    def test_valid_request(self):
        """Test creating a valid PipelineExecuteRequest."""
        request = PipelineExecuteRequest(
            project_id="my-app-123",
            project_name="My Application",
            project_type="web",
            framework="react",
            description="A modern web application"
        )
        
        assert request.project_id == "my-app-123"
        assert request.project_type == "web"
        assert request.framework == "react"

    def test_invalid_project_type(self):
        """Test that invalid project_type is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            PipelineExecuteRequest(
                project_id="test-project",
                project_name="Test App",
                project_type="invalid_type",  # Not in allowed list
                framework="react",
                description="Test description"
            )
        
        assert "project_type" in str(exc_info.value)

    def test_invalid_framework(self):
        """Test that invalid framework is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            PipelineExecuteRequest(
                project_id="test-project",
                project_name="Test App",
                project_type="web",
                framework="invalid_framework",  # Not in allowed list
                description="Test description"
            )
        
        assert "framework" in str(exc_info.value)

    def test_valid_project_types(self):
        """Test that all valid project types are accepted."""
        valid_types = ["web", "mobile", "desktop", "api", "fullstack", "library"]
        
        for project_type in valid_types:
            request = PipelineExecuteRequest(
                project_id="test-project",
                project_name="Test App",
                project_type=project_type,
                framework="react",
                description="Test"
            )
            assert request.project_type == project_type

    def test_valid_frameworks(self):
        """Test that all valid frameworks are accepted."""
        valid_frameworks = ["react", "vue", "angular", "nextjs", "django", "fastapi", "flask", "express", "spring"]
        
        for framework in valid_frameworks:
            request = PipelineExecuteRequest(
                project_id="test-project",
                project_name="Test App",
                project_type="web",
                framework=framework,
                description="Test"
            )
            assert request.framework == framework

    def test_project_name_trimmed(self):
        """Test that project_name whitespace is trimmed."""
        request = PipelineExecuteRequest(
            project_id="test-project",
            project_name="  Test App  ",  # Extra whitespace
            project_type="web",
            framework="react",
            description="Test"
        )
        
        assert request.project_name == "Test App"

    def test_empty_project_name(self):
        """Test that empty project_name is rejected."""
        with pytest.raises(ValidationError):
            PipelineExecuteRequest(
                project_id="test-project",
                project_name="   ",  # Only whitespace
                project_type="web",
                framework="react",
                description="Test"
            )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
