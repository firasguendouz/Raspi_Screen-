#!/bin/bash

# Utility functions for AP scripts
# Provides common logging, validation, and error handling functionality

# Log levels
readonly LOG_ERROR="ERROR"
readonly LOG_WARN="WARN"
readonly LOG_INFO="INFO"
readonly LOG_DEBUG="DEBUG"

# Colors for terminal output
readonly RED='\033[0;31m'
readonly YELLOW='\033[1;33m'
readonly GREEN='\033[0;32m'
readonly BLUE='\033[0;34m'
readonly NC='\033[0m' # No Color

# Logging function with timestamp and log level
log() {
    local level="$1"
    local message="$2"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    local color=""
    
    case "$level" in
        "$LOG_ERROR") color="$RED" ;;
        "$LOG_WARN")  color="$YELLOW" ;;
        "$LOG_INFO")  color="$GREEN" ;;
        "$LOG_DEBUG") color="$BLUE" ;;
    esac
    
    echo -e "${color}[$timestamp] [$level] $message${NC}"
    
    # Log to file if LOG_FILE is defined
    if [[ -n "${LOG_FILE}" ]]; then
        echo "[$timestamp] [$level] $message" >> "${LOG_FILE}"
    fi
}

# Shorthand logging functions
log_error() { log "$LOG_ERROR" "$1"; }
log_warn()  { log "$LOG_WARN"  "$1"; }
log_info()  { log "$LOG_INFO"  "$1"; }
log_debug() { log "$LOG_DEBUG" "$1"; }

# Check if script is running with root privileges
check_root() {
    if [[ $EUID -ne 0 ]]; then
        log_error "This script must be run as root (sudo)"
        exit 1
    fi
}

# Validate command execution
validate_cmd() {
    local cmd_description="$1"
    local exit_code="$2"
    
    if [[ $exit_code -ne 0 ]]; then
        log_error "Failed to $cmd_description (Exit code: $exit_code)"
        return 1
    fi
    return 0
}

# Check if a service is active
check_service() {
    local service_name="$1"
    if systemctl is-active --quiet "$service_name"; then
        return 0
    else
        return 1
    fi
}

# Validate network interface
validate_interface() {
    local interface="$1"
    if ! ip link show "$interface" &>/dev/null; then
        log_error "Network interface $interface not found"
        return 1
    fi
    return 0
}

# Copy configuration file with validation
copy_config() {
    local src="$1"
    local dest="$2"
    
    if [[ ! -f "$src" ]]; then
        log_error "Source configuration file not found: $src"
        return 1
    fi
    
    cp "$src" "$dest"
    validate_cmd "copy configuration file from $src to $dest" $?
}

# Test network connectivity
test_connectivity() {
    local target="${1:-8.8.8.8}"
    local timeout="${2:-5}"
    
    if ping -c 1 -W "$timeout" "$target" >/dev/null 2>&1; then
        return 0
    else
        return 1
    fi
} 