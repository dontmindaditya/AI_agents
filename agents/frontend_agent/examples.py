#!/usr/bin/env python3
"""
Example usage of the Frontend Agent System

This script demonstrates how to use the agent programmatically
rather than through the CLI.
"""

from graph import create_frontend_graph
from utils.output_formatter import print_code, print_success, print_info
from tools import CodeAnalyzer, ComponentValidator


def example_1_simple_counter():
    """Example 1: Generate a simple counter component"""
    print_info("Example 1: Simple Counter Component")
    
    graph = create_frontend_graph()
    
    result = graph.run(
        user_input="Create a simple counter with increment and decrement buttons",
        framework="react"
    )
    
    code = result.get("optimized_code") or result.get("generated_code")
    print_code(code, "typescript")
    print_success("Counter component generated!")
    
    return result


def example_2_todo_list():
    """Example 2: Generate a todo list with full CRUD"""
    print_info("Example 2: Todo List Application")
    
    graph = create_frontend_graph()
    
    result = graph.run(
        user_input="""
        Create a todo list application with:
        - Add new todos with a form
        - Mark todos as complete/incomplete
        - Delete todos
        - Filter todos by status (all, active, completed)
        - Clear all completed todos
        - Show count of active todos
        """,
        framework="react"
    )
    
    code = result.get("optimized_code") or result.get("generated_code")
    
    # Analyze the generated code
    analyzer = CodeAnalyzer()
    components = analyzer.extract_components(code, "react")
    state_patterns = analyzer.detect_state_management(code, "react")
    
    print_success("Todo list application generated!")
    print_info(f"Components: {', '.join(components)}")
    print_info(f"State patterns: {', '.join(state_patterns)}")
    
    return result


def example_3_login_form():
    """Example 3: Generate a login form with validation"""
    print_info("Example 3: Login Form with Validation")
    
    graph = create_frontend_graph()
    
    result = graph.run(
        user_input="""
        Build a login form with:
        - Email input with validation
        - Password input with show/hide toggle
        - Remember me checkbox
        - Submit button with loading state
        - Error message display
        - Form validation on submit
        """,
        framework="react"
    )
    
    code = result.get("optimized_code") or result.get("generated_code")
    
    # Validate the code
    validator = ComponentValidator()
    report = validator.comprehensive_validation(code, "react")
    
    print_success("Login form generated!")
    print_info(f"Code valid: {report['is_valid']}")
    print_info(f"Accessibility score: {report['accessibility']['score']}/100")
    print_info(f"Performance score: {report['performance']['score']}/100")
    
    return result


def example_4_vue_component():
    """Example 4: Generate a Vue component"""
    print_info("Example 4: Vue User Card Component")
    
    graph = create_frontend_graph()
    
    result = graph.run(
        user_input="""
        Create a user profile card component with:
        - Avatar image
        - User name and bio
        - Follow/Unfollow button
        - Stats (followers, following, posts)
        - Responsive design
        """,
        framework="vue"
    )
    
    code = result.get("optimized_code") or result.get("generated_code")
    print_code(code, "vue")
    print_success("Vue component generated!")
    
    return result


def example_5_vanilla_js():
    """Example 5: Generate vanilla JavaScript component"""
    print_info("Example 5: Vanilla JS Modal Component")
    
    graph = create_frontend_graph()
    
    result = graph.run(
        user_input="""
        Build a modal component in vanilla JavaScript with:
        - Open/close functionality
        - Overlay backdrop
        - Close on escape key
        - Close on backdrop click
        - Trap focus inside modal
        - Accessibility features
        """,
        framework="vanilla"
    )
    
    code = result.get("optimized_code") or result.get("generated_code")
    print_code(code, "javascript")
    print_success("Vanilla JS modal generated!")
    
    return result


def main():
    """Run all examples"""
    examples = [
        ("Simple Counter", example_1_simple_counter),
        ("Todo List", example_2_todo_list),
        ("Login Form", example_3_login_form),
        ("Vue Component", example_4_vue_component),
        ("Vanilla JS Modal", example_5_vanilla_js),
    ]
    
    print("\n" + "="*60)
    print("Frontend Agent System - Examples")
    print("="*60 + "\n")
    
    for i, (name, example_func) in enumerate(examples, 1):
        print(f"\n{'='*60}")
        print(f"Example {i}: {name}")
        print(f"{'='*60}\n")
        
        try:
            example_func()
        except Exception as e:
            print(f"Error in {name}: {e}")
        
        if i < len(examples):
            input("\nPress Enter to continue to next example...")
    
    print("\n" + "="*60)
    print("All examples completed!")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()