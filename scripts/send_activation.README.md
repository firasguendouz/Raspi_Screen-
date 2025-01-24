# send_activation.py

## Overview
Device Activation and Metrics Manager for Raspberry Pi Screen that handles device registration, system metrics collection, and health monitoring.

## Features
- Device registration and activation
- System metrics collection
- Network health monitoring
- Automatic retry mechanism
- Detailed logging and reporting

## Dependencies
- `utils.py`: Common utility functions
- `requests`: HTTP client library
- `psutil`: System metrics collection
- `python-dotenv`: Environment configuration

## Installation
```bash
pip install -r requirements.txt
```

## Usage
```bash
# Activate device with default configuration
python send_activation.py

# Use specific configuration profile
python send_activation.py --config custom_profile

# Override device ID
python send_activation.py --device-id "custom-id-123"

# Custom retry attempts
python send_activation.py --retry 5
```

## Configuration

### Environment Variables
- `API_KEY`: Authentication key for API
- `API_URL`: Server endpoint URL
- `LOG_LEVEL`: Logging verbosity
- `METRICS_INTERVAL`: Metrics collection interval

### JSON Configuration (scripts.json)
```json
{
    "activation": {
        "api_url": "http://localhost:5001/api/metrics",
        "api_key": "${API_KEY}",
        "retry_attempts": 3,
        "timeout": 30
    }
}
```

## Metrics Collected
- CPU usage and temperature
- Memory utilization
- Disk usage
- Network information
  - Interface status
  - IP addresses
  - MAC addresses
- System uptime
- Network traffic statistics

## Error Handling
The script implements several error handling mechanisms:
1. API connection retry
2. Exponential backoff
3. Configuration validation
4. Network error recovery
5. Detailed error reporting

## Logging
Logs are written to `/var/log/raspi_screen/send_activation.log` with the following levels:
- `ERROR`: Activation and API failures
- `WARNING`: Metric collection issues
- `INFO`: Activation status and metrics sending
- `DEBUG`: Detailed operation information

## Exit Codes
- `0`: Successful activation/metrics sending
- `1`: Configuration or activation error

## API Usage
```python
from send_activation import activate_device, collect_metrics

# Collect and send metrics
metrics = collect_metrics()
activate_device(config, device_id="device-123", retry_count=3)
```

## Functions

### `get_device_id() -> str`
Generates or retrieves persistent device identifier.

### `get_network_info() -> Dict[str, Any]`
Collects detailed network interface information.

### `collect_metrics() -> Dict[str, Any]`
Gathers system metrics and status information.

### `send_metrics(url: str, api_key: str, device_id: str, metrics: Dict[str, Any], timeout: int = 30) -> None`
Sends collected metrics to the server.

### `activate_device(config: Dict[str, Any], device_id: str, retry_count: int = 3) -> None`
Handles device activation and initial metrics submission.

## Device Identification
- Uses UUID for unique device identification
- Persists device ID in `.device_id` file
- Supports custom device ID override

## See Also
- `stream_url.py`: URL streaming management
- `connect_wifi.py`: WiFi connection management
- `utils.py`: Shared utilities 