#!/bin/bash

# Configuration Variables
domain="google.com"
link="www.google.com"
postdelays="50"
predelays="0"
linkspeeds="200 1000"
buffsizes="2"

# Loop through parameters
for predelay in $predelays; do
    for postdelay in $postdelays; do
        for linkspeed in $linkspeeds; do
            for buffsize in $buffsizes; do
                # Constructing the test name
                test_name="${domain}-${predelay}-${postdelay}-${linkspeed}-${buffsize}"
                echo "==================="
                echo "$test_name"
                echo "==================="
                echo "$link"
                echo "==================="

                # Running the test
                ../run_test.sh "$test_name" "$predelay" "$postdelay" "$linkspeed" "$buffsize" "$link"
                sleep 1
            done
        done
    done
done
