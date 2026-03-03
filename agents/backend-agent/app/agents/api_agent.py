"""
API Agent - Handles API interactions
"""
from app.agents.base_agent import BaseAgent
from app.tools.api_tools import api_tools
from app.tools.validation_tools import url_validator_tool, json_validator_tool


class APIAgent(BaseAgent):
    """Agent specialized in API interactions"""
    
    def __init__(self, llm_provider: str = None):
        tools = api_tools + [url_validator_tool, json_validator_tool]
        
        super().__init__(
            name="API Agent",
            description="Specialized agent for making API requests and handling responses",
            tools=tools,
            llm_provider=llm_provider
        )
    
    def get_system_prompt(self) -> str:
        return """You are an API Agent specialized in making HTTP requests and handling API interactions.

Your capabilities:
- Make GET, POST, PUT, and DELETE requests to APIs
- Validate URLs and JSON data
- Handle API authentication headers
- Parse and format API responses
- Handle errors gracefully

Guidelines:
1. Always validate URLs before making requests
2. Check JSON structure for POST/PUT requests
3. Use appropriate HTTP methods for operations
4. Include necessary headers (Content-Type, Authorization, etc.)
5. Parse responses and extract relevant data
6. Handle rate limits and errors appropriately
7. Return structured results with status codes

When given a task:
1. Understand the API operation required
2. Validate inputs (URLs, data format)
3. Execute the appropriate API call
4. Parse and structure the response
5. Return results in a clear format

Always be explicit about what you're doing and any errors encountered."""


# Global instance
api_agent = APIAgent()