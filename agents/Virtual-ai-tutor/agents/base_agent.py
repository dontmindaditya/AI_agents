"""
Base Agent class that all agents inherit from
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_core.language_models.base import BaseLanguageModel
from models.llm_provider import LLMProvider
from utils.logger import create_agent_logger


class BaseAgent(ABC):
    """
    Abstract base class for all agents in the system
    
    Provides common functionality for:
    - LLM interaction
    - Message history management
    - Logging
    - State management
    """
    
    def __init__(
        self,
        name: str,
        system_prompt: str,
        llm: Optional[BaseLanguageModel] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs
    ):
        """
        Initialize the base agent
        
        Args:
            name: Agent name for identification
            system_prompt: System prompt defining agent's role
            llm: Optional pre-configured LLM instance
            temperature: Temperature for LLM generation
            max_tokens: Maximum tokens for generation
            **kwargs: Additional configuration
        """
        self.name = name
        self.system_prompt = system_prompt
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.config = kwargs
        
        # Initialize LLM
        self.llm = llm or LLMProvider.create_llm(
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        # Initialize message history
        self.message_history: List[Dict[str, str]] = []
        
        # Initialize logger
        self.logger = create_agent_logger(name)
        
        # Agent state
        self.state: Dict[str, Any] = {}
        
        self.logger.info(f"Initialized agent: {name}")
    
    def _format_messages(
        self,
        user_message: Optional[str] = None,
        include_history: bool = True
    ) -> List[Any]:
        """
        Format messages for LLM input
        
        Args:
            user_message: Optional new user message
            include_history: Whether to include message history
            
        Returns:
            List of formatted messages
        """
        messages = []
        
        # Add system message
        messages.append(SystemMessage(content=self.system_prompt))
        
        # Add history if requested
        if include_history:
            for msg in self.message_history:
                if msg["role"] == "user":
                    messages.append(HumanMessage(content=msg["content"]))
                elif msg["role"] == "assistant":
                    messages.append(AIMessage(content=msg["content"]))
        
        # Add new user message if provided
        if user_message:
            messages.append(HumanMessage(content=user_message))
        
        return messages
    
    def add_to_history(self, role: str, content: str):
        """Add a message to the agent's history"""
        self.message_history.append({
            "role": role,
            "content": content
        })
    
    def clear_history(self):
        """Clear the agent's message history"""
        self.message_history = []
        self.logger.info(f"Cleared message history for {self.name}")
    
    def get_response(
        self,
        message: str,
        include_history: bool = True,
        add_to_history: bool = True
    ) -> str:
        """
        Get a response from the agent
        
        Args:
            message: Input message
            include_history: Whether to include conversation history
            add_to_history: Whether to add this exchange to history
            
        Returns:
            Agent's response
        """
        try:
            # Format messages
            messages = self._format_messages(message, include_history)
            
            # Get response from LLM
            self.logger.debug(f"{self.name} processing message...")
            response = self.llm.invoke(messages)
            response_text = response.content
            
            # Add to history if requested
            if add_to_history:
                self.add_to_history("user", message)
                self.add_to_history("assistant", response_text)
            
            self.logger.debug(f"{self.name} generated response")
            return response_text
            
        except Exception as e:
            self.logger.error(f"Error getting response from {self.name}: {str(e)}")
            raise
    
    def update_system_prompt(self, new_prompt: str):
        """Update the agent's system prompt"""
        self.system_prompt = new_prompt
        self.logger.info(f"Updated system prompt for {self.name}")
    
    def update_state(self, **kwargs):
        """Update agent state with new values"""
        self.state.update(kwargs)
    
    def get_state(self, key: str, default: Any = None) -> Any:
        """Get a value from agent state"""
        return self.state.get(key, default)
    
    @abstractmethod
    def process(self, *args, **kwargs) -> Any:
        """
        Main processing method - must be implemented by subclasses
        
        This method defines the agent's primary functionality
        """
        pass
    
    def reset(self):
        """Reset the agent to initial state"""
        self.clear_history()
        self.state = {}
        self.logger.info(f"Reset agent: {self.name}")
    
    def __str__(self) -> str:
        return f"{self.__class__.__name__}(name={self.name})"
    
    def __repr__(self) -> str:
        return self.__str__()


class ConversationalAgent(BaseAgent):
    """
    Base class for agents that engage in conversations
    
    Extends BaseAgent with conversation-specific functionality
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.conversation_context: Dict[str, Any] = {}
    
    def start_conversation(self, context: Optional[Dict[str, Any]] = None):
        """Start a new conversation with optional context"""
        self.clear_history()
        self.conversation_context = context or {}
        self.logger.info(f"{self.name} started new conversation")
    
    def end_conversation(self) -> Dict[str, Any]:
        """End the conversation and return summary"""
        summary = {
            "name": self.name,
            "message_count": len(self.message_history),
            "context": self.conversation_context
        }
        self.logger.info(f"{self.name} ended conversation")
        return summary
    
    def process(self, message: str, **kwargs) -> str:
        """Process a conversational message"""
        return self.get_response(message, **kwargs)