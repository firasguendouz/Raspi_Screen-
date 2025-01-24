#!/bin/bash

# Test script for stop_ap.sh
# Run with sudo privileges

# Source test utilities
source "$(dirname "$0")/test_utils.sh"

# Test setup
setup() {
    echo "Setting up test environment..."
    # Create test configuration files
    mkdir -p /tmp/test_ap/etc/{hostapd,dnsmasq.d}
    touch /tmp/test_ap/etc/dhcpcd.conf
    touch /tmp/test_ap/etc/dnsmasq.conf
    touch /tmp/test_ap/etc/hostapd/hostapd.conf
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

test_service_stop() {
    echo "Testing service stopping..."
    ../ap/stop_ap.sh --test-mode
    
    systemctl is-active hostapd >/dev/null 2>&1
    assert_equals $? 3 "hostapd service should be stopped"
    
    systemctl is-active dnsmasq >/dev/null 2>&1
    assert_equals $? 3 "dnsmasq service should be stopped"
}

test_service_disable() {
    echo "Testing service disable..."
    ../ap/stop_ap.sh --test-mode
    
    systemctl is-enabled hostapd >/dev/null 2>&1
    assert_equals $? 1 "hostapd service should be disabled"
    
    systemctl is-enabled dnsmasq >/dev/null 2>&1
    assert_equals $? 1 "dnsmasq service should be disabled"
}

test_interface_down() {
    echo "Testing interface down..."
    ../ap/stop_ap.sh --test-mode
    
    ip link show wlan0 | grep -q "state DOWN"
    assert_equals $? 0 "wlan0 interface should be down"
}

test_config_backup() {
    echo "Testing configuration backup..."
    ../ap/stop_ap.sh --test-mode
    
    assert_file_exists "/etc/dhcpcd.conf.ap.bak" "dhcpcd.conf backup should exist"
    assert_file_exists "/etc/dnsmasq.conf.ap.bak" "dnsmasq.conf backup should exist"
    assert_file_exists "/etc/hostapd/hostapd.conf.ap.bak" "hostapd.conf backup should exist"
}

test_wpa_supplicant_restore() {
    echo "Testing wpa_supplicant restoration..."
    ../ap/stop_ap.sh --test-mode
    
    assert_file_exists "/etc/wpa_supplicant/wpa_supplicant.conf" "wpa_supplicant.conf should be restored"
}

test_dns_resolver() {
    echo "Testing DNS resolver configuration..."
    ../ap/stop_ap.sh --test-mode
    
    grep -q "nameserver 8.8.8.8" /etc/resolv.conf
    assert_equals $? 0 "Primary DNS should be configured"
    
    grep -q "nameserver 8.8.4.4" /etc/resolv.conf
    assert_equals $? 0 "Secondary DNS should be configured"
}

# Run tests
run_tests() {
    setup
    
    run_test test_root_check
    run_test test_service_stop
    run_test test_service_disable
    run_test test_interface_down
    run_test test_config_backup
    run_test test_wpa_supplicant_restore
    run_test test_dns_resolver
    
    cleanup
    print_summary
}

# Execute tests
run_tests 