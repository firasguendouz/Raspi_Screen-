import requests
import json
import socket
import os
from datetime import datetime

class ActivationClient:
    def __init__(self, server_url="http://localhost:5000"):
        self.server_url = server_url
        self.device_id = self._get_device_id()

    def _get_device_id(self):
        """Get unique device identifier using MAC address"""
        mac = ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff)
                       for elements in range(0,2*6,2)][::-1])
        return mac

    def send_activation_request(self):
        """Send activation request to central server"""
        try:
            payload = {
                'device_id': self.device_id,
                'timestamp': datetime.now().isoformat(),
                'hostname': socket.gethostname()
            }

            response = requests.post(
                f"{self.server_url}/activate",
                json=payload,
                timeout=5
            )

            if response.status_code == 200:
                return True, response.json()
            else:
                return False, f"Server returned status code: {response.status_code}"

        except requests.exceptions.RequestException as e:
            return False, f"Connection error: {str(e)}"

def main():
    client = ActivationClient()
    success, result = client.send_activation_request()
    
    if success:
        print("Device activation successful!")
        print(f"Server response: {result}")
    else:
        print(f"Activation failed: {result}")

if __name__ == "__main__":
    main()