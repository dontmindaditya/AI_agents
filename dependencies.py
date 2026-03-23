"""
Dependency Injection Module

This module provides FastAPI dependency injection for services and components.
It uses FastAPI's Depends() to make services testable and loosely coupled.

Usage:
    from dependencies import get_ws_manager, get_orchestrator
    
    @app.get("/example")
    async def example(ws_manager = Depends(get_ws_manager)):
        await ws_manager.broadcast(...)
"""

from typing import Optional, TYPE_CHECKING
from fastapi import Depends

if TYPE_CHECKING:
    from services.websocket_manager import WebSocketManager
    from pipeline.orchestrator import PipelineOrchestrator


# Global instances (singletons)
_ws_manager: Optional["WebSocketManager"] = None
_orchestrator: Optional["PipelineOrchestrator"] = None
_supabase_client: Optional[Any] = None


def get_ws_manager() -> "WebSocketManager":
    """
    Get the singleton WebSocketManager instance.
    
    Returns:
        WebSocketManager: The shared WebSocket manager instance
        
    Raises:
        RuntimeError: If WebSocketManager hasn't been initialized
    """
    if _ws_manager is None:
        raise RuntimeError("WebSocketManager not initialized. Call init_services() first.")
    return _ws_manager


def get_orchestrator() -> "PipelineOrchestrator":
    """
    Get the singleton PipelineOrchestrator instance.
    
    Returns:
        PipelineOrchestrator: The shared orchestrator instance
        
    Raises:
        RuntimeError: If orchestrator hasn't been initialized
    """
    if _orchestrator is None:
        raise RuntimeError("PipelineOrchestrator not initialized. Call init_services() first.")
    return _orchestrator


def init_services(
    ws_manager: "WebSocketManager",
    orchestrator: "PipelineOrchestrator",
    supabase_client: Optional[Any] = None
) -> None:
    """
    Initialize global service instances.
    
    Args:
        ws_manager: WebSocketManager instance
        orchestrator: PipelineOrchestrator instance
        supabase_client: Optional Supabase client instance
    """
    global _ws_manager, _orchestrator, _supabase_client
    _ws_manager = ws_manager
    _orchestrator = orchestrator
    _supabase_client = supabase_client


def reset_services() -> None:
    """Reset all service instances (useful for testing)."""
    global _ws_manager, _orchestrator, _supabase_client
    _ws_manager = None
    _orchestrator = None
    _supabase_client = None


def get_supabase_client() -> Optional[Any]:
    """
    Get the Supabase client instance.
    
    Returns:
        Supabase client or None if not available
    """
    return _supabase_client


def get_optional_orchestrator() -> Optional["PipelineOrchestrator"]:
    """
    Get orchestrator if available, None otherwise.
    Useful for endpoints that work with or without orchestrator.
    """
    return _orchestrator
