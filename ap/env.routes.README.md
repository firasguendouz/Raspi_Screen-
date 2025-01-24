# env.routes

## Overview
Environment configuration file for the AP (Access Point) management system. Provides centralized configuration for all AP-related scripts, allowing customization of network settings, security options, and operational parameters.

## Usage
The configuration file can be used in two ways:
1. Direct modification of the file
2. Environment variable override

```bash
# Method 1: Edit env.routes directly
vim env.routes

# Method 2: Environment variable override
export AP_SSID="CustomAP"
export AP_PASSPHRASE="SecurePassword123"
./setup_ap.sh
```

## Configuration Sections

### Network Configuration
```bash
# Access Point Settings
AP_SSID="RaspberryPi_AP"           # WiFi network name
AP_PASSPHRASE="raspberry"           # WiFi password
AP_CHANNEL="7"                      # WiFi channel (1-13)
AP_COUNTRY="US"                     # Country code
AP_HIDE_SSID="0"                   # SSID visibility

# Network Interface
AP_INTERFACE="wlan0"               # Wireless interface
AP_DRIVER="nl80211"                # Wireless driver

# IP Configuration
AP_IP="192.168.4.1"                # AP IP address
AP_NETMASK="255.255.255.0"         # Network mask
AP_NETWORK="192.168.4.0"           # Network address
AP_BROADCAST="192.168.4.255"       # Broadcast address
```

### DHCP Configuration
```bash
# DHCP Settings
AP_DHCP_START="192.168.4.2"        # First DHCP address
AP_DHCP_END="192.168.4.20"         # Last DHCP address
AP_LEASE_TIME="24h"                # DHCP lease duration
AP_DNS_PRIMARY="8.8.8.8"           # Primary DNS
AP_DNS_SECONDARY="8.8.4.4"         # Secondary DNS
```

### Security Configuration
```bash
# Authentication
AP_AUTH_ALGS="1"                   # 1=WPA, 2=WEP, 3=both
AP_WPA_VERSION="2"                 # 1=WPAv1, 2=WPAv2
AP_KEY_MGMT="WPA-PSK"             # Key management
AP_PAIRWISE="CCMP"                # Encryption type

# Firewall
AP_ALLOW_PORTS="80,443"           # Allowed ports
AP_FORWARD_PORTS=""               # Port forwarding
AP_BLOCK_PORTS=""                 # Blocked ports
```

### Performance Configuration
```bash
# WiFi Settings
AP_HW_MODE="g"                    # a=5GHz, g=2.4GHz
AP_MAX_NUM_STA="10"              # Max clients
AP_RTS_THRESHOLD="2347"          # RTS/CTS threshold
AP_FRAGM_THRESHOLD="2346"        # Fragmentation
```

### Monitoring Configuration
```bash
# Monitoring
AP_CHECK_INTERVAL="30"           # Check frequency
AP_MAX_FAILURES="3"             # Failure threshold
AP_STABILIZATION_WAIT="10"      # Recovery wait time
```

### Logging Configuration
```bash
# Logging
AP_LOG_DIR="/var/log"           # Log directory
AP_LOG_LEVEL="INFO"            # Log detail level
AP_LOG_MAX_SIZE="10M"          # Max log size
AP_LOG_KEEP_DAYS="7"           # Log retention
```

## Variable Precedence
1. Command line arguments
2. Environment variables
3. env.routes values
4. Default values in scripts

## Environment Types
- `production`: Normal operation mode
- `test`: Dry-run mode for testing

## Security Considerations
- Store sensitive data (passwords, keys) securely
- Use strong passwords (min 8 characters)
- Consider hiding SSID in public environments
- Implement appropriate firewall rules

## Examples

### Basic AP Setup
```bash
# Default configuration
source env.routes
./setup_ap.sh
```

### Custom Security Configuration
```bash
export AP_SSID="SecureAP"
export AP_PASSPHRASE="StrongPass123!"
export AP_WPA_VERSION="2"
export AP_PAIRWISE="CCMP"
./setup_ap.sh
```

### Performance Tuning
```bash
export AP_MAX_NUM_STA="20"
export AP_RTS_THRESHOLD="2000"
export AP_FRAGM_THRESHOLD="2000"
./setup_ap.sh
```

### Monitoring Configuration
```bash
export AP_CHECK_INTERVAL="60"
export AP_MAX_FAILURES="5"
export AP_LOG_LEVEL="DEBUG"
./check_connection.sh
```

## Integration
Used by:
- `setup_ap.sh`: Initial configuration
- `check_connection.sh`: Monitoring
- `stop_ap.sh`: Shutdown
- `utils.sh`: Shared utilities

## See Also
- [utils.README.md](utils.README.md): Utility functions
- [AP.md](AP.md): Main documentation
- [setup_ap.README.md](setup_ap.README.md): Setup script
- [check_connection.README.md](check_connection.README.md): Monitoring script 