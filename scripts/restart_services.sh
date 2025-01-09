#!/bin/bash

# Restart network-related services script
echo "Restarting network-related services..."

# Restart networking service
sudo systemctl restart networking
echo "Network service restarted"

# Restart dhcpcd service (DHCP client daemon)
sudo systemctl restart dhcpcd
echo "DHCP client daemon restarted"

# Restart wpa_supplicant (wireless networking)
sudo systemctl restart wpa_supplicant
echo "WPA supplicant restarted"

# Optional: restart DNS resolver
sudo systemctl restart systemd-resolved
echo "DNS resolver restarted"

echo "All network services have been restarted"