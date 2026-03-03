"""
Conversation management utilities
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import json


@dataclass
class Message:
    """Represents a single message in a conversation"""
    role: str  # 'user', 'assistant', 'system', 'agent1', 'agent2'
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary"""
        return {
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Message':
        """Create message from dictionary"""
        return cls(
            role=data["role"],
            content=data["content"],
            timestamp=datetime.fromisoformat(data.get("timestamp", datetime.now().isoformat())),
            metadata=data.get("metadata", {})
        )


class ConversationManager:
    """Manages conversation history and provides utility methods"""
    
    def __init__(self):
        self.messages: List[Message] = []
        self.metadata: Dict[str, Any] = {}
    
    def add_message(
        self,
        role: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Message:
        """Add a message to the conversation"""
        message = Message(
            role=role,
            content=content,
            metadata=metadata or {}
        )
        self.messages.append(message)
        return message
    
    def get_messages(
        self,
        role: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[Message]:
        """Get messages, optionally filtered by role and limited"""
        messages = self.messages
        
        if role:
            messages = [m for m in messages if m.role == role]
        
        if limit:
            messages = messages[-limit:]
        
        return messages
    
    def get_last_message(self, role: Optional[str] = None) -> Optional[Message]:
        """Get the last message, optionally filtered by role"""
        messages = self.get_messages(role=role)
        return messages[-1] if messages else None
    
    def format_for_llm(
        self,
        include_system: bool = True,
        role_mapping: Optional[Dict[str, str]] = None
    ) -> List[Dict[str, str]]:
        """
        Format conversation for LLM input
        
        Args:
            include_system: Whether to include system messages
            role_mapping: Map custom roles to standard roles (user/assistant)
        """
        role_mapping = role_mapping or {}
        formatted = []
        
        for msg in self.messages:
            if not include_system and msg.role == "system":
                continue
            
            role = role_mapping.get(msg.role, msg.role)
            formatted.append({
                "role": role,
                "content": msg.content
            })
        
        return formatted
    
    def get_discussion_history(
        self,
        agent1_role: str = "agent1",
        agent2_role: str = "agent2"
    ) -> str:
        """Get formatted discussion history between two agents"""
        discussion = []
        
        for msg in self.messages:
            if msg.role in [agent1_role, agent2_role]:
                agent_name = "Agent 1" if msg.role == agent1_role else "Agent 2"
                discussion.append(f"{agent_name}: {msg.content}")
        
        return "\n\n".join(discussion)
    
    def get_conversation_summary(self) -> Dict[str, Any]:
        """Get a summary of the conversation"""
        return {
            "total_messages": len(self.messages),
            "roles": list(set(m.role for m in self.messages)),
            "duration": (
                (self.messages[-1].timestamp - self.messages[0].timestamp).total_seconds()
                if len(self.messages) >= 2 else 0
            ),
            "first_message_time": self.messages[0].timestamp.isoformat() if self.messages else None,
            "last_message_time": self.messages[-1].timestamp.isoformat() if self.messages else None
        }
    
    def save_to_file(self, filepath: str):
        """Save conversation to JSON file"""
        data = {
            "messages": [m.to_dict() for m in self.messages],
            "metadata": self.metadata,
            "summary": self.get_conversation_summary()
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
    
    @classmethod
    def load_from_file(cls, filepath: str) -> 'ConversationManager':
        """Load conversation from JSON file"""
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        manager = cls()
        manager.messages = [Message.from_dict(m) for m in data["messages"]]
        manager.metadata = data.get("metadata", {})
        
        return manager
    
    def clear(self):
        """Clear all messages"""
        self.messages = []
    
    def __len__(self) -> int:
        """Get number of messages"""
        return len(self.messages)
    
    def __str__(self) -> str:
        """String representation"""
        return f"ConversationManager({len(self.messages)} messages)"


class DiscussionManager(ConversationManager):
    """Specialized conversation manager for agent discussions"""
    
    def __init__(self, agent1_name: str = "Agent 1", agent2_name: str = "Agent 2"):
        super().__init__()
        self.agent1_name = agent1_name
        self.agent2_name = agent2_name
        self.current_round = 0
    
    def start_new_round(self):
        """Start a new discussion round"""
        self.current_round += 1
        self.metadata[f"round_{self.current_round}_start"] = datetime.now().isoformat()
    
    def add_agent1_message(self, content: str, **metadata):
        """Add a message from agent 1"""
        return self.add_message(
            "agent1",
            content,
            metadata={"agent_name": self.agent1_name, "round": self.current_round, **metadata}
        )
    
    def add_agent2_message(self, content: str, **metadata):
        """Add a message from agent 2"""
        return self.add_message(
            "agent2",
            content,
            metadata={"agent_name": self.agent2_name, "round": self.current_round, **metadata}
        )
    
    def get_round_messages(self, round_num: int) -> List[Message]:
        """Get messages from a specific round"""
        return [m for m in self.messages if m.metadata.get("round") == round_num]
    
    def get_discussion_text(self) -> str:
        """Get the complete discussion as formatted text"""
        text = []
        for msg in self.messages:
            if msg.role in ["agent1", "agent2"]:
                agent_name = msg.metadata.get("agent_name", msg.role)
                round_num = msg.metadata.get("round", "?")
                text.append(f"[Round {round_num}] {agent_name}:\n{msg.content}\n")
        return "\n".join(text)