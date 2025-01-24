# connect_wifi.py

![Status](https://img.shields.io/badge/status-stable-green)
![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Python](https://img.shields.io/badge/python-3.7+-yellow)
![Coverage](https://img.shields.io/badge/coverage-90%25-brightgreen)

## 🔍 Overview
WiFi Connection Manager for Raspberry Pi Screen that handles network connections with robust error handling and automatic recovery.

## 🔗 Related Documentation
- [Main Scripts Documentation](Scripts.md)
- [Stream URL Module](stream_url.README.md)
- [Send Activation Module](send_activation.README.md)
- [Utilities Module](utils.README.md)

## ⭐ Features
- WiFi network configuration
- Connection monitoring and retry
- Network configuration backup/restore
- Credential validation
- Detailed logging and error reporting

## 📦 Dependencies
- **[utils.py](utils.py)**: Common utility functions
- `subprocess`: System command execution
- `python-dotenv`: Environment configuration
- Network tools: `wpa_supplicant`, `dhcpcd`, `iwgetid`

## 🛠️ Installation
```bash
pip install -r requirements.txt
sudo apt-get install wireless-tools wpasupplicant
```

## 📝 Usage
```bash
# Connect with direct credentials
python connect_wifi.py --ssid "NetworkName" --password "NetworkPassword"

# Connect using saved configuration
python connect_wifi.py --config default

# Connect with custom timeout
python connect_wifi.py --ssid "NetworkName" --password "NetworkPassword" --timeout 60
```

## ⚙️ Configuration

### Environment Variables
See [.env.example](.env.example) for configuration options:
- `WIFI_SSID`: Default network name
- `WIFI_PASSWORD`: Default network password
- `WIFI_COUNTRY`: WiFi country code
- `LOG_LEVEL`: Logging verbosity

### JSON Configuration (scripts.json)
```json
{
    "wifi_networks": {
        "default": {
            "ssid": "${WIFI_SSID}",
            "password": "${WIFI_PASSWORD}",
            "country": "US"
        },
        "backup": {
            "ssid": "${BACKUP_WIFI_SSID}",
            "password": "${BACKUP_WIFI_PASSWORD}",
            "country": "US"
        }
    }
}
```

## ⚠️ Error Handling
The script implements several error handling mechanisms:
1. Network configuration validation
2. Automatic backup before changes
3. Configuration restore on failure
4. Connection retry with timeout
5. Detailed error reporting

## 📊 Logging
Logs are written to `/var/log/raspi_screen/connect_wifi.log` with the following levels:
- `ERROR`: Connection and configuration failures
- `WARNING`: Network issues and retries
- `INFO`: Connection status and configuration changes
- `DEBUG`: Detailed network operations

## 🔍 Exit Codes
- `0`: Successful connection
- `1`: Configuration or connection error

## 🔌 API Usage
```python
from connect_wifi import configure_wifi, connect_with_retry

# Configure and connect to WiFi
configure_wifi(ssid="NetworkName", password="Password", country="US")
connect_with_retry(interface="wlan0", timeout=30)
```

## 🛠️ Functions

### `load_wifi_config(config_name: str) -> Tuple[str, str, str]`
Loads WiFi configuration from the configuration file.

### `backup_network_config() -> None`
Creates backups of network configuration files.

### `restore_network_config() -> None`
Restores network configuration from backups.

### `configure_wifi(ssid: str, password: str, country: str) -> None`
Configures WiFi settings with the provided credentials.

### `connect_with_retry(interface: str, timeout: int) -> None`
Attempts to connect to WiFi with retry mechanism.

## 📁 Configuration Files
- `/etc/wpa_supplicant/wpa_supplicant.conf`: WiFi configuration
- `/etc/dhcpcd.conf`: Network interface configuration

## �� See Also
- [Stream URL Module](stream_url.README.md)
- [Send Activation Module](send_activation.README.md)
- [Utilities Module](utils.README.md)

---
*Last updated: 2024-01-24*

Tags: #wifi #python #network #configuration #raspberry-pi 