#num=$(cat candidates.csv | wc -l)
for i in {1..38} #( i = 1; i <= $num; i++ )
do
i+=p
echo $i
site=$(sed -n -e $i candidates-linux.csv | cut -d ';' -f 1)
url=$(sed -n -e $i candidates-linux.csv | cut -d ';' -f 2)
echo $site $url
./run_test.sh $site 0 100 200 2 $url
sleep 1
./clean.sh
sleep 1
done
