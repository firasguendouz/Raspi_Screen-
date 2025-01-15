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
app.secret_key = secrets.token_hex(32)






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

@app.before_request
def csrf_protect():
    """Protect against CSRF attacks"""
    if request.method == "POST":
        token = session.get('_csrf_token')
        if not token or token != request.form.get('_csrf_token'):
            return jsonify({'status': 'error', 'message': 'CSRF validation failed'}), 403

@app.route('/')
def index():
    """Serve the Wi-Fi setup page."""
    return render_template('index.html')

@app.route('/configure', methods=['POST'])

def submit():
    """Handle Wi-Fi credentials submission with advanced configuration."""
    try:
        # Sanitize inputs
        ssid = sanitize_input(request.form.get('ssid', ''))
        password = request.form.get('password', '')
        country = sanitize_input(request.form.get('country', 'US'))
        channel = sanitize_input(request.form.get('channel', 'auto'))
        
        
        
        # Generate WPA supplicant configuration with encrypted password
        config = f"""
        ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
        update_config=1
        country={country}

        network={{
            ssid=\"{ssid}\"
            psk=\"{password}\"
            key_mgmt=WPA-PSK
            scan_ssid=1
            {f"channel={channel}" if channel != 'auto' else ''}
        }}
        """
        
        # Write configuration
        with open('/etc/wpa_supplicant/wpa_supplicant.conf', 'w') as f:
            f.write(config)
            
        # Restart networking services
        subprocess.run(['sudo', 'systemctl', 'restart', 'wpa_supplicant'], check=True)
        
        # Monitor connection status
        max_retries = 3
        for attempt in range(max_retries):
            try:
                # Check if connected
                check_cmd = "iwconfig wlan0 | grep 'ESSID:'"
                output = subprocess.check_output(check_cmd, shell=True).decode()
                if ssid in output:
                    app.logger.info(f"Successfully connected to {ssid}")
                    return jsonify({
                        'status': 'success',
                        'message': 'Connected successfully'
                    })
            except:
                app.logger.warning(f"Connection attempt {attempt + 1} failed")
                time.sleep(2)  # Wait before retry
                
        raise Exception("Failed to establish connection after multiple attempts")
            
    except Exception as e:
        app.logger.error(f"Configuration failed: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'Configuration failed: {str(e)}'
        })

@app.route('/scan', methods=['GET'])
def scan_networks():
    """Scan for available Wi-Fi networks with enhanced network information."""
    try:
        # Full scan command to get all network information
        cmd = "sudo iwlist wlan0 scan"
        output = subprocess.check_output(cmd, shell=True).decode('utf-8')
        
        networks = []
        current_network = {}
        
        for line in output.split('\n'):
            line = line.strip()
            
            # Extract ESSID
            if "ESSID:" in line:
                current_network['ssid'] = line.split('ESSID:')[1].strip('"')
                networks.append(current_network)
                current_network = {}
                
            # Extract Encryption
            elif "Encryption key:" in line:
                current_network['encryption'] = "Yes" if "on" in line.lower() else "No"
                
            # Extract WPA/WPA2
            elif "IE: IEEE 802.11i/WPA2" in line:
                current_network['security'] = "WPA2"
            elif "IE: WPA Version 1" in line:
                current_network['security'] = "WPA"
                
            # Extract Signal Level
            elif "Signal level=" in line:
                match = re.search(r"Signal level=(-\d+) dBm", line)
                if match:
                    current_network['signal'] = match.group(1)

        app.logger.info(f"Scanned networks: {len(networks)} found")
        return jsonify({'networks': networks})
        
    except Exception as e:
        app.logger.error(f"Network scan failed: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/login', methods=['POST'])
def login():
    """Handle admin login"""
    username = sanitize_input(request.form.get('username'))
    password = request.form.get('password')
    
    # Add your authentication logic here
    if username == "admin" and password == "secure_password":
        session['logged_in'] = True
        session['_csrf_token'] = secrets.token_hex(32)
        return jsonify({'status': 'success'})
    return jsonify({'status': 'error'}), 401

# Add to existing Flask app
translation_service = TranslationService()
app.jinja_env.globals.update(t=translation_service.get_translation)

if __name__ == '__main__':
    setup_logging()
    app.run(host='0.0.0.0', port=80)
