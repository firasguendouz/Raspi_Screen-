import subprocess
import re

class WiFiConfig:
    """
    Handles Wi-Fi setup logic, including scanning networks,
    connecting to Wi-Fi, and checking current connection.
    """
    def __init__(self):
        self.wpa_supplicant_path = "/etc/wpa_supplicant/wpa_supplicant.conf"

    def scan_networks(self):
        """Scan for available Wi-Fi networks."""
        try:
            scan_output = subprocess.check_output(["sudo", "iwlist", "wlan0", "scan"]).decode("utf-8")
            networks = []
            for line in scan_output.split("\n"):
                if "ESSID" in line:
                    match = re.search('ESSID:"(.*?)"', line)
                    if match:
                        networks.append(match.group(1))
            return list(set(networks))  # Remove duplicates
        except Exception as e:
            print(f"Error scanning Wi-Fi networks: {e}")
            return []

    def connect_to_wifi(self, ssid, password):
        """Connect to a Wi-Fi network with the given SSID and password."""
        try:
            # Write the Wi-Fi configuration
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
            with open(self.wpa_supplicant_path, "w") as f:
                f.write(config)

            # Restart Wi-Fi service
            subprocess.run(["sudo", "wpa_cli", "-i", "wlan0", "reconfigure"], check=True)
            print(f"Successfully connected to Wi-Fi network: {ssid}")
            return True
        except Exception as e:
            print(f"Error connecting to Wi-Fi network {ssid}: {e}")
            return False

    def get_current_connection(self):
        """Get the current Wi-Fi connection SSID."""
        try:
            result = subprocess.check_output(["iwgetid"]).decode("utf-8")
            match = re.search('ESSID:"(.*?)"', result)
            if match:
                return match.group(1)
            return None
        except Exception as e:
            print(f"Error retrieving current Wi-Fi connection: {e}")
            return None

if __name__ == "__main__":
    wifi_config = WiFiConfig()

    print("Scanning for networks...")
    networks = wifi_config.scan_networks()
    print(f"Available networks: {networks}")

    # Example usage: Connect to a network
    ssid = "YourSSID"
    password = "YourPassword"
    if wifi_config.connect_to_wifi(ssid, password):
        print(f"Connected to {ssid}")
    else:
        print(f"Failed to connect to {ssid}")

    # Get current connection
    current_ssid = wifi_config.get_current_connection()
    print(f"Currently connected to: {current_ssid}")
