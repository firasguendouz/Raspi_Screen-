#!/usr/bin/env python3
"""
QR Code Generator for WiFi Configuration
Generates styled QR codes with optional logos and caching support.
"""

import os
import json
import hashlib
from typing import Optional, Dict
from datetime import datetime, timedelta
import qrcode
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers import RoundedModuleDrawer
from qrcode.image.styles.colormask import RadialGradiantColorMask
from PIL import Image

# Configuration
CACHE_DIR = "qr_cache"
LOGO_PATH = "static/logo.png"
CACHE_DURATION = timedelta(hours=24)

# Ensure cache directory exists
os.makedirs(CACHE_DIR, exist_ok=True)

class QRCodeCache:
    """Manages caching of generated QR codes."""
    
    def __init__(self, cache_dir: str = CACHE_DIR):
        self.cache_dir = cache_dir
        self.cache_index = self._load_cache_index()
    
    def _load_cache_index(self) -> Dict:
        """Load cache index from file."""
        index_path = os.path.join(self.cache_dir, "index.json")
        try:
            if os.path.exists(index_path):
                with open(index_path, 'r') as f:
                    return json.load(f)
            return {}
        except Exception:
            return {}
    
    def _save_cache_index(self) -> None:
        """Save cache index to file."""
        index_path = os.path.join(self.cache_dir, "index.json")
        try:
            with open(index_path, 'w') as f:
                json.dump(self.cache_index, f)
        except Exception:
            pass
    
    def _generate_key(self, data: str) -> str:
        """Generate cache key from data."""
        return hashlib.md5(data.encode()).hexdigest()
    
    def get(self, data: str) -> Optional[str]:
        """
        Retrieve QR code from cache if valid.
        
        Args:
            data: QR code content
            
        Returns:
            Path to cached QR code or None if not found/expired
        """
        key = self._generate_key(data)
        cache_info = self.cache_index.get(key)
        
        if not cache_info:
            return None
            
        file_path = os.path.join(self.cache_dir, f"{key}.png")
        if not os.path.exists(file_path):
            return None
            
        # Check expiration
        created = datetime.fromisoformat(cache_info['created'])
        if datetime.now() - created > CACHE_DURATION:
            self._cleanup(key)
            return None
            
        return file_path
    
    def put(self, data: str, file_path: str) -> None:
        """
        Add QR code to cache.
        
        Args:
            data: QR code content
            file_path: Path to QR code image
        """
        key = self._generate_key(data)
        self.cache_index[key] = {
            'created': datetime.now().isoformat(),
            'data': data
        }
        self._save_cache_index()
    
    def _cleanup(self, key: str) -> None:
        """Remove expired cache entry."""
        try:
            file_path = os.path.join(self.cache_dir, f"{key}.png")
            if os.path.exists(file_path):
                os.remove(file_path)
            self.cache_index.pop(key, None)
            self._save_cache_index()
        except Exception:
            pass

# Initialize cache
qr_cache = QRCodeCache()

def create_styled_qr(data: str, color: str = "#000000") -> Image:
    """
    Create a styled QR code with custom colors and rounded modules.
    
    Args:
        data: Content to encode
        color: Hex color code for QR code
        
    Returns:
        PIL Image object containing the styled QR code
    """
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    
    # Create styled QR code
    return qr.make_image(
        image_factory=StyledPilImage,
        module_drawer=RoundedModuleDrawer(),
        color_mask=RadialGradiantColorMask(
            back_color=(255, 255, 255),
            center_color=tuple(int(color[i:i+2], 16) for i in (1, 3, 5)),
            edge_color=(0, 0, 0)
        )
    )

def add_logo(qr_image: Image, scale: float = 0.2) -> Image:
    """
    Add logo to center of QR code.
    
    Args:
        qr_image: Base QR code image
        scale: Logo size relative to QR code
        
    Returns:
        QR code image with embedded logo
    """
    if not os.path.exists(LOGO_PATH):
        return qr_image
        
    try:
        logo = Image.open(LOGO_PATH)
        
        # Calculate logo size
        logo_size = int(qr_image.size[0] * scale)
        logo = logo.resize((logo_size, logo_size))
        
        # Calculate position
        pos = ((qr_image.size[0] - logo_size) // 2,
               (qr_image.size[1] - logo_size) // 2)
        
        # Create copy of QR code
        qr_with_logo = qr_image.copy()
        qr_with_logo.paste(logo, pos)
        
        return qr_with_logo
    except Exception:
        return qr_image

def generate_wifi_qr(
    ssid: str,
    password: str,
    security: str = "WPA",
    color: str = "#000000",
    add_logo_flag: bool = True
) -> str:
    """
    Generate QR code for WiFi configuration.
    
    Args:
        ssid: Network name
        password: Network password
        security: Security type (WPA/WEP/nopass)
        color: QR code color
        add_logo_flag: Whether to add logo
        
    Returns:
        Path to generated QR code image
    """
    # Validate input
    if not ssid:
        raise ValueError("SSID is required")
    if security not in ["WPA", "WEP", "nopass"]:
        raise ValueError("Invalid security type")
        
    # Generate WiFi configuration string
    wifi_string = f"WIFI:T:{security};S:{ssid};P:{password};;"
    
    # Check cache
    cached_path = qr_cache.get(wifi_string)
    if cached_path:
        return cached_path
    
    # Generate QR code
    qr_image = create_styled_qr(wifi_string, color)
    
    # Add logo if requested
    if add_logo_flag:
        qr_image = add_logo(qr_image)
    
    # Save and cache
    key = qr_cache._generate_key(wifi_string)
    file_path = os.path.join(CACHE_DIR, f"{key}.png")
    qr_image.save(file_path)
    qr_cache.put(wifi_string, file_path)
    
    return file_path

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