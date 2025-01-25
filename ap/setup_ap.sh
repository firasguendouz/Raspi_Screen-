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

# Source common utility functions
SCRIPT_DIR="$(dirname "$(readlink -f "$0")")"
source "$SCRIPT_DIR/utils.sh"

# Initialize environment with command line arguments
init_environment "$@"

# Configuration
readonly LOG_FILE="/var/log/ap_setup.log"

# Test mode flag
TEST_MODE=0
if [[ "$1" == "--test-mode" ]]; then
    TEST_MODE=1
    log_info "Running in test mode"
fi

# Validate root privileges
check_root

# Stop interfering network services
# Returns:
#   0 on success, 1 on failure
stop_services() {
    log_info "Stopping interfering services..."
    
    # Stop wpa_supplicant first to release wireless interface
    # This prevents conflicts with hostapd
    stop_service "wpa_supplicant"
    
    # Stop AP services in reverse dependency order
    # This ensures clean shutdown and prevents service conflicts
    for service in "${REQUIRED_SERVICES[@]}"; do
        stop_service "$service"
    done
}

# Function to copy and validate configurations
# Creates necessary directories and copies config files
# Returns:
#   0 on success, 1 on failure
setup_configurations() {
    log_info "Setting up configuration files..."
    
    # Set up all configuration files using utility function
    setup_config_files || return 1
    
    # Configure hostapd daemon to use our configuration
    log_debug "Configuring hostapd daemon..."
    sed -i 's|#DAEMON_CONF=""|DAEMON_CONF="/etc/hostapd/hostapd.conf"|' /etc/default/hostapd
    validate_cmd "configure hostapd daemon" $?
    
    # Ensure wireless interface exists and is available
    validate_interface "$AP_INTERFACE"
}

# Configure network settings and firewall rules
# Enables IP forwarding and sets up basic firewall
# Returns:
#   0 on success, 1 on failure
setup_networking() {
    log_info "Configuring network settings..."
    
    # Enable IP forwarding for AP functionality
    echo "net.ipv4.ip_forward=1" > /etc/sysctl.d/routed-ap.conf
    if [[ "$AP_ENV" != "$ENV_TEST" ]]; then
        sysctl -p /etc/sysctl.d/routed-ap.conf
        validate_cmd "enable IP forwarding" $?
        
        # Configure firewall rules from environment settings
        configure_firewall || return 1
    fi
}

# Start and verify all required services
# Ensures services are enabled and running correctly
# Returns:
#   0 on success, 1 on failure
start_services() {
    log_info "Starting AP services..."
    
    if [[ "$AP_ENV" != "$ENV_TEST" ]]; then
        # Unmask hostapd if it was masked
        # This is necessary as hostapd might be masked by default
        systemctl unmask hostapd
        
        # Start services in dependency order
        # This ensures proper service initialization
        for service in "${REQUIRED_SERVICES[@]}"; do
            log_debug "Enabling and starting $service..."
            enable_service "$service"
            restart_service "$service"
            
            # Verify service status after start
            if ! check_service "$service"; then
                log_error "$service failed to start"
                return 1
            fi
            log_debug "$service started successfully"
        done
    fi
    return 0
}

# Main execution function
# Orchestrates the AP setup process
# Returns:
#   0 on success, 1 on failure
main() {
    log_info "Starting Access Point setup..."
    log_info "Environment: $AP_ENV"
    log_info "Interface: $AP_INTERFACE"
    log_info "SSID: $AP_SSID"
    
    # Execute setup steps in sequence
    stop_services || exit 1
    setup_configurations || exit 1
    setup_networking || exit 1
    
    if start_services; then
        log_info "Access Point setup completed successfully!"
        log_info "SSID: $AP_SSID"
        log_info "Password: $AP_PASSPHRASE"
        return 0
    else
        log_error "Failed to setup Access Point"
        return 1
    fi
}

# Execute main function and exit with its status
main
exit $?
