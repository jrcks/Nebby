cc=$1
rm receiver
gcc receiver_c.c -o receiver 
sudo ./receiver 1 index.html $cc