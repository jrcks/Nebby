#!/bin/bash

# Check if the required parameters are provided
if [ $# -ne 1 ]; then
    echo "Usage: $0 <URL>"
    exit 1
fi

# Assign input parameters to meaningful variable names
url="$1"

# Configuration Variables
variants="bic cdg dctcp highspeed htcp hybla illinois lp nv scalable vegas veno westwood yeah cubic bbr reno"

# NOTE: The following "available" CCAs are not detectable by Nebby:
#       cdg hybla illinois nv vegas yeah"

predelay=2
postdelay=48
linkspeed=200
buffsize=1

# Loop through each congestion control variant and run the tests
for cc in $variants; do
    echo "==========================="
    echo "Testing congestion control: $cc"
    echo "==========================="

    # Setting the congestion control algorithm
    sudo /sbin/sysctl -w net.ipv4.tcp_congestion_control="$cc"

    # Run the test for the current variant
    ./run_test.sh "$cc" "$predelay" "$postdelay" "$linkspeed" "$buffsize" "$url"
    sleep 2
done
