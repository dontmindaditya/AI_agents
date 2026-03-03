"""
Logging utilities with colored output
"""

import logging
import sys
from pathlib import Path
from typing import Optional
import colorlog
from config.settings import settings


def setup_logger(
    name: str,
    log_file: Optional[str] = None,
    level: Optional[str] = None
) -> logging.Logger:
    """
    Set up a logger with colored console output and file logging
    
    Args:
        name: Logger name
        log_file: Optional log file path
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    
    # Set level
    log_level = level or settings.log_level
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Avoid adding handlers multiple times
    if logger.handlers:
        return logger
    
    # Console handler with colors
    console_handler = colorlog.StreamHandler(sys.stdout)
    console_formatter = colorlog.ColoredFormatter(
        '%(log_color)s[%(levelname)s]%(reset)s %(name)s: %(message)s',
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red,bg_white',
        }
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # File handler (if specified)
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """Get or create a logger with the given name"""
    return logging.getLogger(name)


# Create default loggers for different components
def create_agent_logger(agent_name: str) -> logging.Logger:
    """Create a logger for an agent"""
    return setup_logger(f"Agent.{agent_name}", settings.log_file)


def create_orchestrator_logger() -> logging.Logger:
    """Create a logger for the orchestrator"""
    return setup_logger("Orchestrator", settings.log_file)


# Pretty print functions for agent interactions
class AgentLogger:
    """Utility class for pretty-printing agent interactions"""
    
    @staticmethod
    def log_agent_message(agent_name: str, message: str, logger: Optional[logging.Logger] = None):
        """Log an agent message with formatting"""
        if logger:
            logger.info(f"\n{'='*60}\n{agent_name}:\n{'-'*60}\n{message}\n{'='*60}")
        else:
            print(f"\n{'='*60}")
            print(f"{agent_name}:")
            print(f"{'-'*60}")
            print(message)
            print(f"{'='*60}")
    
    @staticmethod
    def log_discussion_round(round_num: int, logger: Optional[logging.Logger] = None):
        """Log the start of a discussion round"""
        msg = f"\n{'#'*60}\n  DISCUSSION ROUND {round_num}\n{'#'*60}"
        if logger:
            logger.info(msg)
        else:
            print(msg)
    
    @staticmethod
    def log_phase_transition(phase: str, logger: Optional[logging.Logger] = None):
        """Log transition between phases"""
        msg = f"\n{'*'*60}\n  PHASE: {phase.upper()}\n{'*'*60}"
        if logger:
            logger.info(msg)
        else:
            print(msg)
    
    @staticmethod
    def log_syllabus(syllabus: str, logger: Optional[logging.Logger] = None):
        """Log generated syllabus"""
        msg = f"\n{'='*60}\nGENERATED SYLLABUS:\n{'='*60}\n{syllabus}\n{'='*60}"
        if logger:
            logger.info(msg)
        else:
            print(msg)