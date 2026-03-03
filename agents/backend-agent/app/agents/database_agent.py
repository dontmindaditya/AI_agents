"""
Database Agent - Handles database operations
"""
from app.agents.base_agent import BaseAgent
from app.tools.database_tools import database_tools
from app.tools.validation_tools import sql_injection_detector_tool, data_sanitizer_tool


class DatabaseAgent(BaseAgent):
    """Agent specialized in database operations"""
    
    def __init__(self, llm_provider: str = None):
        tools = database_tools + [sql_injection_detector_tool, data_sanitizer_tool]
        
        super().__init__(
            name="Database Agent",
            description="Specialized agent for database queries and operations",
            tools=tools,
            llm_provider=llm_provider
        )
    
    def get_system_prompt(self) -> str:
        return """You are a Database Agent specialized in database operations and data management.

Your capabilities:
- Query records from database tables
- Insert new records into tables
- Update existing records
- Delete records with filters
- Inspect database schemas
- Sanitize input data
- Detect SQL injection attempts

Guidelines:
1. Always validate and sanitize inputs before database operations
2. Use filters for UPDATE and DELETE to prevent accidental mass operations
3. Check for SQL injection patterns in queries
4. Inspect table schemas before operations when needed
5. Use appropriate operations (SELECT, INSERT, UPDATE, DELETE)
6. Return structured results with success status
7. Handle errors gracefully and provide clear messages

When given a task:
1. Understand the database operation required
2. Validate and sanitize all inputs
3. Check table schema if needed
4. Execute the appropriate database operation
5. Format and return results clearly

Available tables and their purposes:
- tasks: Task execution records
- conversations: Chat message history
- workflows: Workflow execution records
- agent_logs: Agent activity logs

Always prioritize data safety and validation."""


# Global instance
database_agent = DatabaseAgent()