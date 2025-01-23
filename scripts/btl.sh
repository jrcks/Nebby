#!/bin/bash

# Check if the required parameters are provided
if [ $# -ne 6 ]; then
    echo "Usage: $0 <output_pcap_file> <postdelay_ms> <buffer_size_bytes> <buffer_aqm> <congestion_control> <link>"
    exit 1
fi

# Assign input parameters to meaningful variable names
dump="$1"         # Output PCAP file name
postdelay_ms="$2" # Post delay in milliseconds
buffer_size="$3"  # Buffer size in bytes
aqm="$4"          # Buffer AQM (Active Queue Management) type
cc="$5"           # Congestion control algorithm
link="$6"         # Network link

# Define trace directory
trace_dir="../traces"
trace_file="$trace_dir/bw.trace"

# Check if the trace directory exists, create it if not
if [ ! -d "$trace_dir" ]; then
    mkdir -p "$trace_dir"
    echo "Created directory: $trace_dir"
fi

# Start capturing network traffic
echo "Starting tcpdump to capture traffic into $dump"
sudo tcpdump -i ingress -w "$dump" &

# Run the mm-link command with specified parameters
echo "Running mm-link with parameters:"
echo "  Post Delay: $postdelay_ms ms"
echo "  Buffer Size: $buffer_size bytes"
echo "  AQM: $aqm"
echo "  Congestion Control: $cc"
echo "  Link: $link"

mm-link "$trace_file" "$trace_file" \
    --uplink-queue="$aqm" \
    --downlink-queue="$aqm" \
    --downlink-queue-args="bytes=$buffer_size" \
    --uplink-queue-args="bytes=$buffer_size" \
    mm-delay "$postdelay_ms" ./client.sh "$cc" "$link"

# Wait a moment before stopping the tcpdump and related processes
sleep 2

# Stop tcpdump and other running processes
echo "Stopping tcpdump and related processes..."
sudo killall tcpdump mm-link mm-delay
