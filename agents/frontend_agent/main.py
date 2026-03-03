#!/usr/bin/env python3
"""
Frontend Agent System - Main CLI Interface
A multi-agent system for generating frontend code using LangGraph.
"""
import json
import argparse
import sys
import os
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.rule import Rule

from graph import create_frontend_graph
from config.settings import SUPPORTED_FRAMEWORKS, DEFAULT_FRAMEWORK, OUTPUT_DIR
from utils.output_formatter import (
    print_success,
    print_error,
    print_info,
    format_final_output,
    print_code
)
from tools import CodeAnalyzer, ComponentValidator

console = Console()

def print_banner():
    """Print the application banner"""
    banner = """
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║         Frontend Agent System v1.0                        ║
║         AI-Powered Frontend Code Generation               ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
    """
    console.print(banner, style="bold cyan")

def validate_environment():
    """Validate that required environment variables are set"""
    from config.settings import LLM_PROVIDER, OPENAI_API_KEY, ANTHROPIC_API_KEY, GOOGLE_API_KEY
    
    if LLM_PROVIDER == "openai" and not OPENAI_API_KEY:
        print_error("OPENAI_API_KEY not set in environment")
        return False
    elif LLM_PROVIDER == "anthropic" and not ANTHROPIC_API_KEY:
        print_error("ANTHROPIC_API_KEY not set in environment")
        return False
    elif LLM_PROVIDER == "google" and not GOOGLE_API_KEY:
        print_error("GOOGLE_API_KEY not set in environment")
        return False
    
    return True

def save_output(state: dict, output_dir: str):
    """Save the generated code and report to files"""
    try:
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        framework = state.get("framework", "react")
        
        # Extract generated components (structured output)
        generated_data = state.get("generated_components", [])
        if not generated_data:
            # Fallback to old string format
            code_str = state.get("optimized_code") or state.get("generated_code", "")
            if code_str:
                generated_data = [{"name": "App", "code": code_str, "filename": f"App.{framework_ext(framework)}"}]
        
        # Save each component
        for comp in generated_data:
            name = comp.get("name", "Component")
            code = comp.get("code", "")
            filename = comp.get("filename") or f"{name}.{framework_ext(framework)}"
            filepath = os.path.join(output_dir, filename)
            
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(code)
            print_success(f"Saved: {filepath}")
        
        # Save report
        report_path = os.path.join(output_dir, "generation_report.md")
        report = format_final_output(state)
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(report)
        print_success(f"Report saved: {report_path}")
        
    except Exception as e:
        print_error(f"Error saving output: {e}")

def framework_ext(framework: str) -> str:
    """Return appropriate file extension"""
    return {"react": "tsx", "vue": "vue", "vanilla": "js"}.get(framework.lower(), "txt")

def print_generated_components(state: dict, framework: str):
    """Print all generated components with syntax highlighting"""
    generated_data = state.get("generated_components", [])
    
    # Fallback if the structured list is empty
    if not generated_data:
        # These might be dicts now because of our earlier fixes
        code_data = state.get("optimized_code") or state.get("generated_code", "")
        
        if code_data:
            console.print("\n[bold green]Generated Code:[/bold green]")
            
            # --- FIX: Convert dict to string if necessary ---
            if isinstance(code_data, dict):
                # If it's the specific format from our ComponentGenerator
                if "generated_components" in code_data:
                    # Recursively call this function with the inner data
                    print_generated_components(code_data, framework)
                    return
                # Otherwise, just stringify it
                code_str = json.dumps(code_data, indent=2)
            else:
                code_str = str(code_data)
                
            print_code(code_str, get_language(framework))
        else:
            console.print("[yellow]No code was generated.[/yellow]")
        return
    
    console.print(f"\n[bold green]Generated {len(generated_data)} Component(s):[/bold green]\n")
    
    for i, comp in enumerate(generated_data):
        name = comp.get("name", f"Component_{i+1}")
        # --- FIX: Ensure 'code' is extracted as a string ---
        code_content = comp.get("code", "")
        
        if isinstance(code_content, dict):
            code_content = json.dumps(code_content, indent=2)
        
        filename = comp.get("filename", f"{name}.{framework_ext(framework)}")
        
        console.print(f"[bold magenta]📄 {name}[/bold magenta] → [dim]{filename}[/dim]")
        if str(code_content).strip():
            print_code(str(code_content), get_language(framework))
        else:
            console.print("[red]Empty code block[/red]")
            
        if i < len(generated_data) - 1:
            console.print("\n" + "─" * 80 + "\n")

def extract_code_as_string(state: dict) -> str:
    """Helper to get a single string of code from various state formats"""
    gen_comps = state.get("generated_components", [])
    if gen_comps and isinstance(gen_comps, list):
        return "\n".join([c.get("code", "") for c in gen_comps])
    
    raw_code = state.get("optimized_code") or state.get("generated_code", "")
    if isinstance(raw_code, dict):
        return "\n".join([str(v) for v in raw_code.values()])
    
    return str(raw_code)

def get_language(framework: str) -> str:
    """Map framework to Rich syntax language"""
    mapping = {
        "react": "tsx",
        "vue": "vue",
        "vanilla": "javascript"
    }
    return mapping.get(framework.lower(), "text")

def print_code_analysis(state: dict):
    """Print analysis of the generated code"""
    # Use the first component's code for analysis
    generated_data = state.get("generated_components", [])
    code = ""
    
    if generated_data and isinstance(generated_data, list):
        # Join all components into one string for a full analysis
        code = "\n".join([c.get("code", "") for c in generated_data])
    else:
        # Fallback to the other code fields
        code_data = state.get("optimized_code") or state.get("generated_code", "")
        if isinstance(code_data, dict):
            # If it's a dict of filename: code, join the values
            code = "\n".join([str(v) for v in code_data.values()])
        else:
            code = str(code_data)
    
    # --- FIX: Ensure we are checking a string ---
    if not code or not isinstance(code, str) or not code.strip():
        return
    
    framework = state.get("framework", "react")
    console.print("\n[bold cyan]Code Analysis:[/bold cyan]")
    
    analyzer = CodeAnalyzer()
    line_count = analyzer.count_lines(code)
    components = analyzer.extract_components(code, framework)
    state_patterns = analyzer.detect_state_management(code, framework)
    best_practices = analyzer.check_best_practices(code, framework)
    complexity_score, complexity_level = analyzer.calculate_complexity_score(code)
    
    console.print(f"  Lines of Code: {line_count}")
    console.print(f"  Components: {', '.join(components) if components else 'N/A'}")
    console.print(f"  State Management: {', '.join(state_patterns) if state_patterns else 'None detected'}")
    console.print(f"  Complexity: {complexity_level} (score: {complexity_score})")
    
    console.print("\n  Best Practices Check:")
    for practice, status in best_practices.items():
        icon = "✓" if status else "✗"
        color = "green" if status else "red"
        console.print(f"    [{color}]{icon}[/{color}] {practice.replace('_', ' ').title()}")

def print_validation_report(state: dict):
    """Print validation report"""
    generated_data = state.get("generated_components", [])
    code = ""
    
    if generated_data and isinstance(generated_data, list):
        code = "\n".join([c.get("code", "") for c in generated_data])
    else:
        code_data = state.get("optimized_code") or state.get("generated_code", "")
        if isinstance(code_data, dict):
            code = "\n".join([str(v) for v in code_data.values()])
        else:
            code = str(code_data)
    
    # --- FIX: Ensure we are checking a string ---
    if not code or not isinstance(code, str) or not code.strip():
        return
    
    framework = state.get("framework", "react")
    console.print("\n[bold cyan]Validation Report:[/bold cyan]")
    
    validator = ComponentValidator()
    report = validator.comprehensive_validation(code, framework)
    
    if report["is_valid"]:
        console.print("  [bold green]✓ Code is valid and follows best practices![/bold green]")
    else:
        console.print("  [bold yellow]⚠ Code has some issues[/bold yellow]")
    
    # Syntax
    if report.get("syntax", {}).get("errors"):
        console.print("\n  [yellow]Syntax Issues:[/yellow]")
        for error in report["syntax"]["errors"]:
            console.print(f"    • {error}")

def print_validation_report(state: dict):
    """Print validation report"""
    generated_data = state.get("generated_components", [])
    code = ""
    if generated_data:
        code = generated_data[0].get("code", "")
    else:
        code = state.get("optimized_code") or state.get("generated_code", "")
    
    if not code.strip():
        return
    
    framework = state.get("framework", "react")
    
    console.print("\n[bold cyan]Validation Report:[/bold cyan]")
    
    validator = ComponentValidator()
    report = validator.comprehensive_validation(code, framework)
    
    if report["is_valid"]:
        console.print("  [bold green]✓ Code is valid and follows best practices![/bold green]")
    else:
        console.print("  [bold yellow]⚠ Code has some issues[/bold yellow]")
    
    # Syntax
    if report["syntax"]["errors"]:
        console.print("\n  [yellow]Syntax Issues:[/yellow]")
        for error in report["syntax"]["errors"]:
            console.print(f"    • {error}")
    
    # Accessibility
    acc_score = report["accessibility"]["score"]
    color = "green" if acc_score >= 80 else "yellow" if acc_score >= 60 else "red"
    console.print(f"\n  Accessibility Score: [{color}]{acc_score}/100[/{color}]")
    
    # Performance
    perf_score = report["performance"]["score"]
    color = "green" if perf_score >= 80 else "yellow" if perf_score >= 60 else "red"
    console.print(f"  Performance Score: [{color}]{perf_score}/100[/{color}]")

def interactive_mode():
    """Run the agent in interactive mode"""
    print_banner()
    
    console.print("\n[bold]Welcome to Frontend Agent System![/bold]")
    console.print("Generate production-ready frontend code with AI.\n")
    
    if not validate_environment():
        print_error("Please set the required API keys in your environment or .env file")
        return
    
    user_input = Prompt.ask(
        "[bold cyan]What would you like to build?[/bold cyan]",
        default="A modern todo list app with add, edit, delete, and persistence"
    )
    
    framework = Prompt.ask(
        "[bold cyan]Choose framework[/bold cyan]",
        choices=SUPPORTED_FRAMEWORKS,
        default=DEFAULT_FRAMEWORK
    )
    
    console.print("\n[bold]Configuration:[/bold]")
    console.print(f"  Framework: {framework}")
    console.print(f"  Request: {user_input}\n")
    
    if not Confirm.ask("Proceed with generation?", default=True):
        print_info("Generation cancelled by user")
        return
    
    try:
        print_info("Initializing Frontend Agent System...")
        graph = create_frontend_graph()
        
        final_state = graph.run(user_input, framework)
        
        # Print generated code (now handles structured output)
        print_generated_components(final_state, framework)
        
        # Analysis & Validation
        print_code_analysis(final_state)
        print_validation_report(final_state)
        
        # Save option
        if Confirm.ask("\nSave generated project to disk?", default=True):
            save_output(final_state, OUTPUT_DIR)
        
        print_success("\n✨ Frontend Agent Workflow Complete! Thank you for using the system!")
        
    except Exception as e:
        print_error(f"An unexpected error occurred: {e}")
        import traceback
        traceback.print_exc()

def cli_mode(args):
    """Run the agent in CLI mode"""
    if not validate_environment():
        print_error("Please set the required API keys")
        sys.exit(1)
    
    print_info(f"Generating {args.framework} code for: {args.input}")
    
    try:
        graph = create_frontend_graph()
        final_state = graph.run(args.input, args.framework)
        
        print_generated_components(final_state, args.framework)
        
        if args.verbose:
            print_code_analysis(final_state)
            print_validation_report(final_state)
        
        if args.output:
            save_output(final_state, args.output)
            
    except Exception as e:
        print_error(f"Generation failed: {e}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(
        description="Frontend Agent System - AI-powered frontend code generation"
    )
    
    parser.add_argument(
        "input",
        nargs="?",
        help="Description of what to build"
    )
    
    parser.add_argument(
        "-f", "--framework",
        choices=SUPPORTED_FRAMEWORKS,
        default=DEFAULT_FRAMEWORK,
        help=f"Target framework (default: {DEFAULT_FRAMEWORK})"
    )
    
    parser.add_argument(
        "-o", "--output",
        help="Output directory for generated files"
    )
    
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Show detailed analysis and validation"
    )
    
    parser.add_argument(
        "-i", "--interactive",
        action="store_true",
        help="Run in interactive mode"
    )
    
    args = parser.parse_args()
    
    if args.interactive or not args.input:
        interactive_mode()
    else:
        cli_mode(args)

if __name__ == "__main__":
    main()