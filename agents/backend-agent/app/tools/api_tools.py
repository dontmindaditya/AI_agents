"""
API Tools for Agents
"""
from typing import Any, Dict, Optional
import httpx
import asyncio
from langchain.tools import BaseTool
from pydantic import Field

from app.utils.logger import setup_logger
from app.utils.validators import APIRequest

logger = setup_logger(__name__)


class APIGetTool(BaseTool):
    """Tool for making GET API requests"""
    
    name: str = "api_get"
    description: str = """
    Make a GET request to an API endpoint.
    Input should be a JSON string with 'url' and optional 'headers' and 'params'.
    Returns the API response data.
    """
    
    def _run(self, url: str, headers: Optional[Dict[str, str]] = None, 
             params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute GET request"""
        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.get(url, headers=headers, params=params)
                response.raise_for_status()
                
                return {
                    "status_code": response.status_code,
                    "data": response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text,
                    "headers": dict(response.headers)
                }
        except Exception as e:
            logger.error(f"GET request failed: {e}")
            return {"error": str(e), "status_code": 0}
    
    async def _arun(self, url: str, headers: Optional[Dict[str, str]] = None,
                    params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute GET request asynchronously"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url, headers=headers, params=params)
                response.raise_for_status()
                
                return {
                    "status_code": response.status_code,
                    "data": response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text,
                    "headers": dict(response.headers)
                }
        except Exception as e:
            logger.error(f"Async GET request failed: {e}")
            return {"error": str(e), "status_code": 0}


class APIPostTool(BaseTool):
    """Tool for making POST API requests"""
    
    name: str = "api_post"
    description: str = """
    Make a POST request to an API endpoint.
    Input should be a JSON string with 'url', optional 'headers', and 'body'.
    Returns the API response data.
    """
    
    def _run(self, url: str, body: Optional[Dict[str, Any]] = None,
             headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Execute POST request"""
        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.post(url, json=body, headers=headers)
                response.raise_for_status()
                
                return {
                    "status_code": response.status_code,
                    "data": response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text,
                    "headers": dict(response.headers)
                }
        except Exception as e:
            logger.error(f"POST request failed: {e}")
            return {"error": str(e), "status_code": 0}
    
    async def _arun(self, url: str, body: Optional[Dict[str, Any]] = None,
                    headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Execute POST request asynchronously"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(url, json=body, headers=headers)
                response.raise_for_status()
                
                return {
                    "status_code": response.status_code,
                    "data": response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text,
                    "headers": dict(response.headers)
                }
        except Exception as e:
            logger.error(f"Async POST request failed: {e}")
            return {"error": str(e), "status_code": 0}


class APIPutTool(BaseTool):
    """Tool for making PUT API requests"""
    
    name: str = "api_put"
    description: str = """
    Make a PUT request to an API endpoint.
    Input should be a JSON string with 'url', optional 'headers', and 'body'.
    Returns the API response data.
    """
    
    def _run(self, url: str, body: Optional[Dict[str, Any]] = None,
             headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Execute PUT request"""
        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.put(url, json=body, headers=headers)
                response.raise_for_status()
                
                return {
                    "status_code": response.status_code,
                    "data": response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text,
                    "headers": dict(response.headers)
                }
        except Exception as e:
            logger.error(f"PUT request failed: {e}")
            return {"error": str(e), "status_code": 0}
    
    async def _arun(self, url: str, body: Optional[Dict[str, Any]] = None,
                    headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Execute PUT request asynchronously"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.put(url, json=body, headers=headers)
                response.raise_for_status()
                
                return {
                    "status_code": response.status_code,
                    "data": response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text,
                    "headers": dict(response.headers)
                }
        except Exception as e:
            logger.error(f"Async PUT request failed: {e}")
            return {"error": str(e), "status_code": 0}


class APIDeleteTool(BaseTool):
    """Tool for making DELETE API requests"""
    
    name: str = "api_delete"
    description: str = """
    Make a DELETE request to an API endpoint.
    Input should be a JSON string with 'url' and optional 'headers'.
    Returns the API response data.
    """
    
    def _run(self, url: str, headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Execute DELETE request"""
        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.delete(url, headers=headers)
                response.raise_for_status()
                
                return {
                    "status_code": response.status_code,
                    "message": "Resource deleted successfully"
                }
        except Exception as e:
            logger.error(f"DELETE request failed: {e}")
            return {"error": str(e), "status_code": 0}
    
    async def _arun(self, url: str, headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Execute DELETE request asynchronously"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.delete(url, headers=headers)
                response.raise_for_status()
                
                return {
                    "status_code": response.status_code,
                    "message": "Resource deleted successfully"
                }
        except Exception as e:
            logger.error(f"Async DELETE request failed: {e}")
            return {"error": str(e), "status_code": 0}


# Tool instances
api_get_tool = APIGetTool()
api_post_tool = APIPostTool()
api_put_tool = APIPutTool()
api_delete_tool = APIDeleteTool()

# Export all API tools
api_tools = [
    api_get_tool,
    api_post_tool,
    api_put_tool,
    api_delete_tool
]