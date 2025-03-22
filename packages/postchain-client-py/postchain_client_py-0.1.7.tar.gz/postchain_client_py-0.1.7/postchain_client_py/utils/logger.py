import logging
import sys
from typing import Optional

def setup_logger(verbose: bool = False) -> logging.Logger:
    """Configure and return the package logger"""
    logger = logging.getLogger('postchain_client_py')
    
    # Clear any existing handlers
    logger.handlers = []
    
    # Set logging level based on verbose flag
    logger.setLevel(logging.DEBUG if verbose else logging.INFO)
    
    # Create console handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG if verbose else logging.INFO)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    
    # Add handler to logger
    logger.addHandler(handler)
    
    return logger

# Create default logger instance
logger = setup_logger()

def set_verbose(verbose: bool = True):
    """Update logger verbosity level"""
    global logger
    logger = setup_logger(verbose) 