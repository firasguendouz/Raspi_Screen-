# utils.sh

## Overview
Core utility library providing common functionality for AP (Access Point) management scripts. This module handles logging, service management, network validation, and configuration generation.

## Dependencies
- `systemd`: Service management and control
- `ip`: Network interface management
- `ping`: Network connectivity testing
- `iptables`: Firewall configuration
- `bash` (version 4+): Script execution

## Environment Variables
All environment variables can be set either in `env.routes` or exported before running scripts:

### Core Settings
- `AP_ENV`: Environment type (production/test)
- `AP_INTERFACE`: Network interface name
- `AP_LOG_DIR`: Log directory path
- `AP_LOG_LEVEL`: Logging level (DEBUG/INFO/WARN/ERROR)

### Network Settings
- `AP_SSID`: WiFi network name
- `AP_PASSPHRASE`: WiFi password
- `AP_IP`: Access Point IP address
- `AP_NETMASK`: Network mask
- See `env.routes` for complete list

## Functions

### Environment Management
```bash
init_environment [--test-mode] [interface]
load_environment
```

### Logging
```bash
log_error "Error message"
log_warn "Warning message"
log_info "Info message"
log_debug "Debug message"
```

### Service Management
```bash
start_service "service_name"
stop_service "service_name"
restart_service "service_name"
enable_service "service_name"
disable_service "service_name"
check_service "service_name"
```

### Network Management
```bash
validate_interface "interface_name"
test_connectivity [target] [timeout]
configure_firewall
```

### Configuration Management
```bash
copy_config "source_path" "dest_path"
generate_hostapd_config "output_path"
generate_dnsmasq_config "output_path"
```

## Usage Example
```bash
source ./utils.sh
init_environment --test-mode wlan0
check_root

if validate_interface "$AP_INTERFACE"; then
    log_info "Interface $AP_INTERFACE is valid"
    generate_hostapd_config "/etc/hostapd/hostapd.conf"
fi
```

## Error Handling
- All functions return 0 on success, non-zero on failure
- Error messages are logged to both console and log file
- Automatic cleanup on script exit via trap
- Configuration backups are created and restored on failure

## Logging
- Timestamps included in all log messages
- Color-coded output for different log levels
- File logging when `LOG_FILE` is defined
- Log rotation support via `AP_LOG_MAX_SIZE` and `AP_LOG_KEEP_DAYS`

## Test Mode
- Set with `--test-mode` flag in `init_environment`
- Prevents actual system changes
- Logs intended actions for verification
- Useful for testing and debugging

## Security
- Root privilege validation
- Service state validation
- Configuration backup creation
- Secure default settings

## Integration
This module is used by:
- `setup_ap.sh`: AP initialization
- `check_connection.sh`: Connection monitoring
- `stop_ap.sh`: AP termination

## See Also
- [AP.md](AP.md): Main AP documentation
- [env.routes](env.routes): Environment configuration 