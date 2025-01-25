import requests
from typing import Tuple
import os
from dotenv import load_dotenv

class ActivationManager:
    """Manages device activation with the central server."""
    
    def __init__(self, server_url: str = None):
        """
        Initialize the activation manager.
        
        Args:
            server_url: The URL of the activation server. If None, loads from environment.
        """
        load_dotenv()
        self.server_url = server_url or os.getenv("SERVER_URL", "http://localhost:5001")
        
    def send_activation_request(self) -> Tuple[bool, str]:
        """
        Send an activation request to the central server.
        
        Returns:
            Tuple[bool, str]: (success, message)
                - success: True if activation successful, False otherwise
                - message: Success or error message
        """
        try:
            # Get device info
            device_info = self._get_device_info()
            
            # Send activation request
            response = requests.post(
                f"{self.server_url}/activate",
                json=device_info,
                timeout=10
            )
            
            if response.status_code == 200:
                return True, "Device activated successfully"
            else:
                return False, f"Activation failed: {response.text}"
                
        except requests.RequestException as e:
            return False, f"Connection error: {str(e)}"
            
    def _get_device_info(self) -> dict:
        """
        Gather device information for activation.
        
        Returns:
            dict: Device information including MAC address, hostname, etc.
        """
        try:
            # Get MAC address
            mac = open('/sys/class/net/wlan0/address').read().strip()
            
            # Get hostname
            hostname = open('/etc/hostname').read().strip()
            
            return {
                "mac_address": mac,
                "hostname": hostname,
                "device_type": "raspberry_pi"
            }
        except Exception as e:
            return {
                "device_type": "raspberry_pi",
                "error": f"Could not get full device info: {str(e)}"
            } 