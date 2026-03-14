"""
Error handling utilities

This module provides centralized error handling for the AgentHub system.
It offers structured error logging and formatted error responses for:
- Agent execution errors
- Pipeline stage errors
- Code generation errors

Usage:
    from services.error_handler import ErrorHandler
    
    try:
        await agent.run(inputs)
    except Exception as e:
        error_info = ErrorHandler.handle_agent_error(
            agent_id="frontend",
            error=e,
            context={"project_id": "my-project"}
        )
        # error_info contains structured error data
"""

from typing import Optional, Dict, Any
from utils.logger import get_logger

logger = get_logger(__name__)


class ErrorHandler:
    """
    Centralized error handling for AgentHub.
    
    This class provides static methods to handle and format errors
    from different parts of the system in a consistent manner.
    
    Example:
        >>> error = ValueError("Invalid input")
        >>> result = ErrorHandler.handle_agent_error("frontend", error)
        >>> print(result)
        {
            'agent_id': 'frontend',
            'error': 'Invalid input',
            'error_type': 'ValueError',
            'context': {}
        }
    """
    
    @staticmethod
    def handle_agent_error(
        agent_id: str,
        error: Exception,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Handle errors from agent execution.
        
        Args:
            agent_id: Identifier of the agent that encountered the error
            error: The exception that was raised
            context: Optional context information
            
        Returns:
            Dictionary containing error details:
                - agent_id: The agent identifier
                - error: Error message string
                - error_type: Class name of the exception
                - context: Additional context if provided
        """
        logger.error(f"Agent {agent_id} error: {error}", exc_info=True)
        
        return {
            "agent_id": agent_id,
            "error": str(error),
            "error_type": type(error).__name__,
            "context": context or {}
        }
    
    @staticmethod
    def handle_pipeline_error(
        project_id: str,
        stage: str,
        error: Exception,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Handle errors from pipeline stage execution.
        
        Args:
            project_id: Identifier of the project
            stage: Name of the pipeline stage that failed
            error: The exception that was raised
            context: Optional context information
            
        Returns:
            Dictionary containing error details
        """
        logger.error(f"Pipeline error in {stage}: {error}", exc_info=True)
        
        return {
            "project_id": project_id,
            "stage": stage,
            "error": str(error),
            "error_type": type(error).__name__,
            "context": context or {}
        }
    
    @staticmethod
    def handle_generation_error(
        error: Exception,
        component_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Handle errors from code generation.
        
        Args:
            error: The exception that was raised
            component_name: Optional name of the component being generated
            
        Returns:
            Dictionary containing error details
        """
        logger.error(f"Generation error for {component_name}: {error}", exc_info=True)
        
        return {
            "component": component_name,
            "error": str(error),
            "error_type": type(error).__name__
        }