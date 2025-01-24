#!/bin/bash

# Script to stop Access Point mode and restore Wi-Fi mode
# Must be run with sudo privileges

# Test mode flag
TEST_MODE=0
if [[ "$1" == "--test-mode" ]]; then
    TEST_MODE=1
fi

# Check if script is run as root
if [[ $EUID -ne 0 ]]; then
    echo "This script must be run as root (sudo)"
    exit 1
fi

# Stop the Access Point services
echo "Stopping Access Point services..."
if [[ $TEST_MODE -eq 0 ]]; then
    systemctl stop hostapd
    systemctl stop dnsmasq

    # Disable services from starting on boot
    echo "Disabling hostapd and dnsmasq services from starting on boot..."
    systemctl disable hostapd
    systemctl disable dnsmasq

    # Bring down the wlan0 interface
    echo "Bringing down the wlan0 interface..."
    ip link set wlan0 down
fi

# Backup and restore configuration files
echo "Restoring default configurations..."
if [[ -f /etc/dhcpcd.conf ]]; then
    mv /etc/dhcpcd.conf /etc/dhcpcd.conf.ap.bak
fi

if [[ -f /etc/dnsmasq.conf ]]; then
    mv /etc/dnsmasq.conf /etc/dnsmasq.conf.ap.bak
fi

if [[ -f /etc/hostapd/hostapd.conf ]]; then
    mv /etc/hostapd/hostapd.conf /etc/hostapd/hostapd.conf.ap.bak
fi

# Create minimal default configurations
echo "" > /etc/dnsmasq.conf
cp ../config/wpa_supplicant.conf /etc/wpa_supplicant/wpa_supplicant.conf

# Restart necessary services
echo "Restarting necessary services..."
if [[ $TEST_MODE -eq 0 ]]; then
    systemctl restart dhcpcd
    systemctl restart networking
    systemctl restart wpa_supplicant

    # Bring up the wlan0 interface
    echo "Bringing up the wlan0 interface..."
    ip link set wlan0 up
fi

# Restore default DNS resolver
echo "Restoring default DNS resolver..."
echo "nameserver 8.8.8.8" > /etc/resolv.conf
echo "nameserver 8.8.4.4" >> /etc/resolv.conf

# Check Wi-Fi interface status
if [[ $TEST_MODE -eq 0 ]]; then
    if iwconfig wlan0 | grep -q "ESSID"; then
        echo "Wi-Fi interface restored successfully. You can now connect to a Wi-Fi network."
    else
        echo "Failed to restore Wi-Fi interface. Please check your configuration."
    fi
fi

# Confirm the Access Point has been stopped
echo "Access Point mode has been stopped and Wi-Fi mode restored."
