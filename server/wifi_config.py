import subprocess
import re
import os

class WiFiConfig:
    def __init__(self):
        self.wifi_config_path = "/etc/wpa_supplicant/wpa_supplicant.conf"

    def scan_networks(self):
        """Scan for available WiFi networks"""
        try:
            scan_result = subprocess.check_output(["sudo", "iwlist", "wlan0", "scan"]).decode('utf-8')
            networks = []
            for line in scan_result.split('\n'):
                if 'ESSID' in line:
                    ssid = re.search('ESSID:"(.*?)"', line)
                    if ssid and ssid.group(1):
                        networks.append(ssid.group(1))
            return list(set(networks))  # Remove duplicates
        except Exception as e:
            print(f"Error scanning networks: {e}")
            return []

    def connect_to_wifi(self, ssid, password):
        """Connect to a WiFi network with given SSID and password"""
        config_template = (
            'network={\n'
            '\tssid="{}"\n'
            '\tpsk="{}"\n'
            '\tkey_mgmt=WPA-PSK\n'
            '}\n'
        )
        
        try:
            with open(self.wifi_config_path, 'a') as f:
                f.write(config_template.format(ssid, password))
            
            # Restart the wireless interface
            subprocess.run(["sudo", "wpa_cli", "-i", "wlan0", "reconfigure"], check=True)
            return True
        except Exception as e:
            print(f"Error connecting to WiFi: {e}")
            return False

    def get_current_connection(self):
        """Get current WiFi connection status"""
        try:
            result = subprocess.check_output(["iwgetid"]).decode('utf-8')
            ssid = re.search('ESSID:"(.*?)"', result)
            if ssid:
                return ssid.group(1)
            return None
        except Exception:
            return None

if __name__ == "__main__":
    wifi = WiFiConfig()
    print("Available networks:", wifi.scan_networks())
    print("Current connection:", wifi.get_current_connection())