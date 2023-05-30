import sys
from pprint import pprint
import json
file = sys.argv[1]
path = "../logs/"
sum_file = path+"results/"+file+".json"

port_rq_sum_mp = json.load(open(sum_file))

while(True):
    port = input("Enter port number, or x to exit ").strip()
    if port == "x":
        break
    else:
        try : 
            print("Port is", port)
            pprint(port_rq_sum_mp[port])
        except Exception as e :
            print("Error with port ", e)
            print("Try Again")