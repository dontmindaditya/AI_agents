"""
Tests for AutoResearch Agent
"""
import pytest
from unittest.mock import patch, MagicMock
import sys
from pathlib import Path

backend_dir = Path(__file__).parent.parent
sys.path.append(str(backend_dir))


class TestAutoResearchAgent:
    """Tests for AutoResearchAgent."""

    @pytest.fixture
    def agent(self):
        """Create an AutoResearchAgent instance."""
        from agents.autoresearch.agent import AutoResearchAgent
        return AutoResearchAgent()

    def test_agent_metadata(self, agent):
        """Test that agent has correct metadata."""
        metadata = agent.metadata
        
        assert metadata.name == "AutoResearch Agent"
        assert "research" in metadata.tags
        assert "llm" in metadata.tags
        assert metadata.version == "1.0.0"

    def test_agent_inputs(self, agent):
        """Test that agent has correct input schema."""
        inputs = agent.metadata.inputs
        
        assert "properties" in inputs
        assert "operation" in inputs["properties"]
        assert inputs["properties"]["operation"]["type"] == "string"
        assert "enum" in inputs["properties"]["operation"]
        assert "prepare" in inputs["properties"]["operation"]["enum"]
        assert "train" in inputs["properties"]["operation"]["enum"]
        assert "evaluate" in inputs["properties"]["operation"]["enum"]
        assert "status" in inputs["properties"]["operation"]["enum"]

    def test_agent_outputs(self, agent):
        """Test that agent has correct output schema."""
        outputs = agent.metadata.outputs
        
        assert "properties" in outputs
        assert "val_bpb" in outputs["properties"]
        assert "status" in outputs["properties"]
        assert "logs" in outputs["properties"]

    @pytest.mark.asyncio
    async def test_run_prepare_operation(self, agent):
        """Test prepare operation."""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="Prepared successfully", stderr="")
            
            result = await agent.run({"operation": "prepare"})
            
            assert result["status"] in ["success", "failed"]
            mock_run.assert_called_once()

    @pytest.mark.asyncio
    async def test_run_train_operation(self, agent):
        """Test train operation."""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0, 
                stdout='{"val_bpb": 0.75, "train_loss": 0.5}',
                stderr=""
            )
            
            result = await agent.run({
                "operation": "train",
                "experiment_description": "Test experiment"
            })
            
            assert "status" in result

    @pytest.mark.asyncio
    async def test_run_invalid_operation(self, agent):
        """Test invalid operation returns error."""
        result = await agent.run({"operation": "invalid_op"})
        
        assert result["status"] == "error"
        assert "Unknown operation" in result["error"]

    @pytest.mark.asyncio
    async def test_run_status_operation(self, agent):
        """Test status operation."""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0, 
                stdout='{"current_step": 100, "total_steps": 1000}',
                stderr=""
            )
            
            result = await agent.run({"operation": "status"})
            
            assert "status" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
