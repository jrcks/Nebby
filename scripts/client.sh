#!/bin/bash

# Check if the required parameters are provided
if [ $# -ne 3 ]; then
    echo "Usage: $0 <cca> <url> <output_dir>"
    exit 1
fi

# Assign input parameters to meaningful variable names
cca="$1"
url="$2"
output_dir="$3"

# Set the output file for wget logs
# wget_output="${output_dir}/wget.log"
wget_output=""

# Check if the output directory exists, create it if not
if [ ! -d "$output_dir" ]; then
    mkdir -p "$output_dir"
    echo "[client.sh] Created directory: $output_dir"
fi

# Set MTU for ingress interface
sudo ifconfig ingress mtu 100

# Disable TCP selective acknowledgment
sudo sysctl net.ipv4.tcp_sack=0 1>/dev/null

# Uncomment and modify the following lines to launch different clients as needed.

# === iperf3 client === #
# Example client launch with iperf3
# echo "[client.sh] Running iperf3 with congestion control: $cca"
# iperf3 -c "$url" -p 8081 -R -C "$cca" -t 60 -M 100

# === wget client === #
# Run wget with the specified url
echo "[client.sh] Executing wget for the url: $url"
if [[ -n "$wget_output" ]]; then
    # If wget_output is set
    echo "$cca" >>"$wget_output"
    echo "$url" >>"$wget_output"
    wget -U Mozilla --tries=1 --timeout=30 "$url" -O "$output_dir/index.html" &>>"$wget_output"
else
    # If wget_output is not set
    wget -U Mozilla --tries=1 --timeout=30 "$url" -O "$output_dir/index.html"
fi

# === selenium client === #
# Run the selenium client
# python3 ../selenium/chrome/spotify.py "$name"

# === custom client === #
# Run the custom c client
# cd ../custom_clients
# gcc ./client.c -o ./client -lpthread
# sudo ./client "$url" 1
# cd - 1> /dev/null

# Or run the custom c sender
# cd ../custom_clients
# gcc ./sender.c -o ./sender -lpthread
# sudo ./sender "$url" "$cca" "./websites/index.html"
# cd - 1>/dev/null

# === quic client === #
#python3.12 ../quic_clients/cloudflare_aioquic.py --output-dir "$output_dir" "$url"

# Wait for any background processes to complete
sleep 1
echo "[client.sh] Finished running client"
