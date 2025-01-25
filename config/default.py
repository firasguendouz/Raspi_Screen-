"""
Default Flask application configuration
"""

import os

# Flask settings
SECRET_KEY = os.environ.get('SECRET_KEY', 'dev_key_change_this_in_production')
DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'

# Server settings
HOST = os.environ.get('FLASK_HOST', '0.0.0.0')
PORT = int(os.environ.get('FLASK_PORT', 5000))

# Logging
LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
LOG_DIR = '/var/log/raspi_screen'
LOG_FILE = os.path.join(LOG_DIR, 'server.log')

# Application settings
DISPLAY_ROTATION = int(os.environ.get('DISPLAY_ROTATION', 0))  # 0, 90, 180, or 270 degrees
DISPLAY_WIDTH = int(os.environ.get('DISPLAY_WIDTH', 800))
DISPLAY_HEIGHT = int(os.environ.get('DISPLAY_HEIGHT', 480))

# Access Point settings
AP_INTERFACE = os.environ.get('AP_INTERFACE', 'wlan0')
AP_SSID = os.environ.get('AP_SSID', 'RaspberryPi_AP')
AP_PASSPHRASE = os.environ.get('AP_PASSPHRASE', 'raspberry') 