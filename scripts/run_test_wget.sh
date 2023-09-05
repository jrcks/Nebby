cc=$1
predelay=$2
postdelay=$3
linkspeed=$4
buffsize=$5
file=$6

./clean.sh

#sudo echo "0" > /proc/sys/net/ipv4/tcp_sack

./simnet_wget.sh $cc $predelay $postdelay $linkspeed $buffsize $file
../analysis/pcap2csv.sh test.pcap

path="../../1_3K"
if [ ! -d "$path" ]; then
    mkdir -p "$path"
    echo "Folder '$path' created."
else
    echo "Folder '$path' already exists."
fi

cp test.pcap-tcp.csv ../../5_1_3K/$cc-tcp.csv
cp test.pcap-udp.csv ../../5_1_3K/$cc-udp.csv
# cp test.pcap-tcp.csv ../measurements/$cc-tcp.csv
# cp test.pcap-udp.csv ../measurements/$cc-udp.csv

rm -f index*
