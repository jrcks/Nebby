variants="bic cdg dctcp highspeed htcp hybla illinois lp nv scalable vegas veno westwood yeah cubic bbr reno"

predelay=2
postdelay=48
linkspeed=200
buffsize=1

for cc in $variants; do
    echo "==================="
    echo $cc
    echo "==================="
    ./run_test.sh $cc $predelay $postdelay $linkspeed $buffsize
    sleep 2
    ./clean.sh
    sleep 2
done
