"""
Database Tools for Agents
"""
from typing import Any, Dict, List, Optional
from langchain.tools import BaseTool

from app.database.operations import db_operations
from app.utils.logger import setup_logger
from app.utils.validators import validate_sql_injection

logger = setup_logger(__name__)


class DatabaseQueryTool(BaseTool):
    """Tool for querying database"""
    
    name: str = "database_query"
    description: str = """
    Query records from a database table.
    Input should be a JSON string with 'table', optional 'filters', and 'limit'.
    Example: {"table": "users", "filters": {"status": "active"}, "limit": 10}
    Returns the query results.
    """
    
    async def _arun(self, table: str, filters: Optional[Dict[str, Any]] = None,
                    limit: int = 100) -> Dict[str, Any]:
        """Execute database query"""
        try:
            # Validate table name
            if not table.replace('_', '').isalnum():
                return {"error": "Invalid table name"}
            
            results = await db_operations.query(table, filters, limit)
            
            return {
                "success": True,
                "count": len(results),
                "data": results
            }
        except Exception as e:
            logger.error(f"Database query failed: {e}")
            return {"error": str(e), "success": False}
    
    def _run(self, table: str, filters: Optional[Dict[str, Any]] = None,
             limit: int = 100) -> Dict[str, Any]:
        """Sync wrapper for database query"""
        import asyncio
        return asyncio.run(self._arun(table, filters, limit))


class DatabaseInsertTool(BaseTool):
    """Tool for inserting records"""
    
    name: str = "database_insert"
    description: str = """
    Insert a new record into a database table.
    Input should be a JSON string with 'table' and 'data'.
    Example: {"table": "users", "data": {"name": "John", "email": "john@example.com"}}
    Returns the inserted record.
    """
    
    async def _arun(self, table: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute database insert"""
        try:
            # Validate table name
            if not table.replace('_', '').isalnum():
                return {"error": "Invalid table name"}
            
            result = await db_operations.insert(table, data)
            
            if result:
                return {
                    "success": True,
                    "data": result
                }
            return {"error": "Insert failed", "success": False}
        except Exception as e:
            logger.error(f"Database insert failed: {e}")
            return {"error": str(e), "success": False}
    
    def _run(self, table: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Sync wrapper for database insert"""
        import asyncio
        return asyncio.run(self._arun(table, data))


class DatabaseUpdateTool(BaseTool):
    """Tool for updating records"""
    
    name: str = "database_update"
    description: str = """
    Update records in a database table.
    Input should be a JSON string with 'table', 'data', and 'filters'.
    Example: {"table": "users", "data": {"status": "inactive"}, "filters": {"id": "123"}}
    Returns success status.
    """
    
    async def _arun(self, table: str, data: Dict[str, Any],
                    filters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute database update"""
        try:
            # Validate table name
            if not table.replace('_', '').isalnum():
                return {"error": "Invalid table name"}
            
            success = await db_operations.update(table, data, filters)
            
            return {
                "success": success,
                "message": "Record updated successfully" if success else "Update failed"
            }
        except Exception as e:
            logger.error(f"Database update failed: {e}")
            return {"error": str(e), "success": False}
    
    def _run(self, table: str, data: Dict[str, Any],
             filters: Dict[str, Any]) -> Dict[str, Any]:
        """Sync wrapper for database update"""
        import asyncio
        return asyncio.run(self._arun(table, data, filters))


class DatabaseDeleteTool(BaseTool):
    """Tool for deleting records"""
    
    name: str = "database_delete"
    description: str = """
    Delete records from a database table.
    Input should be a JSON string with 'table' and 'filters'.
    Example: {"table": "users", "filters": {"id": "123"}}
    Returns success status.
    """
    
    async def _arun(self, table: str, filters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute database delete"""
        try:
            # Validate table name
            if not table.replace('_', '').isalnum():
                return {"error": "Invalid table name"}
            
            # Ensure filters are provided to prevent accidental deletion of all records
            if not filters:
                return {"error": "Filters are required for delete operation", "success": False}
            
            success = await db_operations.delete(table, filters)
            
            return {
                "success": success,
                "message": "Record deleted successfully" if success else "Delete failed"
            }
        except Exception as e:
            logger.error(f"Database delete failed: {e}")
            return {"error": str(e), "success": False}
    
    def _run(self, table: str, filters: Dict[str, Any]) -> Dict[str, Any]:
        """Sync wrapper for database delete"""
        import asyncio
        return asyncio.run(self._arun(table, filters))


class DatabaseSchemaInspectorTool(BaseTool):
    """Tool for inspecting database schema"""
    
    name: str = "database_schema_inspector"
    description: str = """
    Get information about database tables and their schema.
    Useful for understanding what tables and columns are available.
    Input should be a table name or empty for all tables.
    """
    
    def _run(self, table: Optional[str] = None) -> Dict[str, Any]:
        """Get database schema information"""
        try:
            # This is a placeholder - actual implementation would query schema
            schema_info = {
                "tables": {
                    "tasks": {
                        "columns": ["id", "task_id", "agent_type", "status", "created_at"],
                        "description": "Task execution records"
                    },
                    "conversations": {
                        "columns": ["id", "session_id", "role", "content", "created_at"],
                        "description": "Conversation message history"
                    },
                    "workflows": {
                        "columns": ["id", "workflow_id", "status", "input_data", "created_at"],
                        "description": "Workflow execution records"
                    }
                }
            }
            
            if table:
                if table in schema_info["tables"]:
                    return {
                        "success": True,
                        "table": table,
                        "schema": schema_info["tables"][table]
                    }
                return {"error": f"Table '{table}' not found", "success": False}
            
            return {
                "success": True,
                "available_tables": list(schema_info["tables"].keys()),
                "schemas": schema_info["tables"]
            }
        except Exception as e:
            logger.error(f"Schema inspection failed: {e}")
            return {"error": str(e), "success": False}
    
    async def _arun(self, table: Optional[str] = None) -> Dict[str, Any]:
        """Async wrapper for schema inspection"""
        return self._run(table)


# Tool instances
database_query_tool = DatabaseQueryTool()
database_insert_tool = DatabaseInsertTool()
database_update_tool = DatabaseUpdateTool()
database_delete_tool = DatabaseDeleteTool()
database_schema_tool = DatabaseSchemaInspectorTool()

# Export all database tools
database_tools = [
    database_query_tool,
    database_insert_tool,
    database_update_tool,
    database_delete_tool,
    database_schema_tool
]