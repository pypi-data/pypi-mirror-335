import logging
import sys
from typing import Optional

def setup_logger(name: str, level: Optional[int] = None) -> logging.Logger:
    """
    Set up and configure a logger.
    
    Args:
        name: Logger name
        level: Logging level (if not provided, uses INFO)
        
    Returns:
        Configured logger
    """
    logger = logging.getLogger(name)
    
    # Set level
    if level is not None:
        logger.setLevel(level)
    else:
        logger.setLevel(logging.INFO)
    
    # Only add handlers if they don't exist
    if not logger.handlers:
        # Create console handler
        handler = logging.StreamHandler(sys.stdout)
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Add formatter to handler
        handler.setFormatter(formatter)
        
        # Add handler to logger
        logger.addHandler(handler)
    
    return logger 