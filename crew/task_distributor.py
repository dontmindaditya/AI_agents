"""Task Distributor

This module handles task distribution to agents in the CrewAI framework.
"""

from typing import List, Dict, Any
from crewai import Task
from agents.base_agent import BaseAgent
from utils.logger import setup_logger

logger = setup_logger(__name__)


class TaskDistributor:
    """Distributes tasks to agents"""
    
    @staticmethod
    def create_task(
        description: str,
        agent: BaseAgent,
        expected_output: str = "Task completed successfully"
    ) -> Task:
        """Create task"""
        return Task(
            description=description,
            agent=agent.crew_agent,
            expected_output=expected_output
        )
    
    @staticmethod
    def distribute_tasks(
        agents: List[BaseAgent],
        task_breakdown: List[Dict[str, Any]]
    ) -> List[Task]:
        """Distribute tasks"""
        tasks = []
        
        agent_map = {agent.agent_type: agent for agent in agents}
        
        for task_info in task_breakdown:
            agent_type = task_info.get("agent")
            task_desc = task_info.get("task")
            
            if agent_type in agent_map:
                task = TaskDistributor.create_task(
                    description=task_desc,
                    agent=agent_map[agent_type]
                )
                tasks.append(task)
        
        logger.info(f"✅ Distributed {len(tasks)} tasks")
        return tasks