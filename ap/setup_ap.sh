#!/bin/bash
#
# Access Point Setup Script
# Initializes and configures a WiFi Access Point on a Raspberry Pi.
#
# This script performs the following operations:
# 1. Stops potentially interfering services
# 2. Configures network settings and IP forwarding
# 3. Sets up hostapd (access point) and dnsmasq (DHCP server)
# 4. Starts and validates all required services
#
# Dependencies:
#   - utils.sh (common utility functions)
#   - hostapd (access point daemon)
#   - dnsmasq (DHCP and DNS server)
#   - dhcpcd (DHCP client daemon)
#
# Usage:
#   sudo ./setup_ap.sh [--test-mode]

# Source utility functions
source "$(dirname "$0")/utils.sh"

# Check if running as root
check_root

# Initialize environment
init_environment "$@"

# Configuration
readonly LOG_FILE="/var/log/ap_setup.log"

# Test mode flag
TEST_MODE=0
if [[ "$1" == "--test-mode" ]]; then
    TEST_MODE=1
    log_info "Running in test mode"
fi

# Stop interfering services
log_info "Stopping interfering services..."
stop_service "wpa_supplicant"
stop_service "hostapd"
stop_service "dnsmasq"

# Configure static IP for wlan0
log_info "Configuring static IP for wlan0..."
cat > /etc/dhcpcd.conf << EOF
interface wlan0
static ip_address=192.168.4.1/24
nohook wpa_supplicant
EOF

# Configure hostapd
log_info "Configuring hostapd..."
mkdir -p /etc/hostapd
cat > /etc/hostapd/hostapd.conf << EOF
interface=wlan0
driver=nl80211
ssid=RaspberryPi_AP
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
country_code=GB
EOF

# Configure hostapd daemon
log_debug "Configuring hostapd daemon..."
echo 'DAEMON_CONF="/etc/hostapd/hostapd.conf"' > /etc/default/hostapd

# Configure dnsmasq
log_info "Configuring dnsmasq..."
cat > /etc/dnsmasq.conf << EOF
interface=wlan0
dhcp-range=192.168.4.2,192.168.4.20,255.255.255.0,24h
domain=wlan
address=/gw.wlan/192.168.4.1
EOF

# Enable IP forwarding
log_info "Configuring network settings..."
echo 1 > /proc/sys/net/ipv4/ip_forward
echo "net.ipv4.ip_forward=1" > /etc/sysctl.d/routed-ap.conf
sysctl -p /etc/sysctl.d/routed-ap.conf

# Configure firewall rules
log_debug "Configuring firewall rules..."
iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
iptables -A FORWARD -i eth0 -o wlan0 -m state --state RELATED,ESTABLISHED -j ACCEPT
iptables -A FORWARD -i wlan0 -o eth0 -j ACCEPT

# Start AP services
log_info "Starting AP services..."

# Unmask and enable hostapd
systemctl unmask hostapd
systemctl enable hostapd

# Start services with proper error handling
if ! systemctl restart dhcpcd; then
    log_error "Failed to restart dhcpcd"
    exit 1
fi

if ! systemctl restart dnsmasq; then
    log_error "Failed to restart dnsmasq"
    exit 1
fi

# Start hostapd with detailed error checking
log_debug "Starting hostapd..."
if ! systemctl restart hostapd; then
    log_error "Failed to start hostapd"
    journalctl -xe --no-pager -u hostapd
    exit 1
fi

# Verify services are running
if systemctl is-active --quiet hostapd && \
   systemctl is-active --quiet dnsmasq && \
   systemctl is-active --quiet dhcpcd; then
    log_info "Access Point setup completed successfully"
    log_info "SSID: RaspberryPi_AP"
    log_info "Password: raspberry"
    exit 0
else
    log_error "One or more services failed to start"
    exit 1
fi
