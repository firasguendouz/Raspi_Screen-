#!/usr/bin/env python3
"""
Utility functions for the Raspberry Pi Screen Management Server.
Provides input validation, sanitization, and common helper functions.
"""

import re
import html
from typing import Optional

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