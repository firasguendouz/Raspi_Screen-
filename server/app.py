from flask import Flask, render_template, request, jsonify
import subprocess
import os

app = Flask(__name__)

def restart_wifi_service(ssid, password):
    """Save Wi-Fi credentials and restart the Wi-Fi service."""
    try:
        # Write Wi-Fi credentials to wpa_supplicant.conf
        config = f"""
        ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
        update_config=1
        country=US

        network={{
            ssid=\"{ssid}\"
            psk=\"{password}\"
            key_mgmt=WPA-PSK
        }}
        """
        with open('/etc/wpa_supplicant/wpa_supplicant.conf', 'w') as f:
            f.write(config)

        # Restart Wi-Fi service
        subprocess.run(['sudo', 'systemctl', 'restart', 'wpa_supplicant'], check=True)
        return True
    except Exception as e:
        print(f"Failed to restart Wi-Fi service: {e}")
        return False

@app.route('/')
def index():
    """Serve the Wi-Fi setup page."""
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    """Handle Wi-Fi credentials submission."""
    ssid = request.form.get('ssid')
    password = request.form.get('password')

    if ssid and password:
        if restart_wifi_service(ssid, password):
            return jsonify({'status': 'success', 'message': 'Wi-Fi credentials saved. Attempting to connect.'})
        else:
            return jsonify({'status': 'error', 'message': 'Failed to save credentials or restart Wi-Fi service.'})
    return jsonify({'status': 'error', 'message': 'Missing SSID or Password'})
