import sys
import subprocess
from subprocess import Popen, PIPE
from shlex import split
import socket   

DEBUG=True

IP = [l for l in ([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")][:1], [[(s.connect(('8.8.8.8', 53)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]) if l][0][0]
print(IP)

def getPorts(app, ip=IP):
    all_ports=[]
    #netstat -putan | grep application_name
    out = subprocess.run("netstat -putan | grep "+app, shell=True, stdout=PIPE)
    entries = str(out.stdout)[2:-1].split('\\n')
    
    if DEBUG: 
        print("All ports attached to:",app)
    for line in entries:
        if str(IP) in line:
            index = line.index(IP)
            all_ports.append(line[index+len(str(IP))+1:].split(' ')[0])
            if DEBUG:
                print(all_ports[-1])
        elif "0.0.0.0" in line:
            index = line.index("0.0.0.0")
            all_ports.append(line[index+8:].split(' ')[0])
            if DEBUG:
                print(all_ports[-1])
    return all_ports

if len(sys.argv) < 2:
    print("usage python3 getPorts.py <app name>")
    sys.exit()
app=sys.argv[1]

print(getPorts(app, IP))
