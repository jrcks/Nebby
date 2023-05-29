import sys
import subprocess
from subprocess import Popen, PIPE
from shlex import split
import socket   

DEBUG=True
STATS=True

IP = [l for l in ([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")][:1], [[(s.connect(('8.8.8.8', 53)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]) if l][0][0]
print(IP)

def parseNetstat(IP, line):
    # return [client_port, src_IP, src_port, protocol]
    client_IP = str(line.split(":")[0].split(" ")[-1])
    client_port = str(line.split(":")[1].split(" ")[0])
    src_IP = str(line.split(":")[1].split(" ")[-1])
    src_port = str(line.split(":")[2].split(" ")[0])
    protocol = str(line.split(" ")[0])
    return client_IP,  client_port, src_IP, src_port, protocol

def getFlows(app, ip=IP):
    all_flows={}
    #netstat -putan | grep application_name
    out = subprocess.run("netstat -putan | grep "+app, shell=True, stdout=PIPE)
    entries = str(out.stdout)[2:-1].split('\\n')
    
    if DEBUG: 
        print("All ports attached to:",app)
    for line in entries:
        print(line)
        if IP in line or "0.0.0.0" in line:
            client_IP, client_port, src_IP, src_port, protocol = parseNetstat(IP, line)
            all_flows[(client_IP, client_port)] = [src_IP, src_port, protocol]
    
    return all_flows

if len(sys.argv) < 2:
    print("usage python3 getPorts.py <app name>")
    sys.exit()
app=sys.argv[1]

flows=getFlows(app, IP)
if STATS:
    print("# of flows: ", len(flows))
    print("-----------------------------------")
    print( '%8s'%"Proto", '%15s'%"ClientIP",  '%6s'%"CPort", '%15s'%"SourceIP",  '%6s'%"SPort")
    for client in flows:
        print( '%8s'%flows[client][2], '%15s'%client[0],  '%6s'%client[1], '%15s'%flows[client][0],  '%6s'%flows[client][1] )
