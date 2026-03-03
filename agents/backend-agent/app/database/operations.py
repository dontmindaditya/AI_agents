"""
Database Operations
"""
from typing import Any, Dict, List, Optional
from datetime import datetime

from app.database.supabase_client import supabase_client
from app.database.models import (
    TaskRecord, ConversationMessage, WorkflowExecution,
    AgentLog, APICallRecord, DatabaseOperation, TaskStatus
)
from app.utils.logger import setup_logger
from app.utils.helpers import generate_task_id

logger = setup_logger(__name__)


class DatabaseOperations:
    """Database operations handler"""
    
    def __init__(self):
        self.client = supabase_client.client
    
    # Task Operations
    async def create_task(self, task_data: TaskRecord) -> Optional[TaskRecord]:
        """Create a new task record"""
        try:
            data = task_data.dict(exclude_none=True, exclude={'id'})
            data['created_at'] = datetime.utcnow().isoformat()
            data['updated_at'] = datetime.utcnow().isoformat()
            
            result = self.client.table('tasks').insert(data).execute()
            
            if result.data:
                logger.info(f"Task created: {task_data.task_id}")
                return TaskRecord(**result.data[0])
            return None
        except Exception as e:
            logger.error(f"Failed to create task: {e}")
            return None
    
    async def get_task(self, task_id: str) -> Optional[TaskRecord]:
        """Get task by ID"""
        try:
            result = self.client.table('tasks').select('*').eq('task_id', task_id).execute()
            
            if result.data:
                return TaskRecord(**result.data[0])
            return None
        except Exception as e:
            logger.error(f"Failed to get task: {e}")
            return None
    
    async def update_task_status(
        self,
        task_id: str,
        status: TaskStatus,
        output_data: Optional[Dict[str, Any]] = None,
        error_message: Optional[str] = None
    ) -> bool:
        """Update task status"""
        try:
            update_data = {
                'status': status.value,
                'updated_at': datetime.utcnow().isoformat()
            }
            
            if output_data:
                update_data['output_data'] = output_data
            
            if error_message:
                update_data['error_message'] = error_message
            
            if status == TaskStatus.COMPLETED or status == TaskStatus.FAILED:
                update_data['completed_at'] = datetime.utcnow().isoformat()
            
            result = self.client.table('tasks').update(update_data).eq('task_id', task_id).execute()
            
            logger.info(f"Task {task_id} updated to {status}")
            return True
        except Exception as e:
            logger.error(f"Failed to update task status: {e}")
            return False
    
    async def list_tasks(
        self,
        limit: int = 10,
        status: Optional[TaskStatus] = None
    ) -> List[TaskRecord]:
        """List tasks with optional filtering"""
        try:
            query = self.client.table('tasks').select('*')
            
            if status:
                query = query.eq('status', status.value)
            
            result = query.order('created_at', desc=True).limit(limit).execute()
            
            if result.data:
                return [TaskRecord(**item) for item in result.data]
            return []
        except Exception as e:
            logger.error(f"Failed to list tasks: {e}")
            return []
    
    # Conversation Operations
    async def save_message(self, message: ConversationMessage) -> Optional[ConversationMessage]:
        """Save conversation message"""
        try:
            data = message.dict(exclude_none=True, exclude={'id'})
            data['created_at'] = datetime.utcnow().isoformat()
            
            result = self.client.table('conversations').insert(data).execute()
            
            if result.data:
                logger.info(f"Message saved for session: {message.session_id}")
                return ConversationMessage(**result.data[0])
            return None
        except Exception as e:
            logger.error(f"Failed to save message: {e}")
            return None
    
    async def get_conversation_history(
        self,
        session_id: str,
        limit: int = 50
    ) -> List[ConversationMessage]:
        """Get conversation history"""
        try:
            result = self.client.table('conversations')\
                .select('*')\
                .eq('session_id', session_id)\
                .order('created_at', desc=False)\
                .limit(limit)\
                .execute()
            
            if result.data:
                return [ConversationMessage(**item) for item in result.data]
            return []
        except Exception as e:
            logger.error(f"Failed to get conversation history: {e}")
            return []
    
    # Workflow Operations
    async def create_workflow(self, workflow: WorkflowExecution) -> Optional[WorkflowExecution]:
        """Create workflow execution record"""
        try:
            data = workflow.dict(exclude_none=True, exclude={'id'})
            data['created_at'] = datetime.utcnow().isoformat()
            data['updated_at'] = datetime.utcnow().isoformat()
            
            result = self.client.table('workflows').insert(data).execute()
            
            if result.data:
                logger.info(f"Workflow created: {workflow.workflow_id}")
                return WorkflowExecution(**result.data[0])
            return None
        except Exception as e:
            logger.error(f"Failed to create workflow: {e}")
            return None
    
    async def update_workflow_step(
        self,
        workflow_id: str,
        current_step: str,
        steps_completed: List[str]
    ) -> bool:
        """Update workflow execution step"""
        try:
            update_data = {
                'current_step': current_step,
                'steps_completed': steps_completed,
                'updated_at': datetime.utcnow().isoformat()
            }
            
            result = self.client.table('workflows')\
                .update(update_data)\
                .eq('workflow_id', workflow_id)\
                .execute()
            
            logger.info(f"Workflow {workflow_id} updated to step: {current_step}")
            return True
        except Exception as e:
            logger.error(f"Failed to update workflow step: {e}")
            return False
    
    # Log Operations
    async def create_log(self, log: AgentLog) -> bool:
        """Create agent log entry"""
        try:
            data = log.dict(exclude_none=True, exclude={'id'})
            data['created_at'] = datetime.utcnow().isoformat()
            
            result = self.client.table('agent_logs').insert(data).execute()
            return True
        except Exception as e:
            logger.error(f"Failed to create log: {e}")
            return False
    
    # Generic Operations
    async def query(
        self,
        table: str,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Generic query operation"""
        try:
            query = self.client.table(table).select('*')
            
            if filters:
                for key, value in filters.items():
                    query = query.eq(key, value)
            
            result = query.limit(limit).execute()
            
            if result.data:
                return result.data
            return []
        except Exception as e:
            logger.error(f"Query failed on table {table}: {e}")
            return []
    
    async def insert(self, table: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Generic insert operation"""
        try:
            result = self.client.table(table).insert(data).execute()
            
            if result.data:
                logger.info(f"Record inserted into {table}")
                return result.data[0]
            return None
        except Exception as e:
            logger.error(f"Insert failed on table {table}: {e}")
            return None
    
    async def update(
        self,
        table: str,
        data: Dict[str, Any],
        filters: Dict[str, Any]
    ) -> bool:
        """Generic update operation"""
        try:
            query = self.client.table(table).update(data)
            
            for key, value in filters.items():
                query = query.eq(key, value)
            
            result = query.execute()
            logger.info(f"Record updated in {table}")
            return True
        except Exception as e:
            logger.error(f"Update failed on table {table}: {e}")
            return False
    
    async def delete(self, table: str, filters: Dict[str, Any]) -> bool:
        """Generic delete operation"""
        try:
            query = self.client.table(table).delete()
            
            for key, value in filters.items():
                query = query.eq(key, value)
            
            result = query.execute()
            logger.info(f"Record deleted from {table}")
            return True
        except Exception as e:
            logger.error(f"Delete failed on table {table}: {e}")
            return False


# Global instance
db_operations = DatabaseOperations()