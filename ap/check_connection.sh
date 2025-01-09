#!/bin/bash

# Configuration
AP_INTERFACE="wlan0"
CHECK_INTERVAL=60  # Check every 60 seconds
PING_TARGET="8.8.8.8"  # Google DNS server
MAX_FAILURES=3

# Initialize counter
failures=0

# Function to restart AP
restart_ap() {
    echo "$(date): Restarting AP service..."
    sudo systemctl restart hostapd
    sleep 10
}

# Main monitoring loop
while true; do
    # Test connectivity
    if ! ping -c 1 -W 5 $PING_TARGET >/dev/null 2>&1; then
        ((failures++))
        echo "$(date): Connection test failed. Failure count: $failures"
        
        if [ $failures -ge $MAX_FAILURES ]; then
            echo "$(date): Maximum failures reached. Attempting AP restart..."
            restart_ap
            failures=0  # Reset counter after restart
        fi
    else
        # Reset failure counter on successful ping
        failures=0
    fi

    # Check if AP interface is up
    if ! iwconfig $AP_INTERFACE >/dev/null 2>&1; then
        echo "$(date): AP interface down. Restarting..."
        restart_ap
    fi

    sleep $CHECK_INTERVAL
done