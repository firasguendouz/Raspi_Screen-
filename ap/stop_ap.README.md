# stop_ap.sh

## Overview
Script for safely shutting down the Access Point and restoring normal WiFi client mode. Handles service shutdown, network reconfiguration, and system state restoration.

## Features
- Safe AP shutdown
- Network restoration
- Configuration backup/restore
- Service management
- State verification
- Test mode support
- Detailed logging

## Dependencies
- `utils.sh`: Common utility functions
- `systemd`: Service management
- `ip`: Network interface management
- `wpa_supplicant`: WiFi client mode
- `dhcpcd`: DHCP client

## Usage
```bash
# Normal shutdown
sudo ./stop_ap.sh

# Test mode (dry run)
sudo ./stop_ap.sh --test-mode
```

## Configuration
Settings can be configured via environment variables or `env.routes`. Configuration files are managed from the `/config` directory:

### Configuration Files
- `wpa_supplicant.conf`: WiFi client settings
- `dhcpcd.conf`: Network interface settings
- Other AP configurations for backup/restore

### Core Settings
- `AP_INTERFACE`: Network interface
- `AP_ENV`: Environment (production/test)
- `AP_LOG_LEVEL`: Logging detail level

### Network Settings
- `AP_IP`: Access Point IP address
- `AP_NETMASK`: Network mask
- `AP_NETWORK`: Network address

See `env.routes` for complete configuration options.

## Process Flow
1. **Initialization**
   - Load environment configuration
   - Validate root privileges
   - Set up logging

2. **Service Shutdown**
   - Stop AP services
   - Disable service autostart
   - Clean up service states

3. **Network Restoration**
   - Restore original configurations from backups
   - Disable IP forwarding
   - Remove firewall rules

4. **Client Mode Setup**
   - Copy wpa_supplicant configuration from `/config`
   - Configure client networking
   - Verify connectivity

## Exit Codes
- `0`: Successful shutdown
- `1`: General failure
- Other: Specific error codes

## Configuration Management
- Original configurations backed up during setup
- Automatic restoration during shutdown
- Verification of restored configs
- Fallback to `/config` defaults if needed

## Network Transition
1. **AP Shutdown**
   - Stop hostapd
   - Stop dnsmasq
   - Clear AP configurations

2. **Client Setup**
   - Restore wpa_supplicant from `/config`
   - Configure DHCP client
   - Enable client mode

3. **Verification**
   - Check interface status
   - Verify IP assignment
   - Test connectivity

## Test Mode
Test mode features:
- No actual service changes
- Configuration validation
- Process verification
- Detailed logging

## Logging
- Detailed logs in `/var/log/ap_stop.log`
- Console output with severity levels
- Operation timestamps
- Error tracking

## Error Handling
1. **Service Errors**
   - Graceful service shutdown
   - State verification
   - Error reporting

2. **Configuration Errors**
   - Backup restoration
   - Default fallback from `/config`
   - Error notification

3. **Network Errors**
   - Interface reset
   - Configuration retry
   - Status verification

## Examples

### Basic Shutdown
```bash
sudo ./stop_ap.sh
```

### Debug Mode
```bash
export AP_LOG_LEVEL=DEBUG
sudo ./stop_ap.sh --test-mode
```

### Custom Interface
```bash
export AP_INTERFACE="wlan1"
sudo ./stop_ap.sh
```

## Troubleshooting
1. **Service Issues**
   - Check service status
   - Review logs
   - Verify permissions

2. **Network Problems**
   - Check interface status
   - Verify configurations in `/config`
   - Test connectivity

3. **Configuration Issues**
   - Check backup files
   - Verify `/config` contents
   - Review system logs

## Integration
- Works with `setup_ap.sh` for complete lifecycle
- Uses shared utilities from `utils.sh`
- Compatible with monitoring system

## See Also
- [utils.README.md](utils.README.md): Utility functions documentation
- [AP.md](AP.md): Main AP documentation
- [env.routes](env.routes): Environment configuration 