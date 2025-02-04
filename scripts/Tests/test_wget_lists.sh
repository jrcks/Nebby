#!/bin/bash

# Enable IP forwarding
sudo sysctl -w net.ipv4.ip_forward=1
input="../1_3K.txt"

# Read input file line by line
while IFS= read -r line; do
    arrIN=(${line// / })
    domain="${arrIN[1]}"
    link="${arrIN[2]}"
    postdelays="50"
    predelays="0"
    linkspeeds="200 1000"
    buffsizes="2"

    # Extract the base link
    IFS="/" read -ra parts <<<"$link"
    base_link="${parts[0]}//${parts[2]}"

    # Check if the link is accessible
    wget --tries=1 --timeout=15 "$link" -O temp
    if [ $? -eq 0 ]; then
        echo "$link works fine"
    else
        echo "Going to base link: $base_link"
        link="$base_link"
        # Uncomment the line below if you want to try the base link
        # wget -U Mozilla "$base_link" -O index
    fi

    # Nested loops for test parameters
    for predelay in $predelays; do
        for postdelay in $postdelays; do
            for linkspeed in $linkspeeds; do
                for buffsize in $buffsizes; do
                    test_name="${domain}-${predelay}-${postdelay}-${linkspeed}-${buffsize}"
                    echo "==================="
                    echo "$test_name"
                    echo "==================="
                    echo "$link"
                    echo "==================="

                    # Run the test with the specified parameters
                    ../run_test_wget.sh "$test_name" "$predelay" "$postdelay" "$linkspeed" "$buffsize" "$link"
                    sleep 1
                done
            done
        done
    done
done <"$input"
