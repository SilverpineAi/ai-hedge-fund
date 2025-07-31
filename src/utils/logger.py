"""
Logger Utility

Simple logging configuration for the influencer discovery app.
"""

import logging
import sys
from typing import Optional

def setup_logger(
    name: Optional[str] = None,
    level: str = "INFO",
    show_reasoning: bool = False
) -> logging.Logger:
    """
    Setup logger with appropriate configuration
    
    Args:
        name: Logger name (defaults to root logger)
        level: Logging level
        show_reasoning: Whether to show detailed reasoning
        
    Returns:
        Configured logger
    """
    # Set level based on show_reasoning
    if show_reasoning:
        level = "DEBUG"
    
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Get logger
    logger = logging.getLogger(name)
    
    return logger