"""
Agent state management for UI/UX Agent
"""
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime
from models.schemas import DesignAnalysis, GeneratedCode, UXRecommendation, AccessibilityIssue


@dataclass
class AgentState:
    """State management for the agent workflow"""
    
    # Input
    task: str
    image_path: Optional[str] = None
    image_data: Optional[bytes] = None
    user_preferences: Dict[str, Any] = field(default_factory=dict)
    
    # Processing state
    current_step: str = "initialization"
    iteration: int = 0
    
    # Analysis results
    design_analysis: Optional[DesignAnalysis] = None
    ux_recommendations: List[UXRecommendation] = field(default_factory=list)
    accessibility_issues: List[AccessibilityIssue] = field(default_factory=list)
    
    # Generated outputs
    generated_code: Optional[GeneratedCode] = None
    
    # Agent thoughts and reasoning
    agent_thoughts: List[str] = field(default_factory=list)
    conversation_history: List[Dict[str, str]] = field(default_factory=list)
    
    # Metadata
    started_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    error: Optional[str] = None
    
    def add_thought(self, thought: str):
        """Add an agent thought to the history"""
        self.agent_thoughts.append(f"[{self.current_step}] {thought}")
    
    def add_conversation(self, role: str, content: str):
        """Add to conversation history"""
        self.conversation_history.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
    
    def update_step(self, step: str):
        """Update current processing step"""
        self.current_step = step
        self.add_thought(f"Moving to step: {step}")
    
    def mark_complete(self):
        """Mark the agent workflow as complete"""
        self.completed_at = datetime.now()
        self.current_step = "completed"
    
    def mark_error(self, error_message: str):
        """Mark an error in the workflow"""
        self.error = error_message
        self.completed_at = datetime.now()
        self.current_step = "error"
    
    def get_execution_time(self) -> float:
        """Get total execution time in seconds"""
        if self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return (datetime.now() - self.started_at).total_seconds()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert state to dictionary"""
        return {
            "task": self.task,
            "current_step": self.current_step,
            "iteration": self.iteration,
            "execution_time": self.get_execution_time(),
            "error": self.error,
            "agent_thoughts": self.agent_thoughts,
            "has_design_analysis": self.design_analysis is not None,
            "has_generated_code": self.generated_code is not None,
            "ux_recommendations_count": len(self.ux_recommendations),
            "accessibility_issues_count": len(self.accessibility_issues)
        }


class ConversationMemory:
    """Memory system for maintaining conversation context"""
    
    def __init__(self, max_messages: int = 20):
        self.max_messages = max_messages
        self.messages: List[Dict[str, str]] = []
    
    def add_message(self, role: str, content: str):
        """Add a message to memory"""
        self.messages.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
        
        # Keep only the last N messages
        if len(self.messages) > self.max_messages:
            self.messages = self.messages[-self.max_messages:]
    
    def get_context(self) -> str:
        """Get conversation context as string"""
        context = []
        for msg in self.messages:
            context.append(f"{msg['role']}: {msg['content']}")
        return "\n".join(context)
    
    def clear(self):
        """Clear conversation memory"""
        self.messages = []
    
    def get_messages(self) -> List[Dict[str, str]]:
        """Get all messages"""
        return self.messages.copy()