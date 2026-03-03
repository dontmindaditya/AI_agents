def get_generator_prompt(
    ui_analysis: any,
    components: list,
    framework: str,
    ui_patterns: list = None
) -> str:
    """Get the prompt for component generation"""
    if ui_patterns is None:
        ui_patterns = []

    framework_specifics = {
        "react": """
Use React functional components with hooks.
- Use modern React patterns (hooks, context when needed)
- Implement proper prop types with TypeScript interfaces
- Follow React best practices
- Use component composition
- Support accessibility (ARIA, semantic HTML)
- Prefer Tailwind CSS or CSS Modules for styling
""",
        "vue": """
Use Vue 3 with Composition API and <script setup>.
- Define props and emits properly
- Use TypeScript interfaces where beneficial
- Follow Vue 3 best practices
- Support accessibility and responsive design
- Use scoped styles or CSS modules
""",
        "vanilla": """
Use modern vanilla JavaScript (ES6+).
- Use classes or modules for organization
- Implement clean DOM manipulation
- Use template literals for HTML
- Handle events properly
- Include basic responsive styling with CSS
- Ensure accessibility and semantic structure
"""
    }

    # --- FIX 1: Safely handle ui_analysis if it is a dictionary ---
    if isinstance(ui_analysis, dict):
        # Extract "summary" if it exists, otherwise use the whole dict as a string
        analysis_text = ui_analysis.get("summary", str(ui_analysis))
    else:
        analysis_text = str(ui_analysis) if ui_analysis else ""

    # Extract component names safely
    if components and isinstance(components[0], dict):
        component_names = [c.get("name", f"Component_{i+1}") for i, c in enumerate(components)]
    else:
        component_names = components or []

    component_list = ", ".join(component_names) if component_names else "None identified"

    if ui_patterns and isinstance(ui_patterns[0], dict):
        pattern_names = [p.get("name", p.get("pattern", f"Pattern_{i+1}")) for i, p in enumerate(ui_patterns)]
    else:
        pattern_names = ui_patterns or []

    pattern_list = ", ".join(pattern_names) if pattern_names else "None specified"

    # --- FIX 2: Double curly braces {{ }} for JSON literals in f-strings ---
    return f"""You are a Senior Frontend Developer specializing in {framework}.

UI Analysis Summary:
{analysis_text.strip()}

Components to Generate:
{component_list}

UI Patterns to Implement:
{pattern_list}

{framework_specifics.get(framework.lower(), "")}

Generate production-ready, complete {framework} code that includes:

1. All identified components as separate, reusable modules
2. Proper imports/exports
3. TypeScript interfaces (for React/Vue) or JSDoc (for vanilla)
4. Clean, semantic HTML structure
5. Accessibility features (ARIA labels, keyboard navigation)
6. Responsive design (mobile-first)
7. Basic styling (Tailwind/recommended approach for the framework)
8. Clear comments explaining key decisions

Return your response as valid JSON in this exact format:

```json
{{
  "generated_components": [
    {{
      "name": "ComponentName",
      "filename": "ComponentName.tsx",
      "code": "full component code here (including imports/exports)"
    }}
  ],
  "structure_overview": "Brief description of the component hierarchy and file structure"
}}
```"""