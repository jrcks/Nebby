# post delay in ms
postdelay=$2
# Buffer size in bytes
buff=$3
# buffer AQM
aqm=$4
cc=$5
dump=$1

sudo ifconfig ingress mtu 100
#sudo echo "0" > /proc/sys/net/ipv4/tcp_sack
sudo tcpdump -i ingress -w test.pcap &
mm-delay $postdelay mm-link ../traces/bw.trace ../traces/bw.trace --uplink-queue=$aqm --downlink-queue=$aqm --downlink-queue-args="bytes=$buff" --uplink-queue-args="bytes=$buff" ./client.sh $cc
sudo killall tcpdump mm-link mm-delay   