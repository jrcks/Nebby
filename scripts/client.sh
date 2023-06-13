sudo ifconfig ingress mtu 100

#sudo echo "0" > /proc/sys/net/ipv4/tcp_sack
#sudo tcpdump -i ingress -w test.pcap &
#sudo sysctl net.ipv4.tcp_congestion_control=$1
#iperf -c edith.d2.comp.nus.edu.sg -p 5000 -t 30 -Z $1
#wget -U Mozilla https://www.youtube.com/ -O index
#wget -U Mozilla https://open.spotify.com/user/deutschegrammophon/playlist/2B11k6zJ2vIJTjOiqz3Y35 -O index
#wget -U Mozilla https://www.instagram.com/static/bundles/es6/FeedPageContainer.js/434e5de15e7c.js -O index
wget -U Mozilla https://www.reddit.com/r/AskReddit/comments/brlti4/reddit_what_are_some_underrated_apps/ -O index

#wget -U Mozilla hombre.d2.comp.nus.edu.sg:8080/tcpcensus_sigmetrics2020.pdf -O index

echo "Launching client..."


#launch the desired client below:
name=$1
cd ..
cd selenium/chrome

#wget -U Mozilla https://www.zhihu.com/people/jie-zhi-61/creations/19573493 -O index
#python3 spotify.py $name

cd ..
cd ..

echo "DONE!"
#sudo killall iperf wget
