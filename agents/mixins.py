"""
Self-Improvement Mixin for Agents

This module provides the SelfImprovementMixin class that allows agents to
use the AutoResearch system for autonomous self-improvement.

Agents inheriting from this mixin can:
- Run experiments to test improvements
- Evaluate performance changes
- Automatically iterate on their own implementation

Usage:
    from agents.mixins import SelfImprovementMixin
    
    class MyAgent(BaseAgent, SelfImprovementMixin):
        def __init__(self, config=None):
            super().__init__(config)
            self.init_self_improvement()
        
        async def run(self, inputs, context):
            # Normal agent logic
            result = await self._execute(inputs, context)
            
            # Optionally try self-improvement
            if inputs.get("auto_improve", False):
                improvement_result = await self.improve(
                    metric_target={"val_bpb": 0.95},
                    experiment_description="Optimize agent performance"
                )
                if improvement_result.get("improved"):
                    result["improvement_applied"] = improvement_result
            
            return result
"""

import os
import sys
from typing import Dict, Any, Optional
from pathlib import Path
from datetime import datetime


class SelfImprovementMixin:
    """
    Mixin class that provides autonomous self-improvement capabilities.
    
    Agents can use this to run experiments, evaluate performance,
    and iterate on their own code for improvement.
    """
    
    def init_self_improvement(self) -> None:
        """Initialize self-improvement components."""
        # Find the autoresearch agent directory
        agents_dir = Path(__file__).parent.parent
        self._autoresearch_dir = agents_dir / "autoresearch"
        self._improvement_enabled = self._autoresearch_dir.exists()
        
        if not self._improvement_enabled:
            print(f"Warning: AutoResearch not found at {self._autoresearch_dir}")
    
    async def improve(
        self,
        metric_target: Optional[Dict[str, float]] = None,
        experiment_description: str = "",
        max_iterations: int = 5
    ) -> Dict[str, Any]:
        """
        Run self-improvement experiments.
        
        Args:
            metric_target: Target metrics to achieve (e.g., {"val_bpb": 0.95})
            experiment_description: Description of what to improve
            max_iterations: Maximum number of improvement iterations
            
        Returns:
            Dictionary with improvement results
        """
        if not self._improvement_enabled:
            return {
                "improved": False,
                "reason": "AutoResearch not available",
                "iterations": 0
            }
        
        results = {
            "improved": False,
            "baseline": None,
            "final": None,
            "iterations": 0,
            "experiments": []
        }
        
        # Run baseline experiment
        baseline = await self._run_improvement_experiment(
            description=f"Baseline: {experiment_description}"
        )
        results["baseline"] = baseline.get("val_bpb")
        
        # Try improvements
        for i in range(max_iterations):
            experiment = await self._run_improvement_experiment(
                description=f"Iteration {i+1}: {experiment_description}"
            )
            results["experiments"].append(experiment)
            results["iterations"] = i + 1
            
            # Check if improved
            if baseline.get("val_bpb") and experiment.get("val_bpb"):
                if experiment["val_bpb"] < baseline["val_bpb"]:
                    results["improved"] = True
                    results["final"] = experiment["val_bpb"]
                    break
        
        return results
    
    async def _run_improvement_experiment(self, description: str) -> Dict[str, Any]:
        """Run a single improvement experiment."""
        try:
            from agents.autoresearch.agent import AutoResearchAgent
            
            agent = AutoResearchAgent()
            result = await agent.run({
                "operation": "train",
                "experiment_description": description,
                "config": {}
            })
            return result
        except Exception as e:
            return {"error": str(e), "val_bpb": None}
    
    async def evaluate_performance(self) -> Dict[str, Any]:
        """
        Evaluate current agent performance.
        
        Returns:
            Performance metrics
        """
        if not self._improvement_enabled:
            return {"available": False}
        
        # Run evaluation
        try:
            from agents.autoresearch.agent import AutoResearchAgent
            
            agent = AutoResearchAgent()
            result = await agent.run({
                "operation": "evaluate"
            })
            return result
        except Exception as e:
            return {"error": str(e)}
    
    def check_system_ready(self) -> Dict[str, bool]:
        """
        Check if self-improvement system is ready.
        
        Returns:
            Dictionary with system status
        """
        if not self._improvement_enabled:
            return {
                "available": False,
                "reason": "AutoResearch not installed"
            }
        
        # Check data
        data_dir = Path.home() / ".cache" / "autoresearch" / "data"
        tokenizer_dir = Path.home() / ".cache" / "autoresearch" / "tokenizer"
        
        return {
            "available": True,
            "data_ready": data_dir.exists() and any(data_dir.glob("*.parquet")),
            "tokenizer_ready": tokenizer_dir.exists()
        }
