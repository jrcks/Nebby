#!/bin/bash

# Configuration Variables
variants="bic cdg dctcp highspeed htcp hybla illinois lp nv scalable vegas veno westwood yeah cubic bbr reno"
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
    ../run_test.sh "$cc" "$predelay" "$postdelay" "$linkspeed" "$buffsize"
    sleep 2
done
