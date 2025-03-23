#!/usr/bin/env python3
"""
Logging Utility Module

This module provides consistent logging configuration across the package.
"""

import logging
import sys
from typing import Optional


def setup_logger(
    name: str,
    level: int = logging.INFO,
    log_format: Optional[str] = None,
    log_file: Optional[str] = None
) -> logging.Logger:
    """
    Set up and configure a logger with consistent formatting.
    
    Args:
        name: Name of the logger
        level: Logging level (default: logging.INFO)
        log_format: Format string for log messages (optional)
        log_file: Path to log file (optional)
        
    Returns:
        Configured logger instance
    """
    if log_format is None:
        log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    
    # Create formatter
    formatter = logging.Formatter(log_format)
    console_handler.setFormatter(formatter)
    
    # Add console handler to logger
    logger.addHandler(console_handler)
    
    # Add file handler if log_file is specified
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger
