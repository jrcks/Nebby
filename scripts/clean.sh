#!/bin/bash

# Stop all running processes
sudo killall iperf iperf3 tcpdump mm-delay mm-link

# Remove the output directory
rm -rf ../measurements

# Remove compiled custom clients
rm ../custom_clients/client ../custom_clients/server ../custom_clients/sender ../custom_clients/receiver
rm -f ../custom_clients/stats.csv
