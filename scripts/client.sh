#!/bin/bash

# Set MTU for ingress interface
sudo ifconfig ingress mtu 100

# Disable TCP selective acknowledgment
sudo sysctl net.ipv4.tcp_sack=0

echo "Launching client..."

# Assign input parameters to meaningful variable names
congestion_control="$1"
link="$2"
wget_output="wget.log" # Output file for wget logs

# Uncomment and modify the following lines to launch different clients as needed.

# Example client launch with iperf3 (uncomment and set IP_SERVER)
# echo "Running iperf3 with congestion control: $congestion_control"
# iperf3 -c [IP_SERVER] -p 2500 -C "$congestion_control" -t 60 -R --connect-timeout 2000 -M 100

# Log the link
echo "Executing wget for the link: $link"

# Run wget with the specified link
if [[ -n "$wget_output" ]]; then
    # If wget_output is set
    echo "$congestion_control" >>"$wget_output"
    echo "$link" >>"$wget_output"
    wget -U Mozilla --tries=1 --timeout=30 "$link" -O index &>>"$wget_output"
else
    # If wget_output is not set
    wget -U Mozilla --tries=1 --timeout=30 "$link" -O index
fi

# Uncomment the following block to run custom scripts or navigate directories
# cd ..
# cd selenium/chrome
# cd ..
# cd custom_clients
# python3 spotify.py "$name"
# sudo ./host 1 youtube.html "$congestion_control"
# cd ..
# cd ..

sleep 1 # Wait for any background processes to complete

echo "DONE!"
