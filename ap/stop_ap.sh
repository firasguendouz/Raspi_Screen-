#!/bin/bash
#
# Access Point Termination Script
# Safely stops the AP and restores normal WiFi client mode.
#
# This script performs the following operations:
# 1. Stops and disables AP services
# 2. Restores original network configuration
# 3. Enables and starts WiFi client mode
# 4. Verifies network connectivity
#
# Dependencies:
#   - utils.sh (common utility functions)
#   - systemd (for service management)
#   - wpa_supplicant (for WiFi client mode)
#
# Usage:
#   sudo ./stop_ap.sh [--test-mode]

# Source common utility functions
# shellcheck source=./utils.sh
source "$(dirname "$0")/utils.sh"

# Initialize environment with command line arguments
init_environment "$@"

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
# Stops and disables all AP-related services
# Returns:
#   0 on success, 1 on failure
stop_ap_services() {
    log_info "Stopping AP services..."
    
    if [[ "$AP_ENV" != "$ENV_TEST" ]]; then
        # Stop services in reverse dependency order
        for service in "${REQUIRED_SERVICES[@]}"; do
            stop_service "$service"
            disable_service "$service"
        done
    fi
    return 0
}

# Function to restore network configuration
# Restores original network settings and removes AP configurations
# Returns:
#   0 on success, 1 on failure
restore_network_config() {
    log_info "Restoring network configuration..."
    
    # Restore original configuration files
    restore_config_files || return 1
    
    # Disable IP forwarding for normal client mode
    log_debug "Disabling IP forwarding..."
    echo "net.ipv4.ip_forward=0" > /etc/sysctl.d/routed-ap.conf
    if [[ "$AP_ENV" != "$ENV_TEST" ]]; then
        sysctl -p /etc/sysctl.d/routed-ap.conf
        validate_cmd "disable IP forwarding" $?
    fi
    
    # Remove AP-specific firewall rules
    if [[ "$AP_ENV" != "$ENV_TEST" ]]; then
        log_debug "Removing firewall rules..."
        # Suppress errors if rule doesn't exist
        iptables -D INPUT -p tcp --dport 80 -j ACCEPT 2>/dev/null || true
        log_debug "Firewall rules cleaned"
    fi
}

# Function to start WiFi client mode
# Configures and enables normal WiFi functionality
# Returns:
#   0 on success, 1 on failure
start_wifi_client() {
    log_info "Starting WiFi client mode..."
    
    if [[ "$AP_ENV" != "$ENV_TEST" ]]; then
        # Verify and restore wpa_supplicant configuration
        if [[ ! -f "/etc/wpa_supplicant/wpa_supplicant.conf" ]]; then
            log_warn "No wpa_supplicant configuration found"
            copy_config "$CONFIG_DIR/wpa_supplicant.conf" "/etc/wpa_supplicant/wpa_supplicant.conf"
        fi
        
        # Start WiFi client services
        log_debug "Starting wpa_supplicant..."
        start_service "wpa_supplicant"
        
        # Restart networking to apply changes
        log_debug "Restarting networking services..."
        restart_service "dhcpcd"
        
        # Verify wireless interface is operational
        if ! validate_interface "$AP_INTERFACE"; then
            log_error "Failed to bring up wireless interface"
            return 1
        fi
    fi
    return 0
}

# Function to verify network status
# Ensures network is properly configured and operational
# Returns:
#   0 on success, 1 on failure
verify_network_status() {
    log_info "Verifying network status..."
    
    if [[ "$AP_ENV" != "$ENV_TEST" ]]; then
        # Check if interface is in UP state
        if ! ip link show "$AP_INTERFACE" | grep -q "UP"; then
            log_error "Interface $AP_INTERFACE is not up"
            return 1
        fi
        
        # Wait for IP address assignment
        # This may take time depending on network conditions
        local timeout=30
        local counter=0
        while ! ip addr show "$AP_INTERFACE" | grep -q "inet "; do
            sleep 1
            ((counter++))
            if [[ $counter -ge $timeout ]]; then
                log_error "Timeout waiting for IP address"
                return 1
            fi
        done
        
        log_info "Network interface configured successfully"
    fi
    return 0
}

# Main execution function
# Orchestrates the AP shutdown process
# Returns:
#   0 on success, 1 on failure
main() {
    log_info "Starting AP shutdown procedure..."
    log_info "Environment: $AP_ENV"
    log_info "Interface: $AP_INTERFACE"
    
    # Execute shutdown steps in sequence
    # Each step must succeed before proceeding
    stop_ap_services || exit 1
    restore_network_config || exit 1
    start_wifi_client || exit 1
    verify_network_status || exit 1
    
    log_info "Access Point shutdown completed successfully"
    log_info "System restored to WiFi client mode"
    return 0
}

# Execute main function and exit with its status
main
exit $?
