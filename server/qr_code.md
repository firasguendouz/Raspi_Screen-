# QR Code Generation Module

![Status](https://img.shields.io/badge/status-stable-green)
![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Python](https://img.shields.io/badge/python-3.7+-yellow)
![Coverage](https://img.shields.io/badge/coverage-95%25-brightgreen)

## 🔍 Overview
Module for generating styled QR codes with caching support, custom colors, and logo embedding capabilities. Primarily used for WiFi network configuration.

## 🔗 Related Documentation
- [Server Documentation](Server.md)
- [Utilities Module](utils.md)

## ⭐ Features
- Styled QR codes with rounded corners
- Custom color gradients
- Logo embedding
- Caching system with expiration
- Multiple QR code types (WiFi, URL)

## 📦 Classes

### QRCodeCache
Manages caching of generated QR codes to improve performance.

```python
cache = QRCodeCache(cache_dir="qr_cache")
cached_path = cache.get(data)
cache.put(data, file_path)
```

#### Methods
- `_load_cache_index()`: Loads cache index from file
- `_save_cache_index()`: Saves cache index to file
- `_generate_key(data)`: Generates unique cache key
- `get(data)`: Retrieves cached QR code
- `put(data, file_path)`: Adds QR code to cache
- `_cleanup(key)`: Removes expired cache entries

## 🛠️ Functions

### create_styled_qr(data: str, color: str = "#000000") -> Image
Creates a styled QR code with custom colors and rounded modules.

```python
qr_image = create_styled_qr(
    data="Hello World",
    color="#FF0000"
)
```

Parameters:
- `data`: Content to encode
- `color`: Hex color code for QR code

### add_logo(qr_image: Image, scale: float = 0.2) -> Image
Adds logo to center of QR code.

```python
qr_with_logo = add_logo(
    qr_image=base_image,
    scale=0.3
)
```

Parameters:
- `qr_image`: Base QR code image
- `scale`: Logo size relative to QR code

### generate_wifi_qr(ssid: str, password: str, security: str = "WPA", color: str = "#000000", add_logo_flag: bool = True) -> str
Generates QR code for WiFi configuration.

```python
qr_path = generate_wifi_qr(
    ssid="MyNetwork",
    password="MyPassword",
    security="WPA",
    color="#0000FF",
    add_logo_flag=True
)
```

Parameters:
- `ssid`: Network name
- `password`: Network password
- `security`: Security type (WPA/WEP/nopass)
- `color`: QR code color
- `add_logo_flag`: Whether to add logo

Returns:
- Path to generated QR code image

## ⚙️ Configuration

### Constants
```python
CACHE_DIR = "qr_cache"
LOGO_PATH = "static/logo.png"
CACHE_DURATION = timedelta(hours=24)
```

### Dependencies
- `qrcode[pil]>=7.0`: QR code generation
- `Pillow>=8.0.0`: Image processing

## ⚠️ Error Handling

### Validation Errors
- Empty SSID
- Invalid security type
- Invalid color format

### File Operations
- Cache directory creation
- Logo file missing
- Write permission issues

## 💾 Caching System

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
        "data": "WIFI:T:WPA;S:MyNetwork;P:MyPassword;;"
    }
}
```

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

### URL QR Code
```python
qr_path = generate_url_qr(
    url="https://example.com",
    output_file="url_qr.png"
)
```

## 👌 Best Practices

1. **Cache Management**
   - Regular cache cleanup
   - Appropriate cache duration
   - Error handling for cache operations

2. **Image Generation**
   - Proper error correction level
   - Optimal image size
   - Logo scaling considerations

3. **Security**
   - Input validation (see [Utils Module](utils.md))
   - Safe file handling
   - Error logging

## 🔧 Troubleshooting

Common issues and solutions:

1. **QR Code Not Readable**
   - Increase error correction level
   - Reduce logo size
   - Check color contrast

2. **Cache Issues**
   - Clear cache directory
   - Check permissions
   - Verify index.json integrity

3. **Logo Problems**
   - Verify logo path
   - Check image format
   - Adjust scale factor

## 🚀 Future Enhancements

Planned improvements:
1. SVG output support
2. Additional styling options
3. Batch generation
4. Custom error patterns
5. Animation support

---
*Last updated: 2024-01-24*

Tags: #qr-code #python #image-processing #caching #wifi #styling #logo 