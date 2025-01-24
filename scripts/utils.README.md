# utils.py

## Overview
Utility Module for Raspberry Pi Screen Management Scripts that provides shared functionality for logging, configuration, error handling, and system metrics collection.

## Features
- Centralized logging configuration
- Configuration file management
- HTTP session handling with retries
- System metrics collection
- File backup and restore
- Error handling classes
- Network validation utilities

## Dependencies
- `python-dotenv`: Environment configuration
- `requests`: HTTP client library
- `validators`: URL validation
- `psutil`: System metrics collection
- `logging`: Python standard logging

## Installation
```bash
pip install -r requirements.txt
```

## Configuration

### Environment Variables
- `LOG_DIR`: Log directory path
- `CONFIG_DIR`: Configuration directory path
- `LOG_LEVEL`: Logging verbosity

### Constants
```python
DEFAULT_LOG_DIR = "/var/log/raspi_screen"
DEFAULT_CONFIG_DIR = "../config"
DEFAULT_RETRY_ATTEMPTS = 3
DEFAULT_BACKOFF_FACTOR = 0.3
```

## Error Classes

### ConfigurationError
```python
class ConfigurationError(Exception):
    """Exception raised for configuration-related errors."""
    pass
```

### NetworkError
```python
class NetworkError(Exception):
    """Exception raised for network-related errors."""
    pass
```

## Functions

### Logging

#### `setup_logging(script_name: str, log_level: str = "INFO") -> logging.Logger`
Configures logging with file and console handlers.
```python
logger = setup_logging('my_script')
logger.info("Operation successful")
```

### Configuration

#### `load_config(config_name: str) -> Dict[str, Any]`
Loads configuration from JSON file.
```python
config = load_config('wifi_networks')
wifi_settings = config['default']
```

### HTTP Utilities

#### `create_http_session(retries: int = DEFAULT_RETRY_ATTEMPTS, backoff_factor: float = DEFAULT_BACKOFF_FACTOR) -> requests.Session`
Creates HTTP session with retry capabilities.
```python
session = create_http_session(retries=5)
response = session.get('https://example.com')
```

### URL Validation

#### `validate_url(url: str) -> bool`
Validates URL format.
```python
if validate_url("https://example.com"):
    print("Valid URL")
```

### File Operations

#### `backup_file(file_path: str) -> str`
Creates backup of specified file.
```python
backup_path = backup_file("/etc/config.conf")
```

#### `restore_file(backup_path: str, original_path: str) -> None`
Restores file from backup.
```python
restore_file("/etc/config.conf.backup", "/etc/config.conf")
```

### System Metrics

#### `get_system_metrics() -> Dict[str, Any]`
Collects system performance metrics.
```python
metrics = get_system_metrics()
print(f"CPU Usage: {metrics['cpu_percent']}%")
```

### Network Validation

#### `validate_wifi_credentials(ssid: str, password: Optional[str] = None) -> bool`
Validates WiFi credential format.
```python
if validate_wifi_credentials("MyNetwork", "password123"):
    print("Valid credentials")
```

## Logging Structure
- File Handler: Rotating file with size limit
- Console Handler: Level-based colored output
- Format: `%(asctime)s - %(name)s - %(levelname)s - %(message)s`

## Error Handling
- Configuration validation
- File operation safety
- Network request retries
- Detailed error messages
- Exception hierarchy

## Usage Example
```python
from utils import setup_logging, load_config, create_http_session

# Setup logging
logger = setup_logging('my_script')

try:
    # Load configuration
    config = load_config('app_config')
    
    # Create HTTP session
    session = create_http_session()
    
    # Use configuration
    url = config['api_url']
    response = session.get(url)
    
    logger.info("Operation successful")
    
except ConfigurationError as e:
    logger.error(f"Configuration error: {e}")
except NetworkError as e:
    logger.error(f"Network error: {e}")
```

## See Also
- `stream_url.py`: URL streaming management
- `connect_wifi.py`: WiFi connection management
- `send_activation.py`: Device activation and metrics 