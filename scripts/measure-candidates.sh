for i in {1..10}
do
i+=p
#file=$((
site=$(sed -n -e $i candidates.csv)
./run_test.sh $site-test 0 50 200 2 $site
sleep 2
./clean.sh
done
