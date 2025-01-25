import subprocess
import time
from typing import Optional, Tuple

class APManager:
    """Manages the Raspberry Pi Access Point (AP) operations."""
    
    def __init__(self):
        self.ap_interface = "wlan0"
        
    def start_ap(self) -> bool:
        """
        Start the Access Point mode.
        
        Returns:
            bool: True if AP started successfully, False otherwise
        """
        try:
            subprocess.run(['sudo', 'bash', 'ap/setup_ap.sh'], check=True)
            return True
        except subprocess.CalledProcessError:
            return False
            
    def stop_ap(self) -> bool:
        """
        Stop the Access Point mode.
        
        Returns:
            bool: True if AP stopped successfully, False otherwise
        """
        try:
            subprocess.run(['sudo', 'bash', 'ap/stop_ap.sh'], check=True)
            return True
        except subprocess.CalledProcessError:
            return False
            
    def get_connected_client(self) -> Optional[str]:
        """
        Get the MAC address of the connected client if any.
        
        Returns:
            Optional[str]: MAC address of connected client or None if no client
        """
        try:
            output = subprocess.check_output(
                ['iw', 'dev', self.ap_interface, 'station', 'dump']
            ).decode()
            
            if output:
                client_mac = output.split('\n')[0].split()[1]
                return client_mac
            return None
            
        except subprocess.CalledProcessError:
            return None
            
    def wait_for_client_connection(self, timeout: int = 300) -> Optional[str]:
        """
        Wait for a client to connect to the AP.
        
        Args:
            timeout: Maximum time to wait in seconds
            
        Returns:
            Optional[str]: MAC address of connected client or None if timeout
        """
        start_time = time.time()
        while (time.time() - start_time) < timeout:
            client_mac = self.get_connected_client()
            if client_mac:
                return client_mac
            time.sleep(2)
        return None 