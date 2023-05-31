import csv
import matplotlib.pyplot as plt
import sys
import math

SHOW=True
MULTI_GRAPH=False
SMOOTHENING=False
ONLY_STATS=False
s_factor=0.9

'''
TODO: 
o Add functionality where you only plot flows that send more than x bytes of data
o Sort stats and graphs by flow size
o Organize plots by flow size (larger flows have larger graphs)
o Custom smoothening function
'''

fields=["time", "frame_time_rel", "tcp_time_rel", "frame_num", "frame_len", "ip_src", "src_port", "ip_dest", "dest_port", "tcp_len", "seq", "ack"]

class pkt:
    contents=[]
    def __init__(self, fields) -> None:
        self.contents=[]
        for f in fields:
            self.contents.append(f)

    def get(self, field):
        return self.contents[fields.index(field)]
        

def process_flows(cc, dir):
    with open(dir+cc+"-tcp.csv") as csv_file:
        print("Reading "+dir+cc+"-tcp.csv...")
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        total_bytes=0
        '''
        Flow tracking:
        o Identify all packets that are either sourced from or headed to 100.64.0.2
        o Group different flows by client's port
        '''
        flows={}
        data_sent = 0
        port_set = set()
        for row in csv_reader:
            packet=pkt(row)
            validPkt=False
            if line_count==0:
                # reject the header
                line_count+=1
                continue
            if data_sent == 0 : 
                if len(port_set) < 2:
                    if "100.64.0." in packet.get("ip_src") :    
                        port_set.add(packet.get("ip_src"))
                    if "100.64.0." in packet.get("ip_dest") :
                        port_set.add(packet.get("ip_dest"))
                    continue
                else :
                    data_sent = 1
                    port_list = list(port_set)
                    port_list.sort()
                    host_port = port_list[-1]
            if packet.get("ip_src")==host_port and packet.get("frame_time_rel")!='' and packet.get("ack")!='': 
                # we care about this ACK packet
                validPkt=True
                port=packet.get("src_port")
                if port not in flows:
                    flows[port]={"serverip":packet.get("ip_dest"), "serverport":packet.get("dest_port"), "times":[], "windows":[], "cwnd":[], "bif":0, "last_ack":0, "last_seq":0, "pif":0}
                flows[port]["times"].append(float(packet.get("frame_time_rel")))
                flows[port]["bif"]-=(int(packet.get("ack"))-int(flows[port]["last_ack"]))
                flows[port]["last_ack"]=int(packet.get("ack"))
                #flows[port]["windows"].append(int(flows[port]["bif"]))
                flows[port]["pif"]-=1
                flows[port]["cwnd"].append(flows[port]["pif"])
            elif packet.get("ip_dest")==host_port and packet.get("frame_time_rel")!='' and packet.get("seq")!='':
                #we care about this Data packet
                validPkt=True
                port=packet.get("dest_port")
                if port not in flows:
                    flows[port]={"serverip":packet.get("ip_src"), "serverport":packet.get("src_port"), "times":[], "windows":[], "cwnd":[], "bif":0, "last_ack":0, "last_seq":0, "pif":0}
                flows[port]["times"].append(float(packet.get("frame_time_rel")))
                flows[port]["bif"]+=(int(packet.get("seq"))-int(flows[port]["last_seq"]))
                flows[port]["last_seq"]=int(packet.get("seq"))
                flows[port]["pif"]+=1
                flows[port]["cwnd"].append(flows[port]["pif"])
            if SMOOTHENING and validPkt and len(flows[port]["windows"])>2:
                flows[port]["windows"].append(int((s_factor*flows[port]["windows"][-1])+((1-s_factor)*flows[port]["bif"])))
            elif validPkt:
                flows[port]["windows"].append(int(flows[port]["bif"]))
            line_count+=1
            total_bytes+=int(packet.get("frame_len"))
            #print(line_count, total_bytes)
            
        print("total bytes processed:", total_bytes/1000, "KBytes for", cc, "(unlimited)")
    return flows

def custom_smooth_function():
    pass

def get_flow_stats(flows):
    num=len(flows.keys())
    print("FLOW STATISTICS: \nNumber of flows: ", num)
    print("------------------------------------------------------------------------------")
    print('%6s'%"port", '%15s'%"SrcIP", '%8s'%"SrcPort",  '%8s'%"duration",  '%8s'%"start",  '%8s'%"end", '%8s'%"Sent (B)", '%8s'%"Recv (B)",)
    for k in flows.keys():
        print('%6s'%k, '%15s'%flows[k]["serverip"], '%8s'%flows[k]["serverport"], '%8s'%str('%.2f'%(flows[k]["times"][-1]-flows[k]["times"][0])), '%8s'%str('%.2f'%flows[k]["times"][0]), '%8s'%str('%.2f'%flows[k]["times"][-1]), '%8s'%flows[k]["last_seq"], '%8s'%flows[k]["last_ack"])
        #print("    * Flow "+str(k)+": ", flows[k]["last_ack"], " ", flows[k]["last_seq"], " bytes transfered.")
    return num

def get_flow_stats_include(flows, keys):
    num=len(flows.keys())
    print("FLOW STATISTICS: \nNumber of flows: ", num)
    print("------------------------------------------------------------------------------")
    print('%6s'%"port", '%15s'%"SrcIP", '%8s'%"SrcPort",  '%8s'%"duration",  '%8s'%"start",  '%8s'%"end", '%8s'%"Sent (B)", '%8s'%"Recv (B)",)
    for k in flows.keys():
        if int(k) in keys :
            print('%6s'%k, '%15s'%flows[k]["serverip"], '%8s'%flows[k]["serverport"], '%8s'%str('%.2f'%(flows[k]["times"][-1]-flows[k]["times"][0])), '%8s'%str('%.2f'%flows[k]["times"][0]), '%8s'%str('%.2f'%flows[k]["times"][-1]), '%8s'%flows[k]["last_seq"], '%8s'%flows[k]["last_ack"])
            #print("    * Flow "+str(k)+": ", flows[k]["last_ack"], " ", flows[k]["last_seq"], " bytes transfered.")
    return num
