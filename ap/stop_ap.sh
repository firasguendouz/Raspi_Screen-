#!/bin/bash
#
# Access Point Termination Script
# Safely stops the AP while preserving existing WiFi connections.
#
# This script performs the following operations:
# 1. Stops and disables AP services
# 2. Cleans up AP-specific configurations
#
# Dependencies:
#   - utils.sh (common utility functions)
#   - systemd (for service management)
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

# Function to clean up AP configuration
# Removes AP-specific configurations without affecting client mode
# Returns:
#   0 on success, 1 on failure
cleanup_ap_config() {
    log_info "Cleaning up AP configuration..."
    
    # Remove AP-specific firewall rules
    if [[ "$AP_ENV" != "$ENV_TEST" ]]; then
        log_debug "Removing firewall rules..."
        # Suppress errors if rule doesn't exist
        iptables -D INPUT -p tcp --dport 80 -j ACCEPT 2>/dev/null || true
        log_debug "Firewall rules cleaned"
    fi
    
    # Disable IP forwarding
    log_debug "Disabling IP forwarding..."
    echo "net.ipv4.ip_forward=0" > /etc/sysctl.d/routed-ap.conf
    if [[ "$AP_ENV" != "$ENV_TEST" ]]; then
        sysctl -p /etc/sysctl.d/routed-ap.conf
        validate_cmd "disable IP forwarding" $?
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
    stop_ap_services || exit 1
    cleanup_ap_config || exit 1
    
    log_info "Access Point shutdown completed successfully"
    return 0
}

# Execute main function and exit with its status
main
exit $?
