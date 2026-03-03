import json
from typing import Dict, Any
from langchain_core.messages import HumanMessage, SystemMessage
from utils.llm_factory import create_analyzer_llm
from prompts.ui_analyzer_prompts import get_ui_analyzer_prompt
from schemas.state_schemas import FrontendAgentState
from utils.output_formatter import print_agent_output


class UIAnalyzerAgent:
    """
    Agent responsible for analyzing UI requirements and breaking them down
    into components, patterns, and architectural decisions.
    """

    def __init__(self):
        self.llm = create_analyzer_llm()
        self.name = "UI Analyzer Agent"

    def analyze(self, state: FrontendAgentState) -> Dict[str, Any]:
        """
        Analyze user input and extract UI requirements.

        Args:
            state: Current state of the workflow

        Returns:
            Updated state with UI analysis
        """
        print_agent_output(self.name, "Analyzing UI requirements...")

        user_input = state["user_input"]
        framework = state["framework"]

        # Create the analysis prompt
        prompt = get_ui_analyzer_prompt(user_input, framework)

        # Get analysis from LLM
        messages = [
            SystemMessage(content="You are a UI/UX expert. Always respond with valid JSON matching the expected schema."),
            HumanMessage(content=prompt)
        ]

        response = self.llm.invoke(messages)

        # Parse the response
        try:
            content = response.content.strip()

            # Extract JSON from code blocks if present
            if "```json" in content:
                json_str = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                json_str = content.split("```")[1].split("```")[0].strip()
            else:
                json_str = content

            analysis_data = json.loads(json_str)

            # Extract component names safely (assuming each component is a dict with 'name' key)
            components = analysis_data.get("components", [])
            if components and isinstance(components[0], dict):
                component_names = [comp.get("name", f"Component_{i}") for i, comp in enumerate(components)]
            else:
                component_names = components  # fallback if already strings

            # Extract UI patterns safely
            ui_patterns = analysis_data.get("ui_patterns", [])
            if ui_patterns and isinstance(ui_patterns[0], dict):
                pattern_names = [p.get("name", f"Pattern_{i}") for i, p in enumerate(ui_patterns)]
            else:
                pattern_names = ui_patterns

            # Build human-readable summary
            summary = "Analysis Complete!\n"
            if component_names:
                summary += f"\nComponents: {', '.join(component_names)}"
            if pattern_names:
                summary += f"\nPatterns: {', '.join(pattern_names)}"

            print_agent_output(self.name, summary, "green")

            # Return structured update
            return {
                "ui_analysis": analysis_data.get("ui_analysis", ""),
                "components": components,  # Keep full objects for downstream agents
                "ui_patterns": ui_patterns,
                "messages": [f"UI Analysis completed: {len(component_names)} components identified"],
                "iteration_count": 1
            }

        except json.JSONDecodeError as e:
            print_agent_output(self.name, f"JSON parsing error: {e}\nRaw output:\n{content}", "red")
            # Graceful fallback
            return {
                "ui_analysis": response.content,
                "components": [{"name": "MainComponent"}],
                "ui_patterns": [{"name": "basic"}],
                "messages": ["UI Analysis completed with parsing issues"],
                "iteration_count": 1
            }
        except Exception as e:
            print_agent_output(self.name, f"Unexpected error during analysis: {e}", "red")
            return {
                "ui_analysis": "Analysis failed",
                "components": [],
                "ui_patterns": [],
                "messages": ["UI Analysis failed"],
                "iteration_count": 1
            }

    def __call__(self, state: FrontendAgentState) -> Dict[str, Any]:
        """Make the agent callable"""
        return self.analyze(state)