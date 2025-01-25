#!/usr/bin/env python3
"""QR Code generation module for the Raspberry Pi Screen Management Server.

This module handles the generation of QR codes for WiFi configuration and URLs,
with support for styling, caching, and logo embedding.
"""

import os
import json
import hashlib
from typing import Optional, Dict, Any, Union
from pathlib import Path
from datetime import datetime, timedelta
import qrcode
from PIL import Image
from .utils import (
    logger,
    validate_input,
    validate_color,
    ValidationError,
    ConfigurationError
)

# Constants
CACHE_DURATION = timedelta(hours=24)
DEFAULT_LOGO_PATH = os.path.join(os.path.dirname(__file__), 'static/logo.png')
QR_VERSION = 1
QR_BOX_SIZE = 10
QR_BORDER = 4
DEFAULT_COLOR = "#000000"

class QRCodeCache:
    """Manages caching of generated QR codes."""

    def __init__(self, cache_dir: str = "qr_cache"):
        """Initialize QR code cache.

        Args:
            cache_dir: Directory to store cached QR codes
        """
        self.cache_dir = cache_dir
        self.index_file = os.path.join(cache_dir, "index.json")
        self._ensure_cache_dir()
        self.cache_index = self._load_cache_index()

    def _ensure_cache_dir(self) -> None:
        """Create cache directory if it doesn't exist."""
        os.makedirs(self.cache_dir, exist_ok=True)

    def _load_cache_index(self) -> Dict[str, Any]:
        """Load cache index from file.

        Returns:
            Cache index dictionary
        """
        try:
            with open(self.index_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def _save_cache_index(self) -> None:
        """Save cache index to file."""
        with open(self.index_file, 'w') as f:
            json.dump(self.cache_index, f)

    def _generate_key(self, data: Dict[str, Any]) -> str:
        """Generate unique cache key for QR code data.

        Args:
            data: QR code data dictionary

        Returns:
            Cache key string
        """
        data_str = json.dumps(data, sort_keys=True)
        return hashlib.sha256(data_str.encode()).hexdigest()

    def get(self, data: Dict[str, Any]) -> Optional[str]:
        """Get cached QR code path if available.

        Args:
            data: QR code data dictionary

        Returns:
            Path to cached QR code or None if not found
        """
        key = self._generate_key(data)
        if key not in self.cache_index:
            return None

        entry = self.cache_index[key]
        created = datetime.fromisoformat(entry['created'])
        if datetime.now() - created > CACHE_DURATION:
            self._cleanup(key)
            return None

        file_path = os.path.join(self.cache_dir, f"{key}.png")
        return file_path if os.path.exists(file_path) else None

    def put(self, data: Dict[str, Any], file_path: str) -> str:
        """Add QR code to cache.

        Args:
            data: QR code data dictionary
            file_path: Path to QR code file

        Returns:
            Cache file path
        """
        key = self._generate_key(data)
        cache_path = os.path.join(self.cache_dir, f"{key}.png")
        
        if os.path.exists(file_path):
            os.replace(file_path, cache_path)
            self.cache_index[key] = {
                'created': datetime.now().isoformat(),
                'data': data
            }
            self._save_cache_index()
        
        return cache_path

    def _cleanup(self, key: str) -> None:
        """Remove expired cache entry.

        Args:
            key: Cache key to remove
        """
        file_path = os.path.join(self.cache_dir, f"{key}.png")
        try:
            os.remove(file_path)
        except FileNotFoundError:
            pass
        self.cache_index.pop(key, None)
        self._save_cache_index()

def create_styled_qr(
    data: str,
    color: str = DEFAULT_COLOR,
    version: int = QR_VERSION,
    box_size: int = QR_BOX_SIZE,
    border: int = QR_BORDER
) -> Image.Image:
    """Create a styled QR code.

    Args:
        data: Content to encode in QR code
        color: Hex color code for QR code
        version: QR code version
        box_size: Size of each box in pixels
        border: Border size in boxes

    Returns:
        Generated QR code image

    Raises:
        ValidationError: If color format is invalid
    """
    if not validate_color(color):
        raise ValidationError(f"Invalid color format: {color}")

    qr = qrcode.QRCode(
        version=version,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=box_size,
        border=border
    )
    qr.add_data(data)
    qr.make(fit=True)

    rgb_color = tuple(int(color[i:i+2], 16) for i in (1, 3, 5))
    return qr.make_image(fill_color=rgb_color, back_color="white")

def add_logo(
    qr_image: Image.Image,
    logo_path: str = DEFAULT_LOGO_PATH,
    scale: float = 0.2
) -> Image.Image:
    """Add logo to center of QR code.

    Args:
        qr_image: Base QR code image
        logo_path: Path to logo file
        scale: Logo size relative to QR code

    Returns:
        QR code with embedded logo

    Raises:
        ConfigurationError: If logo file is not found
    """
    try:
        logo = Image.open(logo_path)
    except FileNotFoundError:
        raise ConfigurationError(f"Logo file not found: {logo_path}")

    # Calculate logo size
    logo_size = int(qr_image.size[0] * scale)
    logo = logo.resize((logo_size, logo_size))

    # Calculate position to center logo
    pos = ((qr_image.size[0] - logo_size) // 2,
           (qr_image.size[1] - logo_size) // 2)

    # Create copy of QR code and paste logo
    qr_with_logo = qr_image.copy()
    qr_with_logo.paste(logo, pos)
    return qr_with_logo

def generate_wifi_qr(
    ssid: str,
    password: str,
    security: str = "WPA",
    color: str = DEFAULT_COLOR,
    add_logo_flag: bool = True,
    cache: Optional[QRCodeCache] = None
) -> str:
    """Generate QR code for WiFi configuration.

    Args:
        ssid: Network name
        password: Network password
        security: Security type (WPA/WEP/nopass)
        color: QR code color
        add_logo_flag: Whether to add logo
        cache: Optional QR code cache

    Returns:
        Path to generated QR code image

    Raises:
        ValidationError: If input validation fails
    """
    # Validate inputs
    ssid = validate_input(ssid, max_length=32)
    if security.upper() not in ["WPA", "WEP", "nopass"]:
        raise ValidationError(f"Invalid security type: {security}")

    # Prepare QR code data
    data = {
        "ssid": ssid,
        "password": password,
        "security": security,
        "color": color,
        "add_logo": add_logo_flag
    }

    # Check cache
    if cache:
        cached_path = cache.get(data)
        if cached_path:
            return cached_path

    # Generate WiFi configuration string
    wifi_string = f"WIFI:T:{security};S:{ssid};P:{password};;"

    # Create QR code
    qr_image = create_styled_qr(wifi_string, color=color)
    if add_logo_flag:
        qr_image = add_logo(qr_image)

    # Save QR code
    output_dir = os.path.join(os.path.dirname(__file__), "static/qr")
    os.makedirs(output_dir, exist_ok=True)
    
    temp_path = os.path.join(output_dir, f"temp_{datetime.now().timestamp()}.png")
    qr_image.save(temp_path)

    # Add to cache if enabled
    if cache:
        return cache.put(data, temp_path)
    
    return temp_path

# Initialize cache
qr_cache = QRCodeCache()

def generate_qr_code(data, output_file, qr_type="wifi"):
    """
    Unified QR code generator for both WiFi and URL data.
    
    Args:
        data (dict or str): For WiFi: dict with ssid/password, For URL: string
        output_file (str): Path to save QR code image
        qr_type (str): Either "wifi" or "url"
    
    Returns:
        str: Path to generated QR code file or None if failed
    """
    try:
        if qr_type == "wifi" and isinstance(data, dict):
            qr_string = f"WIFI:T:WPA;S:{data['ssid']};P:{data['password']};;"
        elif qr_type == "url" and isinstance(data, str):
            qr_string = data
        else:
            raise ValueError("Invalid data format for QR type")

        # Generate QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_string)
        qr.make(fit=True)

        # Create and save image
        img = qr.make_image(fill_color="black", back_color="white")
        img.save(output_file)
        print(f"QR code generated successfully: {output_file}")
        return output_file

    except Exception as e:
        print(f"Error generating QR code: {e}")
        return None

# Helper functions for specific QR types
def generate_url_qr(url, output_file="url_qr.png"):
    """Generate URL redirect QR code"""
    return generate_qr_code(url, output_file, "url")