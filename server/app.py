import time
from flask import Flask, render_template, request, jsonify, session
import bleach
import secrets
import base64
import subprocess
import os
import logging
from logging.handlers import RotatingFileHandler
import re
from translation import TranslationService

app = Flask(__name__)






def sanitize_input(text):
    """Sanitize user input"""
    return bleach.clean(text, strip=True)

# Configure logging
def setup_logging():
    """Configure application logging with rotation"""
    log_file = '/var/log/wifi_setup.log'
    handler = RotatingFileHandler(log_file, maxBytes=1024*1024, backupCount=5)
    handler.setFormatter(logging.Formatter(
        '[%(asctime)s] %(levelname)s: %(message)s'
    ))
    app.logger.addHandler(handler)
    app.logger.setLevel(logging.INFO)



@app.route('/')
def index():
    """Serve the Wi-Fi setup page."""
    return render_template('index.html')

@app.route('/configure', methods=['POST'])
def submit():
    """Handle Wi-Fi credentials submission."""
    try:
        # Sanitize inputs
        ssid = sanitize_input(request.form.get('ssid', ''))
        password = request.form.get('password', '')
        
        # Write credentials to a temporary file for main process to read
        creds_file = 'wifi_credentials.tmp'
        with open(creds_file, 'w') as f:
            f.write(f"{ssid}\n{password}")
            
        return jsonify({
            'status': 'success',
            'message': 'Credentials received'
        })
            
    except Exception as e:
        app.logger.error(f"Failed to save credentials: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'Failed to save credentials: {str(e)}'
        })

@app.route('/scan', methods=['GET'])
def scan_networks():
    """Scan for available Wi-Fi networks with enhanced network information and error handling."""
    try:
        # Try multiple scan attempts
        max_retries = 3
        for attempt in range(max_retries):
            try:
                # Ensure interface is up
                subprocess.run(['sudo', 'ifconfig', 'wlan0', 'up'], check=True)
                time.sleep(1)
                
                # Full scan command
                cmd = "sudo iwlist wlan0 scan"
                output = subprocess.check_output(cmd, shell=True, timeout=10).decode('utf-8')
                
                networks = []
                current_network = {}
                
                for line in output.split('\n'):
                    line = line.strip()
                    
                    if "Cell" in line:  # New network found
                        if current_network and 'ssid' in current_network:
                            networks.append(current_network)
                        current_network = {}
                    
                    # Extract network information
                    if "ESSID:" in line:
                        ssid = line.split('ESSID:')[1].strip('"')
                        if ssid:  # Only add non-empty SSIDs
                            current_network['ssid'] = ssid
                    elif "Encryption key:" in line:
                        current_network['encryption'] = "Yes" if "on" in line.lower() else "No"
                    elif "IE: IEEE 802.11i/WPA2" in line:
                        current_network['security'] = "WPA2"
                    elif "IE: WPA Version 1" in line:
                        current_network['security'] = "WPA"
                    elif "Signal level=" in line:
                        match = re.search(r"Signal level=(-\d+) dBm", line)
                        if match:
                            current_network['signal'] = match.group(1)
                
                # Add last network if exists
                if current_network and 'ssid' in current_network:
                    networks.append(current_network)
                
                if networks:
                    app.logger.info(f"Successfully scanned {len(networks)} networks")
                    return jsonify({'networks': networks})
                
            except subprocess.TimeoutExpired:
                app.logger.warning(f"Scan attempt {attempt + 1} timed out")
                if attempt < max_retries - 1:
                    time.sleep(2)
                    continue
                
        return jsonify({'networks': [], 'message': 'No networks found'})
        
    except Exception as e:
        app.logger.error(f"Network scan failed: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e), 'networks': []})

# Add to existing Flask app
translation_service = TranslationService()
app.jinja_env.globals.update(t=translation_service.get_translation)

if __name__ == '__main__':
    setup_logging()
    app.run(host='0.0.0.0', port=80)
