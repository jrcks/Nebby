#!/bin/bash

# Check if the required parameters are provided
if [ $# -ne 6 ]; then
    echo "Usage: $0 <congestion_control> <predelay_ms> <postdelay_ms> <bandwidth_kbps> <buffer_size> <link>"
    exit 1
fi

# Assign input parameters to meaningful variable names
cc="$1"
predelay_ms="$2"
postdelay_ms="$3"
bandwidth_kbps="$4"
buffer_size="$5"
link="$6"

# Output file for the trace
dump="test.pcap"

# Calculate Buffer Delay Product (BDP) in bytes
total_delay_ms=$((predelay_ms + postdelay_ms))
bdp=$(($total_delay_ms * bandwidth_kbps * buffer_size / 4))
echo "Calculated BDP: $bdp bytes"

# Print parameters for debugging
echo "Congestion Control: $cc"
echo "Predelay: $predelay_ms ms"
echo "Postdelay: $postdelay_ms ms"
echo "Bandwidth: $bandwidth_kbps kbps"
echo "Buffer Size (1 BDP): $bdp bytes"

# Set Buffer AQM (Active Queue Management) type
aqm="droptail"

# Define trace file location
trace_dir="../traces"
trace_file="$trace_dir/bw.trace"

# Check if the trace directory exists, create it if not
if [ ! -d "$trace_dir" ]; then
    mkdir -p "$trace_dir"
    echo "Created directory: $trace_dir"
fi

# Create or clear the bandwidth trace file
rm -f "$trace_file"
touch "$trace_file"

# Number of entries for the bandwidth trace
num_entries=$(($bandwidth_kbps / 12))

# Generate bandwidth trace entries
for ((i = 1; i <= num_entries; i++)); do
    echo $(((i * 1000) / num_entries)) >>"$trace_file"
done

# Execute the bandwidth test with specified parameters
mm-delay "$predelay_ms" ./btl.sh "$dump" "$postdelay_ms" "$bdp" "$aqm" "$cc" "$link"

# Stop the mm-delay command
sudo killall mm-delay
