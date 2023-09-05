cc=$1

#pre delay in ms
predelay=$2
# post delay in ms
postdelay=$3
# btl bandwidth in kbps
bw=$4
# Buffer size in bytes, set to 1 BDP
buffBDP=$5
link=$6
bdp=$(($(($(($predelay+$postdelay))*$bw*$buffBDP))/4))
echo $bdp
buff=$bdp #(($(($buffBDP))*$(($bdp))))
echo $buff
# buffer AQM
aqm=droptail

#ssh edith iperf -s -p 3000 &

num=$(($bw/12))

rm -f ../traces/bw.trace
touch ../traces/bw.trace
for (( c=1; c<=$num; c++ ))
do
echo $(($(($c*1000))/$num)) >> ../traces/bw.trace
done
#pcap name
echo $cc
dump=test.pcap
echo $predelay
# mm-delay $predelay ./btl.sh $dump $postdelay $buff $aqm $cc 
mm-delay $predelay ./btl_wget.sh $dump $postdelay $buff $aqm $cc $link
#ssh edith killall iperf
sudo killall mm-delay
