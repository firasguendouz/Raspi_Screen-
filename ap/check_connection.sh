#!/bin/bash

# Script to monitor connectivity and restart Access Point if necessary
# Must be run with sudo privileges

# Test mode flag
TEST_MODE=0
TIMEOUT=0
if [[ "$1" == "--test-mode" ]]; then
    TEST_MODE=1
    if [[ "$2" == "--timeout" ]]; then
        TIMEOUT=$3
    fi
fi

# Configuration
AP_INTERFACE="wlan0"  # This matches our hostapd.conf
CHECK_INTERVAL=30     # Check every 30 seconds
PING_TARGET="8.8.8.8" # Google DNS server
MAX_FAILURES=3

# Initialize failure counter
failures=0

# Function to restart AP
restart_ap() {
    echo "$(date): Restarting Access Point services..."
    
    # Re-copy configuration files to ensure clean state
    cp ../config/hostapd.conf /etc/hostapd/hostapd.conf
    cp ../config/dnsmasq.conf /etc/dnsmasq.conf
    cp ../config/dhcpcd.conf /etc/dhcpcd.conf
    
    # Restart services
    if [[ $TEST_MODE -eq 0 ]]; then
        sudo systemctl restart dhcpcd
        sudo systemctl restart hostapd
        sudo systemctl restart dnsmasq
        sleep 10  # Allow services to stabilize
    fi
}

# Main monitoring loop
start_time=$(date +%s)
while true; do
    # Check timeout in test mode
    if [[ $TEST_MODE -eq 1 && $TIMEOUT -gt 0 ]]; then
        current_time=$(date +%s)
        elapsed=$((current_time - start_time))
        if [[ $elapsed -ge $TIMEOUT ]]; then
            echo "Test timeout reached"
            exit 0
        fi
    fi

    # Check internet connectivity
    if ! ping -c 1 -W 5 $PING_TARGET >/dev/null 2>&1; then
        ((failures++))
        echo "$(date): Connection test failed. Failure count: $failures"

        if [ $failures -ge $MAX_FAILURES ]; then
            echo "$(date): Maximum failures reached. Restarting AP..."
            restart_ap
            failures=0  # Reset failure counter after restart
        fi
    else
        # Reset failure counter on successful connection
        failures=0
    fi

    # Ensure AP interface is active
    if ! iwconfig $AP_INTERFACE >/dev/null 2>&1; then
        echo "$(date): AP interface $AP_INTERFACE is down. Restarting..."
        restart_ap
    fi

    # Wait before next check
    if [[ $TEST_MODE -eq 0 ]]; then
        sleep $CHECK_INTERVAL
    else
        sleep 1  # Faster checks in test mode
    fi
done
