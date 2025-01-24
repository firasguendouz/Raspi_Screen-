#!/usr/bin/env python3
"""
Activation and Metrics Manager for Raspberry Pi Screen

This script handles device activation and metrics reporting, including:
- Device registration and activation
- System metrics collection and reporting
- Network health monitoring
- Error handling and retry mechanisms
"""

import os
import sys
import time
import json
import uuid
import socket
import argparse
from typing import Dict, Any, Optional
from datetime import datetime

from utils import (
    setup_logging,
    load_config,
    create_http_session,
    get_system_metrics,
    ConfigurationError,
    NetworkError
)

# Initialize logging
logger = setup_logging('send_activation')

class ActivationError(Exception):
    """Exception raised for activation-related failures."""
    pass

def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Send device activation and metrics')
    parser.add_argument('--config', default='activation',
                       help='Configuration profile to use')
    parser.add_argument('--device-id',
                       help='Override device ID from configuration')
    parser.add_argument('--retry', type=int, default=3,
                       help='Number of retry attempts')
    return parser.parse_args()

def load_activation_config(profile: str = 'activation') -> Dict[str, Any]:
    """
    Load activation configuration.
    
    Args:
        profile: Configuration profile name
        
    Returns:
        Dictionary containing activation configuration
        
    Raises:
        ConfigurationError: If configuration is invalid
    """
    try:
        config = load_config(profile)
        required_keys = ['api_url', 'api_key']
        missing_keys = [key for key in required_keys if key not in config]
        if missing_keys:
            raise ConfigurationError(
                f"Missing required configuration keys: {', '.join(missing_keys)}"
            )
        return config
    except Exception as e:
        raise ConfigurationError(f"Failed to load activation configuration: {str(e)}")

def get_device_id() -> str:
    """
    Get or generate a unique device ID.
    
    Returns:
        Device ID string
    """
    id_file = os.path.join(os.path.dirname(__file__), '.device_id')
    try:
        if os.path.exists(id_file):
            with open(id_file, 'r') as f:
                return f.read().strip()
        
        # Generate new device ID
        device_id = str(uuid.uuid4())
        with open(id_file, 'w') as f:
            f.write(device_id)
        return device_id
    except Exception as e:
        logger.warning(f"Failed to persist device ID: {str(e)}")
        return str(uuid.uuid4())

def get_network_info() -> Dict[str, Any]:
    """
    Collect network information.
    
    Returns:
        Dictionary containing network metrics
    """
    info = {
        'hostname': socket.gethostname(),
        'interfaces': {}
    }
    
    try:
        # Get IP addresses for all interfaces
        for interface in os.listdir('/sys/class/net/'):
            try:
                with open(f'/sys/class/net/{interface}/address', 'r') as f:
                    mac = f.read().strip()
                info['interfaces'][interface] = {
                    'mac_address': mac,
                    'ip_address': None
                }
                
                # Get IP address if interface is up
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                ip = socket.inet_ntoa(
                    socket.inet_aton('0.0.0.0') |
                    int.from_bytes(
                        socket.inet_aton(
                            socket.gethostbyname(socket.gethostname())
                        ),
                        'big'
                    ).to_bytes(4, 'big')
                )
                info['interfaces'][interface]['ip_address'] = ip
            except Exception as e:
                logger.debug(f"Failed to get info for interface {interface}: {str(e)}")
    except Exception as e:
        logger.warning(f"Failed to collect network information: {str(e)}")
    
    return info

def collect_metrics() -> Dict[str, Any]:
    """
    Collect system metrics and information.
    
    Returns:
        Dictionary containing system metrics
    """
    metrics = get_system_metrics()
    metrics.update({
        'timestamp': datetime.utcnow().isoformat(),
        'network': get_network_info()
    })
    return metrics

def send_metrics(
    url: str,
    api_key: str,
    device_id: str,
    metrics: Dict[str, Any],
    timeout: int = 30
) -> None:
    """
    Send metrics to the server.
    
    Args:
        url: API endpoint URL
        api_key: API authentication key
        device_id: Device identifier
        metrics: Metrics data to send
        timeout: Request timeout in seconds
        
    Raises:
        NetworkError: If sending metrics fails
    """
    try:
        session = create_http_session()
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
            'User-Agent': f'RaspberryPiScreen/{device_id}'
        }
        
        payload = {
            'device_id': device_id,
            'metrics': metrics
        }
        
        response = session.post(
            url,
            headers=headers,
            json=payload,
            timeout=timeout
        )
        
        if response.status_code != 200:
            raise NetworkError(
                f"Failed to send metrics: {response.status_code} - {response.text}"
            )
            
        logger.info("Successfully sent metrics to server")
        
    except Exception as e:
        raise NetworkError(f"Failed to send metrics: {str(e)}")

def activate_device(
    config: Dict[str, Any],
    device_id: str,
    retry_count: int = 3
) -> None:
    """
    Activate device and send initial metrics.
    
    Args:
        config: Activation configuration
        device_id: Device identifier
        retry_count: Number of retry attempts
        
    Raises:
        ActivationError: If activation fails after all retries
    """
    metrics = collect_metrics()
    
    for attempt in range(retry_count):
        try:
            send_metrics(
                config['api_url'],
                config['api_key'],
                device_id,
                metrics
            )
            return
            
        except Exception as e:
            logger.warning(f"Activation attempt {attempt + 1} failed: {str(e)}")
            if attempt < retry_count - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
            else:
                raise ActivationError(
                    f"Device activation failed after {retry_count} attempts"
                )

def main() -> None:
    """Main function."""
    try:
        # Parse arguments
        args = parse_arguments()
        
        # Load configuration
        config = load_activation_config(args.config)
        
        # Get or use provided device ID
        device_id = args.device_id or get_device_id()
        
        # Activate device and send metrics
        activate_device(config, device_id, args.retry)
        
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()
