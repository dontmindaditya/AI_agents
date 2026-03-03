"""
Enhanced memory system for maintaining conversation context
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
from collections import deque


class MemoryEntry:
    """Single memory entry"""
    
    def __init__(self, role: str, content: str, metadata: Optional[Dict[str, Any]] = None):
        self.role = role
        self.content = content
        self.metadata = metadata or {}
        self.timestamp = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "role": self.role,
            "content": self.content,
            "metadata": self.metadata,
            "timestamp": self.timestamp.isoformat()
        }


class ConversationMemory:
    """
    Advanced memory system with sliding window and importance-based retention
    """
    
    def __init__(self, max_messages: int = 20, important_keywords: Optional[List[str]] = None):
        """
        Initialize memory system
        
        Args:
            max_messages: Maximum number of messages to retain
            important_keywords: Keywords that mark important messages
        """
        self.max_messages = max_messages
        self.messages: deque = deque(maxlen=max_messages)
        self.important_messages: List[MemoryEntry] = []
        self.important_keywords = important_keywords or [
            "error", "important", "critical", "remember", "note"
        ]
        self.summary: Optional[str] = None
    
    def add_message(
        self,
        role: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
        is_important: bool = False
    ):
        """
        Add a message to memory
        
        Args:
            role: Message role (user, assistant, system)
            content: Message content
            metadata: Additional metadata
            is_important: Flag as important message
        """
        entry = MemoryEntry(role, content, metadata)
        self.messages.append(entry)
        
        # Check if message should be marked as important
        if is_important or self._is_important(content):
            self.important_messages.append(entry)
    
    def _is_important(self, content: str) -> bool:
        """Check if message contains important keywords"""
        content_lower = content.lower()
        return any(keyword in content_lower for keyword in self.important_keywords)
    
    def get_context(self, include_important: bool = True) -> str:
        """
        Get conversation context as formatted string
        
        Args:
            include_important: Include important messages even if outside window
            
        Returns:
            Formatted conversation context
        """
        context_parts = []
        
        # Add important messages first if requested
        if include_important and self.important_messages:
            context_parts.append("=== Important Context ===")
            for entry in self.important_messages[-5:]:  # Last 5 important messages
                context_parts.append(f"{entry.role}: {entry.content}")
            context_parts.append("\n=== Recent Conversation ===")
        
        # Add recent messages
        for entry in self.messages:
            context_parts.append(f"{entry.role}: {entry.content}")
        
        return "\n".join(context_parts)
    
    def get_messages(self, n: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get recent messages
        
        Args:
            n: Number of messages to retrieve (None for all)
            
        Returns:
            List of message dictionaries
        """
        messages = list(self.messages)
        if n:
            messages = messages[-n:]
        return [msg.to_dict() for msg in messages]
    
    def get_important_messages(self) -> List[Dict[str, Any]]:
        """Get all important messages"""
        return [msg.to_dict() for msg in self.important_messages]
    
    def clear(self, clear_important: bool = False):
        """
        Clear memory
        
        Args:
            clear_important: Also clear important messages
        """
        self.messages.clear()
        if clear_important:
            self.important_messages.clear()
        self.summary = None
    
    def summarize(self, summarizer_fn=None) -> str:
        """
        Create a summary of the conversation
        
        Args:
            summarizer_fn: Optional function to generate summary
            
        Returns:
            Conversation summary
        """
        if summarizer_fn:
            self.summary = summarizer_fn(self.get_messages())
        else:
            # Simple summary
            message_count = len(self.messages)
            important_count = len(self.important_messages)
            self.summary = (
                f"Conversation with {message_count} messages, "
                f"{important_count} marked as important."
            )
        return self.summary
    
    def search(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Search messages by content
        
        Args:
            query: Search query
            limit: Maximum results
            
        Returns:
            List of matching messages
        """
        query_lower = query.lower()
        matches = []
        
        for entry in self.messages:
            if query_lower in entry.content.lower():
                matches.append(entry.to_dict())
                if len(matches) >= limit:
                    break
        
        return matches
    
    def get_stats(self) -> Dict[str, Any]:
        """Get memory statistics"""
        return {
            "total_messages": len(self.messages),
            "important_messages": len(self.important_messages),
            "max_capacity": self.max_messages,
            "usage_percent": (len(self.messages) / self.max_messages) * 100,
            "has_summary": self.summary is not None
        }


class WorkingMemory:
    """
    Short-term working memory for current task context
    """
    
    def __init__(self):
        self.current_task: Optional[str] = None
        self.design_analysis: Optional[Dict[str, Any]] = None
        self.generated_code: Optional[Dict[str, Any]] = None
        self.intermediate_results: Dict[str, Any] = {}
        self.agent_notes: List[str] = []
    
    def set_task(self, task: str):
        """Set current task"""
        self.current_task = task
    
    def add_note(self, note: str):
        """Add agent note"""
        self.agent_notes.append(f"[{datetime.now().strftime('%H:%M:%S')}] {note}")
    
    def store_result(self, key: str, value: Any):
        """Store intermediate result"""
        self.intermediate_results[key] = value
    
    def get_result(self, key: str) -> Any:
        """Retrieve intermediate result"""
        return self.intermediate_results.get(key)
    
    def clear(self):
        """Clear working memory"""
        self.current_task = None
        self.design_analysis = None
        self.generated_code = None
        self.intermediate_results.clear()
        self.agent_notes.clear()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "current_task": self.current_task,
            "has_design_analysis": self.design_analysis is not None,
            "has_generated_code": self.generated_code is not None,
            "intermediate_results_count": len(self.intermediate_results),
            "agent_notes": self.agent_notes
        }