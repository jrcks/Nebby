#!/bin/bash
sudo ifconfig ingress mtu 100
sudo sysctl net.ipv4.tcp_sack=0
echo "Launching client..."
cc=$1
link=$2
wget_out="1_3K_wget_out.txt"
#launch the desired client below:
#get the algo from the name of the file
# name=$1
# arrIN=(${name//-/ })
# cc=${arrIN[0]}  
# echo "Client"
# echo $cc

#sudo echo "0" > /proc/sys/net/ipv4/tcp_sack
# sudo tcpdump -i ingress -w aft-btl-test.pcap &
# iperf3 -c [IP_SERVER] -p 2500 -C $cc -t 60 -R --connect-timeout 2000 -M 100
#sudo sysctl net.ipv4.tcp_congestion_control=$1
#iperf -c [IP_SERVER] -p 5000 -t 30 -Z $1
#wget -U Mozilla https://www.youtube.com/ -O index
#wget -U Mozilla https://open.spotify.com/user/deutschegrammophon/playlist/2B11k6zJ2vIJTjOiqz3Y35 -O index
#wget -U Mozilla https://www.instagram.com/static/bundles/es6/FeedPageContainer.js/434e5de15e7c.js -O index
# wget -U Mozilla https://www.reddit.com/r/AskReddit/comments/brlti4/reddit_what_are_some_underrated_apps/ -O index

#wget -U Mozilla [FILE_LINK] -O index
echo $link 

echo $cc >> $wget_out
echo $link >> $wget_out
wget -U Mozilla --tries=1 --timeout=30 $link -O index &>> $wget_out

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
