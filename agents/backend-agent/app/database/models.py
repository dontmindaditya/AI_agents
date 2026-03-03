"""
Database Models
"""
from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional
from datetime import datetime
from enum import Enum


class TaskStatus(str, Enum):
    """Task status enumeration"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class AgentType(str, Enum):
    """Agent type enumeration"""
    API = "api"
    DATABASE = "database"
    VALIDATION = "validation"
    ORCHESTRATOR = "orchestrator"


class TaskRecord(BaseModel):
    """Task record model"""
    id: Optional[str] = None
    task_id: str
    agent_type: AgentType
    task_description: str
    status: TaskStatus = TaskStatus.PENDING
    input_data: Dict[str, Any] = Field(default_factory=dict)
    output_data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    execution_time: Optional[float] = None
    
    class Config:
        use_enum_values = True


class ConversationMessage(BaseModel):
    """Conversation message model"""
    id: Optional[str] = None
    session_id: str
    role: str  # 'user', 'assistant', 'system'
    content: str
    metadata: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class WorkflowExecution(BaseModel):
    """Workflow execution model"""
    id: Optional[str] = None
    workflow_id: str
    workflow_type: str
    status: TaskStatus = TaskStatus.PENDING
    input_data: Dict[str, Any] = Field(default_factory=dict)
    output_data: Optional[Dict[str, Any]] = None
    steps_completed: List[str] = Field(default_factory=list)
    current_step: Optional[str] = None
    error_message: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    class Config:
        use_enum_values = True


class AgentLog(BaseModel):
    """Agent execution log model"""
    id: Optional[str] = None
    task_id: str
    agent_type: AgentType
    log_level: str  # 'info', 'warning', 'error', 'debug'
    message: str
    details: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime] = None
    
    class Config:
        use_enum_values = True


class APICallRecord(BaseModel):
    """API call record model"""
    id: Optional[str] = None
    task_id: str
    method: str
    url: str
    request_headers: Optional[Dict[str, str]] = None
    request_body: Optional[Dict[str, Any]] = None
    response_status: Optional[int] = None
    response_body: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    execution_time: Optional[float] = None
    created_at: Optional[datetime] = None


class DatabaseOperation(BaseModel):
    """Database operation record model"""
    id: Optional[str] = None
    task_id: str
    operation_type: str  # 'select', 'insert', 'update', 'delete'
    table_name: str
    query: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None
    rows_affected: Optional[int] = None
    error_message: Optional[str] = None
    execution_time: Optional[float] = None
    created_at: Optional[datetime] = None