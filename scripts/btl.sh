# post delay in ms
postdelay=$2
# Buffer size in bytes
buff=$3
# buffer AQM
aqm=$4
cc=$5
link=$6
dump=$1
# sudo ifconfig ingress mtu 100
sudo tcpdump -i ingress -w $dump &
mm-link ../traces/bw.trace ../traces/bw.trace --uplink-queue=$aqm --downlink-queue=$aqm --downlink-queue-args="bytes=$buff" --uplink-queue-args="bytes=$buff" mm-delay $postdelay ./client.sh $cc $link
# sudo killall tcpdump mm-link mm-delay   
sleep 2
sudo killall tcpdump
sudo killall mm-link mm-delay
