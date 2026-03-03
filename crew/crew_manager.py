"""Crew Manager"""

from typing import List, Dict, Any
from crewai import Crew, Task
from agents.base_agent import BaseAgent
from utils.logger import get_logger

logger = get_logger(__name__)


class CrewManager:
    """Manages CrewAI crews"""
    
    def __init__(self):
        self.active_crews: Dict[str, Crew] = {}
    
    def create_crew(
        self,
        project_id: str,
        agents: List[BaseAgent],
        tasks: List[Task]
    ) -> Crew:
        """Create crew"""
        try:
            crew = Crew(
                agents=[agent.crew_agent for agent in agents],
                tasks=tasks,
                verbose=True
            )
            
            self.active_crews[project_id] = crew
            logger.info(f"✅ Crew created: {project_id}")
            
            return crew
            
        except Exception as e:
            logger.error(f"Failed to create crew: {e}")
            raise
    
    async def execute_crew(self, project_id: str) -> Dict[str, Any]:
        """Execute crew"""
        if project_id not in self.active_crews:
            raise ValueError(f"Crew not found: {project_id}")
        
        crew = self.active_crews[project_id]
        result = crew.kickoff()
        
        return {"result": result}
    
    def remove_crew(self, project_id: str):
        """Remove crew"""
        if project_id in self.active_crews:
            del self.active_crews[project_id]
            logger.info(f"Crew removed: {project_id}")