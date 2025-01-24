# stream_url.py

![Status](https://img.shields.io/badge/status-stable-green)
![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Python](https://img.shields.io/badge/python-3.7+-yellow)
![Coverage](https://img.shields.io/badge/coverage-88%25-brightgreen)

## 🔍 Overview
URL Streaming Manager for Raspberry Pi Screen that handles content streaming with robust error handling and fallback mechanisms.

## 🔗 Related Documentation
- [Main Scripts Documentation](Scripts.md)
- [WiFi Connection Module](connect_wifi.README.md)
- [Send Activation Module](send_activation.README.md)
- [Utilities Module](utils.README.md)

## ⭐ Features
- URL validation and sanitization
- Automatic HTTPS upgrade
- Connection monitoring
- Fallback content support
- Detailed logging and error reporting

## 📦 Dependencies
- **[utils.py](utils.py)**: Common utility functions
- `requests`: HTTP client library
- `validators`: URL validation
- `python-dotenv`: Environment configuration

## 🛠️ Installation
```bash
pip install -r requirements.txt
```

## 📝 Usage
```bash
# Stream URL with default settings
python stream_url.py --url "https://example.com"

# Stream with fallback content
python stream_url.py --url "https://example.com" --fallback "/path/to/offline.html"

# Custom retry settings
python stream_url.py --url "https://example.com" --retry 5 --timeout 30
```

## ⚙️ Configuration

### Environment Variables
See [.env.example](.env.example) for configuration options:
- `STREAM_URL`: Default URL to stream
- `FALLBACK_CONTENT`: Path to offline content
- `LOG_LEVEL`: Logging verbosity
- `RETRY_ATTEMPTS`: Number of retry attempts

### JSON Configuration (scripts.json)
```json
{
    "streaming": {
        "default_url": "${STREAM_URL}",
        "fallback_content": "${FALLBACK_CONTENT}",
        "retry_attempts": 3,
        "timeout": 30
    }
}
```

## ⚠️ Error Handling
The script implements several error handling mechanisms:
1. URL validation and sanitization
2. Connection retry with exponential backoff
3. Fallback content on failure
4. Network error recovery
5. Detailed error reporting

## 📝 Logging
Logs are written to `/var/log/raspi_screen/stream_url.log` with the following levels:
- `ERROR`: Connection and streaming failures
- `WARNING`: Connection issues and retries
- `INFO`: Streaming status and URL changes
- `DEBUG`: Detailed operation information

## 🔍 Exit Codes
- `0`: Successful streaming
- `1`: Configuration or streaming error

## 🔌 API Usage
```python
from stream_url import stream_content, validate_url

# Stream content with fallback
stream_content(
    url="https://example.com",
    fallback="/offline.html",
    retry_count=3
)
```

## 🛠️ Functions

### `validate_url(url: str) -> bool`
Validates URL format and accessibility.

### `check_connection(url: str, timeout: int = 30) -> bool`
Checks if URL is reachable.

### `load_fallback_content(path: str) -> str`
Loads fallback content from file.

### `stream_content(url: str, fallback: str = None, retry_count: int = 3) -> None`
Streams content from URL with fallback support.

## 📚 See Also
- [WiFi Connection Module](connect_wifi.README.md)
- [Send Activation Module](send_activation.README.md)
- [Utilities Module](utils.README.md)

---
*Last updated: 2024-01-24*

Tags: #streaming #url #python #raspberry-pi #monitoring 