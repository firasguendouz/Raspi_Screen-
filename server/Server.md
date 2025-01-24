# Raspberry Pi Screen Management Server

![Server Status](https://img.shields.io/badge/status-stable-green)
![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Python](https://img.shields.io/badge/python-3.7+-yellow)
![License](https://img.shields.io/badge/license-MIT-orange)

## 🔍 Overview
Flask-based server application providing web interface and API endpoints for Raspberry Pi screen management, WiFi configuration, and QR code generation.

## 🔗 Related Documentation
- [QR Code Module](qr_code.md)
- [Utilities Module](utils.md)

## 🧩 Components
- **[app.py](app.py)**: Main Flask application
- **[qr_code.py](qr_code.py)**: QR code generation module
- **[utils.py](utils.py)**: Utility functions
- **templates/**: HTML templates

## ⭐ Features
- WiFi network scanning and configuration
- QR code generation with caching
- Internationalization (i18n) support
- Request logging and monitoring
- Error handling and validation

## 📦 Installation

### Dependencies
```bash
pip install -r requirements.txt
```

Required packages:
- `Flask>=2.0.0`: Web framework
- `Flask-Babel>=2.0.0`: i18n support
- `qrcode[pil]>=7.0`: QR code generation
- `Werkzeug>=2.0.0`: WSGI utilities
- `python-dotenv>=0.19.0`: Environment management

### 🔧 Configuration
Environment variables:
```bash
FLASK_SECRET_KEY=your-secret-key
LOG_LEVEL=INFO
```

## 🌐 API Endpoints

### GET /
- Renders main configuration page
- Supports language selection via URL parameter

### GET /api/networks
- Scans for available WiFi networks
- Returns JSON array of networks with signal strength

Example response:
```json
{
    "networks": [
        {
            "ssid": "MyNetwork",
            "quality": 70,
            "encrypted": true
        }
    ]
}
```

### POST /api/connect
- Connects to WiFi network and generates QR code
- Accepts JSON or form data

Request body:
```json
{
    "ssid": "MyNetwork",
    "password": "MyPassword",
    "color": "#000000",
    "add_logo": true
}
```

Response:
```json
{
    "success": true,
    "qr_code": "path/to/qr.png"
}
```

### GET /qr/<filename>
- Serves generated QR code images
- Returns PNG image or 404 error
- See: [QR Code Module](qr_code.md)

## 🌍 Internationalization

Supported languages:
- English (en)
- Spanish (es)
- French (fr)
- German (de)

Language selection:
1. URL parameter: `/?lang=es`
2. Accept-Language header
3. Default to English

## 📝 Logging

Log file: `/var/log/raspi_screen/server.log`

Log format:
```
%(asctime)s - %(name)s - %(levelname)s - %(message)s
```

Logged information:
- Request details (method, path, IP, user agent)
- Network scan results
- QR code generation status
- Error messages

## ⚠️ Error Handling

HTTP Status Codes:
- 200: Success
- 400: Invalid input
- 404: Resource not found
- 500: Internal server error

Error response format:
```json
{
    "error": "Error type",
    "message": "Detailed error message"
}
```

## 🔒 Security

Security features:
- Input sanitization (see [Utils Module](utils.md))
- Request logging
- File type validation
- Size limits (16MB max)
- Proxy support

## 👨‍💻 Development

### Running the Server
```bash
# Development mode
flask run --host=0.0.0.0 --port=5000

# Production mode
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Adding New Features
1. Update API endpoints in app.py
2. Add corresponding templates
3. Update translations
4. Add error handlers
5. Update documentation

### Testing
```bash
# Test WiFi scanning
curl http://localhost:5000/api/networks

# Test WiFi connection
curl -X POST http://localhost:5000/api/connect \
    -H "Content-Type: application/json" \
    -d '{"ssid":"MyNetwork","password":"MyPassword"}'
```

## 🔧 Troubleshooting

Common issues:
1. **Network scan fails**
   - Check sudo permissions
   - Verify wlan0 interface

2. **QR generation fails**
   - Check write permissions
   - Verify logo path
   - See: [QR Code Module](qr_code.md)

3. **Language not loading**
   - Check translation files
   - Verify language code

## 🚀 Future Enhancements

Planned improvements:
1. WebSocket support for real-time updates
2. OAuth2 authentication
3. Rate limiting
4. Metrics collection
5. Admin dashboard

---
*Last updated: 2024-01-24*

Tags: #server #flask #api #wifi #qr-code #python #web-interface 