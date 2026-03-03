def get_ui_analyzer_prompt(user_input: str, framework: str) -> str:
    """Get the prompt for UI analysis"""
    return f"""You are a Senior UI/UX Architect specializing in {framework} development.

User Request: {user_input}
Target Framework: {framework}

Analyze this request and provide:

1. **UI Analysis**: Comprehensive breakdown of the user interface requirements
   - Layout structure
   - Visual hierarchy
   - User interactions
   - Accessibility considerations

2. **Component Breakdown**: List all components needed
   - Component names
   - Component responsibilities
   - Component relationships

3. **UI Patterns**: Identify relevant UI patterns
   - Design patterns (e.g., container/presentational, compound components)
   - Layout patterns (e.g., grid, flexbox, responsive)
   - Interaction patterns (e.g., modal, dropdown, infinite scroll)

Provide your analysis in a structured format that can be used by downstream agents.

Format your response as JSON:
{{
    "ui_analysis": "detailed analysis here",
    "components": ["Component1", "Component2", ...],
    "ui_patterns": ["pattern1", "pattern2", ...],
    "recommendations": "any architectural recommendations"
}}
"""


def get_refinement_prompt(previous_analysis: str, feedback: str) -> str:
    """Get the prompt for refining UI analysis"""
    return f"""Previous UI Analysis:
{previous_analysis}

Feedback/Issues:
{feedback}

Please refine the UI analysis based on the feedback provided. Focus on addressing the specific issues mentioned while maintaining the overall structure and quality of the analysis.

Provide the refined analysis in the same JSON format.
"""