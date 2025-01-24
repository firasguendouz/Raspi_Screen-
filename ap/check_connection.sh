#!/bin/bash
#
# Access Point Connection Monitor
# Monitors AP connectivity and automatically restarts services on failure.
#
# This script continuously monitors:
# 1. Internet connectivity through ping tests
# 2. AP interface status
# 3. Service health
#
# On failure detection, it attempts to restore functionality by:
# 1. Restarting failed services
# 2. Reconfiguring network settings
# 3. Verifying recovery success
#
# Dependencies:
#   - utils.sh (common utility functions)
#   - ping (for connectivity testing)
#   - systemd (for service management)
#
# Usage:
#   sudo ./check_connection.sh [--test-mode] [--timeout SECONDS]

# Source common utility functions
# shellcheck source=./utils.sh
source "$(dirname "$0")/utils.sh"

# Configuration constants
# These values can be overridden by env.routes
readonly CHECK_INTERVAL="${AP_CHECK_INTERVAL:-30}"     # Interval between connectivity checks
readonly PING_TARGET="${AP_TEST_PING_TARGET:-8.8.8.8}" # Target host for connectivity tests
readonly MAX_FAILURES="${AP_MAX_FAILURES:-3}"          # Maximum consecutive failures
readonly STABILIZATION_WAIT="${AP_STABILIZATION_WAIT:-10}" # Post-restart wait time

# Parse and validate command line arguments
# Sets up environment variables and test mode settings
# Args:
#   Command line arguments ($@)
parse_args() {
    local timeout=0
    
    # Process command line arguments
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --test-mode)
                shift
                ;;
            --timeout)
                timeout="${2:-$AP_TEST_TIMEOUT}"
                shift 2
                ;;
            *)
                log_error "Unknown argument: $1"
                exit 1
                ;;
        esac
    done
    
    # Initialize environment with processed arguments
    init_environment "$@"
    
    # Export timeout for test mode operations
    export TEST_TIMEOUT="$timeout"
}

# Initialize script with command line arguments
parse_args "$@"

# Validate root privileges
check_root

# Validate AP interface status
# Checks if the wireless interface exists and is available
# Returns:
#   0 if interface is valid, 1 if not
check_ap_interface() {
    log_debug "Checking AP interface $AP_INTERFACE..."
    validate_interface "$AP_INTERFACE"
}

# Restart AP services after failure
# Recopies configurations and restarts all services
# Returns:
#   0 on successful restart, 1 on failure
restart_ap() {
    log_warn "Initiating AP restart procedure..."
    
    # Generate fresh configurations from current environment
    log_debug "Generating fresh configurations..."
    generate_hostapd_config "/etc/hostapd/hostapd.conf" || return 1
    generate_dnsmasq_config "/etc/dnsmasq.conf" || return 1
    
    # Restart services in correct dependency order
    if [[ "$AP_ENV" != "$ENV_TEST" ]]; then
        for service in "${REQUIRED_SERVICES[@]}"; do
            log_debug "Restarting $service..."
            restart_service "$service"
            
            # Verify service started successfully
            if ! check_service "$service"; then
                log_error "Failed to restart $service"
                return 1
            fi
        done
        
        # Allow services to stabilize before continuing
        log_info "Waiting for services to stabilize..."
        sleep "$STABILIZATION_WAIT"
    fi
    
    log_info "AP restart completed"
    return 0
}

# Check if test mode timeout has been reached
# Used only in test mode to limit runtime
# Returns:
#   0 if timeout not reached, 1 if timeout reached
check_timeout() {
    if [[ "$AP_ENV" == "$ENV_TEST" && -n "$TEST_TIMEOUT" && "$TEST_TIMEOUT" -gt 0 ]]; then
        local current_time=$(date +%s)
        local elapsed=$((current_time - start_time))
        if [[ $elapsed -ge $TEST_TIMEOUT ]]; then
            log_info "Test timeout reached"
            return 1
        fi
    fi
    return 0
}

# Main monitoring loop
# Continuously monitors AP status and handles failures
# Returns:
#   0 on normal exit (test mode), 1 on error
main() {
    local failures=0
    local start_time=$(date +%s)
    
    # Log initial configuration
    log_info "Starting AP monitoring service..."
    log_info "Environment: $AP_ENV"
    log_info "Interface: $AP_INTERFACE"
    log_info "Check interval: $CHECK_INTERVAL seconds"
    log_info "Max failures: $MAX_FAILURES"
    log_info "Ping target: $PING_TARGET"
    
    # Main monitoring loop
    while true; do
        # Check test mode timeout
        if ! check_timeout; then
            exit 0
        fi
        
        # Test internet connectivity
        if ! test_connectivity "$PING_TARGET" 5; then
            ((failures++))
            log_warn "Connection test failed. Failure count: $failures/$MAX_FAILURES"
            
            # Handle maximum failures reached
            if [ $failures -ge $MAX_FAILURES ]; then
                log_error "Maximum failures ($MAX_FAILURES) reached"
                if restart_ap; then
                    failures=0
                    log_info "AP restarted successfully"
                else
                    log_error "AP restart failed"
                fi
            fi
        else
            # Reset failure counter on successful connection
            if [[ $failures -gt 0 ]]; then
                log_info "Connection restored"
                failures=0
            fi
        fi
        
        # Verify AP interface status
        if ! check_ap_interface; then
            log_warn "AP interface check failed, attempting restart..."
            if restart_ap; then
                log_info "Interface restored"
            else
                log_error "Failed to restore interface"
            fi
        fi
        
        # Wait before next check
        if [[ "$AP_ENV" != "$ENV_TEST" ]]; then
            sleep "$CHECK_INTERVAL"
        else
            sleep 1  # Faster checks in test mode
        fi
    done
}

# Execute main function and exit with its status
main
exit $?
