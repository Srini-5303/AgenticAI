import logging
import sys
from pathlib import Path

def setup_logger(name: str, log_file: str = None, level=logging.INFO):
    """Set up logger for an agent"""
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Avoid duplicate handlers
    if logger.handlers:
        return logger
    
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler (optional)
    if log_file:
        Path("logs").mkdir(exist_ok=True)
        file_handler = logging.FileHandler(f"logs/{log_file}")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger