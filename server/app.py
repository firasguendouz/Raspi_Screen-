#!/usr/bin/env python3
"""
Flask Application for Raspberry Pi Screen Management
Provides web interface and API endpoints for device configuration and monitoring.
"""

import os
import json
import asyncio
import logging
from datetime import datetime
from functools import wraps
from typing import Dict, List, Optional, Any
from pathlib import Path

from flask import Flask, request, jsonify, render_template, send_file, send_from_directory, current_app
from flask_babel import Babel, gettext as _
from werkzeug.middleware.proxy_fix import ProxyFix
import subprocess

from .qr_code import generate_wifi_qr, QRCodeCache
from .utils import (
    sanitize_input,
    validate_ssid,
    validate_password,
    validate_color,
    ValidationError,
    NetworkError,
    log_execution_time
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/raspi_screen/server.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config.from_object('config.default')

# Load environment-specific config
env = os.getenv('FLASK_ENV', 'development')
app.config.from_object(f'config.{env}')

# Configure Babel for i18n
babel = Babel(app)
app.config['BABEL_DEFAULT_LOCALE'] = 'en'
app.config['LANGUAGES'] = {
    'en': 'English',
    'es': 'Español',
    'fr': 'Français',
    'de': 'Deutsch'
}

# Configure proxy settings
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Initialize QR code cache
qr_cache = QRCodeCache(app.config['QR_CACHE_DIR'])

# Error messages
ERROR_MESSAGES = {
    'invalid_ssid': _('Invalid SSID format'),
    'invalid_password': _('Invalid password format'),
    'invalid_color': _('Invalid color format'),
    'network_scan_failed': _('Network scan failed'),
    'connection_failed': _('Failed to connect to network'),
    'qr_generation_failed': _('Failed to generate QR code'),
    'file_not_found': _('File not found')
}

def log_request(f):
    """Decorator to log request details."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Log request details
        logger.info(
            'Request: %s %s - IP: %s - User-Agent: %s',
            request.method,
            request.path,
            request.remote_addr,
            request.user_agent
        )
        return f(*args, **kwargs)
    return decorated_function

@babel.select_locale
def get_locale():
    """Determine the best language for the user."""
    # Check URL parameter
    lang = request.args.get('lang')
    if lang and lang in app.config['LANGUAGES']:
        return lang
        
    # Check Accept-Language header
    return request.accept_languages.best_match(app.config['LANGUAGES'].keys())

def handle_errors(f):
    """Decorator for consistent error handling across routes."""
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except ValidationError as e:
            logger.warning(f"Validation error: {str(e)}")
            return jsonify({'error': str(e)}), 400
        except NetworkError as e:
            logger.error(f"Network error: {str(e)}")
            return jsonify({'error': str(e)}), 503
        except Exception as e:
            logger.exception("Unexpected error")
            return jsonify({'error': _('Internal server error')}), 500
    return wrapper

async def scan_networks() -> List[Dict[str, Any]]:
    """
    Scan for available WiFi networks asynchronously.
    
    Returns:
        List of dictionaries containing network information
    """
    try:
        # Run iwlist scan
        proc = await asyncio.create_subprocess_shell(
            "sudo iwlist wlan0 scan | grep -E 'ESSID|Quality'",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await proc.communicate()
        
        if proc.returncode != 0:
            raise NetworkError(ERROR_MESSAGES['network_scan_failed'])
            
        # Parse output
        output = stdout.decode()
        networks = []
        current_network = {}
        
        for line in output.split('\n'):
            if 'ESSID' in line:
                if current_network:
                    networks.append(current_network)
                current_network = {'ssid': line.split(':')[1].strip('"')}
            elif 'Quality' in line:
                quality = line.split('=')[1].split('/')[0]
                current_network['quality'] = int(quality)
                
        if current_network:
            networks.append(current_network)
            
        return sorted(networks, key=lambda x: x['quality'], reverse=True)
        
    except Exception as e:
        logger.exception("Network scan failed")
        raise NetworkError(ERROR_MESSAGES['network_scan_failed'])

@app.route('/')
@log_request
def index():
    """Render main page."""
    return render_template(
        'index.html',
        title=gettext('Raspberry Pi Screen Management'),
        languages=app.config['LANGUAGES'],
        current_lang=get_locale()
    )

@app.route('/api/networks', methods=['GET'])
@log_request
@handle_errors
async def get_networks():
    """API endpoint to scan for WiFi networks."""
    networks = await scan_networks()
    return jsonify({'networks': networks})

@app.route('/api/connect', methods=['POST'])
@log_request
@handle_errors
@log_execution_time(logger)
def connect_wifi():
    """API endpoint to connect to WiFi network."""
    try:
        # Accept both JSON and form data
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form.to_dict()
        
        # Validate and sanitize input
        ssid = sanitize_input(data.get('ssid', ''))
        password = data.get('password', '')
        color = data.get('color', '#000000')
        
        if not validate_ssid(ssid):
            raise ValidationError(ERROR_MESSAGES['invalid_ssid'])
        if not validate_password(password):
            raise ValidationError(ERROR_MESSAGES['invalid_password'])
        if not validate_color(color):
            raise ValidationError(ERROR_MESSAGES['invalid_color'])
            
        # Generate QR code
        try:
            qr_path = generate_wifi_qr(
                ssid=ssid,
                password=password,
                color=color,
                cache=qr_cache
            )
        except Exception as e:
            logger.exception("QR code generation failed")
            raise ValidationError(ERROR_MESSAGES['qr_generation_failed'])
            
        # Return QR code path
        return jsonify({
            'success': True,
            'qr_code': os.path.basename(qr_path)
        })
        
    except Exception as e:
        logger.error("WiFi connection failed: %s", str(e))
        raise ValidationError(ERROR_MESSAGES['connection_failed'])

@app.route('/qr/<path:filename>')
@log_request
@handle_errors
def serve_qr(filename):
    """Serve generated QR code images."""
    try:
        return send_from_directory(
            app.config['QR_CACHE_DIR'],
            filename
        )
    except Exception as e:
        logger.error("Error serving QR code: %s", str(e))
        raise ValidationError(ERROR_MESSAGES['file_not_found'])

@app.route('/translations/<lang>')
def get_translations(lang):
    """Get translation strings for specified language."""
    if lang not in app.config['LANGUAGES']:
        return jsonify({'error': 'Language not supported'}), 400

    translations = {}
    try:
        translation_file = Path(app.root_path) / 'translations' / lang / 'LC_MESSAGES' / 'messages.json'
        if translation_file.exists():
            with open(translation_file, 'r', encoding='utf-8') as f:
                translations = json.load(f)
    except Exception as e:
        logger.warning(f"Failed to load translations for {lang}: {e}")

    return jsonify(translations)

@app.errorhandler(Exception)
def handle_error(error):
    """Global error handler."""
    logger.error("Unhandled error: %s", str(error))
    return jsonify({
        'error': 'Internal server error',
        'message': str(error)
    }), 500

if __name__ == '__main__':
    # Ensure log directory exists
    os.makedirs('/var/log/raspi_screen', exist_ok=True)
    
    # Run app
    app.run(host='0.0.0.0', port=5000)
