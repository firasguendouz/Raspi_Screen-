# Development Notes

## Current Development Status

### Access Point Issues

1. Interface Initialization Problem
   - Symptom: hostapd starts but interface shows "UNINITIALIZED->COU" state
   - Possible causes:
     - Interface not in correct mode
     - Driver conflicts
     - Configuration issues
   - Next steps:
     - Check interface capabilities
     - Verify driver compatibility
     - Review hostapd configuration

2. AP Visibility Issue
   - Symptom: AP not visible to client devices
   - Current configuration:
     ```
     interface=wlan0
     driver=nl80211
     ssid=RaspberryPi_AP
     hw_mode=g
     channel=7
     wmm_enabled=0
     macaddr_acl=0
     auth_algs=1
     ignore_broadcast_ssid=0
     wpa=2
     wpa_passphrase=raspberry
     wpa_key_mgmt=WPA-PSK
     wpa_pairwise=TKIP
     rsn_pairwise=CCMP
     country_code=GB
     ```
   - Next steps:
     - Test with different channels
     - Verify power management settings
     - Check for interference

3. Setup Script Arguments Error
   - Symptom: "Too many arguments" error
   - Current implementation:
     - Script called from APManager class
     - Arguments passed through utils.sh
   - Next steps:
     - Review argument parsing
     - Check environment variable handling
     - Verify script call parameters

### QR Code System

1. Display Issues
   - Current implementation:
     ```python
     self.ui_manager.display_qr_code(wifi_qr, "Scan this QR code to connect to Raspberry Pi AP")
     ```
   - Problems:
     - QR code generates but doesn't display
     - Logo file missing
   - Next steps:
     - Create static file structure
     - Implement proper file path handling
     - Add error recovery for missing resources

2. WiFi QR Format
   - Current format:
     ```
     WIFI:S:<ssid>;T:<security>;P:<password>;;
     ```
   - Needs verification:
     - Test with different devices
     - Verify security type handling
     - Check special character encoding

### UI System

1. Message Update Issues
   - Current implementation uses PyWebView
   - Problems:
     - Inconsistent message updates
     - Status feedback not visible
   - Next steps:
     - Review JavaScript bridge
     - Implement message queue
     - Add update verification

2. QR Code Display
   - Current method:
     ```python
     def display_qr_code(self, path: str, message: str) -> None:
         self.update_ui(message, path)
     ```
   - Improvements needed:
     - Add loading indicators
     - Implement display verification
     - Add error handling

## Testing Environment

### Required Tools
- Python 3.9+
- hostapd
- dnsmasq
- PyWebView
- QR code libraries

### Test Cases Needed
1. Access Point
   - Interface initialization
   - Client visibility
   - Connection handling
   - Security configuration

2. QR Code
   - Generation
   - Display
   - Format compatibility
   - Error handling

3. UI
   - Message updates
   - QR display
   - Status feedback
   - Error presentation

## Debug Commands

```bash
# Check hostapd status
sudo systemctl status hostapd

# View hostapd logs
sudo journalctl -u hostapd

# Check interface status
sudo iw dev wlan0 info

# Test interface mode
sudo iw dev wlan0 set type ap

# View dnsmasq status
sudo systemctl status dnsmasq

# Check network configuration
ip addr show wlan0
```

## Development Workflow

1. Issue Investigation
   - Log analysis
   - Service status checks
   - Configuration verification
   - Interface monitoring

2. Implementation
   - Create feature branch
   - Implement changes
   - Add logging
   - Update documentation

3. Testing
   - Unit tests
   - Integration tests
   - Manual verification
   - Performance checks

4. Deployment
   - Update requirements
   - Verify dependencies
   - Test installation
   - Update documentation 