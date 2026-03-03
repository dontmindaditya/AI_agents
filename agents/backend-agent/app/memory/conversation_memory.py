"""
Conversation Memory Management
"""
from typing import List, Dict, Any, Optional
from langchain.memory import ConversationBufferMemory, ConversationSummaryMemory
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage

from app.config import settings
from app.database.operations import db_operations
from app.database.models import ConversationMessage
from app.services.llm_service import llm_service
from app.utils.logger import setup_logger
from app.utils.helpers import generate_session_id

logger = setup_logger(__name__)


class ConversationMemoryManager:
    """Manage conversation memory and history"""
    
    def __init__(self, session_id: Optional[str] = None):
        self.session_id = session_id or generate_session_id()
        self.memory = self._initialize_memory()
    
    def _initialize_memory(self) -> ConversationBufferMemory:
        """Initialize memory based on configuration"""
        if settings.MEMORY_TYPE == "conversation_buffer":
            return ConversationBufferMemory(
                return_messages=True,
                memory_key="chat_history",
                input_key="input",
                output_key="output"
            )
        elif settings.MEMORY_TYPE == "conversation_summary":
            llm = llm_service.get_model()
            return ConversationSummaryMemory(
                llm=llm,
                return_messages=True,
                memory_key="chat_history",
                input_key="input",
                output_key="output"
            )
        else:
            return ConversationBufferMemory(
                return_messages=True,
                memory_key="chat_history"
            )
    
    async def add_message(self, role: str, content: str, metadata: Optional[Dict[str, Any]] = None):
        """
        Add a message to conversation history
        
        Args:
            role: Message role (user, assistant, system)
            content: Message content
            metadata: Optional metadata
        """
        try:
            # Save to database
            message = ConversationMessage(
                session_id=self.session_id,
                role=role,
                content=content,
                metadata=metadata
            )
            await db_operations.save_message(message)
            
            # Add to memory
            if role == "user":
                self.memory.chat_memory.add_user_message(content)
            elif role == "assistant":
                self.memory.chat_memory.add_ai_message(content)
            
            logger.info(f"Message added to session {self.session_id}")
        except Exception as e:
            logger.error(f"Failed to add message: {e}")
    
    async def get_history(self, limit: int = 50) -> List[ConversationMessage]:
        """
        Get conversation history from database
        
        Args:
            limit: Maximum number of messages
            
        Returns:
            List of messages
        """
        try:
            messages = await db_operations.get_conversation_history(
                self.session_id,
                limit
            )
            return messages
        except Exception as e:
            logger.error(f"Failed to get history: {e}")
            return []
    
    async def load_history(self, limit: int = 10):
        """
        Load conversation history into memory
        
        Args:
            limit: Number of recent messages to load
        """
        try:
            messages = await self.get_history(limit)
            
            # Clear existing memory
            self.memory.clear()
            
            # Add messages to memory
            for msg in messages:
                if msg.role == "user":
                    self.memory.chat_memory.add_user_message(msg.content)
                elif msg.role == "assistant":
                    self.memory.chat_memory.add_ai_message(msg.content)
            
            logger.info(f"Loaded {len(messages)} messages into memory")
        except Exception as e:
            logger.error(f"Failed to load history: {e}")
    
    def get_memory_variables(self) -> Dict[str, Any]:
        """Get memory variables for agent context"""
        return self.memory.load_memory_variables({})
    
    def clear_memory(self):
        """Clear conversation memory"""
        self.memory.clear()
        logger.info(f"Memory cleared for session {self.session_id}")
    
    async def summarize_conversation(self) -> str:
        """
        Generate a summary of the conversation
        
        Returns:
            Conversation summary
        """
        try:
            messages = await self.get_history()
            
            if not messages:
                return "No conversation history"
            
            # Create summary
            conversation_text = "\n".join([
                f"{msg.role}: {msg.content}" for msg in messages
            ])
            
            llm = llm_service.get_model()
            summary_prompt = f"Summarize the following conversation:\n\n{conversation_text}"
            
            summary = await llm.ainvoke([("human", summary_prompt)])
            return summary.content
        except Exception as e:
            logger.error(f"Failed to summarize conversation: {e}")
            return "Failed to generate summary"


def create_memory_manager(session_id: Optional[str] = None) -> ConversationMemoryManager:
    """
    Create a new conversation memory manager
    
    Args:
        session_id: Optional session ID
        
    Returns:
        ConversationMemoryManager instance
    """
    return ConversationMemoryManager(session_id)