import sys
import csv
import random
from matplotlib import pyplot as plt
import numpy as np

PLOT = True
WRITE_TO_FILE = False
WINDOW = 0.1 #should typically be 1 RTT

plot_colors=['#C0C0C0', '#808080', '#000000', '#FF0000', '#800000', '#808000','#008000', '#00FFFF', '#008080', '#0000FF', '#000080', '#FF00FF', '#800080']

fields=["time", "frame_time_rel", "tcp_time_rel", "frame_num", "frame_len", "ip_src", "src_port", "ip_dest", "dest_port", "tcp_len", "seq", "ack"]

class pkt:
    contents=[]
    def __init__(self, fields) -> None:
        self.contents=[]
        for f in fields:
            self.contents.append(f)

    def get(self, field):
        return self.contents[fields.index(field)]

def compute_tp( trace, src_ip, dest_ip):
    sender_throughput={}
    sender_time={}
    """
    Trace format:
    [Frame Number]  [Frame Time] [Frame Size] [Dest IP] [Src IP] [Src Port]
    """
    size={}
    time={}
    # appending only the relavent time and packet size information 
    for row in trace:
        packet=pkt(row)
        port = packet.get("src_port")
        if (packet.get("ip_src")==src_ip and packet.get("ip_dest")==dest_ip):
                if port in time:
                    time[port].append(float(packet.get("tcp_time_rel")))
                    size[port].append(float(packet.get("frame_len")))
                else:
                    time[port]=[float(packet.get("tcp_time_rel"))]
                    size[port]=[float(packet.get("frame_len"))]
                    sender_throughput[port]=[]
                    sender_time[port]=[]
	
    for port in time.keys():
        start_time = 0
        start_sum = 0
        i_fp = 0
        i_bp = 0
        for val in time[port]:
            if val-start_time > WINDOW:
                sender_throughput[port].append(start_sum/(val-start_time))
                sender_time[port].append(val)
                start_sum -= size[port][i_fp]
                i_fp += 1
                start_time = time[port][i_fp]
            start_sum += size[port][i_bp]
            i_bp += 1
        #converting throughput to Mbps
        sender_throughput[port] = [float(8*i/1000000) for i in sender_throughput[port]]	
    return {'time': sender_time,'throughput': sender_throughput}
    #return {'time': np.asarray(sender_time),'throughput': np.asarray(sender_throughput)}

def plotSingle(data):
    plt.title("Throughput")
    plt.xlabel("Time (Seconds)")
    plt.ylabel("Throughput (Mbps)")
    color = int(random.random()*len(plot_colors))
    for port in data['time'].keys():
        plt.plot(data['time'][port], data['throughput'][port])
    #plt.plot( np.asarray(time[src_port[0]]), np.asarray(throughput[src_port[0]]), plot_colors[color], np.asarray(time[src_port[1]]), np.asarray(throughput[src_port[1]]), plot_colors[color+2])
    #plt.tight_layout()
    plt.show()
    plt.legend()

if(len(sys.argv)==1):
	print("This script computes a throughput trace for a given .csv file")
	print("To get the throughput trace X-tp.csv of a file ../pcaps/X.csv,")
	print("Run python3 tp.py X <src ip> <dest ip> ")
	sys.exit(0)

def write_to_file(filename, data):
	""" Function to write processed data into the file"""
	pass

file = "/home/ayush/repos/Nebby/measurements/"+sys.argv[1]+".csv"
input_csv = csv.reader(open(file, 'r'))

processed_data_out = compute_tp(input_csv, sys.argv[2], sys.argv[3])
#processed_data_out = compute_tp(input_csv, sys.argv[3], sys.argv[2], sys.argv[4])

if(PLOT):
	plotSingle(processed_data_out) #, processed_data_out)

if(WRITE_TO_FILE):
	write_to_file(sys.argv[1], processed_data_out)
