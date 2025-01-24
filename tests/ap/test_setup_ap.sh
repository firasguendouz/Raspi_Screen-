#!/bin/bash

# Test script for setup_ap.sh
# Run with sudo privileges

# Source test utilities
source "$(dirname "$0")/test_utils.sh"

# Test setup
setup() {
    echo "Setting up test environment..."
    # Create temporary test directories
    mkdir -p /tmp/test_ap/etc/hostapd
    mkdir -p /tmp/test_ap/etc/default
    mkdir -p /tmp/test_ap/etc/sysctl.d
}

# Test cleanup
cleanup() {
    echo "Cleaning up test environment..."
    rm -rf /tmp/test_ap
}

# Test cases
test_root_check() {
    echo "Testing root privilege check..."
    if [[ $EUID -ne 0 ]]; then
        assert_fail "Script must be run as root"
    fi
    assert_pass "Root privilege check passed"
}

test_config_file_copy() {
    echo "Testing configuration file copying..."
    ../ap/setup_ap.sh --test-mode
    
    assert_file_exists "/etc/dhcpcd.conf" "dhcpcd.conf should be copied"
    assert_file_exists "/etc/hostapd/hostapd.conf" "hostapd.conf should be copied"
    assert_file_exists "/etc/dnsmasq.conf" "dnsmasq.conf should be copied"
}

test_hostapd_daemon_conf() {
    echo "Testing hostapd daemon configuration..."
    ../ap/setup_ap.sh --test-mode
    
    grep -q 'DAEMON_CONF="/etc/hostapd/hostapd.conf"' /etc/default/hostapd
    assert_equals $? 0 "hostapd daemon configuration should be set correctly"
}

test_ip_forwarding() {
    echo "Testing IP forwarding configuration..."
    ../ap/setup_ap.sh --test-mode
    
    assert_file_exists "/etc/sysctl.d/routed-ap.conf" "IP forwarding configuration file should exist"
    grep -q "net.ipv4.ip_forward=1" /etc/sysctl.d/routed-ap.conf
    assert_equals $? 0 "IP forwarding should be enabled"
}

test_firewall_rules() {
    echo "Testing firewall rules..."
    ../ap/setup_ap.sh --test-mode
    
    iptables -C INPUT -p tcp --dport 80 -j ACCEPT >/dev/null 2>&1
    assert_equals $? 0 "Firewall rule for port 80 should be added"
}

test_service_status() {
    echo "Testing service status..."
    ../ap/setup_ap.sh --test-mode
    
    systemctl is-active hostapd >/dev/null 2>&1
    assert_equals $? 0 "hostapd service should be active"
    
    systemctl is-active dnsmasq >/dev/null 2>&1
    assert_equals $? 0 "dnsmasq service should be active"
}

# Run tests
run_tests() {
    setup
    
    run_test test_root_check
    run_test test_config_file_copy
    run_test test_hostapd_daemon_conf
    run_test test_ip_forwarding
    run_test test_firewall_rules
    run_test test_service_status
    
    cleanup
}

# Execute tests
run_tests 