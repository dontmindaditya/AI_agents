"""
Main entry point for UI/UX Agent
"""
import typer
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from rich.markdown import Markdown
from pathlib import Path
import json
from typing import Optional
import sys

# Check setup before importing agents
try:
    from dotenv import load_dotenv
    load_dotenv()  # Load .env file
except ImportError:
    print("Error: python-dotenv not installed. Run: pip install python-dotenv")
    sys.exit(1)

try:
    from agents import OrchestratorAgent
    from config import settings
    from models.schemas import AgentResponse
except Exception as e:
    console = Console()
    console.print(f"[red]Error during import: {e}[/red]\n")
    console.print("[yellow]This might be a configuration issue.[/yellow]")
    console.print("[cyan]Run: python check_setup.py[/cyan] to diagnose the problem.\n")
    sys.exit(1)

app = typer.Typer(help="UI/UX Agent - AI-powered UI/UX design analysis and code generation")
console = Console()


@app.command()
def analyze(
    image: str = typer.Argument(..., help="Path to design image"),
    task: str = typer.Option(
        "Analyze this UI design and provide recommendations",
        "--task", "-t",
        help="Task description"
    ),
    framework: str = typer.Option(
        "react",
        "--framework", "-f",
        help="Target framework (react, html, vue)"
    ),
    generate_code: bool = typer.Option(
        True,
        "--code/--no-code",
        help="Generate code"
    ),
    output: Optional[str] = typer.Option(
        None,
        "--output", "-o",
        help="Output file for generated code"
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose", "-v",
        help="Verbose output"
    )
):
    """
    Analyze a UI/UX design image
    
    Example:
        uiux-agent analyze design.png --task "Create a React component"
    """
    console.print(Panel.fit(
        "[bold cyan]UI/UX Agent[/bold cyan]\n"
        "AI-Powered Design Analysis & Code Generation",
        border_style="cyan"
    ))
    
    # Validate image path
    image_path = Path(image)
    if not image_path.exists():
        console.print(f"[red]Error: Image file not found: {image}[/red]")
        raise typer.Exit(1)
    
    # Initialize orchestrator
    orchestrator = OrchestratorAgent()
    
    # User preferences
    user_preferences = {
        "framework": framework,
        "generate_code": generate_code
    }
    
    # Execute with progress
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task_id = progress.add_task("Analyzing design...", total=None)
        
        response = orchestrator.execute(
            task=task,
            image_path=str(image_path),
            user_preferences=user_preferences
        )
        
        progress.update(task_id, completed=True)
    
    # Display results
    _display_response(response, verbose, output)


@app.command()
def chat():
    """
    Interactive chat mode with the UI/UX agent
    """
    console.print(Panel.fit(
        "[bold cyan]UI/UX Agent - Interactive Mode[/bold cyan]\n"
        "Type 'exit' to quit, 'help' for commands",
        border_style="cyan"
    ))
    
    orchestrator = OrchestratorAgent()
    
    while True:
        try:
            user_input = console.input("\n[cyan]You:[/cyan] ")
            
            if user_input.lower() in ["exit", "quit"]:
                console.print("[yellow]Goodbye![/yellow]")
                break
            
            if user_input.lower() == "help":
                _show_help()
                continue
            
            # For interactive mode, we'd need to handle image uploads
            console.print("[yellow]Note: Interactive mode requires image upload integration[/yellow]")
            
        except KeyboardInterrupt:
            console.print("\n[yellow]Interrupted. Goodbye![/yellow]")
            break


@app.command()
def config(
    show: bool = typer.Option(False, "--show", help="Show current configuration"),
    set_key: Optional[str] = typer.Option(None, "--set-key", help="Set API key"),
    provider: Optional[str] = typer.Option(None, "--provider", help="Set LLM provider (openai/anthropic)")
):
    """
    Manage configuration
    """
    if show:
        console.print(Panel.fit(
            f"[bold]Current Configuration[/bold]\n\n"
            f"LLM Provider: {settings.default_llm_provider}\n"
            f"OpenAI Model: {settings.openai_model}\n"
            f"Anthropic Model: {settings.anthropic_model}\n"
            f"Output Format: {settings.output_code_format}\n"
            f"Max Iterations: {settings.max_iterations}",
            border_style="green"
        ))
    
    if set_key:
        console.print("[yellow]To set API keys, edit the .env file[/yellow]")
    
    if provider:
        console.print(f"[yellow]To change provider, set DEFAULT_LLM_PROVIDER={provider} in .env[/yellow]")


def _display_response(response: AgentResponse, verbose: bool, output_file: Optional[str]):
    """Display agent response in a formatted way"""
    
    if not response.success:
        console.print(f"\n[red]Error: {response.message}[/red]")
        if verbose and response.agent_thoughts:
            console.print("\n[dim]Agent Thoughts:[/dim]")
            for thought in response.agent_thoughts:
                console.print(f"  [dim]{thought}[/dim]")
        return
    
    # Success message
    console.print(f"\n[green]✓ {response.message}[/green]")
    console.print(f"[dim]Execution time: {response.execution_time:.2f}s[/dim]\n")
    
    # Design Analysis
    if response.design_analysis:
        console.print(Panel.fit(
            f"[bold]Design Analysis[/bold]\n\n"
            f"Style: {response.design_analysis.design_style}\n"
            f"Complexity: {response.design_analysis.complexity_score:.2f}\n"
            f"Responsive: {'Yes' if response.design_analysis.responsive_ready else 'No'}\n"
            f"Components: {len(response.design_analysis.components)}\n\n"
            f"[dim]{response.design_analysis.summary}[/dim]",
            title="🎨 Design",
            border_style="blue"
        ))
    
    # Generated Code
    if response.generated_code:
        console.print(Panel.fit(
            f"[bold]{response.generated_code.framework.upper()} Component[/bold]\n\n"
            f"Lines: ~{len(response.generated_code.component_code.split(chr(10)))}\n"
            f"Dependencies: {', '.join(response.generated_code.dependencies[:3])}",
            title="💻 Code",
            border_style="green"
        ))
        
        if output_file:
            # Save code to file
            output_path = Path(output_file)
            output_path.write_text(response.generated_code.component_code)
            console.print(f"\n[green]Code saved to: {output_path}[/green]")
        else:
            # Display code
            console.print("\n[bold]Generated Code:[/bold]")
            console.print(Markdown(f"```{response.generated_code.framework}\n{response.generated_code.component_code}\n```"))
    
    # UX Recommendations
    if response.ux_recommendations:
        table = Table(title="🎯 UX Recommendations", border_style="yellow")
        table.add_column("Severity", style="cyan")
        table.add_column("Title", style="white")
        table.add_column("Category", style="dim")
        
        for rec in response.ux_recommendations[:10]:
            severity_emoji = {"low": "🟢", "medium": "🟡", "high": "🔴", "critical": "🔴"}.get(rec.severity, "⚪")
            table.add_row(
                f"{severity_emoji} {rec.severity}",
                rec.title,
                rec.category
            )
        
        console.print("\n")
        console.print(table)
    
    # Accessibility Issues
    if response.accessibility_issues:
        table = Table(title="♿ Accessibility Issues", border_style="red")
        table.add_column("WCAG", style="cyan")
        table.add_column("Issue", style="white")
        table.add_column("Guideline", style="dim")
        
        for issue in response.accessibility_issues[:10]:
            table.add_row(
                issue.wcag_level,
                issue.issue[:60] + "..." if len(issue.issue) > 60 else issue.issue,
                issue.guideline
            )
        
        console.print("\n")
        console.print(table)
    
    # Verbose output
    if verbose and response.agent_thoughts:
        console.print("\n[bold]Agent Thoughts:[/bold]")
        for thought in response.agent_thoughts:
            console.print(f"  [dim]{thought}[/dim]")


def _show_help():
    """Show interactive mode help"""
    help_text = """
    [bold cyan]Available Commands:[/bold cyan]
    
    [bold]analyze <image>[/bold] - Analyze a design image
    [bold]help[/bold] - Show this help message
    [bold]exit[/bold] - Exit interactive mode
    """
    console.print(Panel(help_text, border_style="cyan"))


@app.command()
def version():
    """Show version information"""
    console.print("[cyan]UI/UX Agent v1.0.0[/cyan]")


if __name__ == "__main__":
    app()