#!/bin/bash

# Script to initialize Access Point mode
# Must be run with sudo privileges

# Check if script is run as root
if [[ $EUID -ne 0 ]]; then
    echo "This script must be run as root (sudo)" 
    exit 1
fi

# Install required packages
apt-get update
apt-get install -y hostapd dnsmasq

# Stop services initially
systemctl stop hostapd
systemctl stop dnsmasq

# Configure static IP for wlan0
cat ./config/dhcpcd.conf > /etc/dhcpcd.conf

# Configure hostapd
cat ./config/hostapd.conf > /etc/hostapd/hostapd.conf

# Configure dnsmasq
cat ./config/dnsmasq.conf > /etc/dnsmasq.conf

# Enable hostapd
sed -i 's/#DAEMON_CONF=""/DAEMON_CONF="\/etc\/hostapd\/hostapd.conf"/' /etc/default/hostapd

# Enable IP forwarding
echo "net.ipv4.ip_forward=1" > /etc/sysctl.d/routed-ap.conf

# Start services
systemctl unmask hostapd
systemctl enable hostapd
systemctl enable dnsmasq
systemctl restart dhcpcd
systemctl restart hostapd
systemctl restart dnsmasq

echo "Access Point setup completed!"
echo "SSID: RaspberryAP"
echo "Password: raspberry"
