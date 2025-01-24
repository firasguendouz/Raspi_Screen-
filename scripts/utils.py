#!/usr/bin/env python3
"""
Utility module for Raspberry Pi Screen Management Scripts.
Provides centralized logging, configuration, and error handling.
"""

import os
import sys
import json
import logging
import logging.handlers
from pathlib import Path
from typing import Any, Dict, Optional
from dotenv import load_dotenv
import validators
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Load environment variables
load_dotenv()

# Constants
DEFAULT_LOG_DIR = "/var/log/raspi_screen"
DEFAULT_CONFIG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config")
DEFAULT_RETRY_ATTEMPTS = 3
DEFAULT_BACKOFF_FACTOR = 0.3

class ConfigurationError(Exception):
    """Exception raised for configuration-related errors."""
    pass

class NetworkError(Exception):
    """Exception raised for network-related errors."""
    pass

def setup_logging(script_name: str, log_level: str = "INFO") -> logging.Logger:
    """
    Configure logging for the script with both file and console handlers.
    
    Args:
        script_name: Name of the script for log file naming
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        
    Returns:
        Configured logger instance
    """
    # Create log directory if it doesn't exist
    log_dir = os.getenv("LOG_DIR", DEFAULT_LOG_DIR)
    os.makedirs(log_dir, exist_ok=True)
    
    # Configure logger
    logger = logging.getLogger(script_name)
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # File handler
    log_file = os.path.join(log_dir, f"{script_name}.log")
    file_handler = logging.handlers.RotatingFileHandler(
        log_file, maxBytes=1024*1024, backupCount=5
    )
    file_handler.setFormatter(
        logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    )
    logger.addHandler(file_handler)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(
        logging.Formatter('%(levelname)s: %(message)s')
    )
    logger.addHandler(console_handler)
    
    return logger

def load_config(config_name: str) -> Dict[str, Any]:
    """
    Load configuration from a JSON file in the config directory.
    
    Args:
        config_name: Name of the configuration file (without .json extension)
        
    Returns:
        Dictionary containing configuration values
        
    Raises:
        ConfigurationError: If config file is not found or invalid
    """
    config_dir = os.getenv("CONFIG_DIR", DEFAULT_CONFIG_DIR)
    config_file = os.path.join(config_dir, f"{config_name}.json")
    
    try:
        with open(config_file, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        raise ConfigurationError(f"Configuration file not found: {config_file}")
    except json.JSONDecodeError:
        raise ConfigurationError(f"Invalid JSON in configuration file: {config_file}")

def create_http_session(
    retries: int = DEFAULT_RETRY_ATTEMPTS,
    backoff_factor: float = DEFAULT_BACKOFF_FACTOR
) -> requests.Session:
    """
    Create an HTTP session with retry capabilities.
    
    Args:
        retries: Number of retry attempts
        backoff_factor: Backoff factor for exponential delay
        
    Returns:
        Configured requests Session object
    """
    session = requests.Session()
    retry_strategy = Retry(
        total=retries,
        backoff_factor=backoff_factor,
        status_forcelist=[429, 500, 502, 503, 504]
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session

def validate_url(url: str) -> bool:
    """
    Validate if a URL is well-formed.
    
    Args:
        url: URL to validate
        
    Returns:
        True if URL is valid, False otherwise
    """
    return bool(validators.url(url))

def backup_file(file_path: str) -> str:
    """
    Create a backup of a file.
    
    Args:
        file_path: Path to the file to backup
        
    Returns:
        Path to the backup file
        
    Raises:
        IOError: If backup creation fails
    """
    backup_path = f"{file_path}.backup"
    try:
        if os.path.exists(file_path):
            with open(file_path, 'rb') as src, open(backup_path, 'wb') as dst:
                dst.write(src.read())
        return backup_path
    except IOError as e:
        raise IOError(f"Failed to create backup of {file_path}: {str(e)}")

def restore_file(backup_path: str, original_path: str) -> None:
    """
    Restore a file from its backup.
    
    Args:
        backup_path: Path to the backup file
        original_path: Path where to restore the file
        
    Raises:
        IOError: If restoration fails
    """
    try:
        if os.path.exists(backup_path):
            with open(backup_path, 'rb') as src, open(original_path, 'wb') as dst:
                dst.write(src.read())
            os.remove(backup_path)
    except IOError as e:
        raise IOError(f"Failed to restore {original_path} from backup: {str(e)}")

def get_system_metrics() -> Dict[str, Any]:
    """
    Collect system metrics for monitoring.
    
    Returns:
        Dictionary containing system metrics
    """
    import psutil
    
    metrics = {
        'cpu_percent': psutil.cpu_percent(),
        'memory_percent': psutil.virtual_memory().percent,
        'disk_usage': psutil.disk_usage('/').percent,
        'uptime': int(time.time() - psutil.boot_time()),
        'network': {
            'bytes_sent': psutil.net_io_counters().bytes_sent,
            'bytes_recv': psutil.net_io_counters().bytes_recv
        }
    }
    return metrics

def validate_wifi_credentials(ssid: str, password: Optional[str] = None) -> bool:
    """
    Validate WiFi credentials format.
    
    Args:
        ssid: WiFi network name
        password: WiFi password (optional)
        
    Returns:
        True if credentials are valid, False otherwise
    """
    if not ssid or len(ssid) > 32:
        return False
    if password and (len(password) < 8 or len(password) > 63):
        return False
    return True 