#!/bin/bash
input="../top1k.txt"
while IFS= read -r line
do
    arrIN=(${line// / })
    domain=${arrIN[1]}
    link=${arrIN[2]}
    echo "$word"
    postdelays="50"
    predelays="0"
    linkspeeds="200 1000"
    buffsizes="2"
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
    ./run_test.sh $name $predelay $postdelay $linkspeed $buffsize $link
    sleep 1
    ./clean.sh
    sleep 1

    done
    done 
    done
    done
done < "$input"
