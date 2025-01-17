#!/bin/bash

# Script to stop Access Point mode and restore Wi-Fi mode
# Must be run with sudo privileges

# Check if script is run as root
if [[ $EUID -ne 0 ]]; then
    echo "This script must be run as root (sudo)"
    exit 1
fi

# Stop the Access Point services
echo "Stopping Access Point services..."
systemctl stop hostapd
systemctl stop dnsmasq

# Disable services from starting on boot
echo "Disabling hostapd and dnsmasq services from starting on boot..."
systemctl disable hostapd
systemctl disable dnsmasq

# Bring down the wlan0 interface
echo "Bringing down the wlan0 interface..."
ip link set wlan0 down


# Restore /etc/dhcpcd.conf
echo "Restoring /etc/dhcpcd.conf..."
sed -i '/interface wlan0/d' /etc/dhcpcd.conf
sed -i '/static ip_address=192.168.4.1/d' /etc/dhcpcd.conf
sed -i '/nohook wpa_supplicant/d' /etc/dhcpcd.conf

# Restore /etc/dnsmasq.conf
echo "Restoring /etc/dnsmasq.conf..."
if [[ -f /etc/dnsmasq.conf ]]; then
    mv /etc/dnsmasq.conf /etc/dnsmasq.conf.bak
fi

touch /etc/dnsmasq.conf

# Restart necessary services
echo "Restarting necessary services..."
systemctl restart dhcpcd
systemctl restart networking
systemctl restart wpa_supplicant

# Bring up the wlan0 interface
echo "Bringing up the wlan0 interface..."
ip link set wlan0 up

# Restore default DNS resolver
echo "Restoring default DNS resolver..."
echo "nameserver 8.8.8.8" > /etc/resolv.conf
echo "nameserver 8.8.4.4" >> /etc/resolv.conf
# Check Wi-Fi interface status
if iwconfig wlan0 | grep -q "ESSID"; then
    echo "Wi-Fi interface restored successfully. You can now connect to a Wi-Fi network."
else
    echo "Failed to restore Wi-Fi interface. Please check your configuration."
fi

# Confirm the Access Point has been stopped
echo "Access Point mode has been stopped and Wi-Fi mode restored."
