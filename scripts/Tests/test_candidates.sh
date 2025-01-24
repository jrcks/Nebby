#!/bin/bash

# Get the number of candidates from the CSV file
num=$(wc -l <candidates-linux.csv)

# Loop through each line number from 1 to the number of candidates
for ((i = 1; i <= num; i++)); do
    # Adding 'p' to the line number for the sed command
    line_number="${i}p"

    # Extract site and URL from the candidates file
    site=$(sed -n "${line_number}" candidates-linux.csv | cut -d ';' -f 1)
    url=$(sed -n "${line_number}" candidates-linux.csv | cut -d ';' -f 2)

    # Output the site and URL
    echo "==================="
    echo "Processing: $site"
    echo "URL: $url"
    echo "==================="

    # Run the test with the extracted site and URL
    ../run_test.sh "$site" 0 100 200 2 "$url"
    sleep 1

    # Clean up after the test
    ../clean.sh
    sleep 1
done
