#!/bin/sh

# Exit immediately if a command exits with a non-zero status
set -e

# Install git and mahimahi dependencies
DEPS="
    git
    # === mahimahi dependencies === #
    protobuf-compiler
    libprotobuf-dev
    autotools-dev
    dh-autoreconf
    iptables
    pkg-config
    dnsmasq-base
    apache2-bin
    debhelper
    libssl-dev
    ssl-cert
    libxcb-present-dev
    libcairo2-dev
    libpango1.0-dev
"

# Update package list and install dependencies
sudo apt update
sudo apt install -y $DEPS

# Install mahimahi as per http://mahimahi.mit.edu/
git clone https://github.com/ravinet/mahimahi
cd mahimahi || { echo "Failed to clone mahimahi."; exit 1; }

# Run the installation steps
./autogen.sh
./configure
make
sudo make install

# Mark scripts as executable
FILES="
    ./scripts/test_wget.sh
    ./scripts/new-btl.sh
    ./scripts/clean.sh
    ./scripts/simnet.sh
    ./scripts/client.sh
"
sudo chmod +x $FILES

# Echo success message
echo "Installation completed successfully!"