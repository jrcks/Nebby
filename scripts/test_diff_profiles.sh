
variants="bic cdg dctcp highspeed htcp hybla illinois lp nv scalable vegas veno westwood yeah cubic bbr reno"

delays="95"
od="15 25 35 45"
speeds="50 100 200 400"

for d in $delays
do
for s in $speeds
do

predelay=5
postdelay=$d
linkspeed=$s
buffsize=1

mkdir $d-ms-$s-kbps

for cc in $variants
do
echo "==================="
echo $cc
echo "==================="
./run_test.sh $cc $predelay $postdelay $linkspeed $buffsize
sleep 2
./clean.sh
sleep 2

cp cc-traces/$cc.csv $d-ms-$s-kbps/$cc.csv

done 

done
done
