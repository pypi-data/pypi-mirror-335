import logging
import sys
from typing import Optional
from pathlib import Path

def setup_logging(
    level: int = logging.INFO,
    log_file: Optional[Path] = None,
    format_string: Optional[str] = None
) -> logging.Logger:
    """
    Configure logging for the workflow system.
    
    Args:
        level: Logging level (default: logging.INFO)
        log_file: Optional path to log file
        format_string: Optional custom format string for log messages
        
    Returns:
        logging.Logger: Configured logger instance
    """
    logger = logging.getLogger("at_common_workflow")
    logger.setLevel(level)
    
    if not format_string:
        format_string = "[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s"
    formatter = logging.Formatter(format_string)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler if log_file is specified
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger 