#!/bin/bash

# Check if the required parameters are provided
if [ $# -ne 2 ]; then
    echo "Usage: $0 <url_list> <max_num_urls>"
    echo "max_num_urls: <= 0 for all urls in list, n for first n urls"
    exit 1
fi

url_list=$1
num_urls=$2

# Configuration Variables
predelays=(0)
postdelays=(50 100)
linkspeeds=(200 1000)
buffsizes=(1 2)

# Get the number of candidates from the CSV file
num=$(wc -l <$url_list)

if [[ $num_urls -gt 0 ]]
then
    num=$(( $num < $num_urls ? $num : $num_urls ))
fi


echo "Num-Urls: $num"
echo "Started at: $(date '+%d/%m/%Y %H:%M:%S')"
SECONDS=0

# Loop through each line number from 1 to the number of candidates
for ((i = 1; i <= 0; i++)); do
    # Adding 'p' to the line number for the sed command
    line_number="${i}p"

    # Extract site and URL from the candidates file
    site=$(sed -n "${line_number}" $url_list | cut -d ';' -f 1)
    url=$(sed -n "${line_number}" $url_list | cut -d ';' -f 2)

    # Output the site and URL
    echo "==================="
    echo "Processing $i: $site"
    echo "URL: $url"
    echo "+++++++++++++++++++"
    for pre in ${predelays[@]}; do
        for post in ${postdelays[@]}; do
            for link in ${linkspeeds[@]}; do
                for size in ${buffsizes[@]}; do
                    # Run the test with the extracted site and URL
                    echo ./run_test.sh "$site" $pre  $post $link $size "$url"
                    ./run_test.sh "$site" $pre  $post $link $size "$url"
                    if [[ $? -ne 0 ]] 
                    then
                        echo "FAILED!"
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
echo "DONE!"