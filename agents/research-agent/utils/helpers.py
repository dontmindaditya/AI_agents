"""
Helper utilities for the research agent system
"""

import os
from datetime import datetime
from pathlib import Path
from typing import Optional
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown

console = Console()


def ensure_directories():
    """Ensure required directories exist"""
    directories = ['output', 'uploads']
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)


def save_report(content: str, filename: Optional[str] = None) -> str:
    """
    Save research report to output directory
    
    Args:
        content: Report content to save
        filename: Optional custom filename
        
    Returns:
        Path to saved file
    """
    ensure_directories()
    
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"research_report_{timestamp}.md"
    
    output_path = Path("output") / filename
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return str(output_path)


def print_header(text: str):
    """Print styled header"""
    console.print(Panel.fit(
        f"[bold cyan]{text}[/bold cyan]",
        border_style="cyan"
    ))


def print_success(text: str):
    """Print success message"""
    console.print(f"[bold green]✓[/bold green] {text}")


def print_error(text: str):
    """Print error message"""
    console.print(f"[bold red]✗[/bold red] {text}")


def print_info(text: str):
    """Print info message"""
    console.print(f"[bold blue]ℹ[/bold blue] {text}")


def print_markdown(content: str):
    """Print markdown formatted content"""
    md = Markdown(content)
    console.print(md)


def validate_env_variables() -> bool:
    """
    Validate required environment variables are set
    
    Returns:
        True if valid, False otherwise
    """
    required_vars = ['OPENAI_API_KEY']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print_error(f"Missing required environment variables: {', '.join(missing_vars)}")
        print_info("Please create a .env file with the required variables.")
        print_info("See .env.example for reference.")
        return False
    
    return True


def truncate_text(text: str, max_length: int = 1000) -> str:
    """
    Truncate text to maximum length
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        
    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    return text[:max_length] + "..."


def get_file_size_mb(filepath: str) -> float:
    """
    Get file size in megabytes
    
    Args:
        filepath: Path to file
        
    Returns:
        File size in MB
    """
    size_bytes = os.path.getsize(filepath)
    return size_bytes / (1024 * 1024)