# check_connection.sh

## Overview
Monitoring script that continuously checks the Access Point's connectivity and health. Automatically detects and recovers from failures by restarting services and reconfiguring network settings as needed.

## Features
- Continuous connectivity monitoring
- Automatic failure detection
- Service recovery
- Interface monitoring
- Configurable thresholds
- Test mode with timeout
- Detailed logging

## Dependencies
- `utils.sh`: Common utility functions
- `ping`: Connectivity testing
- `systemd`: Service management
- `ip`: Network interface management
- `hostapd`: Access Point daemon
- `dnsmasq`: DHCP server

## Usage
```bash
# Normal monitoring mode
sudo ./check_connection.sh

# Test mode with timeout
sudo ./check_connection.sh --test-mode --timeout 300
```

## Configuration
Settings can be configured via environment variables or `env.routes`:

### Monitoring Settings
- `AP_CHECK_INTERVAL`: Time between checks (seconds)
- `AP_MAX_FAILURES`: Failures before restart
- `AP_TEST_PING_TARGET`: Connectivity test target
- `AP_STABILIZATION_WAIT`: Post-restart wait time

### Network Settings
- `AP_INTERFACE`: Network interface to monitor
- `AP_IP`: Access Point IP address
- `AP_SSID`: WiFi network name

See `env.routes` for complete configuration options.

## Process Flow
1. **Initialization**
   - Load environment configuration
   - Parse command line arguments
   - Set up logging
   - Validate root privileges

2. **Monitoring Loop**
   - Check internet connectivity
   - Verify interface status
   - Monitor service health
   - Track failure count

3. **Failure Recovery**
   - Detect failures
   - Attempt service restart
   - Regenerate configurations
   - Verify recovery

4. **Status Reporting**
   - Log all events
   - Track recovery attempts
   - Report connectivity status

## Exit Codes
- `0`: Normal exit (test mode) or terminated
- `1`: Critical error or invalid configuration

## Monitoring Checks
1. **Connectivity Test**
   - Ping test to configured target
   - Configurable timeout
   - Failure counting

2. **Interface Check**
   - Validate interface existence
   - Check interface status
   - Monitor link state

3. **Service Check**
   - Verify service status
   - Check configuration validity
   - Monitor resource usage

## Test Mode
Test mode features:
- Configurable timeout
- No actual service changes
- Faster check intervals
- Detailed debug logging

## Logging
- Detailed logs in `/var/log/ap_monitor.log`
- Color-coded console output
- Timestamped entries
- Multiple severity levels

## Error Recovery
1. **Soft Recovery**
   - Service restart
   - Configuration refresh
   - Interface reset

2. **Hard Recovery**
   - Full service shutdown
   - Configuration regeneration
   - Complete AP restart

## Examples

### Basic Monitoring
```bash
sudo ./check_connection.sh
```

### Custom Configuration
```bash
export AP_CHECK_INTERVAL=60
export AP_MAX_FAILURES=5
export AP_TEST_PING_TARGET="1.1.1.1"
sudo ./check_connection.sh
```

### Debug Testing
```bash
export AP_LOG_LEVEL=DEBUG
sudo ./check_connection.sh --test-mode --timeout 600
```

## Troubleshooting
1. **Frequent Restarts**
   - Check network stability
   - Review failure thresholds
   - Verify service configurations

2. **Recovery Failures**
   - Check service dependencies
   - Verify permissions
   - Review system resources

3. **Monitoring Issues**
   - Validate ping target
   - Check interface configuration
   - Review log files

## Integration
- Works with `setup_ap.sh` for initial configuration
- Complements `stop_ap.sh` for cleanup
- Uses shared utilities from `utils.sh`

## See Also
- [utils.README.md](utils.README.md): Utility functions documentation
- [AP.md](AP.md): Main AP documentation
- [env.routes](env.routes): Environment configuration 