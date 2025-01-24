#!/bin/bash

# Check if the required parameters are provided
if [ $# -ne 7 ]; then
    echo "Usage: $0 <dump> <postdelay> <buffer_size> <aqm> <cca> <link> <output_dir>"
    exit 1
fi

# Assign input parameters to meaningful variable names
dump="$1"        # Output PCAP file name
postdelay="$2"   # Post delay in milliseconds
buffer_size="$3" # Buffer size in bytes
aqm="$4"         # Buffer AQM (Active Queue Management) type
cca="$5"         # Congestion control algorithm
link="$6"        # Network link
output_dir="$7"  # Output directory for measurement results

# Define trace directory
trace_file="$output_dir/bw.trace"

# Check if the trace directory exists, create it if not
if [ ! -d "$output_dir" ]; then
    mkdir -p "$output_dir"
    echo "Created directory: $output_dir"
fi

# Start capturing network traffic
echo "Starting tcpdump to capture traffic into $dump"
sudo tcpdump -i ingress -w "$dump" &

# Run the mm-link command with specified parameters
echo "Running mm-link with parameters:"
echo "  Post Delay: $postdelay ms"
echo "  Buffer Size: $buffer_size bytes"
echo "  AQM: $aqm"
echo "  Congestion Control: $cca"
echo "  Link: $link"

mm-link "$trace_file" "$trace_file" \
    --uplink-queue="$aqm" \
    --downlink-queue="$aqm" \
    --downlink-queue-args="bytes=$buffer_size" \
    --uplink-queue-args="bytes=$buffer_size" \
    mm-delay "$postdelay" ./client.sh "$cca" "$link" "$output_dir"

# Wait a moment before stopping the tcpdump and related processes
sleep 2

# Stop tcpdump and other running processes
echo "Stopping tcpdump and related processes..."
sudo killall tcpdump mm-link mm-delay
