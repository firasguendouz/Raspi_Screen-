#!/bin/bash

# Script to monitor connectivity and restart Access Point if necessary
# Must be run with sudo privileges

# Source utility functions
source "$(dirname "$0")/utils.sh"

# Configuration
readonly AP_INTERFACE="wlan0"  # This matches our hostapd.conf
readonly CHECK_INTERVAL=30     # Check every 30 seconds
readonly PING_TARGET="8.8.8.8" # Google DNS server
readonly MAX_FAILURES=3
readonly LOG_FILE="/var/log/ap_monitor.log"

# Test mode configuration
TEST_MODE=0
TIMEOUT=0
if [[ "$1" == "--test-mode" ]]; then
    TEST_MODE=1
    log_info "Running in test mode"
    if [[ "$2" == "--timeout" ]]; then
        TIMEOUT=$3
        log_debug "Test timeout set to $TIMEOUT seconds"
    fi
fi

# Validate root privileges
check_root

# Function to validate AP interface
check_ap_interface() {
    log_debug "Checking AP interface $AP_INTERFACE..."
    if ! validate_interface "$AP_INTERFACE"; then
        log_error "AP interface $AP_INTERFACE is down"
        return 1
    fi
    return 0
}

# Function to restart AP services
restart_ap() {
    log_warn "Initiating AP restart procedure..."
    
    # Re-copy configuration files
    log_debug "Refreshing configuration files..."
    copy_config "../config/hostapd.conf" "/etc/hostapd/hostapd.conf"
    copy_config "../config/dnsmasq.conf" "/etc/dnsmasq.conf"
    copy_config "../config/dhcpcd.conf" "/etc/dhcpcd.conf"
    
    # Restart services
    if [[ $TEST_MODE -eq 0 ]]; then
        for service in dhcpcd hostapd dnsmasq; do
            log_debug "Restarting $service..."
            systemctl restart "$service"
            if ! check_service "$service"; then
                log_error "Failed to restart $service"
                return 1
            fi
        done
        log_info "Waiting for services to stabilize..."
        sleep 10
    fi
    
    log_info "AP restart completed"
    return 0
}

# Function to check test mode timeout
check_timeout() {
    if [[ $TEST_MODE -eq 1 && $TIMEOUT -gt 0 ]]; then
        local current_time=$(date +%s)
        local elapsed=$((current_time - start_time))
        if [[ $elapsed -ge $TIMEOUT ]]; then
            log_info "Test timeout reached"
            return 1
        fi
    fi
    return 0
}

# Main monitoring loop
main() {
    local failures=0
    local start_time=$(date +%s)
    
    log_info "Starting AP monitoring service..."
    log_info "Monitoring interface: $AP_INTERFACE"
    log_info "Check interval: $CHECK_INTERVAL seconds"
    
    while true; do
        # Check test timeout
        if ! check_timeout; then
            exit 0
        fi
        
        # Check internet connectivity
        if ! test_connectivity "$PING_TARGET" 5; then
            ((failures++))
            log_warn "Connection test failed. Failure count: $failures"
            
            if [ $failures -ge $MAX_FAILURES ]; then
                log_error "Maximum failures ($MAX_FAILURES) reached"
                if restart_ap; then
                    failures=0
                fi
            fi
        else
            if [[ $failures -gt 0 ]]; then
                log_info "Connection restored"
            fi
            failures=0
        fi
        
        # Check AP interface status
        if ! check_ap_interface; then
            log_warn "AP interface check failed, attempting restart..."
            restart_ap
        fi
        
        # Wait before next check
        if [[ $TEST_MODE -eq 0 ]]; then
            sleep $CHECK_INTERVAL
        else
            sleep 1  # Faster checks in test mode
        fi
    done
}

# Execute main function
main
exit $?
