#!/bin/bash

# Color variables
RED='\033[0;31m'
GRN='\033[0;32m'
BLD='\033[1;37m'
RST='\033[0m'

# Display the currently active congestion control algorithm
current_cca=$(sysctl net.ipv4.tcp_congestion_control | awk -F' = ' '{print $2}')
echo -e "Currently active congestion control algorithm: ${BLD}$current_cca${RST}"

# Display currently loaded congestion control algorithms
loaded_algos=$(sysctl -n net.ipv4.tcp_available_congestion_control | tr ' ' ', ')
echo -e "Currently loaded congestion control algorithms: ${BLD}$loaded_algos${RST}"

# Get list of available congestion control algorithms
kernel_version=$(uname -r)
available_algos=$(find /lib/modules/"$kernel_version"/kernel/net/ipv4/ -name 'tcp_*.ko*' -exec basename {} \; | sed 's/^tcp_//' | sed 's/\.ko.*$//' | tr '\n' ',' | sed 's/,$//')

# Display available algorithms
if [ -n "$available_algos" ]; then
    echo -e "Currently available congestion control algorithms: ${BLD}$available_algos${RST}"
else
    echo -e "${RED}No available congestion control algorithms found.${RST}" >&2
    exit 1
fi

# Remove diag from the list of available algorithms
available_algos=$(echo "$available_algos" | sed 's/diag,//')

# Load the available congestion control algorithms
IFS=',' read -r -a algos <<<"$available_algos"

for algo in "${algos[@]}"; do
    algo=$(echo "$algo" | xargs) # Trim whitespace
    echo -n "Loading congestion control algorithm: $algo... "
    if sudo modprobe "tcp_$algo"; then
        echo -e "${GRN}Success!${RST}"
    else
        echo -e "${RED}Failed to load!${RST}" >&2
    fi
done

# Display instruction to temporarily change the congestion control algorithm
echo -e "To temporarily change the congestion control algorithm run:\n${BLD}sudo /sbin/sysctl -w net.ipv4.tcp_congestion_control=bbr${RST}"
