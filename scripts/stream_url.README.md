# stream_url.py

## Overview
URL Streaming Manager for Raspberry Pi Screen that handles content display with robust error handling and fall-back mechanisms.

## Features
- URL validation and sanitization
- Automatic HTTPS upgrade when available
- Fallback content support
- Connection monitoring and retry mechanism
- Detailed logging and error reporting

## Dependencies
- `utils.py`: Common utility functions
- `requests`: HTTP client library
- `validators`: URL validation
- `python-dotenv`: Environment configuration

## Installation
```bash
pip install -r requirements.txt
```

## Usage
```bash
# Stream a URL with default settings
python stream_url.py https://example.com

# Stream with fallback content
python stream_url.py https://example.com --fallback /path/to/local.html

# Stream with custom timeout and retries
python stream_url.py https://example.com --timeout 60 --retry 5
```

## Configuration

### Environment Variables
- `FALLBACK_CONTENT`: Default fallback content path
- `REFRESH_INTERVAL`: Content refresh interval
- `LOG_LEVEL`: Logging verbosity

### JSON Configuration (scripts.json)
```json
{
    "display": {
        "fallback_content": "file:///path/to/offline.html",
        "refresh_interval": 300,
        "timeout": 30,
        "retry_attempts": 3
    }
}
```

## Error Handling
The script implements several error handling mechanisms:
1. URL validation before streaming
2. Automatic fallback to HTTP if HTTPS fails
3. Exponential backoff for retry attempts
4. Fallback content on streaming failure

## Logging
Logs are written to `/var/log/raspi_screen/stream_url.log` with the following levels:
- `ERROR`: Streaming and connection failures
- `WARNING`: URL availability issues
- `INFO`: Streaming status and fallback usage
- `DEBUG`: Detailed connection information

## Exit Codes
- `0`: Successful streaming
- `1`: Configuration or streaming error

## API Usage
```python
from stream_url import stream_url

# Stream URL with fallback
stream_url(
    url="https://example.com",
    fallback="file:///offline.html",
    timeout=30,
    retry_count=3
)
```

## Functions

### `validate_and_prepare_url(url: str) -> str`
Validates and prepares URL for streaming, attempting HTTPS upgrade if possible.

### `check_url_availability(url: str, timeout: int = 5) -> bool`
Checks if a URL is available and responding.

### `load_fallback_content() -> Optional[str]`
Loads fallback content configuration from settings.

### `stream_url(url: str, fallback: Optional[str] = None, timeout: int = 30, retry_count: int = 3) -> None`
Main function to stream URL with fallback and retry mechanisms.

## See Also
- `connect_wifi.py`: WiFi connection management
- `send_activation.py`: Device activation and metrics
- `utils.py`: Shared utilities 