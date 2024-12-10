import logging
import sys
from typing import Optional

def get_logger(name: str, level: Optional[int] = None) -> logging.Logger:
    """Get configured logger instance"""
    logger = logging.getLogger(name)
    
    # Set default level if not already set
    if level or not logger.hasHandlers():
        logger.setLevel(level or logging.INFO)
        logger.propagate = False
        
        # Create console handler with formatting
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(
            logging.Formatter(
                '%(asctime)s - %(levelname)s - %(message)s',
                datefmt='%H:%M:%S'
            )
        )
        logger.handlers = [handler]
    
    return logger 