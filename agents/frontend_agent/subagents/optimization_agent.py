import json
from typing import Dict, Any
from langchain_core.messages import HumanMessage, SystemMessage
from utils.llm_factory import create_optimizer_llm
from prompts.optimizer_prompts import get_optimizer_prompt
from schemas.state_schemas import FrontendAgentState
from utils.output_formatter import print_agent_output, print_success, print_error


class OptimizationAgent:
    """
    Agent responsible for optimizing and validating the generated code.
    """
    
    def __init__(self):
        self.llm = create_optimizer_llm()
        self.name = "Optimization Agent"
    
    def optimize(self, state: FrontendAgentState) -> Dict[str, Any]:
        print_agent_output(self.name, "Optimizing and validating code...")
        
        generated_code = state["generated_code"]
        framework = state["framework"]
        
        # Create the optimization prompt
        prompt = get_optimizer_prompt(generated_code, framework)
        
        messages = [
            SystemMessage(content="You are a code optimization expert. Always respond with valid JSON."),
            HumanMessage(content=prompt)
        ]
        
        response = self.llm.invoke(messages)
        
        try:
            content = response.content
            
            # Handle markdown code blocks
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                json_match = content.find("{")
                if json_match != -1:
                    content = content[json_match:]
                    brace_count = 0
                    for i, char in enumerate(content):
                        if char == "{": brace_count += 1
                        elif char == "}":
                            brace_count -= 1
                            if brace_count == 0:
                                content = content[:i+1]
                                break
            
            optimization_data = json.loads(content)
            
            optimized_code = optimization_data.get("optimized_code", generated_code)
            optimization_notes = optimization_data.get("optimization_notes", "Code optimized")
            is_valid = optimization_data.get("is_valid", True)
            validation_errors = optimization_data.get("validation_errors", [])
            
            # --- FIX: Safe string conversion for slicing ---
            if isinstance(optimization_notes, (list, dict)):
                notes_str = json.dumps(optimization_notes)
            else:
                notes_str = str(optimization_notes)

            if is_valid:
                print_success("Code is valid and optimized!")
            else:
                print_error(f"Validation issues found: {len(validation_errors)}")
                for error in validation_errors[:3]:
                    print_error(f"  - {str(error)}")
            
            # Use notes_str instead of optimization_notes to avoid slice KeyError
            print_agent_output(
                self.name,
                f"Optimization Complete!\n\n{notes_str[:300]}...",
                "green" if is_valid else "yellow"
            )
            
            return {
                "optimized_code": optimized_code,
                "optimization_notes": optimization_notes,
                "is_valid": is_valid,
                "validation_errors": validation_errors,
                "generated_code": optimized_code,
                "is_complete": True,
                "messages": [f"Optimization complete. Valid: {is_valid}"],
                "iteration_count": 1
            }
            
        except json.JSONDecodeError as e:
            print_agent_output(self.name, f"Error parsing JSON: {e}", "yellow")
            return {
                "optimized_code": generated_code,
                "optimization_notes": "Code optimization attempted. Manual review recommended.",
                "is_valid": True,
                "validation_errors": ["JSON parsing error"],
                "is_complete": True,
                "messages": ["Optimization attempted with parsing issues"],
                "iteration_count": 1
            }
    
    def __call__(self, state: FrontendAgentState) -> Dict[str, Any]:
        return self.optimize(state)