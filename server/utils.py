#!/usr/bin/env python3
"""
Utility functions for the Raspberry Pi Screen Management Server.
Provides input validation, sanitization, and common helper functions.
"""

import re
import html
from typing import Optional, Any, Dict, Union
import logging
import ipaddress
from pathlib import Path
from functools import wraps
from datetime import datetime
import json

# Custom exception classes
class ValidationError(Exception):
    """Raised when input validation fails."""
    pass

class ConfigurationError(Exception):
    """Raised when configuration is invalid or missing."""
    pass

class NetworkError(Exception):
    """Raised when network operations fail."""
    pass

# Error message templates
ERROR_MESSAGES = {
    'invalid_input': 'Input contains invalid characters: {details}',
    'invalid_length': 'Input length must be between {min_len} and {max_len}',
    'invalid_ip': 'Invalid IP address format: {ip}',
    'invalid_url': 'Invalid URL format: {url}',
    'invalid_color': 'Invalid color format: {color}',
    'config_not_found': 'Configuration file not found: {path}',
    'network_unreachable': 'Network is unreachable: {details}'
}

def setup_logging(
    name: str,
    level: str = "INFO",
    log_file: Optional[str] = None
) -> logging.Logger:
    """Configure logging with file and console handlers.

    Args:
        name: Logger name
        level: Logging level (default: INFO)
        log_file: Optional log file path

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))

    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler if specified
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger

def validate_input(
    text: str,
    min_length: int = 1,
    max_length: int = 100,
    pattern: str = r'^[\w\s\-\.@!()]+$'
) -> str:
    """Validate and sanitize user input.

    Args:
        text: Input text to validate
        min_length: Minimum allowed length
        max_length: Maximum allowed length
        pattern: Regex pattern for allowed characters

    Returns:
        Sanitized input string

    Raises:
        ValidationError: If input is invalid
    """
    if not min_length <= len(text) <= max_length:
        raise ValidationError(
            ERROR_MESSAGES['invalid_length'].format(
                min_len=min_length,
                max_length=max_length
            )
        )

    if not re.match(pattern, text):
        raise ValidationError(
            ERROR_MESSAGES['invalid_input'].format(
                details='Contains invalid characters'
            )
        )

    return text.strip()

def validate_ip_address(ip: str) -> bool:
    """Validate IPv4 or IPv6 address format.

    Args:
        ip: IP address string

    Returns:
        True if valid, False otherwise
    """
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False

def validate_color(color: str) -> bool:
    """Validate hex color code format.

    Args:
        color: Hex color code (e.g., #FF0000)

    Returns:
        True if valid, False otherwise
    """
    return bool(re.match(r'^#[0-9A-Fa-f]{6}$', color))

def load_config(path: Union[str, Path]) -> Dict[str, Any]:
    """Load configuration from JSON file.

    Args:
        path: Path to configuration file

    Returns:
        Configuration dictionary

    Raises:
        ConfigurationError: If file not found or invalid
    """
    try:
        with open(path) as f:
            return json.load(f)
    except FileNotFoundError:
        raise ConfigurationError(
            ERROR_MESSAGES['config_not_found'].format(path=path)
        )
    except json.JSONDecodeError as e:
        raise ConfigurationError(f'Invalid JSON in config file: {e}')

def log_execution_time(logger: logging.Logger):
    """Decorator to log function execution time.

    Args:
        logger: Logger instance to use
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start = datetime.now()
            result = func(*args, **kwargs)
            duration = (datetime.now() - start).total_seconds()
            logger.debug(
                f'{func.__name__} executed in {duration:.2f} seconds'
            )
            return result
        return wrapper
    return decorator

# Initialize default logger
logger = setup_logging(__name__)

def sanitize_input(text: str) -> str:
    """
    Sanitize user input by removing dangerous characters and HTML escaping.
    
    Args:
        text: Input text to sanitize
        
    Returns:
        Sanitized text string
    """
    # Remove control characters
    text = ''.join(char for char in text if ord(char) >= 32)
    
    # HTML escape
    text = html.escape(text)
    
    # Remove potentially dangerous characters
    text = re.sub(r'[;<>&\'"\\]', '', text)
    
    return text.strip()

def validate_ssid(ssid: str) -> bool:
    """
    Validate WiFi SSID format.
    
    Args:
        ssid: Network SSID to validate
        
    Returns:
        True if SSID is valid, False otherwise
    """
    if not ssid:
        return False
        
    # Check length (1-32 characters)
    if len(ssid) > 32:
        return False
        
    # Check for valid characters
    if not re.match(r'^[\w\-\s\.\@\!\(\)]+$', ssid):
        return False
        
    return True

def validate_password(password: str) -> bool:
    """
    Validate WiFi password format.
    
    Args:
        password: Network password to validate
        
    Returns:
        True if password is valid, False otherwise
    """
    # Empty password is valid for open networks
    if not password:
        return True
        
    # Check length (8-63 characters for WPA)
    if len(password) < 8 or len(password) > 63:
        return False
        
    # Check for valid characters
    if not re.match(r'^[\w\-\s\.\@\!\(\)\{\}\[\]\:\;\<\>\,\?\|\~\`\#\$\%\^\&\*\+\=]+$', password):
        return False
        
    return True

def parse_signal_strength(quality: str) -> Optional[int]:
    """
    Parse WiFi signal strength from iwlist output.
    
    Args:
        quality: Signal quality string from iwlist
        
    Returns:
        Signal strength as percentage or None if parsing fails
    """
    try:
        match = re.search(r'(\d+)/(\d+)', quality)
        if match:
            current, max_val = map(int, match.groups())
            return int((current / max_val) * 100)
    except Exception:
        pass
    return None

def format_bytes(size: int) -> str:
    """
    Format byte size to human readable string.
    
    Args:
        size: Size in bytes
        
    Returns:
        Formatted string (e.g., "1.5 MB")
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} PB"

def is_valid_url(url: str) -> bool:
    """
    Validate URL format.
    
    Args:
        url: URL to validate
        
    Returns:
        True if URL is valid, False otherwise
    """
    pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return bool(pattern.match(url))

def generate_safe_filename(filename: str) -> str:
    """
    Generate a safe filename from user input.
    
    Args:
        filename: Original filename
        
    Returns:
        Safe filename string
    """
    # Remove invalid characters
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)
    
    # Limit length
    filename = filename[:255]
    
    return filename.strip('. ')

def parse_mac_address(mac: str) -> Optional[str]:
    """
    Validate and format MAC address.
    
    Args:
        mac: MAC address string
        
    Returns:
        Formatted MAC address or None if invalid
    """
    mac = mac.replace(':', '').replace('-', '').upper()
    if len(mac) != 12 or not mac.isalnum():
        return None
    return ':'.join(mac[i:i+2] for i in range(0, 12, 2))

def validate_ip_address(ip: str) -> bool:
    """
    Validate IPv4 address format.
    
    Args:
        ip: IP address to validate
        
    Returns:
        True if IP is valid, False otherwise
    """
    try:
        parts = ip.split('.')
        if len(parts) != 4:
            return False
        return all(0 <= int(part) <= 255 for part in parts)
    except (AttributeError, TypeError, ValueError):
        return False 