# Troubleshooting Guide

## 🔍 Quick Diagnostics

### System Status Check
```bash
# Check system metrics
python metrics_info.py

# Check network interfaces
iwconfig
ifconfig wlan0

# Check services
sudo systemctl status hostapd
sudo systemctl status dnsmasq
```

## 🌐 Network Issues

### 1. Wi-Fi Connection Failures

#### Symptoms
- Failed to connect to network
- Connection drops frequently
- No internet access after connection

#### Solutions
1. **Check Network Interface**
   ```bash
   # Verify wlan0 status
   sudo ifconfig wlan0 up
   iwconfig wlan0
   ```

2. **Reset Network Interface**
   ```bash
   sudo ip link set wlan0 down
   sudo ip link set wlan0 up
   ```

3. **Reset DNS Configuration**
   ```python
   from scripts.connect_wifi import reset_dns
   reset_dns()
   ```

### 2. Access Point Issues

#### Symptoms
- AP not visible
- Clients can't connect
- DHCP not working

#### Solutions
1. **Restart AP Services**
   ```bash
   sudo systemctl restart hostapd
   sudo systemctl restart dnsmasq
   ```

2. **Check AP Configuration**
   ```bash
   # Verify hostapd config
   cat /etc/hostapd/hostapd.conf
   
   # Check DHCP settings
   cat /etc/dnsmasq.conf
   ```

3. **Monitor AP Connections**
   ```bash
   # Watch connection attempts
   tail -f /var/log/syslog | grep hostapd
   ```

## 🖥️ Display Issues

### 1. PyWebView Problems

#### Symptoms
- Black screen
- Window not appearing
- Content not rendering

#### Solutions
1. **Check Backend**
   ```python
   import webview
   print(f"PyWebView version: {webview.__version__}")
   print(f"Backend: {webview.initialize()}")
   ```

2. **Verify Display Settings**
   ```python
   from on_off import get_rotation_choice, set_brightness

   # Test display
   set_brightness(8)  # Set to 80% brightness
   ```

3. **Test QR Display**
   ```python
   python test_qr_display.py
   ```

### 2. Screen Rotation Issues

#### Solutions
```python
from on_off import rotate_screen

# Try different orientations
rotate_screen("normal")  # 0°
rotate_screen("right")   # 90°
rotate_screen("left")    # 270°
```

## 🔒 Security and Authentication

### 1. Activation Problems

#### Symptoms
- Activation request fails
- Server connection timeout
- Authentication errors

#### Solutions
1. **Check Server Connection**
   ```python
   # Test activation client
   from scripts.send_activation import ActivationClient
   
   client = ActivationClient(server_url="http://localhost:5001")
   success, result = client.send_activation_request()
   print(f"Activation result: {result}")
   ```

2. **Verify Credentials**
   ```bash
   # Check environment variables
   echo $SERVER_URL
   echo $SERVER_PORT
   ```

## 📝 Logging and Debugging

### 1. Access Logs
```bash
# Application logs
tail -f logs/debug.log

# Network logs
tail -f /var/log/wifi_setup.log

# System logs
journalctl -u hostapd
journalctl -u dnsmasq
```

### 2. Enable Debug Mode
```python
# Set logging level
import logging
logging.basicConfig(
    level=logging.DEBUG,
    format='[%(asctime)s] %(levelname)s: %(message)s'
)
```

## 🐳 Docker Issues

### 1. Container Problems

#### Symptoms
- Container fails to start
- Network access issues
- Volume mount problems

#### Solutions
1. **Check Container Status**
   ```bash
   docker ps -a
   docker logs raspi-screen
   ```

2. **Verify Network Settings**
   ```bash
   docker network ls
   docker network inspect raspi-network
   ```

3. **Reset Container**
   ```bash
   docker-compose down
   docker-compose up -d
   ```

## 🔧 Common Error Messages

### 1. "Failed to initialize display"
- Check display connection
- Verify X server is running
- Check PyWebView dependencies

### 2. "Network interface not found"
- Verify wlan0 exists
- Check network manager status
- Ensure proper permissions

### 3. "Access Point creation failed"
- Check hostapd installation
- Verify configuration files
- Ensure no conflicting services

## 📊 Performance Issues

### 1. System Resources
```python
# Check system metrics
from metrics_info import get_system_info

info = get_system_info()
print(f"CPU Usage: {info['cpu_usage']}")
print(f"Memory Used: {info['memory_used']}")
```

### 2. Network Performance
```bash
# Test network speed
speedtest-cli

# Monitor network traffic
sudo iftop -i wlan0
```

## 🆘 Recovery Procedures

### 1. Reset to Default State
```bash
# Stop services
sudo systemctl stop hostapd
sudo systemctl stop dnsmasq

# Reset network
sudo ip link set wlan0 down
sudo ip link set wlan0 up

# Clear configurations
sudo rm wifi_credentials.tmp
```

### 2. Emergency Recovery
1. Stop all services
2. Reset network interfaces
3. Clear temporary files
4. Restart system

## 📞 Getting Help

### Support Resources
1. Check system logs
2. Review documentation
3. Contact support team

### Required Information
- System logs
- Network configuration
- Error messages
- Steps to reproduce

---
*For development-related issues, see [[Development Guide]]*
