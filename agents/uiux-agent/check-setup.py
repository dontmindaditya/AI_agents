"""
Setup checker - Verifies configuration before running the agent
"""
import os
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from dotenv import load_dotenv

console = Console()


def check_setup():
    """Check if the system is properly configured"""
    issues = []
    warnings = []
    
    # Check 1: .env file exists (check multiple variants)
    env_files = [".env", ".env.local", "env(2).example"]
    env_found = None
    for env_file in env_files:
        if Path(env_file).exists():
            env_found = env_file
            break
    
    if env_found:
        console.print(f"[green]✓[/green] Environment file found: {env_found}")
    else:
        warnings.append(
            "[yellow]⚠[/yellow] No .env file found (but keys may be in environment)\n"
            "  → Recommended: [cyan]cp .env.example .env[/cyan]\n"
            "  → Then edit .env and add your API keys"
        )
    
    # Load environment variables from all possible sources
    load_dotenv()
    load_dotenv(".env.local")
    load_dotenv(".env")
    
    # Check 2: API keys
    openai_key = os.getenv("OPENAI_API_KEY", "")
    anthropic_key = os.getenv("ANTHROPIC_API_KEY", "")
    
    if not openai_key and not anthropic_key:
        issues.append(
            "[red]✗[/red] No API keys configured\n"
            "  → Add at least one of:\n"
            "    • OPENAI_API_KEY=sk-your-key-here\n"
            "    • ANTHROPIC_API_KEY=your-key-here\n"
            "  → Edit the .env file and add your API key"
        )
    else:
        if openai_key:
            if openai_key.startswith("sk-") and len(openai_key) > 20:
                console.print("[green]✓[/green] OpenAI API key configured")
            else:
                warnings.append(
                    "[yellow]⚠[/yellow] OpenAI API key format looks incorrect\n"
                    "  → Should start with 'sk-' and be longer than 20 characters"
                )
        
        if anthropic_key:
            if len(anthropic_key) > 20:
                console.print("[green]✓[/green] Anthropic API key configured")
            else:
                warnings.append(
                    "[yellow]⚠[/yellow] Anthropic API key looks too short"
                )
    
    # Check 3: Provider setting
    provider = os.getenv("DEFAULT_LLM_PROVIDER", "openai")
    if provider == "openai" and not openai_key:
        issues.append(
            "[red]✗[/red] DEFAULT_LLM_PROVIDER is 'openai' but OPENAI_API_KEY is not set\n"
            "  → Either set OPENAI_API_KEY or change DEFAULT_LLM_PROVIDER to 'anthropic'"
        )
    elif provider == "anthropic" and not anthropic_key:
        issues.append(
            "[red]✗[/red] DEFAULT_LLM_PROVIDER is 'anthropic' but ANTHROPIC_API_KEY is not set\n"
            "  → Either set ANTHROPIC_API_KEY or change DEFAULT_LLM_PROVIDER to 'openai'"
        )
    else:
        console.print(f"[green]✓[/green] LLM provider: {provider}")
    
    # Check 4: Dependencies
    try:
        import crewai
        console.print("[green]✓[/green] CrewAI installed")
    except ImportError:
        issues.append(
            "[red]✗[/red] CrewAI not installed\n"
            "  → Run: [cyan]pip install -r requirements.txt --break-system-packages[/cyan]"
        )
    
    try:
        import cv2
        console.print("[green]✓[/green] OpenCV installed")
    except ImportError:
        issues.append(
            "[red]✗[/red] OpenCV not installed\n"
            "  → Run: [cyan]pip install opencv-python --break-system-packages[/cyan]"
        )
    
    try:
        from sklearn.cluster import KMeans
        console.print("[green]✓[/green] scikit-learn installed")
    except ImportError:
        issues.append(
            "[red]✗[/red] scikit-learn not installed\n"
            "  → Run: [cyan]pip install scikit-learn --break-system-packages[/cyan]"
        )
    
    # Display results
    console.print()
    
    if warnings:
        console.print(Panel(
            "\n".join(warnings),
            title="⚠️  Warnings",
            border_style="yellow"
        ))
        console.print()
    
    if issues:
        console.print(Panel(
            "\n\n".join(issues),
            title="❌ Configuration Issues",
            border_style="red"
        ))
        console.print()
        console.print("[red]Please fix the issues above before running the agent.[/red]")
        return False
    else:
        console.print(Panel(
            "[green]✓ All checks passed![/green]\n\n"
            "Your API keys are properly configured.\n"
            "You're ready to use the UI/UX Agent.\n\n"
            "Try: [cyan]python main.py analyze your-image.png[/cyan]",
            title="✅ Setup Complete",
            border_style="green"
        ))
        return True


if __name__ == "__main__":
    console.print(Panel.fit(
        "[bold cyan]UI/UX Agent - Setup Checker[/bold cyan]",
        border_style="cyan"
    ))
    console.print()
    
    check_setup()