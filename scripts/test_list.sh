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
bandwidths=(200 1000)
bufsizes=(1 2)

# Get the number of URLs in the list
total_urls=$(wc -l <"$url_list")

# Clamp the max_num_urls parameter and ensure num_urls is at least 1
num_urls=${max_num_urls:-$total_urls}
num_urls=$(((num_urls < 1) ? 1 : (total_urls < num_urls ? total_urls : num_urls)))

# Log the start time and number of URLs to process
echo "Processing $num_urls URLs from $url_list"
echo "Started at: $(date '+%d/%m/%Y %H:%M:%S')"
SECONDS=0

# Loop through the specified number of URLs
for ((i = 1; i <= num_urls; i++)); do
    # Extract site and URL from the CSV
    site=$(sed -n "${i}p" "$url_list" | cut -d ';' -f 1)
    url=$(sed -n "${i}p" "$url_list" | cut -d ';' -f 2)

    # Output the current site and URL
    echo "==================="
    echo "Processing $i: $site"
    echo "URL: $url"
    echo "+++++++++++++++++++"

    # Loop through each combination of parameters
    for pre in "${predelays[@]}"; do
        for post in "${postdelays[@]}"; do
            for bandwidth in "${bandwidths[@]}"; do
                for buf in "${bufsizes[@]}"; do

                    # Run the test for the current URL
                    ./run_test.sh "$site" "$pre" "$post" "$bandwidth" "$buf" "$url"

                    # Check for errors in test execution
                    if [[ $? -ne 0 ]]; then
                        echo "Test failed for $site at $url"
                        exit 1
                    fi

                    sleep 0.1
                    echo "-------------------"
                done
            done
        done
    done

    echo "==================="
    sleep 0.1
done

duration=$SECONDS
echo "Finished at: $(date '+%d/%m/%Y %H:%M:%S') in $((duration / 60)) minutes and $((duration % 60)) seconds"
