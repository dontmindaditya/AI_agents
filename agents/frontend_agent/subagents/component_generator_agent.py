import json
import re
from typing import Dict, Any
from langchain_core.messages import HumanMessage, SystemMessage
from utils.llm_factory import create_generator_llm
from prompts.generator_prompts import get_generator_prompt
from schemas.state_schemas import FrontendAgentState
from utils.output_formatter import print_agent_output, print_code


class ComponentGeneratorAgent:
    """
    Agent responsible for generating actual component code based on UI analysis.
    """
    
    def __init__(self):
        self.llm = create_generator_llm()
        self.name = "Component Generator Agent"
    
    def generate(self, state: FrontendAgentState) -> Dict[str, Any]:
        """
        Generate component code based on analysis.
        
        Args:
            state: Current state of the workflow
            
        Returns:
            Updated state with generated code
        """
        print_agent_output(self.name, "Generating components...")
        
        ui_analysis = state["ui_analysis"]
        components = state["components"]
        framework = state["framework"]
        ui_patterns = state["ui_patterns"]
        
        # Create the generation prompt
        prompt = get_generator_prompt(ui_analysis, components, framework, ui_patterns)
        
        # Get code from LLM
        messages = [
            SystemMessage(content=f"You are a senior {framework} developer. Generate production-ready code."),
            HumanMessage(content=prompt)
        ]
        
        response = self.llm.invoke(messages)
        content = response.content
        
        # Extract code from response
        generated_code = self._extract_code(content, framework)
        component_structure = self._extract_structure(content)
        
        print_agent_output(self.name, "Code generation complete!", "green")
        print_code(generated_code[:500] + "..." if len(generated_code) > 500 else generated_code, 
                  self._get_language(framework))
        
        return {
            "generated_code": generated_code,
            "component_structure": component_structure,
            "messages": [f"Generated {len(components)} components"],
            "iteration_count": 1
        }
    
    def _extract_code(self, content: str, framework: str) -> str:
        """Extract code from LLM response"""
        # Try to extract code blocks
        code_pattern = r"```(?:typescript|javascript|tsx|jsx|vue|html)?\n(.*?)```"
        matches = re.findall(code_pattern, content, re.DOTALL)
        
        if matches:
            # Return the longest code block (likely the main one)
            return max(matches, key=len).strip()
        
        # If no code blocks, return the whole content
        return content.strip()
    
    def _extract_structure(self, content: str) -> str:
        """Extract component structure description"""
        # Look for structure overview
        lines = content.split("\n")
        structure_lines = []
        in_structure = False
        
        for line in lines:
            if "structure" in line.lower() or "overview" in line.lower():
                in_structure = True
            elif in_structure and line.strip().startswith("```"):
                break
            elif in_structure and line.strip():
                structure_lines.append(line)
        
        return "\n".join(structure_lines) if structure_lines else "Component structure included in code"
    
    def _get_language(self, framework: str) -> str:
        """Get syntax highlighting language for framework"""
        mapping = {
            "react": "typescript",
            "vue": "vue",
            "vanilla": "javascript"
        }
        return mapping.get(framework, "javascript")
    
    def __call__(self, state: FrontendAgentState) -> Dict[str, Any]:
        """Make the agent callable"""
        return self.generate(state)