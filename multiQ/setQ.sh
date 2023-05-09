# dest_port $1 for the flows that need to be routed to queue $2 
iptables -t nat -A PREROUTING -p udp --dport $1 -j NFQUEUE --queue-num $2
