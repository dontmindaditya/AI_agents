"""
AutoResearch Agent

This agent provides autonomous LLM research capabilities. It can:
- Run experiments with the training script
- Evaluate model performance
- Log results automatically
- Iterate on the model architecture

The agent wraps the autoresearch system which allows autonomous
experimentation with LLM training.
"""

import os
import subprocess
import json
from typing import Dict, Any, Optional
from pathlib import Path

from ..base import BaseAgent, AgentMetadata


class AutoResearchAgent(BaseAgent):
    """
    Autonomous LLM Research Agent.
    
    This agent provides an interface to the autoresearch system for
    autonomous LLM training experiments. It can run experiments,
    evaluate results, and iterate on model improvements.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.agent_dir = Path(__file__).parent / "autoresearch"
    
    @property
    def metadata(self) -> AgentMetadata:
        return AgentMetadata(
            name="AutoResearch Agent",
            description="Autonomous LLM research agent. Runs experiments, evaluates performance, and iterates on model improvements.",
            version="1.0.0",
            author="AgentHub",
            tags=["research", "llm", "training", "autonomous"],
            inputs={
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": ["prepare", "train", "evaluate", "status"],
                        "description": "Operation to perform"
                    },
                    "config": {
                        "type": "object",
                        "description": "Experiment configuration",
                        "properties": {
                            "depth": {"type": "integer", "description": "Model depth"},
                            "batch_size": {"type": "integer", "description": "Batch size"},
                            "learning_rate": {"type": "number", "description": "Learning rate"}
                        }
                    },
                    "experiment_description": {
                        "type": "string",
                        "description": "Description of the experiment"
                    }
                },
                "required": ["operation"]
            },
            outputs={
                "type": "object",
                "properties": {
                    "val_bpb": {"type": "number", "description": "Validation bits per byte"},
                    "status": {"type": "string", "description": "Experiment status"},
                    "logs": {"type": "string", "description": "Experiment logs"},
                    "results": {"type": "object", "description": "Detailed results"}
                }
            }
        )

    async def run(self, inputs: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute the autoresearch operation.
        
        Args:
            inputs: Operation and configuration
            context: Optional context
            
        Returns:
            Experiment results
        """
        operation = inputs.get("operation", "status")
        config = inputs.get("config", {})
        
        if operation == "prepare":
            return await self._prepare_data()
        elif operation == "train":
            return await self._run_experiment(config, inputs.get("experiment_description", ""))
        elif operation == "evaluate":
            return await self._evaluate()
        elif operation == "status":
            return await self._get_status()
        else:
            return {
                "status": "error",
                "error": f"Unknown operation: {operation}"
            }

    def _prepare_data(self) -> Dict[str, Any]:
        """Prepare data and tokenizer."""
        try:
            result = subprocess.run(
                ["uv", "run", "prepare.py"],
                cwd=str(self.agent_dir),
                capture_output=True,
                text=True,
                timeout=300
            )
            return {
                "status": "success" if result.returncode == 0 else "failed",
                "logs": result.stdout + result.stderr,
                "val_bpb": None
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }

    def _run_experiment(self, config: Dict[str, Any], description: str) -> Dict[str, Any]:
        """Run a training experiment."""
        try:
            # Apply config modifications to train.py if provided
            if config:
                self._modify_train_config(config)
            
            # Run training
            result = subprocess.run(
                ["uv", "run", "train.py"],
                cwd=str(self.agent_dir),
                capture_output=True,
                text=True,
                timeout=600  # 10 minutes max
            )
            
            # Parse results
            val_bpb = self._parse_val_bpb(result.stdout + result.stderr)
            
            return {
                "status": "success" if result.returncode == 0 else "failed",
                "logs": result.stdout + result.stderr,
                "val_bpb": val_bpb,
                "experiment_description": description
            }
        except subprocess.TimeoutExpired:
            return {
                "status": "timeout",
                "error": "Experiment exceeded time limit"
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }

    def _evaluate(self) -> Dict[str, Any]:
        """Evaluate current model."""
        return {
            "status": "success",
            "message": "Evaluation not implemented - run train to evaluate"
        }

    def _get_status(self) -> Dict[str, Any]:
        """Get system status."""
        data_dir = Path.home() / ".cache" / "autoresearch" / "data"
        tokenizer_dir = Path.home() / ".cache" / "autoresearch" / "tokenizer"
        
        data_ready = data_dir.exists() and any(data_dir.glob("*.parquet"))
        tokenizer_ready = tokenizer_dir.exists() and (tokenizer_dir / "tokenizer.pkl").exists()
        
        return {
            "status": "ready" if (data_ready and tokenizer_ready) else "not_ready",
            "data_downloaded": data_ready,
            "tokenizer_trained": tokenizer_ready,
            "message": "System ready for experiments" if (data_ready and tokenizer_ready) else "Run prepare operation first"
        }

    def _modify_train_config(self, config: Dict[str, Any]) -> None:
        """Modify train.py hyperparameters."""
        train_file = self.agent_dir / "train.py"
        if not train_file.exists():
            return
        
        content = train_file.read_text()
        
        # Modify depth
        if "depth" in config:
            content = content.replace("DEPTH = 8", f"DEPTH = {config['depth']}")
        
        # Modify batch size
        if "batch_size" in config:
            content = content.replace("DEVICE_BATCH_SIZE = 128", f"DEVICE_BATCH_SIZE = {config['batch_size']}")
        
        # Modify learning rates
        if "embedding_lr" in config:
            content = content.replace("EMBEDDING_LR = 0.6", f"EMBEDDING_LR = {config['embedding_lr']}")
        
        if "matrix_lr" in config:
            content = content.replace("MATRIX_LR = 0.04", f"MATRIX_LR = {config['matrix_lr']}")
        
        train_file.write_text(content)

    def _parse_val_bpb(self, output: str) -> Optional[float]:
        """Parse validation bits per byte from output."""
        for line in output.split("\n"):
            if "val_bpb:" in line:
                try:
                    return float(line.split(":")[1].strip())
                except (IndexError, ValueError):
                    pass
        return None

    def validate_inputs(self, inputs: Dict[str, Any]) -> bool:
        """Validate inputs."""
        operation = inputs.get("operation")
        valid_operations = ["prepare", "train", "evaluate", "status"]
        return operation in valid_operations
