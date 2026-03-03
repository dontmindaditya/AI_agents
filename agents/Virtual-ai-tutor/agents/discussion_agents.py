"""
Discussion Agents (Agent 1 and Agent 2) for collaborative syllabus design
"""

from typing import Optional, Dict, Any
from langchain_core.language_models.base import BaseLanguageModel
from agents.base_agent import ConversationalAgent
from config.prompts import prompts
from models.llm_provider import create_discussion_llm


class DiscussionAgent(ConversationalAgent):
    """
    Base class for discussion agents
    
    These agents collaborate to design a syllabus through structured discussion
    """
    
    def __init__(
        self,
        name: str,
        role: str,
        system_prompt_template: str,
        topic: str,
        llm: Optional[BaseLanguageModel] = None,
        **kwargs
    ):
        """
        Initialize a discussion agent
        
        Args:
            name: Agent identifier
            role: Agent's role in the discussion
            system_prompt_template: Template for system prompt (with {topic} placeholder)
            topic: Learning topic to discuss
            llm: Optional pre-configured LLM
            **kwargs: Additional configuration
        """
        # Format system prompt with topic
        system_prompt = system_prompt_template.format(topic=topic)
        
        # Use discussion-optimized LLM if not provided
        llm = llm or create_discussion_llm()
        
        super().__init__(
            name=name,
            system_prompt=system_prompt,
            llm=llm,
            **kwargs
        )
        
        self.role = role
        self.topic = topic
        self.discussion_rounds = 0
    
    def respond_to_partner(self, partner_message: str) -> str:
        """
        Respond to discussion partner's message
        
        Args:
            partner_message: Message from the other agent
            
        Returns:
            This agent's response
        """
        self.discussion_rounds += 1
        response = self.get_response(partner_message)
        
        self.logger.info(
            f"{self.name} (Round {self.discussion_rounds}): "
            f"Generated response ({len(response)} chars)"
        )
        
        return response
    
    def initiate_discussion(self, initial_message: str) -> str:
        """
        Initiate the discussion with an opening message
        
        Args:
            initial_message: Opening message/prompt
            
        Returns:
            Agent's initial response
        """
        self.discussion_rounds = 1
        response = self.get_response(initial_message, include_history=False)
        
        self.logger.info(f"{self.name} initiated discussion on: {self.topic}")
        return response
    
    def get_discussion_summary(self) -> Dict[str, Any]:
        """Get summary of this agent's participation"""
        return {
            "name": self.name,
            "role": self.role,
            "topic": self.topic,
            "rounds": self.discussion_rounds,
            "messages": len([m for m in self.message_history if m["role"] == "assistant"])
        }


class Agent1(DiscussionAgent):
    """
    Agent 1: Machine Learning Instructor
    
    Expert in ML concepts, algorithms, and pedagogy
    Takes the lead in structuring technical content
    """
    
    def __init__(
        self,
        topic: str,
        llm: Optional[BaseLanguageModel] = None,
        **kwargs
    ):
        """
        Initialize Agent 1
        
        Args:
            topic: Learning topic for discussion
            llm: Optional pre-configured LLM
            **kwargs: Additional configuration
        """
        super().__init__(
            name="Agent1_ML_Instructor",
            role="Machine Learning Instructor",
            system_prompt_template=prompts.DISCUSSION_AGENT_1_SYSTEM,
            topic=topic,
            llm=llm,
            **kwargs
        )
    
    def process(self, message: str, **kwargs) -> str:
        """Process message as Agent 1"""
        return self.respond_to_partner(message)


class Agent2(DiscussionAgent):
    """
    Agent 2: Beginner ML Assistant
    
    Expert in pedagogy and beginner-friendly approaches
    Ensures content is accessible and well-structured for learners
    """
    
    def __init__(
        self,
        topic: str,
        llm: Optional[BaseLanguageModel] = None,
        **kwargs
    ):
        """
        Initialize Agent 2
        
        Args:
            topic: Learning topic for discussion
            llm: Optional pre-configured LLM
            **kwargs: Additional configuration
        """
        super().__init__(
            name="Agent2_Beginner_Assistant",
            role="Beginner Machine Learning Assistant",
            system_prompt_template=prompts.DISCUSSION_AGENT_2_SYSTEM,
            topic=topic,
            llm=llm,
            **kwargs
        )
    
    def process(self, message: str, **kwargs) -> str:
        """Process message as Agent 2"""
        return self.respond_to_partner(message)


class DiscussionFacilitator:
    """
    Facilitates discussion between Agent 1 and Agent 2
    
    Manages turn-taking and discussion flow
    """
    
    def __init__(
        self,
        agent1: Agent1,
        agent2: Agent2,
        max_rounds: int = 5
    ):
        """
        Initialize discussion facilitator
        
        Args:
            agent1: First discussion agent
            agent2: Second discussion agent
            max_rounds: Maximum number of discussion rounds
        """
        self.agent1 = agent1
        self.agent2 = agent2
        self.max_rounds = max_rounds
        self.current_round = 0
        self.discussion_history = []
    
    def start_discussion(self, initial_prompt: Optional[str] = None) -> str:
        """
        Start the discussion
        
        Args:
            initial_prompt: Optional custom initial prompt
            
        Returns:
            Agent1's opening message
        """
        # Use default prompt if none provided
        if not initial_prompt:
            initial_prompt = prompts.DISCUSSION_INITIAL_MESSAGE.format(
                topic=self.agent1.topic
            )
        
        # Agent1 starts the discussion
        opening = self.agent1.initiate_discussion(initial_prompt)
        
        self.discussion_history.append({
            "round": 1,
            "agent": "agent1",
            "message": opening
        })
        
        self.current_round = 1
        return opening
    
    def continue_discussion(self) -> Optional[str]:
        """
        Continue the discussion for one more round
        
        Returns:
            Next agent's response, or None if discussion should end
        """
        if self.current_round >= self.max_rounds:
            return None
        
        # Get last message
        last_message = self.discussion_history[-1]["message"]
        last_agent = self.discussion_history[-1]["agent"]
        
        # Determine next agent
        if last_agent == "agent1":
            response = self.agent2.respond_to_partner(last_message)
            next_agent = "agent2"
        else:
            response = self.agent1.respond_to_partner(last_message)
            next_agent = "agent1"
            self.current_round += 1
        
        # Record in history
        self.discussion_history.append({
            "round": self.current_round,
            "agent": next_agent,
            "message": response
        })
        
        return response
    
    def run_full_discussion(self) -> list:
        """
        Run complete discussion until max_rounds
        
        Returns:
            Complete discussion history
        """
        # Start discussion
        self.start_discussion()
        
        # Continue until max rounds
        while self.current_round < self.max_rounds:
            self.continue_discussion()
        
        return self.discussion_history
    
    def get_formatted_discussion(self) -> str:
        """Get discussion formatted as text"""
        formatted = []
        for entry in self.discussion_history:
            agent_name = "Agent 1" if entry["agent"] == "agent1" else "Agent 2"
            formatted.append(
                f"[Round {entry['round']}] {agent_name}:\n{entry['message']}\n"
            )
        return "\n".join(formatted)
    
    def get_discussion_for_syllabus(self) -> str:
        """Get discussion formatted for syllabus generation"""
        return self.get_formatted_discussion()