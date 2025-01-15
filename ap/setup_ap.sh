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

# Configure static IP for wlan0
log_message "Configuring static IP for wlan0..."
cat <<EOF > /etc/dhcpcd.conf
interface wlan0
static ip_address=192.168.4.1/24
nohook wpa_supplicant
EOF
systemctl restart dhcpcd

if [[ $? -ne 0 ]]; then
    echo "[ERROR] Failed to configure static IP. Exiting."
    exit 1
fi

# Configure hostapd
log_message "Configuring hostapd..."
cat <<EOF > /etc/hostapd/hostapd.conf
interface=wlan0
driver=nl80211
ssid=RaspberryPi_AP
hw_mode=g
channel=7
macaddr_acl=0
auth_algs=1
ignore_broadcast_ssid=0
wpa=2
wpa_passphrase=raspberry
wpa_key_mgmt=WPA-PSK
rsn_pairwise=CCMP
EOF

# Point hostapd to its configuration file
sed -i 's|#DAEMON_CONF=""|DAEMON_CONF="/etc/hostapd/hostapd.conf"|' /etc/default/hostapd

if [[ $? -ne 0 ]]; then
    echo "[ERROR] Failed to configure hostapd. Exiting."
    exit 1
fi

# Configure dnsmasq
log_message "Configuring dnsmasq..."
cat <<EOF > /etc/dnsmasq.conf
interface=wlan0
dhcp-range=192.168.4.2,192.168.4.20,255.255.255.0,24h
EOF

if [[ $? -ne 0 ]]; then
    echo "[ERROR] Failed to configure dnsmasq. Exiting."
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
