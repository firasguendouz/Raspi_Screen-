# Utilities Module

![Status](https://img.shields.io/badge/status-stable-green)
![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Python](https://img.shields.io/badge/python-3.7+-yellow)
![Coverage](https://img.shields.io/badge/coverage-98%25-brightgreen)

## 🔍 Overview
Collection of utility functions for input validation, sanitization, and data formatting used throughout the Raspberry Pi Screen Management Server.

## 🔗 Related Documentation
- [Server Documentation](Server.md)
- [QR Code Module](qr_code.md)

## ⭐ Features
- Input sanitization and validation
- Network-related utilities
- File handling functions
- Data formatting helpers

## 🛠️ Functions

### 🔒 Input Sanitization

#### sanitize_input(text: str) -> str
Sanitizes user input by removing dangerous characters and HTML escaping.

```python
clean_text = sanitize_input("<script>alert('test')</script>")
# Result: "alerttest"
```

Parameters:
- `text`: Input text to sanitize

Returns:
- Sanitized text string

### 📡 Network Validation

#### validate_ssid(ssid: str) -> bool
Validates WiFi SSID format.

```python
is_valid = validate_ssid("My Network")
# Result: True
```

Parameters:
- `ssid`: Network SSID to validate

Returns:
- True if SSID is valid, False otherwise

#### validate_password(password: str) -> bool
Validates WiFi password format.

```python
is_valid = validate_password("MySecurePass123")
# Result: True
```

Parameters:
- `password`: Network password to validate

Returns:
- True if password is valid, False otherwise

#### validate_ip_address(ip: str) -> bool
Validates IPv4 address format.

```python
is_valid = validate_ip_address("192.168.1.1")
# Result: True
```

Parameters:
- `ip`: IP address to validate

Returns:
- True if IP is valid, False otherwise

### 📊 Data Parsing

#### parse_signal_strength(quality: str) -> Optional[int]
Parses WiFi signal strength from iwlist output.

```python
strength = parse_signal_strength("70/100")
# Result: 70
```

Parameters:
- `quality`: Signal quality string from iwlist

Returns:
- Signal strength as percentage or None if parsing fails

#### parse_mac_address(mac: str) -> Optional[str]
Validates and formats MAC address.

```python
formatted_mac = parse_mac_address("00:11:22:33:44:55")
# Result: "00:11:22:33:44:55"
```

Parameters:
- `mac`: MAC address string

Returns:
- Formatted MAC address or None if invalid

### 📝 Data Formatting

#### format_bytes(size: int) -> str
Formats byte size to human readable string.

```python
readable_size = format_bytes(1024 * 1024)
# Result: "1.0 MB"
```

Parameters:
- `size`: Size in bytes

Returns:
- Formatted string (e.g., "1.5 MB")

### 🌐 URL Handling

#### is_valid_url(url: str) -> bool
Validates URL format.

```python
is_valid = is_valid_url("https://example.com")
# Result: True
```

Parameters:
- `url`: URL to validate

Returns:
- True if URL is valid, False otherwise

### 📂 File Operations

#### generate_safe_filename(filename: str) -> str
Generates a safe filename from user input.

```python
safe_name = generate_safe_filename("my:file?.txt")
# Result: "myfile.txt"
```

Parameters:
- `filename`: Original filename

Returns:
- Safe filename string

## ⚙️ Input Validation Rules

### SSID Validation
- Length: 1-32 characters
- Allowed characters: alphanumeric, spaces, .-@!()

### Password Validation
- Length: 8-63 characters for WPA
- Empty allowed for open networks
- Allowed characters: alphanumeric, special characters

### URL Validation
- Must start with http:// or https://
- Valid domain or IP address
- Optional port number
- Optional path

## 👌 Best Practices

1. **Input Handling**
   - Always sanitize user input
   - Validate before processing
   - Handle empty/null values

2. **Error Handling**
   - Use Optional types for nullable returns
   - Catch and log exceptions
   - Provide meaningful error messages

3. **Performance**
   - Use regex compilation
   - Efficient string operations
   - Proper type hints

## 📝 Usage Examples

### Complete Input Processing
```python
# Sanitize and validate user input
ssid = sanitize_input(raw_ssid)
if not validate_ssid(ssid):
    raise ValueError("Invalid SSID")

# Process network credentials
password = sanitize_input(raw_password)
if not validate_password(password):
    raise ValueError("Invalid password")
```

### Network Information Formatting
```python
# Format network details
signal = parse_signal_strength("65/100")
mac = parse_mac_address("00:11:22:33:44:55")
ip = validate_ip_address("192.168.1.1")

network_info = {
    "signal": signal,
    "mac": mac,
    "ip": ip
}
```

### File Handling
```python
# Generate safe filename and format size
filename = generate_safe_filename("user input.txt")
size = format_bytes(os.path.getsize(filename))
```

## ⚠️ Error Messages

Common validation errors:
```python
ERRORS = {
    "ssid_length": "SSID must be 1-32 characters",
    "ssid_chars": "SSID contains invalid characters",
    "password_length": "Password must be 8-63 characters",
    "password_chars": "Password contains invalid characters",
    "url_format": "Invalid URL format",
    "mac_format": "Invalid MAC address format",
    "ip_format": "Invalid IP address format"
}
```

## 🚀 Future Enhancements

Planned improvements:
1. IPv6 address validation
2. Extended character support for SSIDs
3. Additional file format validations
4. Network protocol validations
5. Enhanced security checks

---
*Last updated: 2024-01-24*

Tags: #utils #python #validation #security #network #formatting #file-handling 