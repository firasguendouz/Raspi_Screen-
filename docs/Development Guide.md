# Development Guide for Raspberry Pi Screen Management System

## 🎯 Quick Start

1. **Initial Setup**
   ```bash
   git clone <repository-url>
   cd raspi-setup
   python3 -m venv env
   source env/bin/activate
   pip install -r requirements.txt
   ```

2. **Run Development Server**
   ```bash
   # Terminal 1 - Flask Server
   export FLASK_ENV=development
   export FLASK_APP=server/app.py
   flask run --port 5001

   # Terminal 2 - Main Application
   python main.py
   ```

## 💻 Development Environment

### Required Dependencies
```bash
# System Libraries
sudo apt-get update
sudo apt-get install -y \
    python3-dev \
    libcairo2-dev \
    pkg-config \
    hostapd \
    dnsmasq \
    network-manager \
    libgtk-3-dev \
    libwebkit2gtk-4.0-dev

# Python Dependencies
pip install -r requirements.txt
```

### Environment Variables
Create `.env` file:
```bash
SERVER_URL=http://localhost:5001
SERVER_PORT=5001
FLASK_ENV=development
PYTHONUNBUFFERED=1
```

## 🧪 Testing

### Running Tests
```bash
# QR Code Display Test
python test_qr_display.py

# WebView Test
python test_webview.py

# System Metrics
python metrics_info.py
```

### Test Coverage Areas
1. **UI Components**
   - QR code generation and display
   - PyWebView interface
   - Status messages

2. **Network Functions**
   - Wi-Fi connection
   - Access Point setup
   - Connection monitoring

3. **System Integration**
   - Device activation
   - Content streaming
   - Error handling

## 🔧 Core Components Guide

### 1. UI Manager
```python
# ui_manager/ui_manager.py
class UIManager:
    def display_qr_code(self, qr_path, message):
        """
        Display QR code in PyWebView window
        
        Args:
            qr_path (str): Path to QR code image
            message (str): Status message to display
        """
        # Implementation
```

### 2. Network Management
```python
# scripts/connect_wifi.py
def connect_wifi(ssid: str, password: str) -> bool:
    """
    Connect to Wi-Fi network
    
    Args:
        ssid: Network name
        password: Network password
        
    Returns:
        bool: Connection success status
    """
    # Implementation
```

### 3. Access Point Control
```bash
# ap/setup_ap.sh
#!/bin/bash
# Initialize Access Point
systemctl stop wpa_supplicant
systemctl stop hostapd
# Configure network...
```

## 📝 Development Workflow

### 1. Feature Development
1. Create feature branch
   ```bash
   git checkout -b feature/your-feature
   ```

2. Implement changes following patterns:
   ```python
   # Example pattern for UI updates
   def update_ui(message: str, image_path: str = None):
       """Update UI with message and optional image"""
       print(f"Status: {message}")
       if image_path:
           display_image(image_path)
   ```

3. Add tests:
   ```python
   def test_feature():
       """Test new feature functionality"""
       # Setup
       # Test
       # Assert
   ```

### 2. Code Style
- Follow PEP 8
- Use type hints
- Add docstrings
- Maximum line length: 79 characters

## 🐛 Debugging Guide

### Common Issues

1. **PyWebView Display Problems**
   ```python
   # Check backend
   import webview
   print(f"Using backend: {webview.initialize()}")
   ```

2. **Network Connection Issues**
   ```python
   # Debug connection
   def debug_network():
       subprocess.run(['iwconfig'], check=True)
       subprocess.run(['ifconfig'], check=True)
   ```

3. **Access Point Setup**
   ```bash
   # Check AP status
   sudo systemctl status hostapd
   sudo systemctl status dnsmasq
   ```

### Logging
```python
# Configure logging
import logging
logging.basicConfig(
    filename='logs/debug.log',
    level=logging.DEBUG,
    format='[%(asctime)s] %(levelname)s: %(message)s'
)
```

## 🔒 Security Considerations

### 1. Input Validation
```python
# server/app.py
def sanitize_input(text: str) -> str:
    """Sanitize user input"""
    return bleach.clean(text, strip=True)
```

### 2. Network Security
```python
# Access Point Configuration
ssid = "RaspberryPi_AP"
wpa_passphrase = secrets.token_hex(8)
```

### 3. File Operations
```python
# Secure file handling
def save_credentials(ssid: str, password: str):
    """Save Wi-Fi credentials securely"""
    with open('wifi_credentials.tmp', 'w') as f:
        os.chmod('wifi_credentials.tmp', 0o600)
        f.write(f"{ssid}\n{password}")
```

## 📚 API Reference

### Wi-Fi Configuration
```http
POST /configure
Content-Type: application/x-www-form-urlencoded

ssid=NetworkName&password=NetworkPassword
```

### Device Activation
```http
POST /activate
Content-Type: application/json

{
    "device_id": "unique_id",
    "status": "ready"
}
```

## 🔄 Docker Development

### Build Image
```bash
docker build -t raspi-screen .
```

### Run Container
```bash
docker-compose up -d
```

### Debug Container
```bash
docker exec -it raspi-screen bash
```

## 📋 Release Checklist

1. Update version numbers
2. Run full test suite
3. Check security configurations
4. Update documentation
5. Create release tag
6. Build production Docker image

---
*For detailed system architecture and deployment guides, see [[System Architecture]] and [[Deployment Guide]]*
