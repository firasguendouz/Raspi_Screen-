#!/bin/bash

# Script to run all AP tests
# Must be run with sudo privileges

# Check if script is run as root
if [[ $EUID -ne 0 ]]; then
    echo "This script must be run as root (sudo)"
    exit 1
fi

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Directory containing this script
SCRIPT_DIR="$(dirname "$0")"

# Function to run a test script and check its result
run_test_script() {
    local script=$1
    echo -e "\n=== Running $script ==="
    if "$SCRIPT_DIR/$script"; then
        echo -e "${GREEN}✓ $script passed${NC}"
        return 0
    else
        echo -e "${RED}✗ $script failed${NC}"
        return 1
    fi
}

# Run all test scripts
echo "Starting AP test suite..."

# Track failures
FAILURES=0

# Run individual test scripts
run_test_script "test_setup_ap.sh" || ((FAILURES++))
run_test_script "test_stop_ap.sh" || ((FAILURES++))
run_test_script "test_check_connection.sh" || ((FAILURES++))

# Print final summary
echo -e "\n=== Test Suite Summary ==="
if [[ $FAILURES -eq 0 ]]; then
    echo -e "${GREEN}All tests passed successfully!${NC}"
    exit 0
else
    echo -e "${RED}$FAILURES test scripts failed${NC}"
    exit 1
fi 