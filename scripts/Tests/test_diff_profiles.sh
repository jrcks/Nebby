#!/bin/bash

# Configuration Variables
variants="bic cdg dctcp highspeed htcp hybla illinois lp nv scalable vegas veno westwood yeah cubic bbr reno"
delays="95"
speeds="50 100 200 400"

# Loop through each delay and speed
for d in $delays; do
    for s in $speeds; do
        predelay=5
        postdelay=$d
        linkspeed=$s
        buffsize=1

        # Create a directory for the current delay and speed
        output_dir="${d}-ms-${s}-kbps"
        mkdir -p "$output_dir"

        # Loop through each congestion control variant
        for cc in $variants; do
            echo "==========================="
            echo "Testing congestion control: $cc"
            echo "==========================="

            # Run the test with the specified parameters
            ../run_test.sh "$cc" "$predelay" "$postdelay" "$linkspeed" "$buffsize"
            sleep 2

            # Clean up after the test
            ../clean.sh
            sleep 2

            # Copy the traces for the current variant into the output directory
            cp "cc-traces/$cc.csv" "$output_dir/$cc.csv"
        done
    done
done
