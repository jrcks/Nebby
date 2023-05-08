
delays="10 20 30 40 50 60 70 80 90 100"

for d in $delays
do
echo $d
./run_test.sh p-reddit-$d 2 $d 200 1
sleep 2
./clean.sh
done

echo "=========> Tested Reddit.com"
