#!/bin/bash

# Check if the required parameters are provided
if [ $# -ne 7 ]; then
    echo "Usage: $0 <dump> <postdelay> <buffer_size> <aqm> <cca> <link> <output_dir>"
    exit 1
fi

# Assign input parameters to meaningful variable names
dump="$1"               # Output file for packet capture
postdelay_ms="$2"       # Post delay in milliseconds
buffer_size="$3"        # Buffer size in bytes
aqm="$4"                # Buffer AQM (Active Queue Management) type
congestion_control="$5" # Congestion control algorithm
link="$6"               # Network link
output_dir="$7"         # Output directory for measurement results

# Define trace file location
trace_file="$output_dir/bw.trace"

# Check if the output directory exists, create it if not
if [ ! -d "$output_dir" ]; then
    mkdir -p "$output_dir"
    echo "Created directory: $output_dir"
fi

# Set the MTU for the ingress interface
sudo ifconfig ingress mtu 100

# (Optional) Disable TCP selective acknowledgement
# sudo sysctl -w net.ipv4.tcp_sack=0

# Start capturing network traffic
sudo tcpdump -i ingress -w "$dump" &

# Run the mm-link command with specified parameters
mm-delay "$postdelay_ms" mm-link "$trace_file" "$trace_file" \
    --uplink-queue="$aqm" \
    --downlink-queue="$aqm" \
    --downlink-queue-args="bytes=$buffer_size" \
    --uplink-queue-args="bytes=$buffer_size" \
    ./client.sh "$congestion_control" "$link"

# Stop capturing with tcpdump and other processes
sudo killall tcpdump mm-link mm-delay
