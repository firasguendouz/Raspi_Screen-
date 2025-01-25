# Raspberry Pi Screen Management Server

![Server Status](https://img.shields.io/badge/status-stable-green)
![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Python](https://img.shields.io/badge/python-3.7+-yellow)
![License](https://img.shields.io/badge/license-MIT-orange)

## 🔍 Overview
Flask-based server application providing web interface and API endpoints for Raspberry Pi screen management, WiFi configuration, and QR code generation. Features enhanced internationalization, robust error handling, and performance optimizations.

## 🔗 Related Documentation
- [QR Code Module](qr_code.md)
- [Utilities Module](utils.md)

## 🧩 Components
- **[app.py](app.py)**: Main Flask application with async network scanning and i18n support
- **[qr_code.py](qr_code.py)**: QR code generation with caching and styling
- **[utils.py](utils.py)**: Shared utilities for validation and error handling
- **templates/**: HTML templates for web interface

## ⭐ Features
- Asynchronous network scanning
- Robust error handling with i18n support
- Request logging with IP and user agent tracking
- QR code generation with caching
- Dynamic language selection
- Input validation and sanitization
- Performance monitoring

## 📦 Installation

### Dependencies
```bash
pip install -r requirements.txt
```

Required packages:
- `Flask>=2.0.0`: Web framework
- `Flask-Babel>=2.0.0`: Internationalization
- `qrcode[pil]>=7.0`: QR code generation
- `Werkzeug>=2.0.0`: WSGI utilities
- `python-dotenv>=0.19.0`: Environment configuration
- `aiohttp>=3.8.0`: Async HTTP client

### 🔧 Configuration
Environment variables:
```bash
FLASK_ENV=production
FLASK_SECRET_KEY=your-secret-key
LOG_LEVEL=INFO
QR_CACHE_DIR=/path/to/cache
```

## 🌐 API Endpoints

### GET /
- Renders main configuration page
- Supports language selection via URL parameter
- Returns: HTML page

### GET /api/networks
- Asynchronously scans for available WiFi networks
- Returns: JSON array of networks with signal strength
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
- Validates all inputs
- Supports both JSON and form data
```json
{
    "ssid": "MyNetwork",
    "password": "MyPassword",
    "color": "#000000"
}
```

### GET /qr/<filename>
- Serves generated QR code images
- Validates file access
- Returns: PNG image or 404 error

### GET /translations/<lang>
- Provides translation strings for specified language
- Returns: JSON object with translations

## 🌍 Internationalization

### Supported Languages
- English (en)
- Spanish (es)
- French (fr)
- German (de)

### Language Selection
1. URL parameter: `/?lang=es`
2. Accept-Language header
3. Default to English

### Translation Files
Located in `translations/<lang>/LC_MESSAGES/`:
- `messages.po`: Source translations
- `messages.mo`: Compiled translations
- `messages.json`: Frontend translations

## 📝 Logging

### Log File
- Path: `/var/log/raspi_screen/server.log`
- Format: `%(asctime)s - %(name)s - %(levelname)s - %(message)s`

### Logged Information
- Request details (method, path, IP, user agent)
- Network scan results
- QR code generation status
- Error messages with stack traces
- Performance metrics

## ⚠️ Error Handling

### HTTP Status Codes
- 200: Success
- 400: Invalid input
- 404: Resource not found
- 503: Service unavailable
- 500: Internal server error

### Error Response Format
```json
{
    "error": "Error type",
    "message": "Detailed error message"
}
```

## 🔒 Security Features
- Input validation and sanitization
- Request logging with IP tracking
- File access validation
- Size limits (16MB max)
- Proxy support with X-Forwarded-For
- CSRF protection

## 🔍 Performance Monitoring
- Request execution time logging
- Async network operations
- QR code caching
- Translation caching
- Memory usage tracking

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
# Test network scanning
curl http://localhost:5000/api/networks

# Test WiFi connection
curl -X POST http://localhost:5000/api/connect \
    -H "Content-Type: application/json" \
    -d '{"ssid":"MyNetwork","password":"MyPassword"}'
```

## 🔧 Troubleshooting

### Common Issues
1. **Network scan fails**
   - Check sudo permissions
   - Verify wlan0 interface
   - Check async operation timeout

2. **QR generation fails**
   - Check write permissions
   - Verify cache directory
   - Check logo file existence

3. **Language not loading**
   - Verify translation files
   - Check language code
   - Clear translation cache

## 🚀 Future Enhancements
1. WebSocket support for real-time updates
2. OAuth2 authentication
3. Rate limiting
4. Metrics collection
5. Admin dashboard
6. Additional language support
7. SVG QR code output
8. Enhanced caching strategies

---
*Last updated: 2024-01-24*

Tags: #server #flask #api #wifi #qr-code #python #web-interface #async #i18n 