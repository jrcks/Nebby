import sys
import json 

helper = "semantics-helper.py"
nebby_helper = "semantics-nebby-helper.py"

with open(helper) as infile:
    exec(infile.read())
with open(nebby_helper) as infile2:
    exec(infile2.read())

file = sys.argv[1]
path = "../logs/"

netlog_data = json.load(open(path+file+".json"))
har_data = json.load(open(path+file+".har"))

request_list, error_request_list = get_request_list(har_data["log"]["entries"])

cid_rq_dict = get_cid_rq_dict(request_list)

cid_port_mp, cid_groupid_mp = get_cid_port_mp(netlog_data['events'])

print("A connection ID(CID) corresponds to one flow in chrome.")
print("Checking the difference in CIDs")
print("Number of CIDs from RQs (Browser - Websites)", len(cid_rq_dict.keys()))
print("Number of CIDs from NETLOG (All flows started from Browser)", len(cid_port_mp.keys()))

print()
print("The list of CIDs present in RQs and not in NETLOG : ")
diff_s = [key for key in cid_rq_dict if key not in cid_port_mp]
print(diff_s, "Number ", len(diff_s))

print()
port_rq_dict = get_port_rq_dict(cid_rq_dict, cid_port_mp)

print()
flows = process_flows(file, "../measurements/")
print()
print("RQs Ports", len(port_rq_dict.keys()))
print("Netlog Ports", len(cid_port_mp.keys()))
print("Nebby Ports", len(flows.keys()))
print("Ports present in Nebby but not in Netlog(Chrome)")
for key in flows.keys():
    port = int(key)
    ports = [cid_port_mp[key] for key in cid_port_mp]
    if port not in ports:
        print(port)
print()

sum_file = path+"results/"+file+".json"
print("Port wise data saved at " + sum_file)
port_rq_sum_mp = get_port_rq_summary(port_rq_dict,cid_port_mp,cid_groupid_mp, flows)
with open(sum_file, "+w") as f :
    json.dump(port_rq_sum_mp,f)
print()
print("#############################################")
print("Summary of each port")
txt_file = open(path+"results/"+file+".txt", "+w")
version_data = print_port_http_size_type(port_rq_sum_mp, txt_file)
print("This data is saved at ", path+"results/"+file+".txt")
plt_path = path+"results/"+file+".png"
get_http_chart(version_data, plt_path)
print("Chart Saved at ", plt_path)

