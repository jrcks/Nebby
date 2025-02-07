#!/bin/bash

# Color variables
RED='\033[0;31m'
GRN='\033[0;32m'
BLD='\033[1;37m'
RST='\033[0m'

# Display the currently active congestion control algorithm
current_cca=$(sysctl -n net.ipv4.tcp_congestion_control)
echo -e "Currently active congestion control algorithm: ${BLD}$current_cca${RST}"

# Display available congestion control algorithms
available_cca=$(sysctl -n net.ipv4.tcp_available_congestion_control)
echo -e "Available congestion control algorithms:\n${BLD}$available_cca${RST}"

# Display currently allowed congestion control algorithms
allowed_cca=$(sysctl -n net.ipv4.tcp_allowed_congestion_control)
echo -e "Allowed congestion control algorithms:\n${BLD}$allowed_cca${RST}"

# Get list of available congestion control algorithms
kernel_version=$(uname -r)
module_cca=$(find /lib/modules/"$kernel_version"/kernel/net/ipv4/ -name 'tcp_*.ko*' -exec basename {} \; | awk -F'[_|.]' '!/diag/ {print $2}' | paste -sd, -)

# Display available algorithms
if [ -n "$module_cca" ]; then
    echo -e "Found the module of the congestion control algorithms:\n${BLD}$module_cca${RST}"
else
    echo -e "${RED}No available congestion control algorithms modules found.${RST}" >&2
    exit 1
fi

# Load the available congestion control algorithms
IFS=',' read -r -a algos <<<"$module_cca"
for cca in "${algos[@]}"; do
    cca=$(echo "$cca" | xargs) # Trim whitespace
    echo -n "Loading congestion control algorithm: ${BLD}$cca${RST}... "
    if sudo modprobe "tcp_$cca"; then
        # Add the loaded algorithm to the allowed list by loading it
        sudo sysctl -w net.ipv4.tcp_congestion_control="$cca" 1>/dev/null
        echo -e "${GRN}Success!${RST}"
    else
        echo -e "${RED}Failed to load!${RST}" >&2
    fi
done

# Reset the congestion control algorithm to the original value
sudo sysctl -w net.ipv4.tcp_congestion_control="$current_cca" 1>/dev/null

# Display instruction to temporarily change the congestion control algorithm
echo -e "To temporarily change the congestion control algorithm run:\n${BLD}sudo sysctl -w net.ipv4.tcp_congestion_control=bbr${RST}"
