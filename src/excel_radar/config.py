"""
Configuration management for Excel Tech Radar.
Loads settings from environment variables with fallback to defaults.
"""
import os
from pathlib import Path
from typing import Optional


class Config:
    """Application configuration loaded from environment variables."""
    
    def __init__(self):
        """Initialize configuration from environment variables."""
        # Server Configuration
        self.host = os.getenv('RADAR_HOST', '127.0.0.1')
        self.port = int(os.getenv('RADAR_PORT', '8080'))
        self.debug = os.getenv('RADAR_DEBUG', 'false').lower() == 'true'
        
        # Data Configuration
        self.data_dir = Path(os.getenv('RADAR_DATA_DIR', './data'))
        self.dist_dir = Path(os.getenv('RADAR_DIST_DIR', './dist'))
        
        # Backup Configuration
        self.backup_enabled = os.getenv('RADAR_BACKUP_ENABLED', 'true').lower() == 'true'
        self.max_backups = int(os.getenv('RADAR_MAX_BACKUPS', '5'))
        self.retention_days = int(os.getenv('RADAR_RETENTION_DAYS', '30'))
        
        # Logging Configuration
        self.log_level = os.getenv('RADAR_LOG_LEVEL', 'INFO').upper()
        self.log_file = os.getenv('RADAR_LOG_FILE', '')
        self.log_format = os.getenv('RADAR_LOG_FORMAT', 'text').lower()
        
        # Security Configuration
        self.secret_key = os.getenv('RADAR_SECRET_KEY', 'change-me-in-production')
        self.allowed_origins = os.getenv('RADAR_ALLOWED_ORIGINS', '*')
        
        # Feature Flags
        self.enable_export = os.getenv('RADAR_ENABLE_EXPORT', 'true').lower() == 'true'
        self.enable_import = os.getenv('RADAR_ENABLE_IMPORT', 'true').lower() == 'true'
        self.enable_delete = os.getenv('RADAR_ENABLE_DELETE', 'true').lower() == 'true'
        
        # Performance
        self.max_upload_size = int(os.getenv('RADAR_MAX_UPLOAD_SIZE', '10'))  # MB
        self.request_timeout = int(os.getenv('RADAR_REQUEST_TIMEOUT', '30'))  # seconds
        
        # Validate configuration
        self._validate()
    
    def _validate(self):
        """Validate configuration values."""
        if self.port < 1 or self.port > 65535:
            raise ValueError(f"Invalid port number: {self.port}")
        
        if self.log_level not in ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']:
            raise ValueError(f"Invalid log level: {self.log_level}")
        
        if self.log_format not in ['text', 'json']:
            raise ValueError(f"Invalid log format: {self.log_format}")
        
        if self.max_backups < 0:
            raise ValueError(f"Invalid max_backups: {self.max_backups}")
        
        if self.retention_days < 0:
            raise ValueError(f"Invalid retention_days: {self.retention_days}")
        
        if self.secret_key == 'change-me-in-production' and not self.debug:
            import warnings
            warnings.warn(
                "Using default secret key in production mode! "
                "Set RADAR_SECRET_KEY environment variable.",
                UserWarning
            )
    
    def to_dict(self) -> dict:
        """Convert configuration to dictionary."""
        return {
            'server': {
                'host': self.host,
                'port': self.port,
                'debug': self.debug,
            },
            'data': {
                'data_dir': str(self.data_dir),
                'dist_dir': str(self.dist_dir),
            },
            'backup': {
                'enabled': self.backup_enabled,
                'max_backups': self.max_backups,
                'retention_days': self.retention_days,
            },
            'logging': {
                'level': self.log_level,
                'file': self.log_file,
                'format': self.log_format,
            },
            'security': {
                'allowed_origins': self.allowed_origins,
            },
            'features': {
                'export': self.enable_export,
                'import': self.enable_import,
                'delete': self.enable_delete,
            },
            'performance': {
                'max_upload_size_mb': self.max_upload_size,
                'request_timeout_seconds': self.request_timeout,
            }
        }
    
    def __repr__(self) -> str:
        """String representation of configuration."""
        return f"Config(host={self.host}, port={self.port}, debug={self.debug})"


def load_config() -> Config:
    """
    Load configuration from environment variables.
    
    Optionally loads from .env file if python-dotenv is installed.
    
    Returns:
        Config: Configuration object
    """
    # Try to load .env file if python-dotenv is available
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass  # python-dotenv not installed, use environment variables only
    
    return Config()


# Global configuration instance
config = load_config()

# Made with Bob
