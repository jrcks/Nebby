pre_i=1
post_i=2
bw_i=3
bf_i=4

import sys
import csv
import matplotlib.pyplot as plt
import math

import matplotlib.pyplot as plt
from scipy.fft import rfft, rfftfreq
from scipy.fft import irfft
import numpy as np
import statistics
from statistics import mean, pstdev
import pandas as pd


yellow = '\033[93m'
green = '\033[92m'
red = '\033[91m'
blue = '\033[94m'
pink = '\033[95m'
black = '\033[90m'

def smoothen(time, data, rtt):
    # Smoothening 
    left = 0
    right = 0
    run_sum = 0
    avg_data = []
    new_time = []
    roll_time = time
    roll_data = data
    while right < len(roll_time):
        while(right < len(roll_time) and (roll_time[right]-roll_time[left] < 2*rtt)):
            run_sum+=roll_data[right]
            right+=1
        new_time.append(float(roll_time[right-1]+roll_time[left])/2)
        avg_data.append(float(run_sum)/(right-left))
        run_sum-=roll_data[left]
        left+=1
    return new_time, avg_data


def get_fft(data):
    n = len(data)
    data_step = 0.002
    yf = rfft(data)
    xf = rfftfreq(n,data_step)
    return yf,xf

def get_fft_smoothening(data, time, ax,rtt,p):
    rtt=rtt
    yf, xf = get_fft(data)
    thresh  = (1/rtt)
    thresh_ind = 0
    for i in range(len(xf)) :
        freq = xf[i]
        if(freq > thresh):
            thresh_ind = i
            break
            
    yf_clean = yf
    yf_clean[thresh_ind+1:] = 0
    new_f_clean = irfft(yf_clean)
    start_len = len(time) - len(new_f_clean)

    plot_data = new_f_clean
#     if p=="y":
#         ax.plot(time[start_len:], plot_data, 'k', label='FFT smoothening', linewidth=1.5)

    plot_time = time[start_len:] 
    return plot_time, plot_data

def plot_d(ax, time, data, c, l, alpha=1):
    ax.plot(time, data, color=c, lw=2, label = l,alpha=alpha)


def plot_one_bt(f, p,t=1):
#     print(f)
    file_name = f.split("/")[-1]
    fs = file_name.split("-")

    tag = fs[0]
    pre = int(fs[1])
    post = int(fs[2])
    rtt = float(((pre+post)*2))/1000
    ax = 0
    if t==1:
        data, time, retrans = get_window(f,"n",t)
    elif t==2:
        data, time, retrans, OOA, DA = get_window(f,"n",t)
    if p == 'y':
        fig, ax = plt.subplots(1,1, figsize=(15,8))
        plt.title(file_name)
        for t in retrans :
            plt.axvline(x = t, color = 'm',alpha=0.5)
        if t == 2:
            for t in OOA :
                plt.axvline(x = t, color = 'k', lw=2)
            for t in DA:
                plt.axvline(x = t, color = 'g', lw=0.5, alpha = 0.5)
        plot_d(ax,time,data, "r","Original")
    time, data = get_fft_smoothening(data, time, ax,rtt,"y")

    #         plot_d(ax,time,data,"b","FFT Smoothened" )
#         print(len(time), len(data))
    time, data = smoothen(time, data, rtt)
#         print(len(time), len(data))
    if p == 'y':
        plot_d(ax, time, data, "b", "Smoothened",alpha=0.5)
        ax.legend()
        plotfile_name = tag + "-" + str(pre) + "-" + str(post) + "-" + fs[3] + "-" + fs[4] + ".png"
        print("Saved plot to ./plots/"+plotfile_name)
        plt.savefig("./plots/"+plotfile_name)
        #plt.show()
        plt.close(fig)
#     return time, data, grad_time, grad_data, rtt
#     print("Black : OOA, Green : DA, Magenta : RP")
    return time, data, retrans, rtt 


def get_time_features(retrans,time,rtt):
    time_thresh = 20*rtt
    features = []
    for i in range(1, len(retrans)):
        if retrans[i]-retrans[i-1] >= time_thresh:
            features.append([retrans[i-1], retrans[i]])
    # add a feature that finished when the experiment ends
    if len(retrans)>0:
        if time[-1] - retrans[-1] > 20*rtt :
            features.append([retrans[-1],time[-1]])
    return features

def get_features(time, features):
    left = 0
    right = 0
    feature_index = 0
    in_feature = 0
    index_features = []
    while right < len(time) and feature_index < len(features): 
        if in_feature == 0 and time[right]>=features[feature_index][0]:
            in_feature = 1
            left = right
        elif in_feature == 1 and time[right] > features[feature_index][1]:
            in_feature = 0
            index_features.append([left, right-1])
            feature_index+=1
        right+=1
    if in_feature == 1:
        index_features.append([left, right-1])
    return index_features

def get_plot_features(curr_file, p):
    time, data, retrans, rtt = plot_one_bt(curr_file,p=p,t=1)
    time_features = get_time_features(retrans,time,rtt)
    features = get_features(time, time_features)    
    if p == 'y':
        fig, ax = plt.subplots(1,1, figsize=(15,8))
        plot_d(ax, time, data, "b", "Smoothened")
        for ft in features : 
#             print(time[ft[1]]-time[ft[0]])
            ax.plot(time[ft[0]:ft[1]+1], data[ft[0]:ft[1]+1], color = 'r')
        plt.show()
    return time, data, features


SHOW=True
MULTI_GRAPH=False
SMOOTHENING=False
ONLY_STATS=False
s_factor=0.9


PKT_SIZE = 88


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
        

def process_flows(cc, dir,p="y"):
    name = dir+cc+"-tcp.csv"
    with open(name) as csv_file:
        print("Reading "+name+"...")
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        total_bytes=0
        '''
        Flow tracking:
        o Identify all packets that are either sourced from or headed to 10.0.0.2
        o Group different flows by client's port
        '''
        flows={}
        data_sent=0
        # ACK and RTX measurement
        ooa = set()
        rp = set()
        ooaCount=0
        rpCount=0
        daCount=0
        backAck=0
        for row in csv_reader:
            reTx=0
            
            ooAck=0
            dupAck=0
            retPacket=0
            
            packet=pkt(row)
            ackPkt=False
            validPkt=False
            if line_count==0:
                # reject the header
                line_count+=1
                continue
            if data_sent == 0 : 
                if "10.0.0." in packet.get("ip_src") or "100.64.0." in packet.get("ip_src"):
                    num = int(packet.get("ip_src")[-1])
                    if num%2==0:
                        data_sent=1
                        host_port=packet.get("ip_src")
                if "10.0.0." in packet.get("ip_dest") or "100.64.0." in packet.get("ip_dest"):
                    num = int(packet.get("ip_dest")[-1])
                    if num%2==0:
                        data_sent=1
                        host_port=packet.get("ip_dest")
                if data_sent == 0:
                    continue
            if packet.get("ip_src")==host_port and packet.get("frame_time_rel")!='' and packet.get("ack")!='': 
                # we care about this ACK packet
                validPkt=True
                ackPkt=True
                port=packet.get("src_port")
                #PORTCHECK
#                 if int(port) != 50468:
#                     continue
                if port not in flows:
                    flows[port]={"OOA":[],"DA":[],"max_seq":0,"loss_bif":0,"max_ack":int(packet.get("ack")),"serverip":packet.get("ip_dest"), "serverport":packet.get("dest_port"), "act_times":[],"times":[], "windows":[], "cwnd":[], "bif":0, "last_ack":0, "last_seq":0, "pif":0, "drop":[], "next":0, "retrans":[]}
                else:
                    # check for Out of Order Ack (OOA)
                    if int(packet.get("ack")) <= int(flows[port]["max_ack"]):
                        if int(packet.get("ack")) == backAck :
                            dupAck = True
                            flows[port]["DA"].append(float(packet.get("frame_time_rel")))
                        else :
                            ooAck = True
                            flows[port]["OOA"].append(float(packet.get("frame_time_rel")))
                        backAck = int(packet.get("ack"))
                    # update max_ack
                    flows[port]["max_ack"] = max(flows[port]["max_ack"], int(packet.get("ack")))
                    if int(packet.get("seq")) < flows[port]["max_ack"]:
                        reTx += int(packet.get("tcp_len"))
#                     flows[port]["times"].append(float(packet.get("frame_time_rel")) )
                    
            elif packet.get("ip_dest")==host_port and packet.get("frame_time_rel")!='' and packet.get("seq")!='':
                #we care about this Data packet
                validPkt=True
                port=packet.get("dest_port")
                #PORTCHECK
#                 if int(port) != 50468:
#                     continue
                seq=int(packet.get("seq"))
                tcp_len=int(packet.get("tcp_len"))
                if port not in flows:
                    flows[port]={"OOA":[],"DA":[],"max_seq":int(packet.get("seq")),"loss_bif":0,"max_ack":0,"serverip":packet.get("ip_src"), "serverport":packet.get("src_port"),"act_times":[], "times":[], "windows":[], "cwnd":[], "bif":0, "last_ack":0, "last_seq":0, "pif":0, "drop":[], "next":0, "retrans":[]}
                
                else:
                    flows[port]["max_seq"] = max(flows[port]["max_seq"], int(packet.get("seq")))
                
                
                if int(packet.get("seq")) < flows[port]["max_seq"] :
                    retPacket = True
                    flows[port]["retrans"].append(flows[port]["times"][-1])
                    
            if validPkt==True:
                bif = 0
                normal_est_bif = int(flows[port]["max_seq"]) - int(flows[port]["max_ack"]) + PKT_SIZE#+ reTx
                loss_est_bif = flows[port]["loss_bif"]
                if ackPkt and dupAck and len(flows[port]["windows"]) > 10:
                    if dupAck:
                        # if we have received a duplicate ack then we need to reduce the bytes in flight by packet size
                        # we also increase max ack to correct for the consolidated ack being sent later
                        loss_est_bif = int(flows[port]["windows"][-1]) - PKT_SIZE
                        flows[port]["max_ack"] += PKT_SIZE
                        
                        bif = min( normal_est_bif, loss_est_bif)
                        if p == "y" :
                            print(green+"Duplicate Ack",int(packet.get("ack")),"Max Ack",flows[port]["max_ack"],"BIF",bif)
                        
#                     elif ooAck:
#                         # first out of order ack that we have recieved not a duplicated ack
#                         # the reason would be restransimitted packet so dont need to correct for this
                        
                elif ackPkt :
                    loss_est_bif = normal_est_bif 
                    bif = normal_est_bif    
                    if ooAck :
                        ooaCount+=1
                        if p == "y":
                            print(red+"Out of Order Ack",int(packet.get("ack")),"Max Ack",flows[port]["max_ack"],"BIF",normal_est_bif)
                        ooa.add(int(packet.get("ack")))
                    else:
                        if p == "y":
                            print(black+"Inorder Ack",int(packet.get("ack")),"Max Seq",flows[port]["max_seq"],"BIF",normal_est_bif)
                else :
                    bif = normal_est_bif
                    if retPacket==True:
                        rpCount+=1
                        rp.add(int(packet.get("seq")))
                        if p == "y":
                            print(pink+"Retransmitted Packet",int(packet.get("seq")), "Next", flows[port]["max_seq"]+PKT_SIZE, "BIF",bif)
                    else :
                        if p == "y":
                            print(blue+"Inorder Packet", int(packet.get("seq")), "Next", flows[port]["max_seq"]+PKT_SIZE, "BIF",bif)
                flows[port]["loss_bif"] = loss_est_bif
                flows[port]["windows"].append( int(bif) )
                flows[port]["times"].append( float(packet.get("frame_time_rel")) )
                
#                 if ackPkt and dupAck and len(flows[port]["windows"]) > 10: # we have received atleast the first window
# #                     if len(flows[port]["windows"]) < 2000: # print reTx in first 200 packets
# #                         print( packet.get("ack"), flows[port]["max_ack"])
#                     loss_est_bif = int(flows[port]["windows"][-1]) - PKT_SIZE
#                     flows[port]["max_ack"] += PKT_SIZE
#                     bif = min( normal_est_bif, loss_est_bif )
#                 elif ackPkt:
#                     loss_est_bif = normal_est_bif 
#                     bif = normal_est_bif
#                 else:
#                     bif = normal_est_bif
#                 flows[port]["loss_bif"] = loss_est_bif
#                 flows[port]["windows"].append( int(bif) )
            
            
            line_count+=1
            total_bytes+=int(packet.get("frame_len"))
            #print(line_count, total_bytes)
            
#         print("total bytes processed:", total_bytes/1000, "KBytes for", cc, "(unlimited)")
        if p == "y":
            print("Out of Order Acks",len(ooa),"Retransmitted Packets",len(rp))
            print("Count Out of Order Acks",ooaCount,"Retransmitted Packets",rpCount)
            print("OOA",ooa,"RP",rp)
    return flows

def split_path(f):
    path = f.split("/")
    file_name = path[-1][:-8]
    folder_path = "/".join(path[:-1])
    folder_path = folder_path + "/"
    algo_cc = file_name
    return algo_cc, folder_path

def get_window(f,p,t=1):
    algo_cc, folder_path = split_path(f)
    flows = process_flows(algo_cc, folder_path,p=p)
    params = algo_cc.split("-")
    data = []
    time = []
    drops = []
    retrans = []
    OOA = []
    DA = []
    use_port = 0
    maxx = 0
    # print("All Ports : ", flows.keys())
    for port in flows.keys():
        if len(flows[port]['windows']) > maxx:
            maxx = len(flows[port]['windows'])
            use_port = port
    # print("Port",use_port)
    data = flows[use_port]['windows']
    time = flows[use_port]['times']
    retrans = flows[use_port]['retrans']
    OOA = flows[use_port]['OOA']
    DA = flows[use_port]['DA']
    if p == "y":
        plt.plot(time, data)
#     time_index = len(time)-1
#     for index in range(len(flows[use_port]['times'])-1):
#         if flows[use_port]['times'][index+1] - flows[use_port]['times'][index] > :
#             time_index = index
#     time_last = flows[use_port]['times'][time_index]
#     data = data[:time_index+1]
#     time = time[:time_index+1]
    if t==2:
        return data, time, retrans, OOA, DA
    if t==1:
        return data, time, retrans


def getProbes(time, data, rtt, bdp, bw=200):
    if bw==200:
        thresh = 8*rtt
        st_thresh = 0.025
        error = 0.08
        alpha = 1.10
    if bw==1000:
        thresh = 4*rtt
        st_thresh = 0.025
        error = 0.02
        alpha = 1
    probe_index = []
    left = 0
    right = 0
    bdp_thresh = bdp/2
    prev_right = 0
    end = 0
    while right < len(data):
        while right < len(data) and (time[right]-time[left]) < thresh:
            right+=1
        if right == len(data):
            end = 1
            right-=1
        mid = math.floor(left + (right - left)/2)
        mid_val = 0
        left_mid = mid
        right_mid = mid
#         print(left,right)
#         while left_mid > 0 and abs(time[mid]-time[left_mid])<rtt:
#             if data[left_mid] > data[left] and data[left_mid] > data[right]:
#                 mid_val+=1
#             left_mid-=1
#         while right_mid < len(data)-1 and abs(time[right_mid]-time[mid])<rtt:
#             if data[right_mid] > data[left] and data[right_mid] > data[right]:
#                 mid_val+=1
#             right_mid+=1
#         total = right_mid - left_mid
#         peak = 0
#         if round(float(mid_val)/total,2) > 0.99 :
#             print(round(float(mid_val)/total,2))
#             peak=1
        go = 0
        if data[mid] > data[left] and data[mid] > data[right]:
#         if peak == 1:
            #this  is  peak
#             go = 1
            t_l = left
            t_r = right
            while(t_l > 0 and time[left]-time[t_l] < thresh/2):
                t_l-=1
            while(t_r < len(data)-1 and time[t_r]-time[right] < thresh/2):
                t_r+=1
            left_sd = round(np.std(data[t_l:left])/(bdp_thresh*2),3)
            right_sd = round(np.std(data[right:t_r])/(bdp_thresh*2),3)
            if float(abs(data[left]-data[right]))/data[left] < error:
                # this has the left and right points not too different from each other
                side_avg = float((data[left]+data[right]))/2
                local_max = max(data[left:right+1])
#                 go = 1
#                 print("Yes")
                if float(local_max)/side_avg > alpha and local_max > bdp_thresh: 
                    # this means that the peak is quite steep
#                     print("This")
#                     go = 1
                    if (left_sd < st_thresh) and (right_sd < st_thresh):
                        # this means that the lest and right are quite stable respectvely
                        go = 1
#                         print("Out", left_sd, right_sd, st_thresh)
        if go == 1: 
            try :
                probe_index.append([left,right,float(local_max)/side_avg, time[right]-time[left], left_sd, right_sd, t_l,t_r])
            except :
                probe_index.append([left,right])
            #Once you have found something you directly move past it
            left = right-1
        if end:
            right+=1
        left+=1
    return probe_index


def checkBBR(files,p="n"):
    classi = []
    for f in files:
        file_name = f.split("/")[-1]
        para = file_name.split("-")
        rtt = int(para[2])*2
        bw = int(para[3])
        bf = int(para[4])
        bdp = float(bw*rtt*bf)/8
        if bw == 1000 :
            l=5
            r=15
        if bw == 200:
            l=10
            r=20
        try:
            time, data, retrans,rtt = plot_one_bt(f,p=p,t=1)
            probe_index = getProbes(time, data, rtt, bdp, bw)
            # if p=="y":
            #     print_red(time, data, probe_index)
            prev = 0
            time_dis = []
            for p in probe_index:
                curr_ind = data.index(max(data[p[0]:p[1]+1]))
                if curr_ind > p[1] or curr_ind < p[0]:
                    print("Something Wrong")
                if prev != 0:
                    time_dis.append(abs(time[curr_ind]-prev))
                prev = time[curr_ind]
#             print(time_dis)
            count = 0
            isBBR = 0
            for t in time_dis : 
                if  t > l*rtt and t < r*rtt :
                    count+=1
                    if count >= 2: # there are three peaks consecutively
                        isBBR=1
                        break
                else:
                    count = 0
            if isBBR:
                classi.append("YES BBR")
            else:
                if len(probe_index) <= 1 :
                    classi.append("NO BBR")
                else:
                    classi.append("MAYBE BBR")
        except Exception as ex:  
            template = "An exception of type {0} occurred. Arguments:\n{1!r}"
            message = template.format(type(ex).__name__, ex.args)
            new_message = "NC " + message
            classi.append(new_message)
    return classi

def file_filter(file, filter_file="0-50-200-1"):
    if "udp.csv" in file:
        return 0
    else:
        if filter_file in file:
            return 1
        else:
            return 0
 
def getDivision(classi, test_files):
    yes = []
    no = []
    maybe = []
    nan = {}
    for i in range(len(classi)):
        if classi[i] == "YES BBR":
            yes.append(test_files[i])
        elif classi[i] == "NO BBR":
            no.append(test_files[i])
        elif classi[i] == "MAYBE BBR":
            maybe.append(test_files[i])
        else:
            nan[test_files[i]] = classi[i]
    return yes, no,maybe, nan
 
import os 

if (len(sys.argv) < 4):
    print("Usage: python3 checkBBR.py <folder> <filter_file> <print_plots y/n> [output_file]")
    exit()

results = {}
folder=sys.argv[1]+"/"
filter_file = sys.argv[2]

print_plots = sys.argv[3]

if print_plots != "y" and print_plots != "n":
    print("Usage: python3 checkBBR.py <folder> <filter_file> <print_plots y/n> [output_file]")
    exit()

if len(sys.argv) < 5:
    output_file = "a_results"
else:
    output_file = sys.argv[4]

files = []
for f in os.listdir(folder):
    if file_filter(f, filter_file) == 1:
        files.append(folder+f)
files = sorted(files)

if print_plots == "y" or print_plots == "n":
    # create plots folder if not exists
    if not os.path.exists("plots"):
        os.makedirs("plots")

print("...checking for BBR")
classi = checkBBR(files, p=print_plots)

yes,no,maybe,nan = getDivision(classi,files)

print("BBR: ",len(yes)+len(maybe),"Not BBR: ",len(no),"BIF ERROR: ",len(nan))

for f in yes:
    file_name = f.split("/")[-1]
    web_name = file_name.split("-")[0]
    results[web_name] = "BBR"

for f in maybe:
    file_name = f.split("/")[-1]
    web_name = file_name.split("-")[0]
    results[web_name] = "BBR(Maybe)"

for f in nan:
    file_name = f.split("/")[-1]
    web_name = file_name.split("-")[0]
    results[web_name] = "BIF ERROR : " + nan[f]

if (len(no) == 0):
    with open(output_file, "w") as f :
        for web in results:
            formatted_string = f"{web:<40}{results[web]:<60}\n"
            f.write(formatted_string)
    exit()

import bisect
def lower_bound(arr, target):
    index = bisect.bisect_left(arr, target)
    return index

def sample_data_time(time, data, ss, m):
    curr_time, curr_data = adjust(time, data)
    tp = curr_time[len(curr_time)-1] - curr_time[0]
    step = tp/m
    samp_time = [curr_time[0] + i*step for i in range(m)]
    x = np.random.uniform(0,math.pi,ss)
    tr_x = np.cos(x)
    tr_x += 1
    tr_x *= (m-1)/2
    ind = [int(round(e, 0)) for e in tr_x]
    sort_ind = sorted(ind)
    tr_time = [samp_time[i] for i in sort_ind]
    new_time = []
    new_data = []
    for t in tr_time :
        i = lower_bound(curr_time, t)
        temp_t = 0
        temp_d = 0
        if round(t,6) == round(curr_time[i],6):
            temp_t = curr_time[i]
            temp_d = curr_data[i]
        else : 
            if i == 0 :
                temp_t = curr_time[i]
                temp_d = curr_data[i]
            elif i == len(curr_time)-1 :
                temp_t = curr_time[i]
                temp_d = curr_data[i]
            else :
                temp_t = (curr_time[i-1] + curr_time[i])/2
                temp_d = (curr_data[i-1] + curr_data[i])/2
        new_time.append(temp_t)
        new_data.append(temp_d)
    new_data.insert(0,curr_data[0])
    new_data.append(curr_data[-1])
    new_time.insert(0,curr_time[0])
    new_time.append(curr_time[-1])
#     return curr_time, curr_data
    return new_time, new_data

def adjust(time, data):
    try :
        start = data.index(min(data[:int(len(data)/2)]))
        end = data.index(max(data[int(len(data)/2):]))
    except :
        start = 0 
        end = len(data) - 1
    # print("Difference in max and min ", end-start)
    if end - start <= 0: 
        return time, data
    new_time = time[start:end+1]
    new_data = data[start:end+1]
    return new_time, new_data


def getRed_R(files,ss=125,p="y", ft_thresh=100):
    fn_results = []
    for curr_file in files : 
        print(curr_file)
        file, folder_path = split_path(curr_file)
        f_split = file.split("-")
        v = f_split[0]
        rtt = float((int(f_split[pre_i]) + int(f_split[post_i]))*2)/1000
        bdp = float(rtt*1000*int(f_split[bw_i])*int(f_split[bf_i]))/8
        time, data, features = get_plot_features(curr_file, p=p)
        count = 1
        if len(features) == 0:
            # This file gets dropped after this, so we have to save the result here
            results[v] = "NAN - NO FEATURES"
        for ft in features : 
            if count > ft_thresh:
                break
            curr_time = time[ft[0]:ft[1]+1]
            curr_data = data[ft[0]:ft[1]+1]
            tr_time, tr_data = sample_data_time(curr_time, curr_data, ss, 1000)
            tr_time_pd = pd.DataFrame(tr_time)
            tr_data_pd = pd.DataFrame(tr_data)
            tr_time = list(tr_time_pd.rolling(25, center=True).mean().dropna()[0])
            tr_data = list(tr_data_pd.rolling(25, center=True).mean().dropna()[0])
            # print("Feature Length ", len(tr_data))
            if p == "y" :
                plt.plot(curr_time, curr_data, c='b', alpha = 0.5, lw = 5)
                plt.plot(tr_time, tr_data, c='r', alpha = 1)
                plt.scatter(tr_time, tr_data, c='k')
#                 plt.scatter(tr_time, tr_data, c='r', s=10)
                plt.title(v)
                plt.show()
            fn_results.append(
                {v+"_"+"data"+"_"+str(count):tr_data,
                     v+"_"+"time"+"_"+str(count):tr_time,
                        v+"_"+"rtt"+"_"+str(count):rtt, 
                             v+"_"+"bdp"+"_"+str(count):bdp})
            count+=1
    return fn_results

def getRed(files,ss=125,p="y", ft_thresh=100):
    results = []
    for file in files :   
        f_split = file.split("-")
        v = f_split[0] + "-" + f_split[1]
        rtt = float((int(f_split[2]) + int(f_split[3]))*2)/1000
        bdp = float(rtt*1000*int(f_split[4])*int(f_split[5]))/8
        print(file)
        print("RTT",rtt,"BDP",bdp)
        time, data, features = get_plot_features(file, p=p)
        count = 1
        for ft in features : 
            if count > ft_thresh:
                break
            curr_time = time[ft[0]:ft[1]+1]
            curr_data = data[ft[0]:ft[1]+1]
            tr_time, tr_data = sample_data_time(curr_time, curr_data, ss, 1000)
            tr_time_pd = pd.DataFrame(tr_time)
            tr_data_pd = pd.DataFrame(tr_data)
            tr_time = list(tr_time_pd.rolling(25, center=True).mean().dropna()[0])
            tr_data = list(tr_data_pd.rolling(25, center=True).mean().dropna()[0])
            # print("Feature Length ", len(tr_data))
            if p == "y" :
                plt.plot(curr_time, curr_data, c='b', alpha = 0.5, lw = 5)
                plt.plot(tr_time, tr_data, c='r', alpha = 1)
                plt.scatter(tr_time, tr_data, c='k')
#                 plt.scatter(tr_time, tr_data, c='r', s=10)
                plt.title(v)
                plt.show()
            results.append(
                {v+"_"+"data"+"_"+str(count):tr_data,
                     v+"_"+"time"+"_"+str(count):tr_time,
                        v+"_"+"rtt"+"_"+str(count):rtt, 
                             v+"_"+"bdp"+"_"+str(count):bdp})
            count+=1
    return results
# results = getRed(var)

def get_degree_all(time,data, p="n", max_deg=3):
    p_net = []
    mse_l = []
    fit_net = []
    for d in range(1,max_deg+1):
        p_temp = np.polyfit(time,data,d)
        p_net.append(p_temp)
        fit_net.append(np.polyval(p_temp,time))
        mse_l.append(mse(data,fit_net[-1]))
    if p =='y':
#         print("1 ", p1, "MSE ", mse(data, fit_l))
        plt.plot(time, data,c='k',label='Truth')
#         plt.plot(time, fit_l)
        for d in range(0, max_deg):
            plot_label = "degree"+str(d+1)
            plt.plot(time, fit_net[d],label="degree" + str(d+1))
        plt.legend()
        plt.show()
    return max_deg,p_net, mse_l

MAX_DEG=3
from sklearn.metrics import mean_squared_error as mse
def get_degree(time,data, p="n", max_deg=MAX_DEG):
    p_net = []
    mse_l = []
    fit_net = []
    for d in range(1,max_deg+1):
        p_temp = np.polyfit(time,data, d)
        p_net.append(p_temp[0:-1])
        fit_net.append(np.polyval(p_temp,time))
        mse_l.append(mse(data,fit_net[-1]))
    if p =='y':
#         print("1 ", p1, "MSE ", mse(data, fit_l))
        plt.plot(time, data,c='k',label='Truth')
#         plt.plot(time, fit_l)
        for d in range(max_deg-1, max_deg):
            plot_label = "degree"+str(d)
            plt.plot(time, fit_net[d],label="degree" + str(d+1))
        plt.legend()
        plt.show()
    return max_deg,p_net[max_deg-1], mse_l

def normalize(time, data, rtt, bdp):
    new_time = time - min(time)
    new_data = data - min(data)
    new_time = (new_time/max(new_time))*10
    new_data = (new_data/max(new_data))*10    
    return new_time, new_data
    

from statistics import mean 
def get_feature_degree_R(files,ss=225,p='n',ft_thresh=3,max_deg=MAX_DEG):
    results = getRed_R(files,ss,p=p,ft_thresh=ft_thresh)
    if (len(results) == 0):
        print("get_feature_degree_R: No results found")
        return {}
    count_features = 0
    mp = {}
    for item in results :
        for ele in list(item.keys()):
            name_list = ele.split("_")
            website = name_list[0]
            if "data"==name_list[1] :
                curr_data = np.array(item[ele])
            if "time"==name_list[1] :
                curr_time = np.array(item[ele])
            if "rtt"==name_list[1] :
                curr_rtt = item[ele]
            if "bdp"==name_list[1] :
                curr_bdp = item[ele]
        #print(website)
        #print(curr_time, curr_data)
        curr_time, curr_data = normalize(curr_time, curr_data, curr_rtt, curr_bdp)
        count_features += 1
        max_deg,p_net,mse_l = get_degree_all(curr_time, curr_data,p=p,max_deg=max_deg)
        mp[website] = {
        'data':curr_data,
        'time':curr_time,
        "max_deg":max_deg,
        "p_net":p_net,
        "mse_l":mse_l
    }
    return mp

from statistics import mean 
def get_feature_degree(files,ss=225,p='n',ft_thresh=3,max_deg=MAX_DEG):
    results = getRed(files,ss,p=p,ft_thresh=ft_thresh)
    errors = []
    mp = {}
    cc_mp = {}
    count_features = 0
    for item in results :
        for ele in list(item.keys()):
            name_list = ele.split("_")
            cc = name_list[0]
            name = name_list[0] + name_list[-1]
            if "data" in ele :
                curr_data = np.array(item[ele])
            if "time" in ele :
                curr_time = np.array(item[ele])
            if "rtt" in ele :
                curr_rtt = item[ele]
            if "bdp" in ele :
                curr_bdp = item[ele]
        curr_time, curr_data = normalize(curr_time, curr_data, curr_rtt, curr_bdp)
        count_features += 1
        print("Name :",name)
        degree, coeff, error_item = get_degree(curr_time, curr_data,p=p,max_deg=max_deg)
        cc_curr = cc.split("-")[0]
        mp[name] = {'d':degree, 'coeff':coeff, 'error':error_item, 'data':curr_data, 'time':curr_time}
        if cc not in cc_mp :
            cc_mp[cc] = []
        cc_mp[cc].append(mp[name])
    return cc_mp


def getBestDegree(nmp, p="y"):
    results = {}
    too_much_error = {}
    for name in nmp.keys():
        # print(name)
#         curr_time, curr_data, retrans, rtt = plot_one_bt(name+"-0-50-200-2-aws-88-60",'y',1)
        data = nmp[name]['data']
        time = nmp[name]['time']
        max_deg = nmp[name]['max_deg']
        p_net = []
        for coeff in nmp[name]['p_net']:
            temp_pnet = [c for c in coeff]
            p_net.append(temp_pnet)
        mse_l = nmp[name]['mse_l']
        if p == "y":
            plt.plot(time, data,c='k',label='Truth')
    #         plt.plot(time, fit_l)
            for d in range(0, max_deg):
                plot_label = "degree"+str(d+1)
                fit_net = np.polyval(p_net[d],time)
                plt.plot(time, fit_net,label="degree" + str(d+1))
            plt.legend()
            plt.show()

        names = []
        loss = []
        lambd = 0.02
        for i in range(len(mse_l)):
            loss.append((i+1)*sum(p_net[i])*lambd)
        if p == "y":
            print("loss", loss)
            print("mse", mse_l)
            for d in range(0, max_deg):
                names.append("degree "+str(d+1))
            plt.bar(names,mse_l,color='blue',width=0.4,label="mse")
            plt.bar(names,loss,bottom=mse_l,color='maroon',width=0.4,label="reg_loss")

            plt.legend()
            plt.show()
        errors = []
        # The code for deciding the categories
        for i in range(0,max_deg):
            errors.append(loss[i]+mse_l[i])
        deg = errors.index(min(errors))+1
        
        # Error threshold
        error_threshold = 1
        if errors[deg-1] > error_threshold:
            current_cc = name.split("-")[0]
            too_much_error[current_cc]={
                'deg':deg,
                'coeff':p_net[deg-1],
                'error':errors[deg-1]
            }
            continue
        
    #     if deg < 3:
    #         deg = mse_l.index(min(mse_l[0:2]))+1
    #     print(deg)
        current_cc = name.split("-")[0]
        results[current_cc]={
            'deg':deg,
            'coeff':p_net[deg-1],
            'error':errors[deg-1]
        }
    return results, too_much_error

def get_website_by_degree(d):
    labels = []
    result = []
    for web in web_cc_mp:
        if web_cc_mp[web]['deg'] == d:
            labels.append(web)
            result.append(web_cc_mp[web]['coeff'][0:d])
    return {'labels' : labels, 'data' : result}

web_mp = get_feature_degree_R(no,ss=225,p="n",ft_thresh=1,max_deg=3)
web_cc_mp, too_much_error = getBestDegree(web_mp,p="n")

for web in too_much_error:
    results[web] = "TOO MUCH MSE ERROR"

#importing important data
import pickle

# Assumes that these files are located in the same directory as the script
script_dir = os.path.dirname(os.path.realpath(__file__))

scaled_vals = pickle.load(open(script_dir + "/scaled_vals.txt","rb"))
classifiers = pickle.load(open(script_dir + "/classifiers.txt","rb"))
count_to_mp = pickle.load(open(script_dir + "/count_to_mp.txt","rb"))

cc_degree = {
 'bic': 1,
 'dctcp': 2,
 'highspeed': 2,
 'htcp': 3,
 'lp': 2,
 'scalable': 1,
 'veno': 3,
 'westwood': 2,
 'yeah': 1,
 'cubic': 3,
 'reno': 2,
 'cubicQ':3
}
degrees = [1,2,3]

web_data = {}
scaled_web_data = {}
usable_web = {}

print("Checking the files against other CCs")

for degree in degrees:
    web_data[degree]  = get_website_by_degree(degree)
    if len(web_data[degree]['data']) == 0:
        continue
    scaled_web_data[degree] = {'labels':web_data[degree]['labels'], 'data':np.array(scaled_vals[degree]['scaler'].transform(web_data[degree]['data']))}

    if degree in [1,3]:
        thresh = 3
    else:
        thresh = 10
    
    non_outliers_index = []
    x = scaled_web_data[degree]['data']
    l = scaled_web_data[degree]['labels'] 
    for cc in scaled_vals[degree]:
        if cc == 'scaler':
            continue
        for i in range(len(x)):
            isNo = 1
            for d in range(degree):
                if abs(x[i][d]) > thresh:
                    isNo = 0
            if isNo:
                non_outliers_index.append(i)
    non_outliers_index = list(set(non_outliers_index))
    outliers_index = [i for i in range(len(l)) if i not in non_outliers_index]
    for i in outliers_index:
        results[l[i]] = "Outlier with degree fit = " + str(degree)
    usable_web[degree] = non_outliers_index

for degree in degrees:
    if degree not in usable_web:
        continue
    data = []
    labels = []
    for i in usable_web[degree]:
        data.append(scaled_web_data[degree]['data'][i])
        labels.append(scaled_web_data[degree]['labels'][i])

    if (len(data) == 0):
        print("No data for degree", degree)
        continue
    
    clf = classifiers[degree]
    estimates = clf.predict(data)
    prob = clf.predict_proba(data)
    cc_predict = [count_to_mp[degree][i] for i in estimates]
    for i in range(len(labels)):
        results[labels[i]] = cc_predict[i].upper()

print("Writing result to", output_file)
with open(output_file, "w") as f :
    for web in results:
        formatted_string = f"{web:<40}{results[web]:<60}\n"
        f.write(formatted_string)
print("Finished")
exit()




