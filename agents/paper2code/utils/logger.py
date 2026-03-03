"""
Logging utilities for Paper2Code Agent System
"""
import logging
import sys
from pathlib import Path
from datetime import datetime
from rich.logging import RichHandler
from rich.console import Console
from config.settings import settings

console = Console()


def setup_logger(name: str = "paper2code") -> logging.Logger:
    """
    Setup and configure logger with both file and console handlers
    
    Args:
        name: Logger name
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, settings.log_level.upper()))
    
    # Remove existing handlers
    logger.handlers.clear()
    
    # Console handler with Rich formatting
    console_handler = RichHandler(
        console=console,
        rich_tracebacks=True,
        tracebacks_show_locals=True,
        markup=True
    )
    console_handler.setLevel(logging.INFO)
    console_format = logging.Formatter(
        "%(message)s",
        datefmt="[%X]"
    )
    console_handler.setFormatter(console_format)
    
    # File handler
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    file_handler = logging.FileHandler(
        log_dir / settings.log_file,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_format = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    file_handler.setFormatter(file_format)
    
    # Add handlers
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    return logger


def log_agent_step(logger: logging.Logger, agent_name: str, step: str, details: str = ""):
    """
    Log agent execution step with formatting
    
    Args:
        logger: Logger instance
        agent_name: Name of the agent
        step: Current step description
        details: Additional details
    """
    logger.info(f"[bold cyan]{agent_name}[/bold cyan] → {step}")
    if details:
        logger.debug(f"  └─ {details}")


def log_success(logger: logging.Logger, message: str):
    """Log success message"""
    logger.info(f"[bold green]✓[/bold green] {message}")


def log_error(logger: logging.Logger, message: str, exc: Exception = None):
    """Log error message"""
    logger.error(f"[bold red]✗[/bold red] {message}")
    if exc:
        logger.exception(exc)


def log_warning(logger: logging.Logger, message: str):
    """Log warning message"""
    logger.warning(f"[bold yellow]⚠[/bold yellow] {message}")


# Global logger instance
logger = setup_logger()