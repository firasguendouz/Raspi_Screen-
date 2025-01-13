import subprocess
import time

def connect_wifi(ssid, password, timeout=30):
    """
    Connect to a Wi-Fi network using wpa_supplicant and track connection status.

    Args:
        ssid (str): Wi-Fi network name.
        password (str): Wi-Fi password.
        timeout (int): Maximum time (in seconds) to wait for connection.

    Returns:
        bool: True if connected successfully, False otherwise.
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
        
        print("Wi-Fi configuration written.")
        
        # Restart wireless interface
        print("Restarting wireless interface...")
        subprocess.run(['sudo', 'ifconfig', 'wlan0', 'down'], check=True)
        time.sleep(1)
        subprocess.run(['sudo', 'ifconfig', 'wlan0', 'up'], check=True)
        time.sleep(2)
        
        # Reconfigure wireless network
        print("Reconfiguring Wi-Fi...")
        subprocess.run(['sudo', 'wpa_cli', '-i', 'wlan0', 'reconfigure'], check=True)
        
        # Wait for the connection to establish
        print("Waiting for connection...")
        start_time = time.time()
        while time.time() - start_time < timeout:
            result = subprocess.run(['iwgetid'], capture_output=True, text=True)
            if ssid in result.stdout:
                print(f"Successfully connected to {ssid}")
                return True
            time.sleep(2)  # Wait before checking again
        
        print(f"Failed to connect to {ssid}. Check credentials or signal strength.")
        return False
    
    except subprocess.CalledProcessError as e:
        print(f"Command failed: {e}")
        return False
    except Exception as e:
        print(f"Error connecting to Wi-Fi: {e}")
        return False
def reset_dns():
    """Reset DNS configuration to use Google's public DNS servers."""
    try:
        with open('/etc/resolv.conf', 'w') as resolv_file:
            resolv_file.write("nameserver 8.8.8.8\n")
            resolv_file.write("nameserver 8.8.4.4\n")
        print("DNS configuration reset to 8.8.8.8 and 8.8.4.4.")
    except Exception as e:
        print(f"Failed to reset DNS configuration: {e}")

if __name__ == "__main__":
    # Example usage
    WIFI_SSID = "Vodafone-AAB4"
    WIFI_PASSWORD = "RxymGnMT9p3LzPzP"
    if connect_wifi(WIFI_SSID, WIFI_PASSWORD):
        reset_dns()
        print(f"Connected to {WIFI_SSID}")
    else:
        print(f"Failed to connect to {WIFI_SSID}")
    # Example usage
    WIFI_SSID = "Vodafone-AAB4"
    WIFI_PASSWORD = "RxymGnMT9p3LzPzP"
    if connect_wifi(WIFI_SSID, WIFI_PASSWORD):
        print("Wi-Fi setup complete.")
    else:
        print("Wi-Fi setup failed.")
