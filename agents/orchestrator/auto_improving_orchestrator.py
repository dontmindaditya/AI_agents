"""
Auto-Improving Orchestrator Agent

This agent coordinates multiple sub-agents and uses AutoResearch
to autonomously improve the entire system.
"""

import os
import sys
from typing import Dict, Any, Optional, List
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from agents.base import BaseAgent, AgentMetadata
from agents.mixins import SelfImprovementMixin
from agents.registry import agent_registry


class AutoImprovingOrchestrator(BaseAgent, SelfImprovementMixin):
    """
    An orchestrator agent that can improve itself and its sub-agents.
    
    This agent coordinates the work of multiple agents and uses
    AutoResearch to run experiments and optimize the system.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.init_self_improvement()
        self._sub_agents: Dict[str, BaseAgent] = {}
    
    @property
    def metadata(self) -> AgentMetadata:
        return AgentMetadata(
            name="Auto-Improving Orchestrator",
            description="Orchestrates multiple agents and can autonomously improve the entire system through experiments.",
            version="1.0.0",
            author="AgentHub",
            tags=["orchestrator", "autonomous", "self-improvement", "multi-agent"],
            inputs={
                "type": "object",
                "properties": {
                    "task": {"type": "string", "description": "Main task to accomplish"},
                    "agent_ids": {"type": "array", "items": {"type": "string"}, "description": "Agents to use"},
                    "auto_improve": {"type": "boolean", "description": "Enable system improvement", "default": False},
                    "workflow": {"type": "array", "description": "Workflow of agent executions"}
                },
                "required": ["task"]
            },
            outputs={
                "type": "object",
                "properties": {
                    "results": {"type": "object", "description": "Results from all agents"},
                    "system_improvement": {"type": "object", "description": "Improvement results if enabled"}
                }
            }
        )
    
    async def run(self, inputs: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute the orchestrator.
        
        Args:
            inputs: Task and configuration
            context: Optional context
        """
        task = inputs.get("task", "")
        agent_ids = inputs.get("agent_ids", [])
        workflow = inputs.get("workflow", [])
        auto_improve = inputs.get("auto_improve", False)
        
        results = {
            "task": task,
            "agent_results": {},
            "workflow_results": []
        }
        
        # Execute agents
        if workflow:
            # Execute workflow
            current_context = context or {}
            for step in workflow:
                agent_id = step.get("agent_id")
                action = step.get("action", "run")
                
                agent_result = await self._execute_agent(agent_id, step.get("inputs", {}), current_context)
                results["workflow_results"].append({
                    "agent_id": agent_id,
                    "result": agent_result
                })
                current_context[agent_id] = agent_result
        else:
            # Execute specified agents
            for agent_id in agent_ids:
                agent_result = await self._execute_agent(agent_id, inputs, context)
                results["agent_results"][agent_id] = agent_result
        
        # Run system improvement if enabled
        if auto_improve:
            improvement = await self._improve_system(task, results)
            results["system_improvement"] = improvement
        
        return results
    
    async def _execute_agent(self, agent_id: str, inputs: Dict[str, Any], context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Execute a sub-agent."""
        try:
            agent_class = agent_registry.get_agent_class(agent_id)
            if not agent_class:
                return {"error": f"Agent {agent_id} not found"}
            
            agent = agent_class()
            return await agent.run(inputs, context)
        except Exception as e:
            return {"error": str(e)}
    
    async def _improve_system(self, task: str, current_results: Dict[str, Any]) -> Dict[str, Any]:
        """Run system improvement experiments."""
        # Analyze current results to find improvement opportunities
        improvements = {
            "analyzed_task": task,
            "experiments": [],
            "recommendations": []
        }
        
        # Check if improvement system is available
        system_status = self.check_system_ready()
        if not system_status.get("available"):
            return {
                "improved": False,
                "reason": "AutoResearch not available",
                "status": system_status
            }
        
        # Run improvement experiment
        experiment_result = await self.improve(
            experiment_description=f"Improve orchestrator for task: {task[:50]}",
            max_iterations=3
        )
        
        improvements["experiments"].append(experiment_result)
        
        if experiment_result.get("improved"):
            improvements["recommendations"].append({
                "type": "experiment_success",
                "val_bpb_improvement": experiment_result.get("final") and experiment_result.get("baseline") and 
                    experiment_result.get("baseline") - experiment_result.get("final")
            })
        
        return improvements
    
    def get_available_agents(self) -> List[Dict[str, Any]]:
        """Get list of available sub-agents."""
        return agent_registry.get_all_agents()
    
    def validate_inputs(self, inputs: Dict[str, Any]) -> bool:
        """Validate inputs."""
        return "task" in inputs
