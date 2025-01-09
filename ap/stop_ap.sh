#!/bin/bash

# Stop the access point services
sudo systemctl stop hostapd
sudo systemctl stop dnsmasq

# Disable services from starting on boot
sudo systemctl disable hostapd
sudo systemctl disable dnsmasq

# Stop the access point interface
sudo ip link set wlan0 down

# Restore normal networking
sudo systemctl restart dhcpcd
sudo systemctl restart networking

echo "Access Point mode has been stopped"