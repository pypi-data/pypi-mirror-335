import logging
import os
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path
from typing import Optional, Dict, Any


def setup_logger(
    log_file="logs/chatlog",
    log_handler='my_logger',
    backup=15,
    rotate='midnight',
    log_format="%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s",
    date_format="%Y-%m-%d %H:%M:%S",
    _utc=False,
    bugsnag_config: Optional[Dict[str, Any]] = None,
    bugsnag_level: int = logging.ERROR
):
    """
    Setup logger with optional formatting and Bugsnag integration.
    Creates log file directory if it doesn't exist.
    
    Args:
        log_file (str): Path to log file
        log_handler (str): Handler name
        backup (int): Number of backup files to keep
        rotate (str[S,M,H,D,'midnight',W{0-6}]): When to rotate files
            (S - Seconds, M - Minutes, H - Hours, D - Days, midnight,
            W{0-6} - roll over on a certain day; 0 - Monday)
        log_format (str): Format for log messages
        date_format (str): Format for the date in log messages
        _utc (bool): Whether timestamps for log rotation are based on UTC
        bugsnag_config (dict, optional): Configuration for Bugsnag
            Example: {'api_key': 'your-api-key', 'project_root': 'project-root'}
            If None, Bugsnag integration is disabled
        bugsnag_level (int): Minimum log level to send to Bugsnag
            Default is logging.ERROR (only errors and critical messages)
    
    Returns:
        logger (object): Configured logger object
    """
    logger = logging.getLogger(log_handler)
    
    # Check if logger already has handlers to avoid adding duplicate handlers
    if not logger.handlers:
        logger.setLevel(logging.DEBUG)

        # Create log directory if it doesn't exist
        log_path = Path(log_file)
        log_dir = log_path.parent
        log_dir.mkdir(parents=True, exist_ok=True)
        
        # File handler setup
        file_handler = TimedRotatingFileHandler(
            log_file, 
            when=rotate, 
            interval=1, 
            backupCount=backup, 
            utc=_utc
        )
        formatter = logging.Formatter(log_format, datefmt=date_format)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        # Optional Bugsnag integration
        if bugsnag_config:
            try:
                import bugsnag
                from bugsnag.handlers import BugsnagHandler
                
                # Configure Bugsnag if not already configured
                if not bugsnag.configuration.api_key:
                    bugsnag.configure(**bugsnag_config)
                
                # Add Bugsnag handler
                bugsnag_handler = BugsnagHandler()
                bugsnag_handler.setLevel(bugsnag_level)
                bugsnag_handler.setFormatter(formatter)
                logger.addHandler(bugsnag_handler)
                
                logger.info(f"Bugsnag integration enabled for {log_handler} at level {logging.getLevelName(bugsnag_level)}")
            except ImportError:
                logger.warning("Bugsnag package not installed. Bugsnag integration disabled.")
            except Exception as e:
                logger.warning(f"Failed to configure Bugsnag: {str(e)}")

    return logger


def add_bugsnag_to_logger(
    logger: logging.Logger,
    bugsnag_config: Dict[str, Any],
    bugsnag_level: int = logging.ERROR,
    log_format: Optional[str] = None
):
    """
    Add Bugsnag handler to an existing logger.
    
    Args:
        logger (logging.Logger): The logger to add Bugsnag to
        bugsnag_config (dict): Configuration for Bugsnag
            Example: {'api_key': 'your-api-key', 'project_root': 'project-root'}
        bugsnag_level (int): Minimum log level to send to Bugsnag
        log_format (str, optional): Format for log messages. If None, uses existing format
            from the first handler if available
    
    Returns:
        logger (logging.Logger): The updated logger
    """
    try:
        import bugsnag
        from bugsnag.handlers import BugsnagHandler
        
        # Configure Bugsnag if not already configured
        if not bugsnag.configuration.api_key:
            bugsnag.configure(**bugsnag_config)
        
        # Check if Bugsnag handler already exists
        for handler in logger.handlers:
            if isinstance(handler, BugsnagHandler):
                logger.warning("Bugsnag handler already exists for this logger")
                return logger
        
        # Create formatter if provided, otherwise try to use existing
        formatter = None
        if log_format:
            formatter = logging.Formatter(log_format)
        elif logger.handlers:
            formatter = logger.handlers[0].formatter
        
        # Add Bugsnag handler
        bugsnag_handler = BugsnagHandler()
        bugsnag_handler.setLevel(bugsnag_level)
        if formatter:
            bugsnag_handler.setFormatter(formatter)
        
        logger.addHandler(bugsnag_handler)
        logger.info(f"Bugsnag handler added at level {logging.getLevelName(bugsnag_level)}")
        
    except ImportError:
        logger.warning("Bugsnag package not installed. Bugsnag integration failed.")
    except Exception as e:
        logger.warning(f"Failed to add Bugsnag handler: {str(e)}")
    
    return logger


def ensure_log_directory(log_file_path: str) -> bool:
    """
    Ensure that the directory for a log file exists.
    
    Args:
        log_file_path (str): Path to the log file
    
    Returns:
        bool: True if directory exists or was created, False on failure
    """
    try:
        log_path = Path(log_file_path)
        log_dir = log_path.parent
        log_dir.mkdir(parents=True, exist_ok=True)
        return True
    except Exception as e:
        print(f"Failed to create log directory for {log_file_path}: {str(e)}")
        return False