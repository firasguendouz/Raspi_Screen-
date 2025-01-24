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
from typing import Dict, List, Optional

from flask import Flask, request, jsonify, render_template, send_file
from flask_babel import Babel, gettext
from werkzeug.middleware.proxy_fix import ProxyFix
import subprocess

from .qr_code import generate_wifi_qr
from .utils import sanitize_input, validate_ssid, validate_password

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
app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY', 'default-secret-key')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

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

@babel.localeselector
def get_locale():
    """Determine the best language for the user."""
    # Check URL parameter
    lang = request.args.get('lang')
    if lang and lang in app.config['LANGUAGES']:
        return lang
        
    # Check Accept-Language header
    return request.accept_languages.best_match(app.config['LANGUAGES'].keys())

async def scan_networks() -> List[Dict]:
    """
    Scan for available WiFi networks asynchronously.
    
    Returns:
        List of dictionaries containing network information
    """
    try:
        # Run iwlist scan
        proc = await asyncio.create_subprocess_shell(
            "sudo iwlist wlan0 scan | grep -E 'ESSID|Quality|Encryption'",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await proc.communicate()
        
        if proc.returncode != 0:
            logger.error("Network scan failed: %s", stderr.decode())
            return []
            
        # Parse output
        output = stdout.decode()
        networks = []
        current_network = {}
        
        for line in output.split('\n'):
            if 'ESSID' in line:
                if current_network:
                    networks.append(current_network)
                current_network = {'ssid': line.split('"')[1]}
            elif 'Quality' in line:
                quality = line.split('=')[1].split('/')[0]
                current_network['quality'] = int(quality)
            elif 'Encryption' in line:
                current_network['encrypted'] = 'on' in line.lower()
                
        if current_network:
            networks.append(current_network)
            
        return sorted(networks, key=lambda x: x['quality'], reverse=True)
        
    except Exception as e:
        logger.error("Error scanning networks: %s", str(e))
        return []

@app.route('/')
@log_request
def index():
    """Render main page."""
    return render_template(
        'index.html',
        title=gettext('Raspberry Pi Screen Management')
    )

@app.route('/api/networks', methods=['GET'])
@log_request
async def get_networks():
    """API endpoint to scan for WiFi networks."""
    networks = await scan_networks()
    return jsonify({'networks': networks})

@app.route('/api/connect', methods=['POST'])
@log_request
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
        
        if not validate_ssid(ssid):
            return jsonify({'error': 'Invalid SSID'}), 400
        if not validate_password(password):
            return jsonify({'error': 'Invalid password'}), 400
            
        # Generate QR code
        try:
            qr_path = generate_wifi_qr(
                ssid=ssid,
                password=password,
                security='WPA',
                color=data.get('color', '#000000'),
                add_logo_flag=data.get('add_logo', True)
            )
        except Exception as e:
            logger.error("QR code generation failed: %s", str(e))
            return jsonify({'error': 'QR code generation failed'}), 500
            
        # Return QR code path
        return jsonify({
            'success': True,
            'qr_code': qr_path
        })
        
    except Exception as e:
        logger.error("WiFi connection failed: %s", str(e))
        return jsonify({'error': str(e)}), 500

@app.route('/qr/<path:filename>')
@log_request
def serve_qr(filename):
    """Serve generated QR code images."""
    try:
        return send_file(
            os.path.join('qr_cache', filename),
            mimetype='image/png'
        )
    except Exception as e:
        logger.error("Error serving QR code: %s", str(e))
        return jsonify({'error': 'QR code not found'}), 404

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
