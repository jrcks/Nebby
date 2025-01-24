# Set this folder to be the ones containing the training files
PATH="../../../../control_tests_n/" # Fodler with the files for training
yellow = '\033[93m'
green = '\033[92m'
red = '\033[91m'
blue = '\033[94m'
pink = '\033[95m'
black = '\033[90m'
import csv
import matplotlib.pyplot as plt
import sys
import math

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
                if "10.0.0." in packet.get("ip_src"):
                    num = int(packet.get("ip_src")[-1])
                    if num%2==0:
                        data_sent=1
                        host_port=packet.get("ip_src")
                if "10.0.0." in packet.get("ip_dest"):
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

def run(files):
    flows = {}
    for f in files:
        algo_cc=f
        #Get the data for all the flows
        print("==============================================================================")
        print("opening trace ../measurements/"+algo_cc+".csv...")
        flows = process_flows(algo_cc, "./Nebby/measurements-new-btl/50-200-2-60/")
        #decide on final graph layout
        num = get_flow_stats(flows)

        if ONLY_STATS:
            sys.exit()

        if num==1:
            MULTI_GRAPH=False
        #grid size
        if MULTI_GRAPH:
            size=(0,0)
            grids={1:(2,2), 2:(2,2), 4:(2,2), 6:(2,3), 9:(3,3), 12:(3,4), 15:(3,5), 16:(4,4), 20:(5,4), 24:(6,4), 30:(6,5), 36:(6,6), 40:(8,5), 42:(8,7), 49:(7,7)}
            g=num
            while g<=49 and g not in grids:
                g+=1
            if g in grids.keys():
                size=grids[g]
            else:
                size=grids[49]  
            fig, axs = plt.subplots(size[0], size[1])
            for i in range(size[0]):
                for j in range(size[1]):
                    #axs[i][j].legend(loc="lower right")
                    if i==size[0]-1:
                        axs[i][j].set_xlabel("Time (s)")
                    if j==0:
                        axs[i][j].set_ylabel("Bytes in flight")
        else:
            plt.xlabel("Time (s)")
            plt.ylabel("Bytes in flight")
        counter=0
        for port in flows.keys():
            if MULTI_GRAPH:  
                axs[counter%size[0]][(counter//size[0])%size[1]].scatter(flows[port]["times"], flows[port]["windows"], color="#858585")
                axs[counter%size[0]][(counter//size[0])%size[1]].plot(flows[port]["times"], flows[port]["windows"], label=str(port), linestyle="solid")
            else:
                plt.plot(flows[port]["times"], flows[port]["windows"], label=str(port), linestyle="solid")
                plt.scatter(flows[port]["times"], flows[port]["windows"], color="#858585")
            counter+=1
        if MULTI_GRAPH:
            counter=0
            for port in flows.keys():
                axs[counter%size[0]][(counter//size[0])%size[1]].legend()
                counter+=1
        else:
            plt.legend()
        if MULTI_GRAPH:
            fig.set_size_inches(16, 12)
        if SHOW:
            plt.show()
        else:
            plt.savefig("../logs/results/"+algo_cc+".png", dpi=600, bbox_inches='tight', pad_inches=0)
    return flows


def get_window(f,p,t=1,path=PATH):
    algo_cc = f
    flows = process_flows(algo_cc,path,p=p)
#     flows = process_flows(algo_cc, "../measurements/m/",p=p)
#     flows = process_flows(algo_cc, "./Nebby/measurements/",p=p)    
#     flows = process_flows(algo_cc, "./Nebby/measurements-new-btl/50-200-2-60/",p=p)
#     flows = process_flows(algo_cc, "./Nebby/measurements-100-150/",p=p)
    params = algo_cc.split("-")
    data = []
    time = []
    drops = []
    retrans = []
    OOA = []
    DA = []
    use_port = 0
    maxx = 0
    print("All Ports : ", flows.keys())
    for port in flows.keys():
        if len(flows[port]['windows']) > maxx:
            maxx = len(flows[port]['windows'])
            use_port = port
    print("Port",use_port)
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

import matplotlib.pyplot as plt
from scipy.fft import rfft, rfftfreq
from scipy.fft import irfft
import numpy as np
import statistics
from statistics import mean, pstdev
import pandas as pd

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
    # print(f)
    fs = f.split("-")

    pre = int(fs[2])
    post = int(fs[3])
    rtt = float(((pre+post)*2))/1000
    ax = 0
    if t==1:
        data, time, retrans = get_window(f,"n",t,PATH)
    elif t==2:
        data, time, retrans, OOA, DA = get_window(f,"n",t,PATH)
    if p == 'y':
        fig, ax = plt.subplots(1,1, figsize=(15,8))
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
#             plt.savefig("./plots/"+f+".png")
        plt.show()
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
    if len(retrans) > 0  and time[-1] - retrans[-1] > 20*rtt :
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
    start = data.index(min(data[:int(len(data)/2)]))
    end = data.index(max(data[int(len(data)/2):]))
#     print("Difference in max and min ", end-start)
    if end - start <= 0: 
        return time, data
    new_time = time[start:end+1]
    new_data = data[start:end+1]
    return new_time, new_data

# Taking 100 as the threshold is fine 
# Now we have to see how the graphs look if we use it. 
# var = ["reno", "cubic", "bbr"]
def getRed(files,ss=125,p="y", ft_thresh=100):
    results = []
    for file in files :   
        f_split = file.split("-")
        v = f_split[0] + "-" + f_split[1]
        rtt = float((int(f_split[2]) + int(f_split[3]))*2)/1000
        bdp = float(rtt*1000*int(f_split[4])*int(f_split[5]))/8
        # print(file)
        # print("RTT",rtt,"BDP",bdp)
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

from sklearn.metrics import mean_squared_error as mse
def get_degree(time,data, p="n", max_deg=3,cc="default"):
    # print("Degree to fit",max_deg)
    p_net = []
    mse_l = []
    fit_net = []
    for d in range(1,max_deg+1):
        p_temp = np.polyfit(time,data, d)
        # No need of the constant term
        p_net.append(p_temp[0:-1])
        fit_net.append(np.polyval(p_temp,time))
        mse_l.append(mse(data,fit_net[-1]))
    if p =='y':
        plt.plot(time, data,c='k',label='Truth')
        for d in range(max_deg-1, max_deg):
            plot_label = "degree"+str(d)
            plt.plot(time, fit_net[d],label="degree" + str(d+1))
        plt.legend()
        plt.show()
    return max_deg,p_net[max_deg-1], mse_l

def normalize(time, data, rtt, bdp):
    new_time = time - min(time)
    new_data = data - min(data)
    new_time = (new_time/rtt)
    new_data = (new_data/max(new_data))*10
    return new_time, new_data
    
from statistics import mean 
def get_feature_degree(files,ss=225,p='n',ft_thresh=3,max_deg=3):
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
        # print("Name :",name)
        degree, coeff, error_item = get_degree(curr_time, curr_data,p=p,max_deg=max_deg,cc=cc)
        # Adding time feature here
#         coeff_list = list(coeff)
#         coeff_list.append(abs(curr_time[-1]-curr_time[0]))
#         coeff = np.array(coeff_list)
#         print(coeff)
#         print(cc)
#         cc_curr = cc.split("-")[0]
        # Adding another check for scalable and yeah
#         if cc_curr in ['scalable','yeah']:
#             # Look at the fifth coefficient
#             if round(coeff[0],6) < 0.000015:
#                 print(coeff[0])
#                 continue
#         coeff.append(abs(curr_time[-1]-curr_time[0]))
        mp[name] = {'d':degree, 'coeff':coeff, 'error':error_item, 'data':curr_data, 'time':curr_time}
        if cc not in cc_mp :
            cc_mp[cc] = []
        cc_mp[cc].append(mp[name])
    return cc_mp

def getCC(files,cc_mp, p="n"):
    # experiment change start
    cc_coeff = {}
    for file in files :
#         file = v + "-0-50-1000-2"
        curr_file = file
        f_split = file.split("-") 
        cc = f_split[0]
        version = f_split[1]
        v = cc+"-"+version
        if cc not in cc_coeff:
            cc_coeff[cc] = []
    # experiment change end
        time, data, retrans, rtt = plot_one_bt(curr_file, p)
        count = 0
        temp = []
        if v not in cc_mp.keys():
            continue
        n = math.ceil(float(len(cc_mp[v]))/3)
        for item in cc_mp[v]:
            time = item['time']
            data = item['data']
            deg = item['d']
            temp.append(item['coeff'])    
            xlim = 0
            ylim = 0
            t = 1
            while time[-1] > t:
                t*=2
            xlim = t
            while data[-1] > t:
                t*=2
            ylim = t
            lim = max(xlim, ylim)
            # print(lim)
            names = []
            bars=[]
            for i in range(1,deg+1):
                bars.append(i)
                names.append(str(i))
#             print(names)
#             print(item['error'])
            count+=1
            if p == 'y':
                print([round(x,5) for x in item['coeff']])
                plt.plot(time,data)
                plt.plot(time, np.polyval(item['coeff'],time))
                plt.xlim(0,lim)
                plt.ylim(0,lim)
                plt.title(str(count)+" " + cc)
                plt.show()
#                 Showing the coefficient magnitude on a bar plot
#                 plt.figure().set_figwidth(4)
#                 plt.figure().set_figheight(2)
#                 plt.bar([i for i in range(1,deg+2)], item['coeff'])
#                 plt.show()
#                 Showing the change in error magnitute on a bar plot
                plt.figure().set_figwidth(4)
                plt.figure().set_figheight(2)
                plt.bar(bars, item['error'][0:deg], tick_label=names)
                plt.show()
        cc_coeff[cc].append(temp)
    return cc_coeff 


def getCCcoeff(ccs,cc_degree,present_files,ss=225,p="n",ft_thresh=1):
    cc_coeff = {}
    for v in ccs: 
        files = []
        for f in present_files:
            curr_cc = f.split("-")[0]
            if v == curr_cc :
                files.append(f)
        degree = cc_degree[v]
        if len(files) > 0 :
            cc_mp = get_feature_degree(files,ss=ss,p=p,ft_thresh=ft_thresh,max_deg=degree)
            coeff = getCC(files, cc_mp,p=p)
#             print(v)
#             print(files)
            cc_coeff[v] = coeff[v]
        #     getRed(files,p="y")
    return cc_coeff 


def getCoeff(cc_coeff):
    vals = {}
    degree = 0
    for cc in cc_coeff:
        coeff = cc_coeff[cc]
        if cc not in vals :
            vals[cc] = {}
        for trace in coeff:
            i = 1
            for feature in trace:
                if i not in vals[cc]:
                    vals[cc][i] = []
                vals[cc][i].append(feature)
                i+=1
    return vals

def getGaussianParams(vals):
    cc_gaussian_params = {}
    for cc in vals :
        # Taking the first feature only
        if len(list(vals[cc].keys()))==0 :
            continue
        data = vals[cc][1]
        n = 0
        cc_coeff_mean = np.mean(data,axis=0)
        # OGb
#         coeff_var = np.cov(data, rowvar=False)
#         iden = np.identity(len(cc_coeff_mean))
#         cc_coeff_var = coeff_var * iden
        #TRY
        cc_coeff_var = np.cov(data,rowvar=False)
        cc_gaussian_params[cc] = {
            'mean' : cc_coeff_mean,
            'covar' : cc_coeff_var
        }
    return cc_gaussian_params

def train(var,cc_degree,present_files,ss=225):
    cc_coeff = getCCcoeff(var,cc_degree,present_files,ss=ss,ft_thresh=1)
    vals = getCoeff(cc_coeff)
    cc_gaussian_params = getGaussianParams(vals)
    return vals, cc_gaussian_params

def is_pos_def(A):
    if np.allclose(A, A.T):
        try:
            np.linalg.cholesky(A)
            return True
        except np.linalg.LinAlgError:
            return False
    else:
        return False 

from scipy.stats import chi2

# Code Start -------------------------------------------------------------------

ccs = ['bic', 'dctcp', 'highspeed', 'htcp', 'lp', 'nv', 'scalable', 'vegas', 'veno', 'westwood', 'yeah', 'cubic', 'reno']
# First we will get the training files that can be used for traning
dont_use_ind = {}
import pickle

# Loading in the cc_degree map created by running the define_cc_degreee.py file
with open('cc_degree.txt', 'rb') as f:
    cc_degree = pickle.load(f)

total = 51
for cc in ccs:
    temp_check = []
    for i in range(1,total):
        temp_check.append(cc+"-"+str(i)+"-0-50-200-2-aws-88-60")
    cc_mp = get_feature_degree(temp_check, ss=225,p="n",ft_thresh=1,max_deg=cc_degree[cc])
    x = []
    for key in cc_mp.keys():
        x.append(cc_mp[key][0]['coeff'])
    x = np.array(x)
    x_mean = x.mean(axis=0)
    if cc_degree[cc] == 1:
        x_covar = np.array([[np.cov(x, rowvar=False)]])
    else :
        x_covar = np.cov(x, rowvar=False)
    x_covar_inv = np.linalg.inv(x_covar)
    # print(x_mean)
    # print(x_covar)
    # print(is_pos_def(x_covar))
    # print(is_pos_def(x_covar_inv))
    x_diff = x - x_mean
    md = []
    for i in range(len(x_diff)):
        md.append(x_diff[i].dot(x_covar_inv).dot(x_diff[i]))
    p = 1 - chi2.cdf(md, 4)
    ind = []
    thresh = 0.05
    for i in range(len(md)):
        if p[i] < thresh:
            # print(red)
            ind.append(i)
        # print(i,md[i],p[i],p[i]<thresh)
        # print(black)
    dont_use_ind[cc] = ind

usable_ind = {}
print("CC, Total Used, Total Rejected")
for cc in dont_use_ind.keys():
    temp = []
    for i in range(0,total):
        if i not in dont_use_ind[cc]:
            temp.append(i+1)
    usable_ind[cc] = temp
    print(cc, len(temp), len(dont_use_ind[cc]))

import random

def generate_unique_natural_numbers(start_range, end_range, count):
    # If the range is smaller than the required count, adjust the count
    count = min(count, end_range - start_range + 1)

    # Create a list of numbers in the given range
    numbers = list(range(start_range, end_range + 1))

    # Generate unique random numbers using random.sample
    unique_random_numbers = random.sample(numbers, count)

    return unique_random_numbers


# Getting the training files, 100 from all those that can be used, randomly
train_files = []
# test_files = []
count_train_files = 20
for cc in ccs:
    temp_i = generate_unique_natural_numbers(0,len(usable_ind[cc])-1,count_train_files)
#     test_i = []
#     for i in range(0,len(usable_ind[cc])-1):
#         if i not in temp_i:
#             test_i.append(i)
#     test_actual_i = [usable_ind[cc][x] for x in test_i] 
    actual_i = [usable_ind[cc][x] for x in temp_i]
    for i in actual_i:
        file = cc+"-"+str(i)+"-0-50-200-2-aws-88-60"
        train_files.append(file)
#     for i in test_actual_i:
#         file = cc+"-"+str(i)+"-0-50-200-2-aws-88-60"
#         test_files.append(file)
#     print(len(usable_ind[cc]),len(train_files),len(test_files))

# Training for the gaussian params
print("Number of training files", len(train_files))
vals, cc_gaussian_params = train(ccs,cc_degree,train_files,ss=225)

# Saving the cc_gaussian_params:

import pickle
with open("cc_gp.txt",'wb') as f:
    pickle.dump(cc_gaussian_params,f)