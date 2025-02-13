#!/bin/bash

# Check if the required parameters are provided
if [ $# -ne 1 ]; then
    echo "Usage: $0 <URL>"
    exit 1
fi

# Assign input parameters to meaningful variable names
url="$1"

### Configuration Variables ###

# NOTE: The following "available" CCAs are not detectable by Nebby:
#      cdg hybla illinois nv vegas

#variants=(bic cdg dctcp highspeed htcp hybla illinois lp nv scalable vegas veno westwood yeah cubic bbr reno)
variants=(bic cubic bbr reno highspeed htcp westwood lp scalable veno dctcp yeah vegas)

iterations=25

# From the Paper: 2 Network Profiles are enough for detection all 13 "known" CCAs
# (and are used for the measurements in the paper)
#   both with bandwidth 200
#   both with bottleneck buffer size 2
#   one with 'one-way' delay 50ms and the other with 100ms
#       100ms required for CCAs with similar graphs, like (New) Reno, Illinois and HSTCP
#       It is not stated what a 50ms or 100ms 'one-way' delay means exactly, given that we can configure predelay and postdelay separately

predelays=(0)
postdelays=(50 100)
bandwidths=(200)
buffersizes=(2)

output_dir="../measurements"

### End of Configuration Variables ###

# Formatting variables
INV="\033[7m"
RST_INV="\033[27m"
BLD_RED="\033[1;31m"
BLD_GRN="\033[1;32m"
BLD_YLW="\033[1;33m"
RST="\033[0m"

# Count how many tests will be run
total_tests=$((iterations * ${#variants[@]} * ${#predelays[@]} * ${#postdelays[@]} * ${#bandwidths[@]} * ${#buffersizes[@]}))
echo "Total tests to run: $total_tests"
counter=0

# Log the start time
echo "Started at: $(date '+%d/%m/%Y %H:%M:%S')"
SECONDS=0

for cc in "${variants[@]}"; do

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
                    echo "$cc $pre-$post-$bandwidth-$buff"
                    echo "==========================="

                    for i in $(seq 1 $iterations); do
                        ((counter++))

                        echo "--- $cc $pre-$post-$bandwidth-$buff #$i ---"

                        # Run the test with the specified parameters
                        ./run_test.sh "$cc" "$pre" "$post" "$bandwidth" "$buff" "$url"

                        # Check for errors in test execution
                        if [[ $? -ne 0 ]]; then
                            echo -e "${BLD_RED}Test failed for ${cc} at ${url}${RST}"
                            exit 1
                        fi

                        #sleep 1

                        mv "$output_dir/$cc-$pre-$post-$bandwidth-$buff-tcp.csv" "$output_dir/$cc$i-$pre-$post-$bandwidth-$buff-tcp.csv"
                        
                        echo "$counter out of $total_tests measurements completed."

                        echo "-------------------"
                    done
                done
            done
        done
    done
    sleep 2
done

duration=$SECONDS
echo -e "${BLD_GRN}Finished at $(date '+%d/%m/%Y %H:%M:%S') in $((duration / 60)) minutes and $((duration % 60)) seconds\033[0m"
