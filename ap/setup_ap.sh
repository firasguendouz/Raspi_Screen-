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
cat > /etc/dhcpcd.conf << EOF
interface wlan0
     static ip_address=192.168.4.1/24
     nohook wpa_supplicant
EOF

# Configure hostapd
cat > /etc/hostapd/hostapd.conf << EOF
interface=wlan0
driver=nl80211
ssid=RaspberryAP
hw_mode=g
channel=7
wmm_enabled=0
macaddr_acl=0
auth_algs=1
ignore_broadcast_ssid=0
wpa=2
wpa_passphrase=raspberry
wpa_key_mgmt=WPA-PSK
wpa_pairwise=TKIP
rsn_pairwise=CCMP
EOF

# Configure dnsmasq
cat > /etc/dnsmasq.conf << EOF
interface=wlan0
dhcp-range=192.168.4.2,192.168.4.20,255.255.255.0,24h
EOF

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