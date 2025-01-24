#!/bin/bash

# Check if the required parameters are provided
if [ $# -ne 3 ]; then
    echo "Usage: $0 <cca> <link> <output_dir>"
    exit 1
fi

# Assign input parameters to meaningful variable names
cca="$1"
link="$2"
output_dir="$3"

# Set the output file for wget logs
wget_output="${output_dir}/wget.log"

# Check if the output directory exists, create it if not
if [ ! -d "$output_dir" ]; then
    mkdir -p "$output_dir"
    echo "Created directory: $output_dir"
fi

# Set MTU for ingress interface
sudo ifconfig ingress mtu 100

# Disable TCP selective acknowledgment
sudo sysctl net.ipv4.tcp_sack=0

echo "Launching client..."

# Uncomment and modify the following lines to launch different clients as needed.

# Example client launch with iperf3 (uncomment and set IP_SERVER)
# echo "Running iperf3 with congestion control: $cca"
# iperf3 -c [IP_SERVER] -p 2500 -C "$cca" -t 60 -R --connect-timeout 2000 -M 100

# Log the link
echo "Executing wget for the link: $link"

# Run wget with the specified link
if [[ -n "$wget_output" ]]; then
    # If wget_output is set
    echo "$cca" >>"$wget_output"
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
# sudo ./host 1 youtube.html "$cca"
# cd ..
# cd ..

sleep 1 # Wait for any background processes to complete

echo "DONE!"
