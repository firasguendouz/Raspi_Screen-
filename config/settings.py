import os
from pathlib import Path
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base paths
BASE_DIR = Path(__file__).parent.parent
SCRIPTS_DIR = BASE_DIR / "scripts"
AP_DIR = BASE_DIR / "ap"

# Network configuration
NETWORK = {
    "ap_ssid": os.getenv("AP_SSID", "RaspberryAP"),
    "ap_password": os.getenv("AP_PASSWORD", "raspberry"),
    "ap_ip": "192.168.4.1",
    "ap_setup_script": AP_DIR / "setup_ap.sh",
    "ap_stop_script": AP_DIR / "stop_ap.sh",
}

# Server configuration
SERVER = {
    "host": "0.0.0.0",
    "port": 80,
    "url": os.getenv("SERVER_URL", "http://localhost:5001"),
    "activation_endpoint": "/activate",
}

# File paths
PATHS = {
    "wifi_credentials_tmp": BASE_DIR / "wifi_credentials.tmp",
    "wifi_qr": BASE_DIR / "wifi_qr.png",
    "url_qr": BASE_DIR / "web_qr.png",
}

# Timeouts and retries
TIMEOUTS = {
    "client_connection": 300,  # 5 minutes
    "dns_reset_attempts": 3,
    "dns_reset_delay": 2,
}

def get_config() -> Dict[str, Any]:
    """Get the complete configuration dictionary."""
    return {
        "network": NETWORK,
        "server": SERVER,
        "paths": PATHS,
        "timeouts": TIMEOUTS,
    } 