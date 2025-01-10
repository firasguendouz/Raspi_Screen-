#!/bin/bash

# Script to stop Access Point mode
# Must be run with sudo privileges

# Check if script is run as root
if [[ $EUID -ne 0 ]]; then
    echo "This script must be run as root (sudo)"
    exit 1
fi

# Stop the access point services
echo "Stopping Access Point services..."
systemctl stop hostapd
systemctl stop dnsmasq

# Disable services from starting on boot
echo "Disabling services from starting on boot..."
systemctl disable hostapd
systemctl disable dnsmasq

# Bring down the wlan0 interface
echo "Bringing down the wlan0 interface..."
ip link set wlan0 down

# Restore normal networking configuration
echo "Restoring normal networking configuration..."
sed -i '/interface wlan0/d' /etc/dhcpcd.conf
sed -i '/static ip_address=192.168.4.1/d' /etc/dhcpcd.conf
systemctl restart dhcpcd
systemctl restart networking

# Confirm the Access Point has been stopped
echo "Access Point mode has been stopped and normal networking restored."
