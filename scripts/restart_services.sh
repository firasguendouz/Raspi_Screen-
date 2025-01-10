#!/bin/bash

# Script to restart network-related services
# Must be run with sudo privileges

# Check if script is run as root
if [[ $EUID -ne 0 ]]; then
    echo "This script must be run as root (sudo)"
    exit 1
fi

# Restart network-related services
echo "Restarting network-related services..."

# Restart dhcpcd service
systemctl restart dhcpcd
if [[ $? -eq 0 ]]; then
    echo "dhcpcd restarted successfully."
else
    echo "Failed to restart dhcpcd."
fi

# Restart wpa_supplicant service
systemctl restart wpa_supplicant
if [[ $? -eq 0 ]]; then
    echo "wpa_supplicant restarted successfully."
else
    echo "Failed to restart wpa_supplicant."
fi

# Restart hostapd service (if running)
systemctl is-active --quiet hostapd && systemctl restart hostapd
if [[ $? -eq 0 ]]; then
    echo "hostapd restarted successfully."
else
    echo "hostapd is not active or failed to restart."
fi

# Restart dnsmasq service (if running)
systemctl is-active --quiet dnsmasq && systemctl restart dnsmasq
if [[ $? -eq 0 ]]; then
    echo "dnsmasq restarted successfully."
else
    echo "dnsmasq is not active or failed to restart."
fi

# Confirm completion
echo "Network-related services restarted."
