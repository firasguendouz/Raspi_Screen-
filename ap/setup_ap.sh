#!/bin/bash

# Enhanced Script to initialize and stabilize Access Point mode
# Must be run with sudo privileges

# Source utility functions
source "$(dirname "$0")/utils.sh"

# Configuration
readonly CONFIG_DIR="../config"
readonly REQUIRED_SERVICES=("hostapd" "dnsmasq" "dhcpcd")
readonly LOG_FILE="/var/log/ap_setup.log"

# Test mode flag
TEST_MODE=0
if [[ "$1" == "--test-mode" ]]; then
    TEST_MODE=1
    log_info "Running in test mode"
fi

# Validate root privileges
check_root

# Function to stop services
stop_services() {
    log_info "Stopping interfering services..."
    if [[ $TEST_MODE -eq 0 ]]; then
        for service in wpa_supplicant "${REQUIRED_SERVICES[@]}"; do
            systemctl stop "$service"
            validate_cmd "stop $service service" $?
        done
    fi
}

# Function to copy and validate configurations
setup_configurations() {
    log_info "Setting up configuration files..."
    
    # Copy configuration files
    copy_config "$CONFIG_DIR/dhcpcd.conf" "/etc/dhcpcd.conf"
    copy_config "$CONFIG_DIR/hostapd.conf" "/etc/hostapd/hostapd.conf"
    copy_config "$CONFIG_DIR/dnsmasq.conf" "/etc/dnsmasq.conf"
    
    # Configure hostapd daemon
    log_debug "Configuring hostapd daemon..."
    sed -i 's|#DAEMON_CONF=""|DAEMON_CONF="/etc/hostapd/hostapd.conf"|' /etc/default/hostapd
    validate_cmd "configure hostapd daemon" $?
}

# Function to configure networking
setup_networking() {
    log_info "Configuring network settings..."
    
    # Enable IP forwarding
    echo "net.ipv4.ip_forward=1" > /etc/sysctl.d/routed-ap.conf
    if [[ $TEST_MODE -eq 0 ]]; then
        sysctl -p /etc/sysctl.d/routed-ap.conf
        validate_cmd "enable IP forwarding" $?
    fi
    
    # Configure firewall rules
    if [[ $TEST_MODE -eq 0 ]]; then
        log_debug "Setting up firewall rules..."
        iptables -A INPUT -p tcp --dport 80 -j ACCEPT
        validate_cmd "configure firewall rules" $?
    fi
}

# Function to start services
start_services() {
    log_info "Starting AP services..."
    if [[ $TEST_MODE -eq 0 ]]; then
        systemctl unmask hostapd
        
        # Enable and restart services
        for service in "${REQUIRED_SERVICES[@]}"; do
            log_debug "Enabling and starting $service..."
            systemctl enable "$service"
            systemctl restart "$service"
            
            if ! check_service "$service"; then
                log_error "$service failed to start"
                return 1
            fi
        done
    fi
    return 0
}

# Main execution
main() {
    log_info "Starting Access Point setup..."
    
    # Execute setup steps
    stop_services
    setup_configurations
    setup_networking
    
    if start_services; then
        log_info "Access Point setup completed successfully!"
        log_info "SSID: RaspberryPi_AP"
        log_info "Password: raspberry"
        return 0
    else
        log_error "Failed to setup Access Point"
        return 1
    fi
}

# Execute main function
main
exit $?
