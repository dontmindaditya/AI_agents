"""Error handling utilities"""

from typing import Optional, Dict, Any
from utils.logger import get_logger

logger = get_logger(__name__)


class ErrorHandler:
    """Centralized error handling"""
    
    @staticmethod
    def handle_agent_error(
        agent_id: str,
        error: Exception,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Handle agent errors"""
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
        """Handle pipeline errors"""
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
        """Handle code generation errors"""
        logger.error(f"Generation error for {component_name}: {error}", exc_info=True)
        
        return {
            "component": component_name,
            "error": str(error),
            "error_type": type(error).__name__
        }