import json

def get_state_manager_prompt(generated_code: any, components: list, framework: str) -> str:
    """Get the prompt for adding state management logic"""
    
    state_approaches = {
        "react": """
State Management Options for React:
1. **Local State**: useState for component-level state
2. **Context API**: For sharing state across components
3. **useReducer**: For complex state logic
4. **Custom Hooks**: For reusable state logic
5. **External Libraries**: Redux, Zustand, Jotai (mention if needed)

Choose the most appropriate approach based on complexity.
""",
        "vue": """
State Management Options for Vue:
1. **Reactive State**: ref() and reactive() for component-level state
2. **Provide/Inject**: For sharing state across components
3. **Composables**: For reusable state logic
4. **Pinia**: For global state management (mention if needed)

Choose the most appropriate approach based on complexity.
""",
        "vanilla": """
State Management Options for Vanilla JS:
1. **Class Properties**: For encapsulated state
2. **Observer Pattern**: For reactive state updates
3. **Event Emitters**: For component communication
4. **Pub/Sub Pattern**: For decoupled communication

Choose the most appropriate approach based on complexity.
"""
    }

    # --- FIX 1: Safely handle components list (convert dicts to strings) ---
    if components and isinstance(components[0], dict):
        component_names = [c.get("name", f"Component_{i+1}") for i, c in enumerate(components)]
    else:
        component_names = components or []
    
    component_list_str = ", ".join(component_names) if component_names else "None identified"

    # --- FIX 2: Safely handle generated_code (stringify if it's a dict) ---
    if isinstance(generated_code, (dict, list)):
        code_str = json.dumps(generated_code, indent=2)
    else:
        code_str = str(generated_code)
    
    # --- FIX 3: Use double braces {{ }} for the JSON template ---
    return f"""You are a State Management Expert for {framework}.

Current Code:
{code_str}
Components:
{component_list_str}

{state_approaches.get(framework.lower(), "")}

Your task:
1. **Analyze State Requirements**: Identify what state is needed
   - UI state (loading, errors, modals)
   - Data state (fetched data, form inputs)
   - Derived state (computed values)

2. **Choose State Pattern**: Select the most appropriate state management approach
   - Consider component complexity
   - Consider data flow requirements
   - Consider performance implications

3. **Implement State Logic**: Add state management to the existing code
   - Initialize state properly
   - Implement state updates
   - Handle side effects
   - Add proper error handling

4. **Add State Persistence** (if needed): LocalStorage, SessionStorage, etc.

Provide:
1. The state pattern/approach you chose and why
2. The enhanced code with state management integrated
3. Explanation of the state logic

Format your response as valid JSON:
{{
    "state_pattern": "chosen pattern name",
    "state_logic": "explanation of state management approach",
    "enhanced_code": "complete code with state management"
}}
"""


def get_state_optimization_prompt(current_state_logic: str, performance_issues: list) -> str:
    """Get the prompt for optimizing state management"""
    # Use chr(10) for newlines inside f-string expressions if needed
    issues_str = "\n".join(f"- {issue}" for issue in performance_issues)
    
    return f"""Current State Logic:
{current_state_logic}

Performance Issues:
{issues_str}

Please optimize the state management to address these issues. Consider:
- Memoization and caching
- Preventing unnecessary re-renders
- Efficient state updates
- Proper cleanup

Provide the optimized state logic.
"""