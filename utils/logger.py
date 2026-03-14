"""Logging configuration

This module provides consistent logging setup for the AgentHub application.
It supports both JSON and text logging formats based on configuration.

Usage:
    from utils.logger import setup_logger
    
    logger = setup_logger(__name__)
    logger.info("Application started")
"""

import logging
import sys
from datetime import datetime
from typing import Optional
from pythonjsonlogger import jsonlogger
from config import settings


class CustomJsonFormatter(jsonlogger.JsonFormatter):
    """
    Custom JSON formatter for structured logging.
    
    Adds timestamp, level, and logger name to each log entry.
    """
    
    def add_fields(self, log_record: dict, record: logging.LogRecord, message_dict: dict) -> None:
        """Add custom fields to log record."""
        super().add_fields(log_record, record, message_dict)
        log_record['timestamp'] = datetime.utcnow().isoformat()
        log_record['level'] = record.levelname
        log_record['logger'] = record.name


def setup_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Setup and configure a logger instance.
    
    Args:
        name: Logger name, typically __name__ of the module.
        
    Returns:
        Configured logger instance.
    """
    logger = logging.getLogger(name or __name__)
    
    if logger.handlers:
        return logger
    
    logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper()))
    handler = logging.StreamHandler(sys.stdout)
    
    if settings.LOG_FORMAT == "json":
        formatter = CustomJsonFormatter('%(timestamp)s %(level)s %(name)s %(message)s')
    else:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a configured logger instance.
    
    This is an alias for setup_logger for backwards compatibility.
    
    Args:
        name: Logger name, typically __name__ of the module.
        
    Returns:
        Configured logger instance.
    """
    return setup_logger(name)