#!/bin/bash

# Check if the required parameters are provided
if [ $# -lt 1 ] || [ $# -gt 2 ]; then
    echo "Usage: $0 <url_list> [<max_num_urls>]"
    echo "  <url_list>         : Path to the CSV file containing URLs"
    echo "  <max_num_urls>     : Optional, number of URLs to process. "
    echo "                         Use a positive integer for the first n entries."
    echo "                         Omit for all URLs in the list."
    exit 1
fi

url_list="$1"
max_num_urls="$2"

# Configuration Variables
predelays=(0)
postdelays=(50 100)
bandwidths=(200)
buffersizes=(2)
iterations=50 # TODO

# Formatting variables
INV="\033[7m"
RST_INV="\033[27m"
BLD_RED="\033[1;31m"
BLD_GRN="\033[1;32m"
BLD_YLW="\033[1;33m"
RST="\033[0m"

# Get the number of URLs in the list
total_urls=$(wc -l <"$url_list")

# Clamp the max_num_urls parameter
num_urls=${max_num_urls:-$total_urls}

# Set num_urls to total_urls, if < 1 or > total_urls
num_urls=$(((num_urls < 1) ? total_urls : (total_urls < num_urls ? total_urls : num_urls)))

# Log the start time and number of URLs to process
echo "Processing $num_urls URLs from $url_list"

# Count how many tests will be run
total_tests=$((iterations * num_urls * ${#predelays[@]} * ${#postdelays[@]} * ${#bandwidths[@]} * ${#buffersizes[@]}))
echo "Total tests to run: $total_tests"
# Initialize a counter for processed URLs
counter=0

echo "Started at: $(date '+%d/%m/%Y %H:%M:%S')"
SECONDS=0

for i in $(seq 1 $iterations); do

    echo "==========================="
    echo "Round $i"
    echo "==========================="
    # Read the URL list using a while loop and process only the first num_urls
    while IFS= read -r line && [ "$counter" -lt "$num_urls" ]; do
        # Increment the URL counter
        ((counter++))

        # Extract site and URL from the line
        site=$(echo "$line" | cut -d ';' -f 1)
        link=$(echo "$line" | cut -d ';' -f 2)

        # Extract the base link
        IFS="/" read -ra parts <<<"$link"

        # Check if the link is accessible
        wget --tries=1 --timeout=15 -O /dev/null -q "$link"
        if [ $? -ne 0 ]; then
            base_link="${parts[0]}//${parts[2]}"
            echo -e "${BLD_YLW}Link not accessible. Going to base link: ${base_link}${RST}"
            link="$base_link"
        fi

        # Output the current site and URL with counter
        echo -e "${INV}                                        "
        echo -e "[${counter} / ${num_urls}] Processing: ${site}\nURL: ${link}"
        echo -e "                                        ${RST_INV}"

        for pre in "${predelays[@]}"; do
            for post in "${postdelays[@]}"; do
                for bandwidth in "${bandwidths[@]}"; do
                    for buff in "${buffersizes[@]}"; do
                        # Run the test with the specified parameters
                        #./run_test.sh "$site" "$pre" "$post" "$bandwidth" "$buff" "$link"

                        # Check for errors in test execution
                        if [[ $? -ne 0 ]]; then
                            echo -e "${BLD_RED}Test failed for ${site} at ${link}${RST}"
                            echo "Test failed for ${site}${i}-${pre}-${post}-${bandwidth}-${buff}-${link}" > log.txt
                            #exit 1
                        fi

                        sleep 0.1

                        mv "$output_dir/$site-$pre-$post-$bandwidth-$buff-tcp.csv" "$output_dir/$cc$i-$pre-$post-$bandwidth-$buff-tcp.csv"
                        
                        echo "$counter out of $total_tests measurements completed."
                        echo "________________________________________"
                    done
                done
            done
        done

        echo -e "\n"
        sleep 1

    done <"$url_list"
    sleep 10
done

duration=$SECONDS
echo -e "${BLD_GRN}Finished at $(date '+%d/%m/%Y %H:%M:%S') in $((duration / 60)) minutes and $((duration % 60)) seconds\033[0m"
