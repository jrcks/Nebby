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
buffersizes=(1 2)

# Get the number of URLs in the list
total_urls=$(wc -l <"$url_list")

# Clamp the max_num_urls parameter and ensure num_urls is at least 1
num_urls=${max_num_urls:-$total_urls}
num_urls=$(((num_urls < 1) ? 1 : (total_urls < num_urls ? total_urls : num_urls)))

# Log the start time and number of URLs to process
echo "Processing $num_urls URLs from $url_list"
echo "Started at: $(date '+%d/%m/%Y %H:%M:%S')"
SECONDS=0

# Initialize a counter for processed URLs
counter=0

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
    wget --tries=1 --timeout=15 "$link" -O /dev/null
    if [ $? -ne 0 ]; then
        base_link="${parts[0]}//${parts[2]}"
        echo "Link not accessible. Going to base link: $base_link"
        link="$base_link"
        # Uncomment the line below if you want to try the base link
        # wget -U Mozilla "$base_link" -O index
    fi

    # Output the current site and URL with counter
    echo "==================="
    echo "[$counter / $num_urls] Processing: $site"
    echo "URL: $link"
    echo "+++++++++++++++++++"

    for pre in "${predelays[@]}"; do
        for post in "${postdelays[@]}"; do
            for bandwidth in "${bandwidths[@]}"; do
                for buff in "${buffersizes[@]}"; do
                    # Run the test with the specified parameters
                    ./run_test.sh "$site" "$pre" "$post" "$bandwidth" "$buff" "$link"

                    # Check for errors in test execution
                    if [[ $? -ne 0 ]]; then
                        echo "Test failed for $site at $link"
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

done <"$url_list"

duration=$SECONDS
echo "Finished at: $(date '+%d/%m/%Y %H:%M:%S') in $((duration / 60)) minutes and $((duration % 60)) seconds"
