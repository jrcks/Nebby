#!/bin/bash

# Configuration Variables
#variants="bic cdg dctcp highspeed htcp hybla illinois lp nv scalable vegas veno westwood yeah cubic bbr reno"

# NOTE: The following "available" CCAs are not detectable by Nebby:
#      cdg hybla illinois nv vegas

variants="bic cubic bbr reno highspeed htcp westwood lp scalable veno dctcp yeah vegas"

link="192.168.178.95"

iterations=25

predelays=(0)
postdelays=(50)
bandwidths=(200)
buffersizes=(2)

output_dir="../measurements"

for cc in $variants; do

    echo "==========================="
    echo "Testing congestion control: $cc"
    echo "==========================="

    # Setting the congestion control algorithm
    sudo /sbin/sysctl -w net.ipv4.tcp_congestion_control="$cc"

    for pre in "${predelays[@]}"; do
        for post in "${postdelays[@]}"; do
            for bandwidth in "${bandwidths[@]}"; do
                for buff in "${buffersizes[@]}"; do

                    echo "==========================="
                    echo "$pre-$post-$bandwidth-$buff"
                    echo "==========================="

                    for i in $(seq 1 $iterations); do

                        echo "--- Iteration $i ---"

                        # Run the test with the specified parameters
                        ./run_test.sh "$cc" "$pre" "$post" "$bandwidth" "$buff" "$link"

                        # Check for errors in test execution
                        if [[ $? -ne 0 ]]; then
                            echo "Test failed for $site at $link"
                            exit 1
                        fi

                        sleep 1

                        mv "$output_dir/$cc-$pre-$post-$bandwidth-$buff-tcp.csv" "$output_dir/$cc$i-$pre-$post-$bandwidth-$buff-tcp.csv"
                        
                        echo "Iteration $i completed."

                        echo "-------------------"
                    done
                done
            done
        done
    done
    sleep 2
done
