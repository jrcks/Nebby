#!/bin/sh

# Exit immediately if a command exits with a non-zero status
set -e

# Install nebby and mahimahi dependencies
DEPS="
    git
    tshark
    net-tools
    python3-matplotlib
    python3-pandas
    python3-sklearn
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
    apache2-dev
"

# Update package list and install dependencies
sudo apt update
sudo apt install -y $DEPS

# Install mahimahi as per http://mahimahi.mit.edu/
cd mahimahi
./autogen.sh || {
    # ltmain.sh is wrongly in the parent dir, not sure how to fix this
    rm ../ltmain.sh
    libtoolize --install --copy
    ./autogen.sh
}
./configure
make
sudo make install
cd ..

# Mark scripts as executable
FILES="
    ./scripts/btl.sh
    ./scripts/clean.sh
    ./scripts/client.sh
    ./scripts/new-btl.sh
    ./scripts/run_test.sh
    ./scripts/simnet.sh
"
chmod +x $FILES

# Echo success message
echo "Installation completed successfully!"
