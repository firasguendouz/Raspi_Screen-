#!/bin/bash

# Enhanced Script to initialize and stabilize Access Point mode
# Must be run with sudo privileges

# Check if script is run as root
if [[ $EUID -ne 0 ]]; then
    echo "[ERROR] This script must be run as root (sudo). Exiting."
    exit 1
fi

# Helper function for logging
log_message() {
    echo "[INFO] $1"
}

# Stop interfering services
log_message "Stopping interfering services..."
systemctl stop wpa_supplicant
systemctl stop hostapd
systemctl stop dnsmasq

# Copy configuration files
log_message "Copying configuration files..."
cp ../config/dhcpcd.conf /etc/dhcpcd.conf
cp ../config/hostapd.conf /etc/hostapd/hostapd.conf
cp ../config/dnsmasq.conf /etc/dnsmasq.conf

if [[ $? -ne 0 ]]; then
    echo "[ERROR] Failed to copy configuration files. Exiting."
    exit 1
fi

# Point hostapd to its configuration file
sed -i 's|#DAEMON_CONF=""|DAEMON_CONF="/etc/hostapd/hostapd.conf"|' /etc/default/hostapd

if [[ $? -ne 0 ]]; then
    echo "[ERROR] Failed to configure hostapd. Exiting."
    exit 1
fi

# Enable IP forwarding
log_message "Enabling IP forwarding..."
echo "net.ipv4.ip_forward=1" > /etc/sysctl.d/routed-ap.conf
sysctl -p /etc/sysctl.d/routed-ap.conf

if [[ $? -ne 0 ]]; then
    echo "[ERROR] Failed to enable IP forwarding. Exiting."
    exit 1
fi

# Configure firewall rules
log_message "Configuring firewall rules..."
iptables -A INPUT -p tcp --dport 80 -j ACCEPT

if [[ $? -ne 0 ]]; then
    echo "[ERROR] Failed to configure firewall rules. Exiting."
    exit 1
fi

# Restart services
log_message "Restarting services..."
systemctl unmask hostapd
systemctl enable hostapd
systemctl enable dnsmasq
systemctl restart dhcpcd
systemctl restart hostapd
systemctl restart dnsmasq

if [[ $? -eq 0 ]]; then
    log_message "Access Point setup completed successfully!"
    log_message "SSID: RaspberryPi_AP"
    log_message "Password: raspberry"
else
    echo "[ERROR] Failed to restart services. Please check configurations."
    exit 1
fi
