#!/bin/bash

# Script to safely stop Access Point mode and restore normal WiFi
# Must be run with sudo privileges

# Source utility functions
source "$(dirname "$0")/utils.sh"

# Configuration
readonly REQUIRED_SERVICES=("hostapd" "dnsmasq")
readonly LOG_FILE="/var/log/ap_stop.log"

# Test mode flag
TEST_MODE=0
if [[ "$1" == "--test-mode" ]]; then
    TEST_MODE=1
    log_info "Running in test mode"
fi

# Validate root privileges
check_root

# Function to stop AP services
stop_ap_services() {
    log_info "Stopping AP services..."
    
    if [[ $TEST_MODE -eq 0 ]]; then
        for service in "${REQUIRED_SERVICES[@]}"; do
            log_debug "Stopping $service..."
            systemctl stop "$service"
            systemctl disable "$service"
            validate_cmd "stop and disable $service" $?
        done
    fi
}

# Function to restore network configuration
restore_network_config() {
    log_info "Restoring network configuration..."
    
    # Restore original configuration files
    if [[ -f /etc/dhcpcd.conf.backup ]]; then
        log_debug "Restoring dhcpcd configuration..."
        copy_config "/etc/dhcpcd.conf.backup" "/etc/dhcpcd.conf"
    else
        log_warn "No dhcpcd backup configuration found"
    fi
    
    # Disable IP forwarding
    log_debug "Disabling IP forwarding..."
    echo "net.ipv4.ip_forward=0" > /etc/sysctl.d/routed-ap.conf
    if [[ $TEST_MODE -eq 0 ]]; then
        sysctl -p /etc/sysctl.d/routed-ap.conf
        validate_cmd "disable IP forwarding" $?
    fi
    
    # Remove firewall rules
    if [[ $TEST_MODE -eq 0 ]]; then
        log_debug "Removing firewall rules..."
        iptables -D INPUT -p tcp --dport 80 -j ACCEPT
        validate_cmd "remove firewall rules" $?
    fi
}

# Function to start WiFi client mode
start_wifi_client() {
    log_info "Starting WiFi client mode..."
    
    if [[ $TEST_MODE -eq 0 ]]; then
        # Start wpa_supplicant
        log_debug "Starting wpa_supplicant..."
        systemctl start wpa_supplicant
        validate_cmd "start wpa_supplicant" $?
        
        # Restart networking
        log_debug "Restarting networking services..."
        systemctl restart dhcpcd
        validate_cmd "restart networking" $?
    fi
}

# Main execution
main() {
    log_info "Starting AP shutdown procedure..."
    
    # Execute shutdown steps
    stop_ap_services
    restore_network_config
    start_wifi_client
    
    log_info "Access Point shutdown completed successfully"
    log_info "System restored to WiFi client mode"
    return 0
}

# Execute main function
main
exit $?
