import subprocess
import time

def connect_wifi(ssid, password):
    """
    Connect to a WiFi network using wpa_supplicant
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
        
        # Reconnect to wireless network
        subprocess.run(['sudo', 'wpa_cli', '-i', 'wlan0', 'reconfigure'])
        
        print(f"Successfully connected to {ssid}")
        return True
        
    except Exception as e:
        print(f"Failed to connect to WiFi: {str(e)}")
        return False

if __name__ == "__main__":
    # Example usage
    WIFI_SSID = "your_wifi_name"
    WIFI_PASSWORD = "your_wifi_password"
    connect_wifi(WIFI_SSID, WIFI_PASSWORD)