import logging
import os
from datetime import datetime

def setup_logger(name: str, log_file: str = None, level: int = logging.INFO) -> logging.Logger:
    """Set up a logger with the specified name, file, and level"""
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Check if logger already has handlers to prevent duplicates
    if logger.hasHandlers():
        return logger
    
    # Create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Create file handler if log file is specified
    if log_file:
        # Ensure log directory exists
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger

def get_app_logger(log_dir: str = None) -> logging.Logger:
    """Get the application logger"""
    if not log_dir:
        # Default to logs directory in project root
        log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'logs')
    
    # Ensure log directory exists
    os.makedirs(log_dir, exist_ok=True)
    
    # Create log file name with timestamp
    timestamp = datetime.now().strftime("%Y%m%d")
    log_file = os.path.join(log_dir, f"app_{timestamp}.log")
    
    return setup_logger('app', log_file)