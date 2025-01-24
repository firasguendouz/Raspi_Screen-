#!/bin/bash

# Test script for check_connection.sh
# Run with sudo privileges

# Source test utilities
source "$(dirname "$0")/test_utils.sh"

# Mock functions
mock_ping() {
    return ${MOCK_PING_RETURN:-0}
}

mock_iwconfig() {
    if [[ ${MOCK_IWCONFIG_RETURN:-0} -eq 0 ]]; then
        echo "wlan0     IEEE 802.11  ESSID:\"test\""
    else
        return 1
    fi
}

# Test setup
setup() {
    echo "Setting up test environment..."
    # Create test configuration files
    mkdir -p /tmp/test_ap/etc/{hostapd,dnsmasq.d}
    cp ../config/hostapd.conf /tmp/test_ap/etc/hostapd/
    cp ../config/dnsmasq.conf /tmp/test_ap/etc/
    cp ../config/dhcpcd.conf /tmp/test_ap/etc/
    
    # Mock commands
    alias ping=mock_ping
    alias iwconfig=mock_iwconfig
}

# Test cleanup
cleanup() {
    echo "Cleaning up test environment..."
    rm -rf /tmp/test_ap
    unalias ping 2>/dev/null || true
    unalias iwconfig 2>/dev/null || true
}

# Test cases
test_connection_success() {
    echo "Testing successful connection..."
    MOCK_PING_RETURN=0
    
    # Run script in background and capture PID
    ../ap/check_connection.sh --test-mode &
    SCRIPT_PID=$!
    
    # Wait a bit and check if script is running
    sleep 2
    kill -0 $SCRIPT_PID 2>/dev/null
    assert_equals $? 0 "Script should continue running on successful connection"
    
    # Cleanup
    kill $SCRIPT_PID 2>/dev/null || true
}

test_connection_failure() {
    echo "Testing connection failure..."
    MOCK_PING_RETURN=1
    export MAX_FAILURES=2
    
    # Capture script output
    output=$(../ap/check_connection.sh --test-mode --timeout 5 2>&1)
    
    echo "$output" | grep -q "Connection test failed"
    assert_equals $? 0 "Should detect connection failure"
    
    echo "$output" | grep -q "Maximum failures reached"
    assert_equals $? 0 "Should reach maximum failures"
}

test_interface_monitoring() {
    echo "Testing interface monitoring..."
    MOCK_IWCONFIG_RETURN=1
    
    # Capture script output
    output=$(../ap/check_connection.sh --test-mode --timeout 5 2>&1)
    
    echo "$output" | grep -q "AP interface wlan0 is down"
    assert_equals $? 0 "Should detect interface down state"
}

test_config_restoration() {
    echo "Testing configuration restoration on restart..."
    MOCK_PING_RETURN=1
    export MAX_FAILURES=1
    
    # Run script and capture output
    output=$(../ap/check_connection.sh --test-mode --timeout 5 2>&1)
    
    # Check if configuration files are copied during restart
    assert_file_exists "/etc/hostapd/hostapd.conf" "hostapd.conf should be restored"
    assert_file_exists "/etc/dnsmasq.conf" "dnsmasq.conf should be restored"
    assert_file_exists "/etc/dhcpcd.conf" "dhcpcd.conf should be restored"
}

test_service_restart() {
    echo "Testing service restart..."
    MOCK_PING_RETURN=1
    export MAX_FAILURES=1
    
    # Run script and capture output
    output=$(../ap/check_connection.sh --test-mode --timeout 5 2>&1)
    
    echo "$output" | grep -q "Restarting Access Point services"
    assert_equals $? 0 "Should attempt to restart services"
}

# Run tests
run_tests() {
    setup
    
    run_test test_connection_success
    run_test test_connection_failure
    run_test test_interface_monitoring
    run_test test_config_restoration
    run_test test_service_restart
    
    cleanup
    print_summary
}

# Execute tests
run_tests 