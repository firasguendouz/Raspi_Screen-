import subprocess
import re
import requests
import uuid
import socket
from datetime import datetime
from typing import Dict, Any
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Constants
SERVER_URL = os.getenv("SERVER_URL", "http://localhost:5001")
METRICS_ENDPOINT = f"{SERVER_URL}/metrics"

# ANSI Colors
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def format_section(title: str) -> str:
    return f"\n{Colors.HEADER}{Colors.BOLD}=== {title} ==={Colors.ENDC}"

def format_value(label: str, value: str) -> str:
    return f"{Colors.BLUE}{label}:{Colors.ENDC} {Colors.GREEN}{value}{Colors.ENDC}"

def get_cpu_usage() -> str:
    try:
        cmd = "top -bn1 | grep '%Cpu' | awk '{print $2}'"
        return subprocess.check_output(cmd, shell=True, universal_newlines=True).strip() + "%"
    except:
        return "Unknown"

def get_display_info() -> Dict[str, Any]:
    try:
        xrandr_output = subprocess.check_output(['xrandr'], universal_newlines=True)
        connected_display = re.search(r'(\w+) connected (\d+x\d+)', xrandr_output)
        if connected_display:
            return {
                "status": "Connected",
                "resolution": connected_display.group(2)
            }
        return {"status": "Disconnected", "resolution": "None"}
    except Exception:
        return {"status": "Unknown", "resolution": "Unknown"}

def get_power_info() -> Dict[str, str]:
    try:
        voltage = subprocess.check_output(['vcgencmd', 'measure_volts', 'core'], universal_newlines=True).strip()
        throttled = subprocess.check_output(['vcgencmd', 'get_throttled'], universal_newlines=True).strip()
        return {"coreVoltage": voltage.replace('volt=', ''), "throttling": throttled}
    except Exception:
        return {"coreVoltage": "Unknown", "throttling": "Unknown"}

def get_wifi_info() -> Dict[str, str]:
    try:
        iwconfig_output = subprocess.check_output(['iwconfig'], universal_newlines=True)
        essid = re.search(r'ESSID:"([^"]+)"', iwconfig_output)
        signal_level = re.search(r'Signal level=(-?\d+ dBm)', iwconfig_output)
        return {
            "network": essid.group(1) if essid else "Unknown",
            "signalStrength": signal_level.group(1) if signal_level else "Unknown"
        }
    except Exception:
        return {"network": "Unknown", "signalStrength": "Unknown"}

def get_system_info() -> Dict[str, Any]:
    try:
        temp = subprocess.check_output(['vcgencmd', 'measure_temp'], universal_newlines=True).strip()
        mem = subprocess.check_output(['free', '-h'], shell=True, universal_newlines=True).split('\n')[1].split()
        cpu_usage = get_cpu_usage()
        disk = subprocess.check_output(['df', '-h', '/'], universal_newlines=True).split('\n')[1].split()
        return {
            "cpuTemperature": float(temp.replace('temp=', '').replace('C', '').strip()),
            "cpuUsage": float(cpu_usage.replace('%', '').strip()),
            "memory": {
                "total": mem[1],
                "used": mem[2],
                "free": mem[3]
            },
            "disk": {
                "total": disk[1],
                "used": disk[2],
                "free": disk[3],
                "usage": float(disk[4].replace('%', ''))
            }
        }
    except Exception:
        return {
            "cpuTemperature": "Unknown",
            "cpuUsage": "Unknown",
            "memory": {"total": "Unknown", "used": "Unknown", "free": "Unknown"},
            "disk": {"total": "Unknown", "used": "Unknown", "free": "Unknown", "usage": "Unknown"}
        }

def get_network_info() -> Dict[str, Any]:
    try:
        ip_address = subprocess.check_output(['hostname', '-I'], universal_newlines=True).strip()
        return {"ipAddress": ip_address}
    except Exception:
        return {"ipAddress": "Unknown"}

def gather_metrics() -> Dict[str, Any]:
    return {
        "display": get_display_info(),
        "power": get_power_info(),
        "wifi": get_wifi_info(),
        "system": get_system_info(),
        "network": get_network_info()
    }

def send_metrics_to_server(metrics: Dict[str, Any]):
    try:
        payload = {
            "hoster": "Unknown",  # Placeholder
            "location": "Unknown",  # Placeholder
            "address": {
                "street": "Unknown",
                "streetNumber": "Unknown",
                "postalCode": "Unknown",
                "city": "Unknown",
                "country": "Unknown",
                "timezone": "Europe/Berlin"
            },
            "images": [],
            "isActive": False,
            "isConnected": True,
            "locationType": "Normal",
            "trafficType": "Low",
            "metrics": metrics
        }

        response = requests.post(METRICS_ENDPOINT, json=payload, timeout=10)

        if response.status_code == 201:
            print("Metrics sent successfully!")
            print("Response:", response.json())
        else:
            print(f"Failed to send metrics: {response.status_code}")
            print("Response:", response.text)
    except requests.exceptions.RequestException as e:
        print(f"Error sending metrics: {str(e)}")

def main():
    client = ActivationClient(server_url=SERVER_URL)
    success, result = client.send_activation_request()

    if success:
        print("Device activation successful!")
        print(f"Server response: {result}")
        metrics = gather_metrics()
        send_metrics_to_server(metrics)
    else:
        print(f"Activation failed: {result}")

class ActivationClient:
    def __init__(self, server_url):
        self.server_url = server_url
        self.device_id = self._get_device_id()

    def _get_device_id(self):
        mac = ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff)
                        for elements in range(0, 2 * 6, 2)][::-1])
        return mac

    def send_activation_request(self):
        try:
            payload = {
                'device_id': self.device_id,
                'timestamp': datetime.now().isoformat(),
                'hostname': socket.gethostname()
            }

            response = requests.post(
                f"{self.server_url}/api/screens/create",
                json=payload,
                timeout=10
            )

            if response.status_code == 201:
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
        metrics = gather_metrics()
        send_metrics_to_server(metrics)
    else:
        print(f"Activation failed: {result}")
