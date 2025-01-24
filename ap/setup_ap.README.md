# setup_ap.sh

## Overview
Script for initializing and configuring a WiFi Access Point on a Raspberry Pi. This script handles the complete setup process, from stopping interfering services to starting and validating the AP configuration.

## Features
- Automated AP setup and configuration
- Service dependency management
- Network and firewall configuration
- Configuration validation
- Detailed logging
- Test mode support

## Dependencies
- `utils.sh`: Common utility functions
- `hostapd`: Access Point daemon
- `dnsmasq`: DHCP and DNS server
- `dhcpcd`: DHCP client daemon
- `systemd`: Service management
- `iptables`: Firewall configuration

## Usage
```bash
# Normal mode
sudo ./setup_ap.sh

# Test mode (dry run)
sudo ./setup_ap.sh --test-mode
```

## Configuration
All settings can be configured via environment variables or `env.routes`:

### Core Settings
- `AP_SSID`: WiFi network name
- `AP_PASSPHRASE`: WiFi password
- `AP_INTERFACE`: Network interface
- `AP_CHANNEL`: WiFi channel

### Network Settings
- `AP_IP`: Access Point IP address
- `AP_NETMASK`: Network mask
- `AP_DHCP_START`: First DHCP address
- `AP_DHCP_END`: Last DHCP address

See `env.routes` for complete configuration options.

## Process Flow
1. **Initialization**
   - Load environment configuration
   - Validate root privileges
   - Set up logging

2. **Service Shutdown**
   - Stop wpa_supplicant
   - Stop existing AP services
   - Clean up service states

3. **Configuration**
   - Generate hostapd configuration
   - Generate dnsmasq configuration
   - Configure network settings
   - Set up firewall rules

4. **Service Startup**
   - Start required services
   - Enable services for boot
   - Validate service status

## Exit Codes
- `0`: Success
- `1`: General failure
- Other: Specific error codes from failed operations

## Logging
- Detailed logs written to `/var/log/ap_setup.log`
- Console output with color-coded severity levels
- Debug logging available with `AP_LOG_LEVEL=DEBUG`

## Test Mode
Test mode (`--test-mode`) provides:
- Validation without system changes
- Configuration verification
- Service dependency checking
- Dry-run logging

## Error Handling
- Service startup validation
- Configuration validation
- Network interface checking
- Automatic cleanup on failure
- Configuration backups

## Security
- Root privilege requirement
- Secure default configurations
- WPA2 encryption
- Firewall configuration
- Service state validation

## Examples

### Basic Setup
```bash
sudo ./setup_ap.sh
```

### Custom Configuration
```bash
export AP_SSID="MyNetwork"
export AP_PASSPHRASE="MySecurePassword"
export AP_CHANNEL="6"
sudo ./setup_ap.sh
```

### Testing Configuration
```bash
export AP_LOG_LEVEL=DEBUG
sudo ./setup_ap.sh --test-mode
```

## Troubleshooting
1. **Service Failures**
   - Check service status with `systemctl status <service>`
   - Review logs in `/var/log/ap_setup.log`
   - Verify configuration files

2. **Network Issues**
   - Validate interface with `ip link show`
   - Check IP configuration
   - Verify firewall rules

3. **Permission Issues**
   - Ensure running with sudo
   - Check file permissions
   - Verify service access

## See Also
- [utils.README.md](utils.README.md): Utility functions documentation
- [AP.md](AP.md): Main AP documentation
- [env.routes](env.routes): Environment configuration 