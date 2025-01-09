app = Flask(__name__)

@app.route('/wifi/scan', methods=['GET'])
def scan_networks():
    try:
        # Scan for available networks
        cmd = "sudo iwlist wlan0 scan | grep ESSID"
        networks = subprocess.check_output(cmd, shell=True).decode('utf-8').split('\n')
        network_list = [network.split('ESSID:')[1].strip('"') for network in networks if network]
        return jsonify({'networks': network_list})
    except Exception as e:
        return jsonify({'error': str(e)}), 500