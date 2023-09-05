#!/bin/sh
#These are for mahimahi

LIST_OF_APPS="protobuf-compiler libprotobuf-dev autotools-dev dh-autoreconf iptables pkg-config dnsmasq-base apache2-bin debhelper libssl-dev ssl-cert libxcb-present-dev libcairo2-dev libpango1.0-dev tshark"

sudo apt update
sudo apt install -y $LIST_OF_APPS

# git clone https://github.com/ravinet/mahimahi
# cd mahimahi
# ./autogen.sh
# ./configure
# make
# sudo make install