import requests
import uuid
import socket
from datetime import datetime
from dotenv import load_dotenv
import os

class ActivationClient:
    """
    Handles communication with the central server for device activation.
    """
    def __init__(self, server_url):
        """
        Initialize the ActivationClient.

        Args:
            server_url (str): The URL of the central server (e.g., "http://<IP>:5001").
        """
        self.server_url = server_url
        self.device_id = self._get_device_id()

    def _get_device_id(self):
        """Generate a unique device identifier using MAC address."""
        mac = ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff)
                        for elements in range(0, 2 * 6, 2)][::-1])
        return mac

    def send_activation_request(self):
        """Send an activation request to the central server."""
        try:
            payload = {
                'device_id': self.device_id,
                'timestamp': datetime.now().isoformat(),
                'hostname': socket.gethostname()
            }

            response = requests.post(
                f"{self.server_url}/activate",
                json=payload,
                timeout=10
            )

            if response.status_code == 200:
                return True, response.json()
            else:
                return False, f"Server returned status code: {response.status_code}"

        except requests.exceptions.RequestException as e:
            return False, f"Connection error: {str(e)}"

if __name__ == "__main__":
    # Load environment variables from .env
    load_dotenv()

    # Retrieve the server URL from the .env file
    SERVER_URL = os.getenv("SERVER_URL", "http://localhost:5001")

    client = ActivationClient(server_url=SERVER_URL)
    success, result = client.send_activation_request()

    if success:
        print("Device activation successful!")
        print(f"Server response: {result}")
    else:
        print(f"Activation failed: {result}")
