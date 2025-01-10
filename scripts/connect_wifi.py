import subprocess
import time

def connect_wifi(ssid, password):
    """
    Connect to a Wi-Fi network using wpa_supplicant

    Args:
        ssid (str): Wi-Fi network name
        password (str): Wi-Fi password

    Returns:
        bool: True if connected successfully, False otherwise
    """
    try:
        # Create wpa_supplicant.conf file
        config = (
            f'ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev\n'
            f'update_config=1\n'
            f'country=US\n'
            f'network={{\n'
            f'    ssid="{ssid}"\n'
            f'    psk="{password}"\n'
            f'    key_mgmt=WPA-PSK\n'
            f'}}\n'
        )
        
        with open('/etc/wpa_supplicant/wpa_supplicant.conf', 'w') as f:
            f.write(config)
        
        # Restart wireless interface
        subprocess.run(['sudo', 'ifconfig', 'wlan0', 'down'])
        time.sleep(1)
        subprocess.run(['sudo', 'ifconfig', 'wlan0', 'up'])
        time.sleep(2)
        
        # Reconfigure wireless network
        subprocess.run(['sudo', 'wpa_cli', '-i', 'wlan0', 'reconfigure'])
        
        # Check connection status
        result = subprocess.run(['iwgetid'], capture_output=True, text=True)
        if ssid in result.stdout:
            print(f"Successfully connected to {ssid}")
            return True
        else:
            print(f"Failed to connect to {ssid}")
            return False
        
    except Exception as e:
        print(f"Error connecting to Wi-Fi: {e}")
        return False

if __name__ == "__main__":
    # Example usage
    WIFI_SSID = "YourSSID"
    WIFI_PASSWORD = "YourPassword"
    connect_wifi(WIFI_SSID, WIFI_PASSWORD)
