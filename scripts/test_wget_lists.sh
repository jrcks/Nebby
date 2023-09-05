#!/bin/bash
sudo sysctl -w net.ipv4.ip_forward=1
input="../1_3K.txt"
while IFS= read -r line
do
    arrIN=(${line// / })
    domain=${arrIN[1]}
    link=${arrIN[2]}
    postdelays="50"
    predelays="0"
    linkspeeds="200 1000"
    buffsizes="2"    

    IFS="/" read -ra parts <<< "$link"

    part1="${parts[0]}"
    part2="${parts[2]}"
    delim="//"
    base_link="$part1$delim$part2"
    wget --tries=1 --timeout=15 $link -O temp 
    if [ $? -eq 0 ]; then
        echo "$link works fine" 
    else
        echo "Going to base"
        link=$base_link
        # wget -U Mozilla $base_link -O index
    fi

    for predelay in $predelays
    do
    for postdelay in $postdelays
    do
    for linkspeed in $linkspeeds
    do
    for buffsize in $buffsizes
    do
    name=$domain-$predelay-$postdelay-$linkspeed-$buffsize
    echo "==================="
    echo $name
    echo "==================="
    echo $link
    echo "==================="

    ./run_test_wget.sh $name $predelay $postdelay $linkspeed $buffsize $link
    sleep 1
    ./clean.sh
    sleep 1

    done
    done 
    done
    done
done < "$input"

python3 check_test_runs.py