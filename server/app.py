from flask import Flask, render_template, request, jsonify
import subprocess
import os

app = Flask(__name__)

@app.route('/')
def index():
    """Serve the Wi-Fi setup page."""
    return render_template('index.html')

@app.route('/configure', methods=['POST'])
def submit():
    """Handle Wi-Fi credentials submission."""
    ssid = request.form.get('ssid')
    password = request.form.get('password')

    if ssid and password:
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
            return jsonify({'status': 'success', 'message': 'Wi-Fi credentials saved. Attempting to connect.'})

        except Exception as e:
            return jsonify({'status': 'error', 'message': f'Failed to save credentials: {e}'})

    return jsonify({'status': 'error', 'message': 'Missing SSID or Password'})

@app.route('/scan', methods=['GET'])
def scan_networks():
    """Scan for available Wi-Fi networks."""
    try:
        # Scan for networks using iwlist
        cmd = "sudo iwlist wlan0 scan | grep ESSID"
        networks = subprocess.check_output(cmd, shell=True).decode('utf-8').split('\n')
        network_list = [line.split('ESSID:')[1].strip('"') for line in networks if 'ESSID' in line]
        return jsonify({'networks': network_list})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
