#!/bin/bash
sudo ifconfig ingress mtu 100
sudo sysctl net.ipv4.tcp_sack=0
echo "Launching client..."
cc=$1
link=$2

#launch the desired client below:
#get the algo from the name of the file
# name=$1
# arrIN=(${name//-/ })
# cc=${arrIN[0]}  
# echo "Client"
# echo $cc

#sudo echo "0" > /proc/sys/net/ipv4/tcp_sack
# sudo tcpdump -i ingress -w aft-btl-test.pcap &
# iperf3 -c 54.254.209.251 -p 2500 -C $cc -t 60 -R --connect-timeout 2000 -M 100
#sudo sysctl net.ipv4.tcp_congestion_control=$1
#iperf -c edith.d2.comp.nus.edu.sg -p 5000 -t 30 -Z $1
#wget -U Mozilla https://www.youtube.com/ -O index
#wget -U Mozilla https://open.spotify.com/user/deutschegrammophon/playlist/2B11k6zJ2vIJTjOiqz3Y35 -O index
#wget -U Mozilla https://www.instagram.com/static/bundles/es6/FeedPageContainer.js/434e5de15e7c.js -O index
# wget -U Mozilla https://www.reddit.com/r/AskReddit/comments/brlti4/reddit_what_are_some_underrated_apps/ -O index

#wget -U Mozilla hombayre.d2.comp.nus.edu.sg:8080/tcpcensus_sigmetrics2020.pdf -O index
echo $link 

wget -U Mozilla $link -O index

# cd ..
# cd selenium/chrome
# cd ..
# cd custom_clients
# python3 spotify.py $name
# sudo ./host 1 youtube.html $cc
# cd ..
# cd ..

sleep 2
echo "DONE!"
# sudo killall iperf 
#sudo killall iperf wget
