"""
Development environment configuration
"""

from .default import *

# Enable debug mode
DEBUG = True

# Use a more verbose log level
LOG_LEVEL = 'DEBUG'

# QR code cache directory
QR_CACHE_DIR = '/tmp/qr_cache'

# Development server settings
HOST = 'localhost'
PORT = 5000 