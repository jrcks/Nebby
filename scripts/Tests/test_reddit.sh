#!/bin/bash

# Define delay values
delays="10 20 30 40 50 60 70 80 90 100"

# Loop through each delay value
for d in $delays; do
    echo "Running test with delay: $d"

    # Execute the test command with specified parameters
    ../run_test.sh "p-reddit-$d" 2 "$d" 200 1
    sleep 2
done

# Confirmation message after tests
echo "=========> Tested Reddit.com"
