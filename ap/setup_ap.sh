#!/bin/bash
#
# Raspberry Pi Access Point Setup Script
# ====================================
# This script configures a Raspberry Pi as a WiFi access point.
#
# Requirements:
# - Raspberry Pi with WiFi capability
# - hostapd and dnsmasq packages
# - Root privileges
#
# Usage:
#   sudo ./setup_ap.sh [-s SSID] [-p PASSWORD]
#
# Options:
#   -s SSID       Set custom SSID (default: RaspberryPi_AP)
#   -p PASSWORD   Set custom password (default: randomly generated)
#
# Examples:
#   sudo ./setup_ap.sh                     # Use defaults
#   sudo ./setup_ap.sh -s MyNetwork        # Custom SSID
#   sudo ./setup_ap.sh -s MyNet -p Pass123 # Custom SSID and password

set -e  # Exit on any error

# Global variables and defaults
DEFAULT_SSID="RaspberryPi_AP"
DEFAULT_PASS="raspberry"
MIN_PASS_LENGTH=8
BACKUP_DIR="/tmp/ap_backup"
IPV6_ENABLED=false

# Environment validation
check_environment() {
    # Check for required packages
    for pkg in hostapd dnsmasq; do
        if ! dpkg -s $pkg >/dev/null 2>&1; then
            echo "Error: Required package '$pkg' is not installed"
            echo "Please install it with: apt-get install $pkg"
            exit 1
        fi
    done

    # Check wireless interface
    if ! ip link show wlan0 >/dev/null 2>&1; then
        echo "Error: Wireless interface 'wlan0' not found"
        echo "Available interfaces:"
        ip link show
        exit 1
    fi

    # Check for systemd
    if ! command -v systemctl >/dev/null 2>&1; then
        echo "Error: systemd is required but not found"
        exit 1
    fi
}

generate_password() {
    # Generate 16 char random password with letters, numbers, symbols
    tr -dc 'A-Za-z0-9!#$%&()*+,-./:;<=>?@[\]^_`{|}~' < /dev/urandom | head -c 16
}

# Parse command line arguments
while getopts "s:p:r6" opt; do
    case $opt in
        s) SSID="$OPTARG" ;;
        p) PASSWORD="$OPTARG" ;;
        r) revert_changes; exit 0 ;;
        6) IPV6_ENABLED=true ;;
        *) echo "Usage: $0 [-s SSID] [-p PASSWORD] [-r] [-6]" >&2; exit 1 ;;
    esac
done

# Interactive input if arguments not provided
if [ -z "$SSID" ]; then
    read -p "Enter SSID [$DEFAULT_SSID]: " SSID
    SSID=${SSID:-$DEFAULT_SSID}
fi

if [ -z "$PASSWORD" ]; then
    read -s -p "Enter Password (leave empty for random) [$DEFAULT_PASS]: " PASSWORD
    echo
    if [ -z "$PASSWORD" ]; then
        PASSWORD=$(generate_password)
        echo "Generated random password: $PASSWORD"
        # Store password securely
        echo "$PASSWORD" > /etc/hostapd/ap_password
        chmod 600 /etc/hostapd/ap_password
    else
        PASSWORD=${PASSWORD:-$DEFAULT_PASS}
        if [ "$PASSWORD" = "$DEFAULT_PASS" ]; then
            echo "Warning: Using default password is not recommended!"
        fi
    fi
fi

# Validate password length
if [ ${#PASSWORD} -lt $MIN_PASS_LENGTH; then
    echo "Error: Password must be at least $MIN_PASS_LENGTH characters"
    exit 1
fi

# Error checking function
check_error() {
    if [ $? -ne 0 ]; then
        echo "Error: $1 failed"
        exit 1
    fi
}

check_service_status() {
    local service=$1
    if ! systemctl is-active --quiet $service; then
        echo "Error: $service failed to start"
        systemctl status $service
        exit 1
    fi
    if ! systemctl is-enabled --quiet $service; then
        echo "Error: $service is not enabled"
        exit 1
    fi
}

# Check if script is run as root
if [[ $EUID -ne 0 ]]; then
    echo "This script must be run as root (sudo)"
    exit 1
fi

# Network configuration
setup_networking() {
    # Configure static IP and DHCP
    cat <<EOF > /etc/dhcpcd.conf
    interface=wlan0
    static ip_address=192.168.4.1/24
    nohook wpa_supplicant
EOF
    check_error "configuring network"
    
    systemctl restart dhcpcd
    check_error "restarting network"
}

# Service configuration
configure_services() {
    # Setup hostapd and dnsmasq
    cat <<EOF > /etc/hostapd/hostapd.conf
    interface=wlan0
    driver=nl80211
    ssid=$SSID
    hw_mode=g
    channel=7
    wpa=2
    wpa_passphrase=$PASSWORD
    wpa_key_mgmt=WPA-PSK
    rsn_pairwise=CCMP
EOF
    check_error "configuring hostapd"

    # Configure dnsmasq
    cat <<EOF > /etc/dnsmasq.conf
    interface=wlan0
    dhcp-range=192.168.4.2,192.168.4.20,255.255.255.0,24h
EOF
    check_error "configuring dnsmasq"
}

# Service management
start_services() {
    # Enable and start required services
    systemctl unmask hostapd
    systemctl enable hostapd dnsmasq
    systemctl restart hostapd dnsmasq
    check_service_status hostapd
    check_service_status dnsmasq
}

# Setup verification
verify_setup() {
    # Verify services and network
    echo "Verifying setup..."
    check_service_status hostapd
    check_service_status dnsmasq
    ip addr show wlan0
}

# Cleanup on failure
cleanup() {
    # Restore original state if setup fails
    echo "Cleaning up..."
    if [ $? -ne 0 ]; then
        systemctl stop hostapd dnsmasq
    fi
}

backup_configs() {
    mkdir -p "$BACKUP_DIR"
    cp /etc/dhcpcd.conf "$BACKUP_DIR/" 2>/dev/null || true
    cp /etc/hostapd/hostapd.conf "$BACKUP_DIR/" 2>/dev/null || true
    cp /etc/dnsmasq.conf "$BACKUP_DIR/" 2>/dev/null || true
    check_error "backing up configurations"
}

revert_changes() {
    echo "Reverting changes..."
    
    # Stop services
    systemctl stop hostapd dnsmasq
    
    # Restore original configs if they exist
    if [ -d "$BACKUP_DIR" ]; then
        cp "$BACKUP_DIR"/* /etc/ 2>/dev/null || true
        rm -rf "$BACKUP_DIR"
    fi
    
    # Reset network
    systemctl restart dhcpcd
    
    echo "System restored to original state"
}

configure_ipv6() {
    if [ "$IPV6_ENABLED" = true ]; then
        cat <<EOF >> /etc/dnsmasq.conf
dhcp-range=2001:db8::2,2001:db8::ff,64,24h
enable-ra
EOF
        check_error "configuring IPv6"
    fi
}

# Main execution flow
main() {
    backup_configs
    check_environment
    setup_networking
    configure_services
    [ "$IPV6_ENABLED" = true ] && configure_ipv6
    start_services
    verify_setup
}

trap cleanup EXIT
main "$@"

# Add status summary before final success message
echo "Service Status:"
echo "- hostapd: $(systemctl is-active hostapd)"
echo "- dnsmasq: $(systemctl is-active dnsmasq)"

# Create systemd override directory
mkdir -p /etc/systemd/system/hostapd.service.d/
check_error "creating hostapd override directory"

mkdir -p /etc/systemd/system/dnsmasq.service.d/
check_error "creating dnsmasq override directory"

# Configure auto-restart for hostapd
cat <<EOF > /etc/systemd/system/hostapd.service.d/override.conf
[Service]
Restart=on-failure
RestartSec=5
StartLimitInterval=200
StartLimitBurst=3
EOF
check_error "writing hostapd override configuration"

# Configure auto-restart for dnsmasq
cat <<EOF > /etc/systemd/system/dnsmasq.service.d/override.conf
[Service]
Restart=on-failure
RestartSec=5
StartLimitInterval=200
StartLimitBurst=3
EOF
check_error "writing dnsmasq override configuration"

# Reload systemd daemon
systemctl daemon-reload
check_error "reloading systemd daemon"

echo "✓ Access Point setup completed successfully!"
echo "SSID: $SSID"
if [ "$PASSWORD" = "$DEFAULT_PASS" ]; then
    echo "Password: $PASSWORD (Warning: default password in use!)"
else
    echo "Password: $PASSWORD"
fi
if [ -f /etc/hostapd/ap_password ]; then
    echo "Password stored in /etc/hostapd/ap_password"
fi
