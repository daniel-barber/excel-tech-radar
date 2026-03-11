"""
Logging configuration for Excel Tech Radar.
Provides structured logging with support for text and JSON formats.
"""
import logging
import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Optional
from logging.handlers import RotatingFileHandler


class JSONFormatter(logging.Formatter):
    """Format log records as JSON for structured logging."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format the log record as JSON."""
        log_data = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
        
        # Add extra fields
        if hasattr(record, 'user_id'):
            log_data['user_id'] = record.user_id
        if hasattr(record, 'request_id'):
            log_data['request_id'] = record.request_id
        if hasattr(record, 'project_id'):
            log_data['project_id'] = record.project_id
        
        return json.dumps(log_data)


class ColoredFormatter(logging.Formatter):
    """Format log records with colors for console output."""
    
    # ANSI color codes
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
    }
    RESET = '\033[0m'
    
    def format(self, record: logging.LogRecord) -> str:
        """Format the log record with colors."""
        # Add color to level name
        levelname = record.levelname
        if levelname in self.COLORS:
            record.levelname = f"{self.COLORS[levelname]}{levelname}{self.RESET}"
        
        # Format the message
        formatted = super().format(record)
        
        # Reset levelname for next use
        record.levelname = levelname
        
        return formatted


def setup_logging(
    level: str = 'INFO',
    log_file: Optional[str] = None,
    log_format: str = 'text',
    max_bytes: int = 10 * 1024 * 1024,  # 10 MB
    backup_count: int = 5,
) -> logging.Logger:
    """
    Set up logging configuration.
    
    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file (None for console only)
        log_format: Format type ('text' or 'json')
        max_bytes: Maximum size of log file before rotation
        backup_count: Number of backup files to keep
    
    Returns:
        Configured logger instance
    """
    # Get root logger
    logger = logging.getLogger('excel_radar')
    logger.setLevel(getattr(logging, level.upper()))
    
    # Remove existing handlers
    logger.handlers.clear()
    
    # Console handler with colored output
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    
    if log_format == 'json':
        console_formatter = JSONFormatter()
    else:
        console_formatter = ColoredFormatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # File handler with rotation
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        
        if log_format == 'json':
            file_formatter = JSONFormatter()
        else:
            file_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
        
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    
    # Log startup message
    logger.info(
        f"Logging initialized: level={level}, format={log_format}, "
        f"file={log_file or 'console only'}"
    )
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a specific module.
    
    Args:
        name: Logger name (usually __name__)
    
    Returns:
        Logger instance
    """
    return logging.getLogger(f'excel_radar.{name}')


# Request logging middleware
class RequestLogger:
    """Middleware for logging HTTP requests."""
    
    def __init__(self, app, logger: logging.Logger):
        """Initialize request logger."""
        self.app = app
        self.logger = logger
    
    def __call__(self, environ, start_response):
        """Log the request."""
        from time import time
        
        # Extract request info
        method = environ.get('REQUEST_METHOD', '')
        path = environ.get('PATH_INFO', '')
        query = environ.get('QUERY_STRING', '')
        remote_addr = environ.get('REMOTE_ADDR', '')
        
        # Start timing
        start_time = time()
        
        # Log request
        self.logger.info(
            f"Request started: {method} {path}",
            extra={
                'method': method,
                'path': path,
                'query': query,
                'remote_addr': remote_addr,
            }
        )
        
        # Capture response status
        status_code = [None]
        
        def custom_start_response(status, headers, exc_info=None):
            status_code[0] = status.split()[0]
            return start_response(status, headers, exc_info)
        
        # Call the app
        try:
            response = self.app(environ, custom_start_response)
            
            # Log response
            duration = time() - start_time
            self.logger.info(
                f"Request completed: {method} {path} - {status_code[0]} ({duration:.3f}s)",
                extra={
                    'method': method,
                    'path': path,
                    'status': status_code[0],
                    'duration': duration,
                }
            )
            
            return response
        except Exception as e:
            # Log error
            duration = time() - start_time
            self.logger.error(
                f"Request failed: {method} {path} - {str(e)} ({duration:.3f}s)",
                exc_info=True,
                extra={
                    'method': method,
                    'path': path,
                    'duration': duration,
                }
            )
            raise

# Made with Bob
