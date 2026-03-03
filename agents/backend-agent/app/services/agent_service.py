"""
Agent Service - Manage agent lifecycle and execution
"""
from typing import Dict, Any, Optional, List
from datetime import datetime
import asyncio

from app.agents.api_agent import api_agent
from app.agents.database_agent import database_agent
from app.agents.validation_agent import validation_agent
from app.agents.orchestrator import orchestrator
from app.database.operations import db_operations
from app.database.models import TaskRecord, TaskStatus, AgentType
from app.utils.logger import setup_logger
from app.utils.helpers import generate_task_id

logger = setup_logger(__name__)


class AgentService:
    """Service for managing agents and their execution"""
    
    def __init__(self):
        self.agents = {
            "api": api_agent,
            "database": database_agent,
            "validation": validation_agent
        }
        self.active_tasks: Dict[str, asyncio.Task] = {}
    
    def get_agent(self, agent_type: str):
        """Get agent by type"""
        return self.agents.get(agent_type)
    
    def list_agents(self) -> List[Dict[str, str]]:
        """List all available agents"""
        return [
            {
                "type": agent_type,
                "name": agent.name,
                "description": agent.description
            }
            for agent_type, agent in self.agents.items()
        ]
    
    async def execute_task(
        self,
        task: str,
        agent_type: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        save_to_db: bool = True
    ) -> Dict[str, Any]:
        """
        Execute a task using appropriate agent
        
        Args:
            task: Task description
            agent_type: Agent type to use
            context: Optional context
            save_to_db: Whether to save task to database
            
        Returns:
            Task execution result
        """
        task_id = generate_task_id()
        
        try:
            logger.info(f"Executing task {task_id}")
            
            # Save initial task record
            if save_to_db:
                task_record = TaskRecord(
                    task_id=task_id,
                    agent_type=AgentType(agent_type or "orchestrator"),
                    task_description=task,
                    status=TaskStatus.IN_PROGRESS,
                    input_data={"task": task, "context": context or {}}
                )
                await db_operations.create_task(task_record)
            
            # Execute task
            result = await orchestrator.execute_task(
                task=task,
                agent_type=agent_type,
                context=context
            )
            
            # Update task record
            if save_to_db:
                await db_operations.update_task_status(
                    task_id=task_id,
                    status=TaskStatus.COMPLETED if result.get("result", {}).get("success") else TaskStatus.FAILED,
                    output_data=result
                )
            
            return result
        except Exception as e:
            logger.error(f"Task {task_id} failed: {e}")
            
            # Update task as failed
            if save_to_db:
                await db_operations.update_task_status(
                    task_id=task_id,
                    status=TaskStatus.FAILED,
                    error_message=str(e)
                )
            
            return {
                "task_id": task_id,
                "success": False,
                "error": str(e)
            }
    
    async def execute_task_async(
        self,
        task: str,
        agent_type: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Execute task asynchronously in background
        
        Args:
            task: Task description
            agent_type: Agent type
            context: Optional context
            
        Returns:
            Task ID for tracking
        """
        task_id = generate_task_id()
        
        # Create background task
        async_task = asyncio.create_task(
            self.execute_task(task, agent_type, context, save_to_db=True)
        )
        
        # Store task reference
        self.active_tasks[task_id] = async_task
        
        logger.info(f"Started async task {task_id}")
        
        return task_id
    
    async def get_task_status(self, task_id: str) -> Optional[TaskRecord]:
        """
        Get task status from database
        
        Args:
            task_id: Task ID
            
        Returns:
            Task record or None
        """
        return await db_operations.get_task(task_id)
    
    async def cancel_task(self, task_id: str) -> bool:
        """
        Cancel an active task
        
        Args:
            task_id: Task ID
            
        Returns:
            Success status
        """
        if task_id in self.active_tasks:
            task = self.active_tasks[task_id]
            task.cancel()
            
            # Update database
            await db_operations.update_task_status(
                task_id=task_id,
                status=TaskStatus.CANCELLED
            )
            
            logger.info(f"Cancelled task {task_id}")
            return True
        
        return False
    
    async def list_active_tasks(self) -> List[str]:
        """
        List all active task IDs
        
        Returns:
            List of task IDs
        """
        # Clean up completed tasks
        completed = [
            task_id for task_id, task in self.active_tasks.items()
            if task.done()
        ]
        
        for task_id in completed:
            del self.active_tasks[task_id]
        
        return list(self.active_tasks.keys())
    
    async def get_agent_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about agent usage
        
        Returns:
            Statistics dictionary
        """
        try:
            # Get tasks from database
            tasks = await db_operations.list_tasks(limit=100)
            
            stats = {
                "total_tasks": len(tasks),
                "by_agent": {},
                "by_status": {},
                "average_execution_time": 0
            }
            
            # Calculate statistics
            execution_times = []
            for task in tasks:
                # Count by agent
                agent_type = task.agent_type.value
                stats["by_agent"][agent_type] = stats["by_agent"].get(agent_type, 0) + 1
                
                # Count by status
                status = task.status.value
                stats["by_status"][status] = stats["by_status"].get(status, 0) + 1
                
                # Collect execution times
                if task.execution_time:
                    execution_times.append(task.execution_time)
            
            # Calculate average execution time
            if execution_times:
                stats["average_execution_time"] = sum(execution_times) / len(execution_times)
            
            return stats
        except Exception as e:
            logger.error(f"Failed to get agent statistics: {e}")
            return {"error": str(e)}
    
    async def cleanup_old_tasks(self, days: int = 7) -> int:
        """
        Clean up old completed tasks
        
        Args:
            days: Delete tasks older than this many days
            
        Returns:
            Number of tasks deleted
        """
        try:
            # This is a placeholder - implement based on your database
            logger.info(f"Cleaning up tasks older than {days} days")
            # TODO: Implement actual cleanup logic
            return 0
        except Exception as e:
            logger.error(f"Failed to cleanup old tasks: {e}")
            return 0


# Global instance
agent_service = AgentService()