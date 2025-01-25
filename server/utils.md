# Utilities Module

![Status](https://img.shields.io/badge/status-stable-green)
![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Python](https://img.shields.io/badge/python-3.7+-yellow)
![Coverage](https://img.shields.io/badge/coverage-98%25-brightgreen)

## 🔍 Overview
Core utility functions for the Raspberry Pi Screen Management Server, providing robust input validation, error handling, logging configuration, and common helper functions. Emphasizes security and maintainability through centralized error handling and consistent validation patterns.

## 🔗 Related Documentation
- [Server Documentation](Server.md)
- [QR Code Module](qr_code.md)

## ⭐ Features
- Comprehensive input validation
- Centralized error handling
- Advanced logging configuration
- Type hints and docstrings
- Performance monitoring
- Security-focused utilities

## 📦 Dependencies
- Python standard library
- `typing`: Type hints
- `logging`: Logging system
- `pathlib`: Path handling
- `ipaddress`: IP validation

## 🛠️ Exception Classes

### ValidationError
```python
class ValidationError(Exception):
    """Raised when input validation fails."""
    pass
```

### ConfigurationError
```python
class ConfigurationError(Exception):
    """Raised when configuration is invalid or missing."""
    pass
```

### NetworkError
```python
class NetworkError(Exception):
    """Raised when network operations fail."""
    pass
```

## 📝 Functions

### Logging Setup

#### setup_logging()
```python
def setup_logging(
    name: str,
    level: str = "INFO",
    log_file: Optional[str] = None
) -> logging.Logger:
    """Configure logging with file and console handlers."""
```

Parameters:
- `name`: Logger name
- `level`: Logging level
- `log_file`: Optional log file path

### Input Validation

#### validate_input()
```python
def validate_input(
    text: str,
    min_length: int = 1,
    max_length: int = 100,
    pattern: str = r'^[\w\s\-\.@!()]+$'
) -> str:
    """Validate and sanitize user input."""
```

Parameters:
- `text`: Input text
- `min_length`: Minimum length
- `max_length`: Maximum length
- `pattern`: Regex pattern

#### validate_ip_address()
```python
def validate_ip_address(ip: str) -> bool:
    """Validate IPv4 or IPv6 address format."""
```

#### validate_color()
```python
def validate_color(color: str) -> bool:
    """Validate hex color code format."""
```

### Configuration Management

#### load_config()
```python
def load_config(path: Union[str, Path]) -> Dict[str, Any]:
    """Load configuration from JSON file."""
```

### Performance Monitoring

#### log_execution_time()
```python
def log_execution_time(logger: logging.Logger):
    """Decorator to log function execution time."""
```

## ⚙️ Configuration

### Error Messages
```python
ERROR_MESSAGES = {
    'invalid_input': 'Input contains invalid characters: {details}',
    'invalid_length': 'Input length must be between {min_len} and {max_len}',
    'invalid_ip': 'Invalid IP address format: {ip}',
    'invalid_url': 'Invalid URL format: {url}',
    'invalid_color': 'Invalid color format: {color}',
    'config_not_found': 'Configuration file not found: {path}',
    'network_unreachable': 'Network is unreachable: {details}'
}
```

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
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default"
        },
        "file": {
            "class": "logging.FileHandler",
            "formatter": "default",
            "filename": "/var/log/raspi_screen/utils.log"
        }
    },
    "root": {
        "level": "INFO",
        "handlers": ["console", "file"]
    }
}
```

## 🔒 Security Features

### Input Validation Rules
- Strict character whitelisting
- Length restrictions
- Pattern matching
- HTML escaping
- Control character removal

### File Operations
- Path validation
- Permission checking
- Safe file handling
- Atomic operations

### Network Validation
- IPv4/IPv6 support
- URL format checking
- Network reachability tests
- Timeout handling

## 📊 Performance

### Optimization Techniques
- Regex compilation
- Efficient string operations
- Cached properties
- Lazy loading
- Resource cleanup

### Monitoring
- Function execution timing
- Resource usage tracking
- Error rate monitoring
- Performance logging

## 📝 Usage Examples

### Input Validation
```python
try:
    clean_text = validate_input(
        text="User input",
        min_length=5,
        max_length=50,
        pattern=r'^[\w\s]+$'
    )
except ValidationError as e:
    logger.error(f"Validation failed: {e}")
```

### Configuration Loading
```python
try:
    config = load_config("/path/to/config.json")
except ConfigurationError as e:
    logger.error(f"Config error: {e}")
```

### Performance Monitoring
```python
@log_execution_time(logger)
def long_running_function():
    # Function code here
    pass
```

## 🚀 Future Enhancements
1. Enhanced IPv6 support
2. Additional validation patterns
3. Configuration versioning
4. Performance profiling
5. Memory usage optimization
6. Extended security checks
7. Async support
8. Caching mechanisms

---
*Last updated: 2024-01-24*

Tags: #utils #python #validation #security #logging #configuration #performance 