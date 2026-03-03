import json
import re
from typing import Dict, Any
from langchain_core.messages import HumanMessage, SystemMessage
from utils.llm_factory import create_generator_llm
from prompts.state_manager_prompts import get_state_manager_prompt
from schemas.state_schemas import FrontendAgentState
from utils.output_formatter import print_agent_output


class StateManagerAgent:
    """
    Agent responsible for adding state management logic to components.
    """
    
    def __init__(self):
        self.llm = create_generator_llm()
        self.name = "State Manager Agent"
    
    def add_state_logic(self, state: FrontendAgentState) -> Dict[str, Any]:
        """
        Add state management to generated components.
        
        Args:
            state: Current state of the workflow
            
        Returns:
            Updated state with state management logic
        """
        print_agent_output(self.name, "Adding state management logic...")
        
        generated_code = state["generated_code"]
        components = state["components"]
        framework = state["framework"]
        
        # Create the state management prompt
        prompt = get_state_manager_prompt(generated_code, components, framework)
        
        # Get state management logic from LLM
        messages = [
            SystemMessage(content=f"You are a state management expert for {framework}. Always respond with valid JSON."),
            HumanMessage(content=prompt)
        ]
        
        response = self.llm.invoke(messages)
        
        # Parse the response
        try:
            content = response.content
            
            # Handle markdown code blocks
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            
            state_data = json.loads(content)
            
            state_pattern = state_data.get("state_pattern", "local state")
            state_logic = state_data.get("state_logic", "State management added")
            enhanced_code = state_data.get("enhanced_code", generated_code)
            
            print_agent_output(
                self.name,
                f"State Management Complete!\n\nPattern: {state_pattern}\n"
                f"Logic: {state_logic[:200]}...",
                "green"
            )
            
            return {
                "state_pattern": state_pattern,
                "state_logic": state_logic,
                "generated_code": enhanced_code,  # Update with enhanced code
                "messages": [f"State management added using {state_pattern}"],
                "iteration_count": 1
            }
            
        except json.JSONDecodeError as e:
            print_agent_output(self.name, f"Error parsing JSON: {e}", "yellow")
            
            # Fallback: try to extract information from raw response
            content = response.content
            state_pattern = self._extract_pattern(content)
            
            return {
                "state_pattern": state_pattern,
                "state_logic": "State management logic added (see code)",
                "generated_code": generated_code,  # Keep original if parsing fails
                "messages": [f"State management added (pattern extraction)"],
                "iteration_count": 1
            }
    
    def _extract_pattern(self, content: str) -> str:
        """Extract state pattern from content if JSON parsing fails"""
        patterns = ["useState", "useReducer", "Context", "Redux", "Zustand", 
                   "ref", "reactive", "Pinia", "Observer", "Event Emitter"]
        
        for pattern in patterns:
            if pattern.lower() in content.lower():
                return pattern
        
        return "local state"
    
    def __call__(self, state: FrontendAgentState) -> Dict[str, Any]:
        """Make the agent callable"""
        return self.add_state_logic(state)