"""
Test suite for pipeline configurations.
"""
import sys
from pathlib import Path

backend_dir = Path(__file__).parent.parent
sys.path.append(str(backend_dir))

import pytest
from pydantic import ValidationError
from pipeline.dynamic import PipelineConfig, PipelineStep


class TestPipelineStep:
    """Tests for PipelineStep model."""

    def test_valid_step(self):
        """Test creating a valid PipelineStep."""
        step = PipelineStep(
            agent_id="frontend",
            inputs={"task": "build a button"},
            output_key="button_component"
        )
        
        assert step.agent_id == "frontend"
        assert step.output_key == "button_component"

    def test_empty_agent_id(self):
        """Test that empty agent_id is rejected."""
        with pytest.raises(ValidationError):
            PipelineStep(
                agent_id="",  # Empty
                inputs={}
            )

    def test_whitespace_agent_id(self):
        """Test that whitespace-only agent_id is rejected."""
        with pytest.raises(ValidationError):
            PipelineStep(
                agent_id="   ",  # Whitespace only
                inputs={}
            )

    def test_max_agent_id_length(self):
        """Test that too long agent_id is rejected."""
        with pytest.raises(ValidationError):
            PipelineStep(
                agent_id="a" * 101,  # Exceeds max
                inputs={}
            )

    def test_valid_output_key(self):
        """Test valid output_key."""
        step = PipelineStep(
            agent_id="test",
            inputs={},
            output_key="result"
        )
        assert step.output_key == "result"

    def test_optional_fields(self):
        """Test that output_key and inputs are optional."""
        step = PipelineStep(agent_id="test")
        assert step.agent_id == "test"
        assert step.inputs == {}


class TestPipelineConfig:
    """Tests for PipelineConfig model."""

    def test_valid_config(self):
        """Test creating a valid PipelineConfig."""
        config = PipelineConfig(
            name="Test Pipeline",
            steps=[
                PipelineStep(agent_id="frontend", inputs={}),
                PipelineStep(agent_id="backend", inputs={})
            ]
        )
        
        assert config.name == "Test Pipeline"
        assert len(config.steps) == 2

    def test_empty_steps(self):
        """Test that empty steps list is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            PipelineConfig(steps=[])
        
        assert "steps cannot be empty" in str(exc_info.value)

    def test_max_steps(self):
        """Test that exceeding max steps is rejected."""
        with pytest.raises(ValidationError):
            steps = [PipelineStep(agent_id=f"agent-{i}", inputs={}) for i in range(51)]
            PipelineConfig(steps=steps)

    def test_valid_name(self):
        """Test valid name."""
        config = PipelineConfig(
            name="My Pipeline",
            steps=[PipelineStep(agent_id="test", inputs={})]
        )
        assert config.name == "My Pipeline"

    def test_default_name(self):
        """Test default name."""
        config = PipelineConfig(
            steps=[PipelineStep(agent_id="test", inputs={})]
        )
        assert config.name == "Dynamic Pipeline"

    def test_max_name_length(self):
        """Test that too long name is rejected."""
        with pytest.raises(ValidationError):
            PipelineConfig(
                name="a" * 201,
                steps=[PipelineStep(agent_id="test", inputs={})]
            )

    def test_initial_context(self):
        """Test initial context."""
        config = PipelineConfig(
            steps=[PipelineStep(agent_id="test", inputs={})],
            initial_context={"user": "tester"}
        )
        
        assert config.initial_context["user"] == "tester"

    def test_default_initial_context(self):
        """Test default initial context."""
        config = PipelineConfig(
            steps=[PipelineStep(agent_id="test", inputs={})]
        )
        assert config.initial_context == {}


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
