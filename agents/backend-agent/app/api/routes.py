"""
API Routes
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, Any, Optional

from app.agents.orchestrator import orchestrator
from app.utils.validators import TaskInput, WorkflowInput
from app.utils.logger import setup_logger
from app.database.operations import db_operations
from app.database.models import TaskRecord, TaskStatus, AgentType

logger = setup_logger(__name__)

api_router = APIRouter()


@api_router.post("/agent/execute")
async def execute_agent_task(
    task_input: TaskInput,
    background_tasks: BackgroundTasks
) -> Dict[str, Any]:
    """
    Execute a task using the appropriate agent
    
    Args:
        task_input: Task input with task description and optional agent type
        background_tasks: FastAPI background tasks
        
    Returns:
        Task execution result
    """
    try:
        logger.info(f"Received task: {task_input.task[:100]}...")
        
        # Execute task
        result = await orchestrator.execute_task(
            task=task_input.task,
            agent_type=task_input.agent_type,
            context=task_input.context
        )
        
        # Save task to database in background
        if result.get("success"):
            task_record = TaskRecord(
                task_id=result.get("task_id", "unknown"),
                agent_type=AgentType(task_input.agent_type or "orchestrator"),
                task_description=task_input.task,
                status=TaskStatus.COMPLETED,
                input_data={"task": task_input.task, "context": task_input.context},
                output_data=result
            )
            background_tasks.add_task(db_operations.create_task, task_record)
        
        return {
            "success": True,
            "data": result
        }
    except Exception as e:
        logger.error(f"Task execution failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.post("/workflow/run")
async def run_workflow(workflow_input: WorkflowInput) -> Dict[str, Any]:
    """
    Execute a multi-step workflow
    
    Args:
        workflow_input: Workflow configuration with steps
        
    Returns:
        Workflow execution result
    """
    try:
        logger.info(f"Running workflow: {workflow_input.workflow_type}")
        
        # Build workflow steps based on type
        steps = []
        
        if workflow_input.workflow_type == "data_processing":
            # Example data processing workflow
            steps = [
                {"agent_type": "validation", "task": "Validate input data structure"},
                {"agent_type": "database", "task": "Query relevant data from database"},
                {"agent_type": "validation", "task": "Format and analyze the results"}
            ]
        elif workflow_input.workflow_type == "api_workflow":
            # Example API workflow
            steps = [
                {"agent_type": "validation", "task": "Validate API request parameters"},
                {"agent_type": "api", "task": "Make API request to external service"},
                {"agent_type": "database", "task": "Store API response in database"}
            ]
        else:
            # Custom workflow from input
            steps = workflow_input.input_data.get("steps", [])
        
        # Execute workflow
        result = await orchestrator.execute_workflow(steps)
        
        return {
            "success": True,
            "data": result
        }
    except Exception as e:
        logger.error(f"Workflow execution failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/agents/list")
async def list_agents() -> Dict[str, Any]:
    """
    List available agents
    
    Returns:
        List of available agents and their descriptions
    """
    return {
        "success": True,
        "agents": [
            {
                "name": "api",
                "description": "Handles API interactions and HTTP requests"
            },
            {
                "name": "database",
                "description": "Manages database queries and operations"
            },
            {
                "name": "validation",
                "description": "Validates and analyzes data"
            },
            {
                "name": "orchestrator",
                "description": "Coordinates multiple agents for complex tasks"
            }
        ]
    }


@api_router.get("/tasks/{task_id}")
async def get_task_status(task_id: str) -> Dict[str, Any]:
    """
    Get task status and results
    
    Args:
        task_id: Task identifier
        
    Returns:
        Task details
    """
    try:
        task = await db_operations.get_task(task_id)
        
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        return {
            "success": True,
            "data": task.dict()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get task: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/tasks")
async def list_tasks(
    limit: int = 10,
    status: Optional[str] = None
) -> Dict[str, Any]:
    """
    List recent tasks
    
    Args:
        limit: Maximum number of tasks to return
        status: Optional status filter
        
    Returns:
        List of tasks
    """
    try:
        status_filter = TaskStatus(status) if status else None
        tasks = await db_operations.list_tasks(limit, status_filter)
        
        return {
            "success": True,
            "count": len(tasks),
            "data": [task.dict() for task in tasks]
        }
    except Exception as e:
        logger.error(f"Failed to list tasks: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.post("/database/query")
async def query_database(
    table: str,
    filters: Optional[Dict[str, Any]] = None,
    limit: int = 100
) -> Dict[str, Any]:
    """
    Direct database query endpoint
    
    Args:
        table: Table name
        filters: Optional filters
        limit: Result limit
        
    Returns:
        Query results
    """
    try:
        results = await db_operations.query(table, filters, limit)
        
        return {
            "success": True,
            "count": len(results),
            "data": results
        }
    except Exception as e:
        logger.error(f"Database query failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))