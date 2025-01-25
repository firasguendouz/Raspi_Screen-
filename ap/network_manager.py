import subprocess
from typing import Tuple, Optional
import time

class NetworkManager:
    """Handles all network-related operations including WiFi connections and DNS management."""
    
    @staticmethod
    def check_internet_connection() -> bool:
        """Check if there is an active internet connection."""
        try:
            subprocess.run(['ping', '-c', '1', '8.8.8.8'], check=True)
            return True
        except subprocess.CalledProcessError:
            return False

    @staticmethod
    def connect_wifi(ssid: str, password: str) -> bool:
        """
        Connect to a WiFi network using provided credentials.
        
        Args:
            ssid: The network name
            password: The network password
            
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            # Configure wpa_supplicant
            config_cmd = f'wpa_passphrase "{ssid}" "{password}" | sudo tee /etc/wpa_supplicant/wpa_supplicant.conf'
            subprocess.run(config_cmd, shell=True, check=True)
            
            # Restart networking services
            subprocess.run(['sudo', 'systemctl', 'restart', 'wpa_supplicant'], check=True)
            subprocess.run(['sudo', 'systemctl', 'restart', 'dhcpcd'], check=True)
            
            # Wait for connection
            time.sleep(5)
            return NetworkManager.check_internet_connection()
            
        except subprocess.CalledProcessError:
            return False

    @staticmethod
    def reset_dns() -> bool:
        """Reset DNS configuration to default values."""
        try:
            # Backup existing resolv.conf
            subprocess.run(['sudo', 'cp', '/etc/resolv.conf', '/etc/resolv.conf.backup'], check=True)
            
            # Write new DNS configuration
            dns_config = "nameserver 8.8.8.8\nnameserver 8.8.4.4\n"
            with open('/tmp/resolv.conf', 'w') as f:
                f.write(dns_config)
            
            subprocess.run(['sudo', 'mv', '/tmp/resolv.conf', '/etc/resolv.conf'], check=True)
            return True
            
        except (subprocess.CalledProcessError, IOError):
            return False

    @staticmethod
    def verify_dns_config() -> bool:
        """Verify DNS configuration is correct."""
        try:
            with open('/etc/resolv.conf', 'r') as f:
                content = f.read()
                return '8.8.8.8' in content and '8.8.4.4' in content
        except:
            return False 