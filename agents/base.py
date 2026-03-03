"""
Base Agent Interface
Defines the standard interface for all agents in the marketplace.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field


class AgentMetadata(BaseModel):
    """Metadata for an agent"""
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
    All plugins must inherit from this class and implement the required methods.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the agent with optional configuration"""
        self.config = config or {}

    @property
    @abstractmethod
    def metadata(self) -> AgentMetadata:
        """
        Return metadata about the agent.
        This is used for the registry and UI display.
        """
        pass

    @abstractmethod
    async def run(self, inputs: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute the agent logic.
        
        Args:
            inputs: Dictionary of input parameters defined in metadata
            context: Shared context from the pipeline/environment (optional)
            
        Returns:
            Dictionary containing the agent's output
        """
        pass

    def validate_inputs(self, inputs: Dict[str, Any]) -> bool:
        """
        Validate provided inputs against the agent's schema.
        Can be overridden for custom validation logic.
        """
        # Basic implementation could use pydantic validation or json schema
        # For now, we assume true if not implemented
        return True
