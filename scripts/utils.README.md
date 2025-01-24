# utils.py

![Status](https://img.shields.io/badge/status-stable-green)
![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Python](https://img.shields.io/badge/python-3.7+-yellow)
![Coverage](https://img.shields.io/badge/coverage-95%25-brightgreen)

## 🔍 Overview
Common utility functions for the Raspberry Pi Screen Management scripts, providing input validation, network utilities, and logging functionality.

## 🔗 Related Documentation
- [Main Scripts Documentation](Scripts.md)
- [WiFi Connection Module](connect_wifi.README.md)
- [Send Activation Module](send_activation.README.md)
- [Stream URL Module](stream_url.README.md)

## ⭐ Features
- Input validation and sanitization
- Network interface management
- Configuration file handling
- Logging setup and management
- Error handling utilities

## 📦 Dependencies
- `python-dotenv`: Environment configuration
- `validators`: Input validation
- `requests`: HTTP client library
- `psutil`: System metrics collection

## 🛠️ Installation
```bash
pip install -r requirements.txt
```

## 📝 Usage
```python
from utils import (
    validate_input,
    setup_logging,
    load_config,
    get_network_info
)

# Setup logging
logger = setup_logging("my_script")

# Validate user input
if validate_input(user_input):
    # Process input
    pass

# Load configuration
config = load_config()

# Get network information
network_info = get_network_info()
```

## ⚙️ Configuration

### Environment Variables
See [.env.example](.env.example) for configuration options:
- `LOG_LEVEL`: Logging verbosity
- `CONFIG_DIR`: Configuration directory
- `LOG_DIR`: Log file directory

### Logging Configuration
```python
LOGGING_CONFIG = {
    "version": 1,
    "formatters": {
        "default": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        }
    },
    "handlers": {
        "file": {
            "class": "logging.FileHandler",
            "formatter": "default",
            "filename": "/var/log/raspi_screen/utils.log"
        }
    },
    "root": {
        "level": "INFO",
        "handlers": ["file"]
    }
}
```

## 🛠️ Functions

### Input Validation

#### `validate_input(text: str, max_length: int = 100) -> bool`
Validates user input for safety and length.

```python
if validate_input(user_text, max_length=50):
    process_input(user_text)
```

#### `sanitize_string(text: str) -> str`
Removes dangerous characters from input.

```python
clean_text = sanitize_string(raw_input)
```

### Network Utilities

#### `get_network_info() -> Dict[str, Any]`
Retrieves network interface information.

```python
network_info = get_network_info()
print(f"IP Address: {network_info['ip_address']}")
```

#### `check_connection(host: str = "8.8.8.8") -> bool`
Checks internet connectivity.

```python
if check_connection():
    print("Internet available")
```

### Configuration Management

#### `load_config(config_path: str = None) -> Dict[str, Any]`
Loads configuration from JSON file.

```python
config = load_config("/path/to/config.json")
```

#### `save_config(config: Dict[str, Any], config_path: str) -> None`
Saves configuration to JSON file.

```python
save_config(updated_config, "/path/to/config.json")
```

### Logging

#### `setup_logging(name: str, level: str = "INFO") -> logging.Logger`
Sets up logging with file handler.

```python
logger = setup_logging("my_script", "DEBUG")
logger.info("Script started")
```

## ⚠️ Error Handling

### Custom Exceptions
```python
class ConfigError(Exception):
    """Configuration related errors"""
    pass

class NetworkError(Exception):
    """Network operation errors"""
    pass

class ValidationError(Exception):
    """Input validation errors"""
    pass
```

### Error Messages
```python
ERROR_MESSAGES = {
    "invalid_input": "Input contains invalid characters",
    "network_unreachable": "Network is unreachable",
    "config_not_found": "Configuration file not found"
}
```

## 📝 Best Practices

1. **Input Validation**
   - Always sanitize user input
   - Validate before processing
   - Use appropriate length limits

2. **Error Handling**
   - Use custom exceptions
   - Log errors with context
   - Provide helpful error messages

3. **Configuration**
   - Use environment variables
   - Validate configuration
   - Handle missing values

4. **Logging**
   - Use appropriate log levels
   - Include context in messages
   - Rotate log files

## 📚 See Also
- [WiFi Connection Module](connect_wifi.README.md)
- [Send Activation Module](send_activation.README.md)
- [Stream URL Module](stream_url.README.md)

---
*Last updated: 2024-01-24*

Tags: #utils #python #validation #networking #logging #configuration 