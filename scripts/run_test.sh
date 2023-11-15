cc=$1
predelay=$2
postdelay=$3
linkspeed=$4
buffsize=$5
file=$6

./clean.sh

#sudo echo "0" > /proc/sys/net/ipv4/tcp_sack

./simnet.sh $cc $predelay $postdelay $linkspeed $buffsize $file
../analysis/pcap2csv.sh test.pcap

cp test.pcap-tcp.csv ../candidates-measurements/$cc-tcp.csv
cp test.pcap-udp.csv ../candidates-measurements/$cc-udp.csv

rm -f index*
