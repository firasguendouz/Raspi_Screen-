#!/bin/bash

# Test utilities for AP scripts testing

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

# Test counters
TESTS_RUN=0
TESTS_PASSED=0
TESTS_FAILED=0

# Assert functions
assert_equals() {
    local actual=$1
    local expected=$2
    local message=$3
    
    ((TESTS_RUN++))
    if [[ "$actual" == "$expected" ]]; then
        echo -e "${GREEN}✓ PASS${NC}: $message"
        ((TESTS_PASSED++))
        return 0
    else
        echo -e "${RED}✗ FAIL${NC}: $message (Expected: $expected, Got: $actual)"
        ((TESTS_FAILED++))
        return 1
    fi
}

assert_file_exists() {
    local file=$1
    local message=$2
    
    ((TESTS_RUN++))
    if [[ -f "$file" ]]; then
        echo -e "${GREEN}✓ PASS${NC}: $message"
        ((TESTS_PASSED++))
        return 0
    else
        echo -e "${RED}✗ FAIL${NC}: $message (File not found: $file)"
        ((TESTS_FAILED++))
        return 1
    fi
}

assert_service_running() {
    local service=$1
    local message=$2
    
    ((TESTS_RUN++))
    if systemctl is-active "$service" >/dev/null 2>&1; then
        echo -e "${GREEN}✓ PASS${NC}: $message"
        ((TESTS_PASSED++))
        return 0
    else
        echo -e "${RED}✗ FAIL${NC}: $message (Service not running: $service)"
        ((TESTS_FAILED++))
        return 1
    fi
}

assert_pass() {
    local message=$1
    ((TESTS_RUN++))
    echo -e "${GREEN}✓ PASS${NC}: $message"
    ((TESTS_PASSED++))
    return 0
}

assert_fail() {
    local message=$1
    ((TESTS_RUN++))
    echo -e "${RED}✗ FAIL${NC}: $message"
    ((TESTS_FAILED++))
    return 1
}

# Test runner
run_test() {
    local test_func=$1
    echo -e "\nRunning test: ${test_func}"
    $test_func
}

# Print test summary
print_summary() {
    echo -e "\n=== Test Summary ==="
    echo "Tests run: $TESTS_RUN"
    echo -e "Tests passed: ${GREEN}$TESTS_PASSED${NC}"
    echo -e "Tests failed: ${RED}$TESTS_FAILED${NC}"
    
    if [[ $TESTS_FAILED -eq 0 ]]; then
        echo -e "\n${GREEN}All tests passed!${NC}"
        exit 0
    else
        echo -e "\n${RED}Some tests failed!${NC}"
        exit 1
    fi
} 