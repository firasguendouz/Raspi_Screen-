# API Documentation

## 🔍 Overview

The Raspberry Pi Screen Management System provides a RESTful API for device configuration, network management, and screen activation. This documentation covers all available endpoints, their usage, and examples.

## 🔒 Authentication

Currently, the API uses basic authentication for internal network communication. Future versions will implement token-based authentication.

## 📡 Network Configuration API

### Configure Wi-Fi Network

```http
POST /configure
Content-Type: application/x-www-form-urlencoded
```

#### Request Parameters
| Parameter | Type   | Required | Description           |
|-----------|--------|----------|-----------------------|
| ssid      | string | Yes      | Wi-Fi network name   |
| password  | string | Yes      | Network password     |

#### Example Request
```bash
curl -X POST http://localhost:5001/configure \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "ssid=NetworkName&password=NetworkPassword"
```

#### Success Response
```json
{
    "status": "success",
    "message": "Credentials received"
}
```

#### Error Response
```json
{
    "status": "error",
    "message": "Failed to save credentials: {error_details}"
}
```

### Check Network Status

```http
GET /status
```

#### Response
```json
{
    "connected": true,
    "ssid": "Current_Network",
    "signal_strength": -65,
    "ip_address": "192.168.1.100"
}
```

## 🖥️ Device Activation API

### Send Activation Request

```http
POST /activate
Content-Type: application/json
```

#### Request Body
```json
{
    "device_id": "unique_device_id",
    "status": "ready",
    "capabilities": {
        "display": true,
        "rotation": true,
        "brightness": true
    }
}
```

#### Success Response
```json
{
    "status": "success",
    "activation_token": "token_string",
    "server_url": "http://content-server.com"
}
```

## 🎯 Display Control API

### Update Display Settings

```http
POST /display/settings
Content-Type: application/json
```

#### Request Body
```json
{
    "brightness": 80,
    "rotation": "normal",
    "power_mode": "on"
}
```

#### Example Using Python
```python
from scripts.on_off import set_brightness, rotate_screen

# Set display brightness
set_brightness(8)  # 80% brightness

# Rotate screen
rotate_screen("normal")  # 0° rotation
```

## 📊 System Metrics API

### Get System Information

```http
GET /metrics
```

#### Response
```json
{
    "cpu_temperature": 45.2,
    "cpu_usage": 23.5,
    "memory": {
        "total": 4096,
        "used": 1024,
        "free": 3072
    },
    "disk": {
        "total": 32768,
        "used": 8192,
        "free": 24576
    }
}
```

#### Implementation
```python
from metrics_info import get_system_info

def get_metrics():
    info = get_system_info()
    return {
        'temperature': info['temperature'],
        'cpu_usage': info['cpu_usage'],
        'memory_used': info['memory_used'],
        'disk_usage': info['disk_used']
    }
```

## 🌐 Access Point API

### AP Status

```http
GET /ap/status
```

#### Response
```json
{
    "active": true,
    "clients": [
        {
            "mac": "00:11:22:33:44:55",
            "ip": "192.168.4.2",
            "hostname": "client-device"
        }
    ],
    "uptime": 3600
}
```

### Control AP

```http
POST /ap/control
Content-Type: application/json
```

#### Request Body
```json
{
    "action": "start|stop|restart",
    "config": {
        "ssid": "RaspberryPi_AP",
        "password": "secure_password",
        "channel": 7
    }
}
```

## 🔄 WebSocket Events

### Connection Status Updates

```javascript
// Connect to WebSocket
const ws = new WebSocket('ws://localhost:5001/ws');

// Listen for updates
ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log('Status Update:', data);
};
```

#### Event Types
```json
{
    "type": "connection_status",
    "data": {
        "status": "connected|disconnected|connecting",
        "details": "Additional information"
    }
}
```

## 🛠️ Error Handling

### Error Responses
All API errors follow this format:
```json
{
    "status": "error",
    "code": "ERROR_CODE",
    "message": "Human readable message",
    "details": {
        "additional": "error details"
    }
}
```

### Common Error Codes
| Code              | Description                           |
|-------------------|---------------------------------------|
| NETWORK_ERROR     | Network connection failed             |
| AUTH_ERROR        | Authentication failed                 |
| INVALID_INPUT     | Invalid request parameters            |
| DEVICE_ERROR      | Hardware/device error                 |
| SERVER_ERROR      | Internal server error                 |

## 📝 API Versioning

Current API version: v1

Include version in URL:
```http
https://device-ip/api/v1/endpoint
```

## 🔐 Security Considerations

1. **Input Validation**
```python
def sanitize_input(text: str) -> str:
    """Sanitize user input"""
    return bleach.clean(text, strip=True)
```

2. **Rate Limiting**
- 100 requests per minute per IP
- Configurable in server settings

3. **SSL/TLS**
- HTTPS required for production
- Self-signed certificates for local network

## 📚 SDK Examples

### Python Client
```python
from scripts.send_activation import ActivationClient

client = ActivationClient(server_url="http://localhost:5001")
success, result = client.send_activation_request()
```

### JavaScript Client
```javascript
async function configureWiFi(ssid, password) {
    const response = await fetch('/configure', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: `ssid=${ssid}&password=${password}`
    });
    return response.json();
}
```

---
*See also: [[System Architecture]], [[Development Guide]]*
