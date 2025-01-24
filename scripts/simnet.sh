#!/bin/bash

# Check if the required parameters are provided
if [ $# -ne 8 ]; then
    echo "Usage: $0 <cca> <predelay> <postdelay> <bandwidth> <buffer_size> <url> <dump> <output_dir>"
    exit 1
fi

# Assign input parameters to meaningful variable names
cca="$1"
predelay="$2"
postdelay="$3"
bandwidth="$4"
buffer_size="$5"
url="$6"
dump="$7"
output_dir="$8"

# Calculate Buffer Delay Product (BDP) in bytes
total_delay_ms=$((predelay + postdelay))
bdp=$(($total_delay_ms * bandwidth * buffer_size / 4))
echo "[simnet.sh] Calculated BDP: $bdp bytes"

# Print parameters for debugging
echo "[simnet.sh] Congestion Control: $cca"
echo "[simnet.sh] Predelay: $predelay ms"
echo "[simnet.sh] Postdelay: $postdelay ms"
echo "[simnet.sh] Bandwidth: $bandwidth kbps"
echo "[simnet.sh] Buffer Size (1 BDP): $bdp bytes"

# Set Buffer AQM (Active Queue Management) type
aqm="droptail"

# Define trace file location
trace_file="$output_dir/bw.trace"

# Check if the output directory exists, create it if not
if [ ! -d "$output_dir" ]; then
    mkdir -p "$output_dir"
    echo "[simnet.sh] Created directory: $output_dir"
fi

# Create or clear the bandwidth trace file
rm -f "$trace_file"
touch "$trace_file"

# Number of entries for the bandwidth trace
num_entries=$(($bandwidth / 12))

# Generate bandwidth trace entries
for ((i = 1; i <= num_entries; i++)); do
    echo $(((i * 1000) / num_entries)) >>"$trace_file"
done

# Enable IP forwarding
sudo sysctl -w net.ipv4.ip_forward=1

# Execute the bandwidth test with specified parameters
mm-delay "$predelay" ./btl.sh "$dump" "$postdelay" "$bdp" "$aqm" "$cca" "$url" "$output_dir"

# Stop the mm-delay command
sudo killall mm-delay 2>/dev/null
