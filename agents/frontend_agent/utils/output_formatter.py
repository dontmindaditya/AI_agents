from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.markdown import Markdown
from typing import Dict, Any

console = Console()


def print_agent_output(agent_name: str, output: str, color: str = "cyan"):
    """Print agent output with formatting"""
    console.print(f"\n[bold {color}]{'='*60}[/bold {color}]")
    console.print(f"[bold {color}]{agent_name}[/bold {color}]")
    console.print(f"[bold {color}]{'='*60}[/bold {color}]\n")
    console.print(output)


def print_code(code: str, language: str = "javascript"):
    """Print code with syntax highlighting"""
    syntax = Syntax(code, language, theme="monokai", line_numbers=True)
    console.print(syntax)


def print_state(state: Dict[str, Any]):
    """Print current state in a formatted way"""
    console.print("\n[bold yellow]Current State:[/bold yellow]")
    for key, value in state.items():
        if key == "generated_code":
            console.print(f"  [cyan]{key}:[/cyan] [dim](code omitted)[/dim]")
        else:
            console.print(f"  [cyan]{key}:[/cyan] {value}")


def print_success(message: str):
    """Print success message"""
    console.print(f"[bold green]✓[/bold green] {message}")


def print_error(message: str):
    """Print error message"""
    console.print(f"[bold red]✗[/bold red] {message}")


def print_info(message: str):
    """Print info message"""
    console.print(f"[bold blue]ℹ[/bold blue] {message}")


def format_final_output(state: Dict[str, Any]) -> str:
    """Format the final output for display"""
    output = []
    
    output.append("# Frontend Agent Output\n")
    output.append(f"**Framework:** {state.get('framework', 'N/A')}\n")
    output.append(f"**Components:** {', '.join(state.get('components', []))}\n")
    output.append(f"**State Management:** {state.get('state_pattern', 'N/A')}\n\n")
    
    if state.get("ui_analysis"):
        output.append("## UI Analysis\n")
        output.append(f"{state['ui_analysis']}\n\n")
    
    if state.get("generated_code"):
        output.append("## Generated Code\n")
        output.append(f"```{state.get('framework', 'javascript')}\n")
        output.append(f"{state['generated_code']}\n")
        output.append("```\n\n")
    
    if state.get("optimization_notes"):
        output.append("## Optimization Notes\n")
        output.append(f"{state['optimization_notes']}\n\n")
    
    return "".join(output)