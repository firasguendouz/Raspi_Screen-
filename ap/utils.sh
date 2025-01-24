#!/bin/bash
#
# Utility functions for AP (Access Point) management scripts.
# This module provides common functionality for logging, validation,
# service management, and error handling.
#
# Dependencies:
#   - systemd (for service management)
#   - ip (for network interface management)
#   - ping (for connectivity testing)
#
# Usage:
#   source ./utils.sh
#   init_environment [--test-mode] [interface]
#   check_root
#   # ... use other functions as needed

# shellcheck disable=SC2034  # Variables used in other scripts
# Environment configuration
readonly ENV_PROD="production"  # Production environment identifier
readonly ENV_TEST="test"        # Test environment identifier
readonly DEFAULT_ENV="$ENV_PROD"  # Default to production environment

# Network configuration defaults
# shellcheck disable=SC2034  # Variables used in other scripts
readonly DEFAULT_INTERFACE="wlan0"  # Default wireless interface
readonly DEFAULT_IP="192.168.4.1"   # Default AP IP address
readonly DEFAULT_NETMASK="255.255.255.0"  # Default network mask
readonly DEFAULT_DHCP_RANGE="192.168.4.2,192.168.4.20"  # DHCP address range
readonly DEFAULT_LEASE_TIME="24h"    # DHCP lease duration

# Service and directory configuration
readonly REQUIRED_SERVICES=("hostapd" "dnsmasq" "dhcpcd")  # Core AP services
readonly CONFIG_DIR="../config"  # Configuration files directory
readonly LOG_DIR="/var/log"      # System logs directory

# Log level definitions and ANSI color codes for terminal output
readonly LOG_ERROR="ERROR"  # Critical errors that prevent normal operation
readonly LOG_WARN="WARN"    # Warning messages for potential issues
readonly LOG_INFO="INFO"    # General information about operations
readonly LOG_DEBUG="DEBUG"  # Detailed debug information

readonly RED='\033[0;31m'     # Red for errors
readonly YELLOW='\033[1;33m'  # Yellow for warnings
readonly GREEN='\033[0;32m'   # Green for success/info
readonly BLUE='\033[0;34m'    # Blue for debug
readonly NC='\033[0m'         # Reset color

# Load environment configuration
# Args:
#   None
# Returns:
#   0 on success, 1 if config file not found
load_environment() {
    local env_file
    env_file="$(dirname "$0")/env.routes"
    
    if [[ -f "$env_file" ]]; then
        log_debug "Loading environment configuration from $env_file"
        # shellcheck source=./env.routes
        source "$env_file"
        return 0
    else
        log_warn "Environment configuration file not found: $env_file"
        log_warn "Using default values"
        return 1
    fi
}

# Initialize the environment with command line arguments
# Args:
#   $1 - Optional: --test-mode flag
#   $2 - Optional: Interface name (defaults to AP_INTERFACE from env.routes)
# Exports:
#   AP_ENV - Current environment (production/test)
#   AP_INTERFACE - Network interface to use
#   LOG_FILE - Log file path based on script name
init_environment() {
    # Load environment configuration first
    load_environment
    
    # Set environment based on --test-mode flag
    if [[ "$1" == "--test-mode" ]]; then
        export AP_ENV="$ENV_TEST"
    else
        export AP_ENV="$DEFAULT_ENV"
    fi
    
    # Set interface from env.routes or command line argument
    export AP_INTERFACE="${2:-${AP_INTERFACE}}"
    
    # Set up logging
    local script_name
    script_name=$(basename "$0" .sh)
    export LOG_FILE="${AP_LOG_DIR}/ap_${script_name}.log"
    
    # Configure log level
    case "${AP_LOG_LEVEL^^}" in
        DEBUG) export LOG_LEVEL="$LOG_DEBUG" ;;
        WARN)  export LOG_LEVEL="$LOG_WARN" ;;
        ERROR) export LOG_LEVEL="$LOG_ERROR" ;;
        *)     export LOG_LEVEL="$LOG_INFO" ;;
    esac
    
    # Log initialization details
    log_debug "Environment initialized: $AP_ENV"
    log_debug "Interface: $AP_INTERFACE"
    log_debug "Log file: $LOG_FILE"
    log_debug "Log level: $LOG_LEVEL"
}

# Enhanced logging function with timestamp and severity level
# Args:
#   $1 - Log level (ERROR/WARN/INFO/DEBUG)
#   $2 - Message to log
# Outputs:
#   Writes to stdout with color and to LOG_FILE if defined
log() {
    local level="$1"
    local message="$2"
    local timestamp
    timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    local color=""
    
    # Select color based on log level
    case "$level" in
        "$LOG_ERROR") color="$RED" ;;
        "$LOG_WARN")  color="$YELLOW" ;;
        "$LOG_INFO")  color="$GREEN" ;;
        "$LOG_DEBUG") color="$BLUE" ;;
    esac
    
    # Output to terminal with color
    echo -e "${color}[$timestamp] [$level] $message${NC}"
    
    # Write to log file if defined
    if [[ -n "${LOG_FILE}" ]]; then
        echo "[$timestamp] [$level] $message" >> "${LOG_FILE}"
    fi
}

# Convenience logging functions with predefined levels
log_error() { log "$LOG_ERROR" "$1"; }
log_warn()  { log "$LOG_WARN"  "$1"; }
log_info()  { log "$LOG_INFO"  "$1"; }
log_debug() { log "$LOG_DEBUG" "$1"; }

# Verify script is running with root privileges
# Exits with status 1 if not running as root
check_root() {
    if [[ $EUID -ne 0 ]]; then
        log_error "This script must be run as root (sudo)"
        exit 1
    fi
}

# Validate command execution status
# Args:
#   $1 - Description of the command being validated
#   $2 - Exit code to validate
# Returns:
#   0 if command succeeded, 1 if failed
validate_cmd() {
    local cmd_description="$1"
    local exit_code="$2"
    
    if [[ $exit_code -ne 0 ]]; then
        log_error "Failed to $cmd_description (Exit code: $exit_code)"
        return 1
    fi
    return 0
}

# Check if a systemd service is active
# Args:
#   $1 - Service name to check
# Returns:
#   0 if service is active, 1 if inactive or not found
check_service() {
    local service_name="$1"
    if systemctl is-active --quiet "$service_name"; then
        return 0
    else
        return 1
    fi
}

# Validate network interface exists and is available
# Args:
#   $1 - Interface name to validate
# Returns:
#   0 if interface exists, 1 if not found
validate_interface() {
    local interface="$1"
    if ! ip link show "$interface" &>/dev/null; then
        log_error "Network interface $interface not found"
        return 1
    fi
    return 0
}

# Copy configuration file with backup creation
# Args:
#   $1 - Source file path
#   $2 - Destination file path
# Returns:
#   0 on success, 1 on failure
copy_config() {
    local src="$1"
    local dest="$2"
    
    # Verify source file exists
    if [[ ! -f "$src" ]]; then
        log_error "Source configuration file not found: $src"
        return 1
    fi
    
    # Create backup of existing destination
    if [[ -f "$dest" ]]; then
        cp "$dest" "${dest}.backup"
        log_debug "Created backup: ${dest}.backup"
    fi
    
    # Copy file and validate
    cp "$src" "$dest"
    validate_cmd "copy configuration file from $src to $dest" $?
}

# Test network connectivity to a target
# Args:
#   $1 - Optional: Target host (default: 8.8.8.8)
#   $2 - Optional: Timeout in seconds (default: 5)
# Returns:
#   0 if ping succeeds, 1 if fails
test_connectivity() {
    local target="${1:-8.8.8.8}"
    local timeout="${2:-5}"
    
    if ping -c 1 -W "$timeout" "$target" >/dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

# Service management functions with test mode support
# Each function takes a service name as argument
# Returns 0 on success, 1 on failure

# Start a systemd service
start_service() {
    local service="$1"
    if [[ "$AP_ENV" != "$ENV_TEST" ]]; then
        systemctl start "$service"
        validate_cmd "start $service" $?
    else
        log_debug "[TEST] Would start $service"
    fi
}

# Stop a systemd service
stop_service() {
    local service="$1"
    if [[ "$AP_ENV" != "$ENV_TEST" ]]; then
        systemctl stop "$service"
        validate_cmd "stop $service" $?
    else
        log_debug "[TEST] Would stop $service"
    fi
}

# Restart a systemd service
restart_service() {
    local service="$1"
    if [[ "$AP_ENV" != "$ENV_TEST" ]]; then
        systemctl restart "$service"
        validate_cmd "restart $service" $?
    else
        log_debug "[TEST] Would restart $service"
    fi
}

# Enable a systemd service
enable_service() {
    local service="$1"
    if [[ "$AP_ENV" != "$ENV_TEST" ]]; then
        systemctl enable "$service"
        validate_cmd "enable $service" $?
    else
        log_debug "[TEST] Would enable $service"
    fi
}

# Disable a systemd service
disable_service() {
    local service="$1"
    if [[ "$AP_ENV" != "$ENV_TEST" ]]; then
        systemctl disable "$service"
        validate_cmd "disable $service" $?
    else
        log_debug "[TEST] Would disable $service"
    fi
}

# Cleanup function for error handling
# Called automatically on script exit via trap
# Args:
#   None (uses $? for exit code)
cleanup() {
    local exit_code=$?
    log_debug "Cleanup started (exit code: $exit_code)"
    
    # Restore configuration backups if they exist
    for config in /etc/hostapd/hostapd.conf /etc/dnsmasq.conf /etc/dhcpcd.conf; do
        if [[ -f "${config}.backup" ]]; then
            log_debug "Restoring backup: $config"
            mv "${config}.backup" "$config"
        fi
    done
    
    exit $exit_code
}

# Set trap to ensure cleanup runs on script exit
trap cleanup EXIT

# Configure firewall rules based on environment settings
# Args:
#   None
# Returns:
#   0 on success, 1 on failure
configure_firewall() {
    log_info "Configuring firewall rules..."
    
    if [[ "$AP_ENV" != "$ENV_TEST" ]]; then
        # Allow specified ports
        IFS=',' read -ra PORTS <<< "$AP_ALLOW_PORTS"
        for port in "${PORTS[@]}"; do
            log_debug "Allowing incoming traffic on port $port"
            iptables -A INPUT -p tcp --dport "$port" -j ACCEPT
            validate_cmd "allow port $port" $?
        done
        
        # Configure port forwarding
        if [[ -n "$AP_FORWARD_PORTS" ]]; then
            IFS=',' read -ra FORWARDS <<< "$AP_FORWARD_PORTS"
            for forward in "${FORWARDS[@]}"; do
                IFS=':' read -ra PARTS <<< "$forward"
                if [[ ${#PARTS[@]} -eq 2 ]]; then
                    log_debug "Forwarding port ${PARTS[0]} to ${PARTS[1]}"
                    iptables -t nat -A PREROUTING -p tcp --dport "${PARTS[0]}" -j REDIRECT --to-port "${PARTS[1]}"
                    validate_cmd "forward port ${PARTS[0]} to ${PARTS[1]}" $?
                fi
            done
        fi
        
        # Block specified ports
        if [[ -n "$AP_BLOCK_PORTS" ]]; then
            IFS=',' read -ra BLOCKS <<< "$AP_BLOCK_PORTS"
            for port in "${BLOCKS[@]}"; do
                log_debug "Blocking traffic on port $port"
                iptables -A INPUT -p tcp --dport "$port" -j DROP
                validate_cmd "block port $port" $?
            done
        fi
    else
        log_debug "[TEST] Would configure firewall rules"
    fi
    
    return 0
}

# Generate hostapd configuration from environment settings
# Args:
#   $1 - Output file path
# Returns:
#   0 on success, 1 on failure
generate_hostapd_config() {
    local output_file="$1"
    
    cat > "$output_file" << EOF
# Generated hostapd configuration
# Generated on: $(date)

interface=$AP_INTERFACE
driver=$AP_DRIVER
ssid=$AP_SSID
hw_mode=$AP_HW_MODE
channel=$AP_CHANNEL
country_code=$AP_COUNTRY

# Security settings
auth_algs=$AP_AUTH_ALGS
wpa=$AP_WPA_VERSION
wpa_key_mgmt=$AP_KEY_MGMT
wpa_pairwise=$AP_PAIRWISE
wpa_passphrase=$AP_PASSPHRASE

# Advanced settings
ignore_broadcast_ssid=$AP_HIDE_SSID
max_num_sta=$AP_MAX_NUM_STA
rts_threshold=$AP_RTS_THRESHOLD
fragm_threshold=$AP_FRAGM_THRESHOLD
EOF
    
    validate_cmd "generate hostapd configuration" $?
}

# Generate dnsmasq configuration from environment settings
# Args:
#   $1 - Output file path
# Returns:
#   0 on success, 1 on failure
generate_dnsmasq_config() {
    local output_file="$1"
    
    cat > "$output_file" << EOF
# Generated dnsmasq configuration
# Generated on: $(date)

interface=$AP_INTERFACE
dhcp-range=$AP_DHCP_START,$AP_DHCP_END,$AP_NETMASK,$AP_LEASE_TIME
dhcp-option=option:router,$AP_IP
dhcp-option=option:dns-server,$AP_DNS_PRIMARY,$AP_DNS_SECONDARY

# Basic settings
domain=wlan
address=/gw.wlan/$AP_IP
EOF
    
    validate_cmd "generate dnsmasq configuration" $?
} 