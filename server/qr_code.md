# QR Code Generation Module

![Status](https://img.shields.io/badge/status-stable-green)
![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Python](https://img.shields.io/badge/python-3.7+-yellow)
![Coverage](https://img.shields.io/badge/coverage-95%25-brightgreen)

## 🔍 Overview
Advanced QR code generation module for the Raspberry Pi Screen Management Server. Provides styled QR codes with caching support, custom colors, and logo embedding capabilities. Primarily used for WiFi network configuration.

## 🔗 Related Documentation
- [Server Documentation](Server.md)
- [Utilities Module](utils.md)

## ⭐ Features
- Styled QR codes with rounded modules
- Custom color support with hex codes
- Logo embedding with size control
- Efficient caching system with expiration
- Multiple QR code types (WiFi, URL)
- Input validation and error handling

## 📦 Dependencies
- `qrcode[pil]>=7.0`: QR code generation
- `Pillow>=8.0.0`: Image processing
- Custom utilities for validation

## 🛠️ Classes

### QRCodeCache
Manages caching of generated QR codes to improve performance.

```python
cache = QRCodeCache(cache_dir="qr_cache")
cached_path = cache.get(data)
cache.put(data, file_path)
```

#### Methods
- `_ensure_cache_dir()`: Creates cache directory if needed
- `_load_cache_index()`: Loads cache index from file
- `_save_cache_index()`: Saves cache index to file
- `_generate_key(data)`: Generates unique cache key
- `get(data)`: Retrieves cached QR code
- `put(data, file_path)`: Adds QR code to cache
- `_cleanup(key)`: Removes expired cache entries

## 🎨 Functions

### create_styled_qr()
```python
def create_styled_qr(
    data: str,
    color: str = "#000000",
    version: int = 1,
    box_size: int = 10,
    border: int = 4
) -> Image.Image:
    """Create a styled QR code with rounded modules."""
```

Parameters:
- `data`: Content to encode
- `color`: Hex color code
- `version`: QR code version
- `box_size`: Module size in pixels
- `border`: Border width in modules

### add_logo()
```python
def add_logo(
    qr_image: Image.Image,
    logo_path: str = "static/logo.png",
    scale: float = 0.2
) -> Image.Image:
    """Add logo to center of QR code."""
```

Parameters:
- `qr_image`: Base QR code image
- `logo_path`: Path to logo file
- `scale`: Logo size relative to QR code

### generate_wifi_qr()
```python
def generate_wifi_qr(
    ssid: str,
    password: str,
    security: str = "WPA",
    color: str = "#000000",
    add_logo_flag: bool = True,
    cache: Optional[QRCodeCache] = None
) -> str:
    """Generate QR code for WiFi configuration."""
```

Parameters:
- `ssid`: Network name
- `password`: Network password
- `security`: Security type (WPA/WEP/nopass)
- `color`: QR code color
- `add_logo_flag`: Whether to add logo
- `cache`: Optional QR code cache

## ⚙️ Configuration

### Constants
```python
CACHE_DURATION = timedelta(hours=24)
DEFAULT_LOGO_PATH = "static/logo.png"
QR_VERSION = 1
QR_BOX_SIZE = 10
QR_BORDER = 4
DEFAULT_COLOR = "#000000"
```

### Cache Structure
```
qr_cache/
├── index.json    # Cache index
└── {hash}.png    # Cached QR codes
```

### Cache Entry Format
```json
{
    "hash": {
        "created": "2024-01-24T12:00:00",
        "data": {
            "ssid": "MyNetwork",
            "password": "MyPassword",
            "security": "WPA",
            "color": "#000000",
            "add_logo": true
        }
    }
}
```

## ⚠️ Error Handling

### Validation
- SSID format and length
- Security type validation
- Color code format
- Logo file existence
- Cache directory permissions

### Exceptions
- `ValidationError`: Input validation failures
- `ConfigurationError`: Missing or invalid config
- `IOError`: File operations failures

## 🔍 Performance

### Caching Strategy
- SHA-256 hashing for cache keys
- 24-hour cache duration
- Automatic cleanup of expired entries
- Memory-efficient index storage

### Image Optimization
- Optimal QR version selection
- Efficient image processing
- Logo size optimization
- PNG compression

## 📝 Usage Examples

### Basic WiFi QR Code
```python
qr_path = generate_wifi_qr(
    ssid="MyNetwork",
    password="MyPassword"
)
```

### Styled WiFi QR Code
```python
qr_path = generate_wifi_qr(
    ssid="MyNetwork",
    password="MyPassword",
    color="#FF0000",
    add_logo_flag=True
)
```

### Custom QR Code
```python
qr_image = create_styled_qr(
    data="Custom data",
    color="#0000FF",
    version=2
)
qr_with_logo = add_logo(qr_image, scale=0.3)
```

## 🚀 Future Enhancements
1. SVG output support
2. Additional styling options
3. Animated QR codes
4. Custom error patterns
5. QR code validation
6. Multiple logo support
7. Advanced color gradients
8. WebP format support

---
*Last updated: 2024-01-24*

Tags: #qr-code #python #image-processing #caching #wifi #styling #logo 