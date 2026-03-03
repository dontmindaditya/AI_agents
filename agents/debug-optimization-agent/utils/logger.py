"""Logging configuration and utilities."""

import logging
import sys
from pathlib import Path
from typing import Optional

from config.settings import get_settings


def setup_logger(
    name: str = "debug_agent",
    log_file: Optional[str] = None,
    level: Optional[str] = None
) -> logging.Logger:
    """
    Setup logger with file and console handlers.
    
    Args:
        name: Logger name
        log_file: Path to log file (optional)
        level: Logging level (optional)
        
    Returns:
        Configured logger instance
    """
    settings = get_settings()
    
    # Use settings if not provided
    log_file = log_file or settings.log_file
    level = level or settings.log_level
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))
    
    # Remove existing handlers
    logger.handlers.clear()
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    simple_formatter = logging.Formatter(
        fmt='%(levelname)s - %(message)s'
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(simple_formatter)
    logger.addHandler(console_handler)
    
    # File handler
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(detailed_formatter)
        logger.addHandler(file_handler)
    
    return logger


def get_logger(name: str = "debug_agent") -> logging.Logger:
    """
    Get or create logger instance.
    
    Args:
        name: Logger name
        
    Returns:
        Logger instance
    """
    logger = logging.getLogger(name)
    
    if not logger.handlers:
        return setup_logger(name)
    
    return logger


class AgentLogger:
    """Context-aware logger for agent operations."""
    
    def __init__(self, agent_name: str):
        """Initialize agent logger."""
        self.agent_name = agent_name
        self.logger = get_logger(f"agent.{agent_name}")
    
    def info(self, message: str, **kwargs):
        """Log info message with context."""
        self.logger.info(f"[{self.agent_name}] {message}", extra=kwargs)
    
    def debug(self, message: str, **kwargs):
        """Log debug message with context."""
        self.logger.debug(f"[{self.agent_name}] {message}", extra=kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log warning message with context."""
        self.logger.warning(f"[{self.agent_name}] {message}", extra=kwargs)
    
    def error(self, message: str, **kwargs):
        """Log error message with context."""
        self.logger.error(f"[{self.agent_name}] {message}", extra=kwargs)
    
    def critical(self, message: str, **kwargs):
        """Log critical message with context."""
        self.logger.critical(f"[{self.agent_name}] {message}", extra=kwargs)