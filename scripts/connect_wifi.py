#!/usr/bin/env python3
"""
WiFi Connection Manager for Raspberry Pi Screen

This script manages WiFi connections on the Raspberry Pi, including:
- Connecting to specified WiFi networks
- Managing network configurations
- Handling connection retries and failures
- Backing up and restoring network settings
"""

import os
import sys
import time
import argparse
import subprocess
from typing import Optional, Tuple

from utils import (
    setup_logging,
    load_config,
    backup_file,
    restore_file,
    validate_wifi_credentials,
    ConfigurationError
)

# Initialize logging
logger = setup_logging('connect_wifi')

class WiFiConnectionError(Exception):
    """Exception raised for WiFi connection failures."""
    pass

def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Connect to a WiFi network')
    parser.add_argument('--ssid', help='WiFi network name')
    parser.add_argument('--password', help='WiFi password')
    parser.add_argument('--country', help='WiFi country code')
    parser.add_argument('--config', help='Use saved configuration')
    parser.add_argument('--timeout', type=int, default=30,
                       help='Connection timeout in seconds')
    return parser.parse_args()

def load_wifi_config(config_name: str) -> Tuple[str, str, str]:
    """
    Load WiFi configuration from config file.
    
    Args:
        config_name: Name of the configuration to load
        
    Returns:
        Tuple of (ssid, password, country)
        
    Raises:
        ConfigurationError: If configuration is invalid
    """
    try:
        config = load_config('wifi_networks')
        network = config.get(config_name)
        if not network:
            raise ConfigurationError(f"Network '{config_name}' not found in configuration")
        
        return (
            network.get('ssid', ''),
            network.get('password', ''),
            network.get('country', 'US')
        )
    except Exception as e:
        raise ConfigurationError(f"Failed to load WiFi configuration: {str(e)}")

def backup_network_config() -> None:
    """Backup network configuration files."""
    try:
        logger.info("Backing up network configuration files")
        backup_file('/etc/wpa_supplicant/wpa_supplicant.conf')
        backup_file('/etc/dhcpcd.conf')
    except IOError as e:
        logger.error(f"Failed to backup network configuration: {str(e)}")
        raise

def restore_network_config() -> None:
    """Restore network configuration files from backup."""
    try:
        logger.info("Restoring network configuration files")
        restore_file('/etc/wpa_supplicant/wpa_supplicant.conf.backup',
                    '/etc/wpa_supplicant/wpa_supplicant.conf')
        restore_file('/etc/dhcpcd.conf.backup',
                    '/etc/dhcpcd.conf')
    except IOError as e:
        logger.error(f"Failed to restore network configuration: {str(e)}")
        raise

def configure_wifi(ssid: str, password: str, country: str) -> None:
    """
    Configure WiFi settings.
    
    Args:
        ssid: Network name
        password: Network password
        country: Country code
        
    Raises:
        ConfigurationError: If configuration fails
    """
    try:
        # Validate credentials
        if not validate_wifi_credentials(ssid, password):
            raise ConfigurationError("Invalid WiFi credentials")
            
        # Create wpa_supplicant configuration
        config = [
            'ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev',
            'update_config=1',
            f'country={country}',
            'network={',
            f'    ssid="{ssid}"',
            '    scan_ssid=1',
            f'    psk="{password}"' if password else '    key_mgmt=NONE',
            '    key_mgmt=WPA-PSK',
            '}'
        ]
        
        # Write configuration
        with open('/etc/wpa_supplicant/wpa_supplicant.conf', 'w') as f:
            f.write('\n'.join(config))
            
        logger.info("WiFi configuration updated successfully")
    except Exception as e:
        raise ConfigurationError(f"Failed to configure WiFi: {str(e)}")

def connect_with_retry(interface: str, timeout: int) -> None:
    """
    Attempt to connect to WiFi with retry mechanism.
    
    Args:
        interface: Network interface name
        timeout: Connection timeout in seconds
        
    Raises:
        WiFiConnectionError: If connection fails after retries
    """
    logger.info(f"Attempting to connect to WiFi on {interface}")
    
    # Restart networking services
    try:
        subprocess.run(['wpa_cli', '-i', interface, 'reconfigure'],
                      check=True, capture_output=True)
        subprocess.run(['systemctl', 'restart', 'dhcpcd'],
                      check=True, capture_output=True)
    except subprocess.CalledProcessError as e:
        raise WiFiConnectionError(f"Failed to restart networking services: {str(e)}")
    
    # Wait for connection
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            result = subprocess.run(['iwgetid', interface],
                                  capture_output=True, text=True)
            if result.returncode == 0:
                logger.info("Successfully connected to WiFi")
                return
        except subprocess.CalledProcessError:
            pass
        
        time.sleep(1)
    
    raise WiFiConnectionError(f"Failed to connect within {timeout} seconds")

def main() -> None:
    """Main function."""
    try:
        # Parse arguments
        args = parse_arguments()
        
        # Load configuration if specified
        if args.config:
            ssid, password, country = load_wifi_config(args.config)
        else:
            ssid = args.ssid
            password = args.password
            country = args.country or os.getenv('WIFI_COUNTRY', 'US')
        
        if not ssid:
            raise ConfigurationError("SSID is required")
            
        # Backup existing configuration
        backup_network_config()
        
        try:
            # Configure and connect
            configure_wifi(ssid, password, country)
            connect_with_retry('wlan0', args.timeout)
        except Exception as e:
            logger.error(f"Connection failed: {str(e)}")
            restore_network_config()
            raise
            
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()
