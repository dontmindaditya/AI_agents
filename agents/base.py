"""
Base Agent Interface

This module defines the standard interface for all agents in the AgentHub marketplace.
All agents must inherit from BaseAgent and implement the required abstract methods.

Usage:
    from agents.base import BaseAgent, AgentMetadata
    
    class MyAgent(BaseAgent):
        @property
        def metadata(self) -> AgentMetadata:
            return AgentMetadata(
                name="My Agent",
                description="Does something useful",
                inputs={"task": {"type": "string"}},
                outputs={"result": {"type": "string"}}
            )
        
        async def run(self, inputs: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
            return {"result": f"Processed: {inputs['task']}"}
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field


class AgentMetadata(BaseModel):
    """
    Metadata for an agent.
    
    This model defines the information that describes an agent,
    including its name, description, version, and input/output schemas.
    
    Attributes:
        name: Human-readable display name
        description: Short description of what the agent does
        version: Semantic version string (e.g., "1.0.0")
        author: Author or organization name
        tags: List of tags for categorization
        inputs: JSON schema for input parameters
        outputs: JSON schema for output structure
    
    Example:
        >>> metadata = AgentMetadata(
        ...     name="Frontend Agent",
        ...     description="Generates React code",
        ...     version="1.0.0",
        ...     author="AgentHub",
        ...     tags=["frontend", "react"],
        ...     inputs={"task": {"type": "string"}},
        ...     outputs={"code": {"type": "string"}}
        ... )
    """
    name: str = Field(..., description="Display name of the agent")
    description: str = Field(..., description="Short description of what the agent does")
    version: str = Field("1.0.0", description="Semantic version of the agent")
    author: str = Field("System", description="Author of the agent")
    tags: List[str] = Field(default_factory=list, description="Tags for categorization")
    inputs: Dict[str, Any] = Field(..., description="JSON schema for input parameters")
    outputs: Dict[str, Any] = Field(..., description="JSON schema for output structure")


class BaseAgent(ABC):
    """
    Abstract Base Class for all Agents.
    
    All agents in AgentHub must inherit from this class and implement
    the required abstract methods: metadata and run.
    
    Attributes:
        config: Optional configuration dictionary for the agent
    
    Example:
        class MyAgent(BaseAgent):
            @property
            def metadata(self) -> AgentMetadata:
                return AgentMetadata(...)
            
            async def run(self, inputs: Dict, context: Optional[Dict] = None) -> Dict:
                # Agent logic here
                return {"result": "..."}
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the agent with optional configuration.
        
        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}

    @property
    @abstractmethod
    def metadata(self) -> AgentMetadata:
        """
        Return metadata about the agent.
        
        This is used for the registry and UI display.
        Must be implemented by all agent subclasses.
        
        Returns:
            AgentMetadata: Instance containing agent information
        """

    @abstractmethod
    async def run(self, inputs: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute the agent logic.
        
        This is the main entry point for running an agent. All agent
        implementations must implement this method.
        
        Args:
            inputs: Dictionary of input parameters defined in metadata
            context: Optional shared context from pipeline/environment
            
        Returns:
            Dictionary containing the agent's output
            
        Example:
            >>> agent = MyAgent()
            >>> result = await agent.run(
            ...     inputs={"task": "build a todo app"},
            ...     context={"framework": "react"}
            ... )
            >>> print(result)
            {'code': '...', 'files': [...]}
        """

    def validate_inputs(self, inputs: Dict[str, Any]) -> bool:
        """
        Validate provided inputs against the agent's schema.
        
        Can be overridden for custom validation logic.
        
        Args:
            inputs: Dictionary of inputs to validate
            
        Returns:
            True if valid, False otherwise
        """
        # Basic implementation could use pydantic validation or json schema
        # For now, we assume true if not implemented
        return True
