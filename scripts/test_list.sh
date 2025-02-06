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

# Formatting variables
INV="\033[7m"
RST_INV="\033[27m"
BLD_RED="\033[1;31m"
BLD_GRN="\033[1;32m"
BLD_YLW="\033[1;33m"
RST="\033[0m"

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
                    ./run_test.sh "$site" "$pre" "$post" "$bandwidth" "$buff" "$link"

                    # Check for errors in test execution
                    if [[ $? -ne 0 ]]; then
                        echo -e "${BLD_RED}Test failed for ${site} at ${link}${RST}"
                        exit 1
                    fi

                    sleep 0.1
                    echo "________________________________________"
                done
            done
        done
    done

    echo -e "\n"
    sleep 0.1

done <"$url_list"

duration=$SECONDS
echo -e "${BLD_GRN}Finished at $(date '+%d/%m/%Y %H:%M:%S') in $((duration / 60)) minutes and $((duration % 60)) seconds\033[0m"
