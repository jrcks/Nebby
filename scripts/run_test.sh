#!/bin/bash

# +----------------------------------------------+
# | Script to run simulation and process results |
# +----------------------------------------------+

# Set output directory for measurement results
output_dir="../measurements"

# Do you want to delete the original .pcap file after conversion?
delete_pcap_after_conversion=True

# Do you want to disable TCP SACK?
disable_SACK=False

# Assign input parameters to meaningful variable names
cca=$1
predelay=$2
postdelay=$3
link_speed=$4
buffer_size=$5
file_name=$6

# Define colors for output
green="\033[0;32m"
plain="\033[0m"

# +-------------------------------------+
# | Run the simulation and capture data |
# +-------------------------------------+

# Clean previous results
./clean.sh

# Disable TCP SACK if the parameter is True
if [ "$disable_SACK" == "True" ]; then
    sudo sh -c "echo '0' > /proc/sys/net/ipv4/tcp_sack"
fi

# Run the simulation
./simnet.sh "$cca" "$predelay" "$postdelay" "$link_speed" "$buffer_size" "$file_name"

# +-------------------------------------+
# | Convert received .pcap to .csv file |
# +-------------------------------------+

# Assign the input file to a variable for clarity
pcap_file="test.pcap"

echo -e "[${green}Converting received data to .csv format${plain}]"

# Create separate traces for TCP and UDP traffic
# Note: The output CSV for TCP traffic includes specific fields.
tshark -r "$pcap_file" -T fields \
    -o "gui.column.format:\"Time\",\"%Aut\"" \
    -e _ws.col.Time \
    -e frame.time_relative \
    -e tcp.time_relative \
    -e frame.number \
    -e frame.len \
    -e ip.src \
    -e tcp.srcport \
    -e ip.dst \
    -e tcp.dstport \
    -e tcp.len \
    -e tcp.seq \
    -e tcp.ack \
    -E header=y \
    -E separator=, \
    -E quote=d \
    -E occurrence=f >"${pcap_file}-tcp.csv"

# Capture UDP traffic
tshark -r "$pcap_file" -f "udp" -T fields -E header=y -E separator=, -E quote=d >"${pcap_file}-udp.csv"

# Delete PCAP file if the parameter is True
if [ "$delete_pcap_file" == "True" ]; then
    rm "$pcap_file"
fi

# Log the completion of the conversion
echo -e "${green}Conversion completed: ${pcap_file}-tcp.csv and ${pcap_file}-udp.csv generated.${plain}"

# +------------------------------------+
# | Move generated CSV files to output |
# +------------------------------------+

# Create output directory if it doesn't exist
if [ ! -d "$output_dir" ]; then
    mkdir -p "$output_dir"
    echo "Folder '$output_dir' created."
else
    echo "Folder '$output_dir' already exists."
fi

# Copy generated CSV files to the output directory
cp test.pcap-tcp.csv "$output_dir/$congestion_control-tcp.csv"
cp test.pcap-udp.csv "$output_dir/$congestion_control-udp.csv"

# Remove residual index files
# rm -f index*

# Completion message
echo "Test completed successfully."
