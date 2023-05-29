from datetime import datetime 

def get_request_list(entries):
    request_list = []
    error_request_list = []
    for index, entry in enumerate(entries):
        request_dict = {}
        try : 
            # Removing requests that had no response
            if entry['response']['status'] == 0 :
                error_request_list.append({'entry': entry, 'error' : "No Response", 'index' : index})
                print("No response for " + str(index))
                continue
            
            request_dict['cId'] = 'NaN'
            if "connection" in entry.keys():
                request_dict['cId'] = entry['connection']
            request_dict['index'] = index
            request_dict['status'] = entry['response']['status']
            request_dict['resourceType'] = entry['_resourceType']
            request_dict['priority'] = entry['_priority']
            # Request Data
            request_dict['url'] = entry['request']['url']
            request_dict['httpVersion'] = entry['request']['httpVersion']
            # Response Data - might vary for different pages -- verify
            request_dict['serverType'] = 'NaN'
            for pair in entry['response']['headers'] :
                if pair['name'] == 'server' :
                    request_dict['serverType'] = pair['value']
                    
            request_dict['contentType'] = entry['response']['content']['mimeType']
            request_dict['contentSize'] = entry['response']['content']['size']
            request_dict['serverIP'] = entry['serverIPAddress']
            request_dict['startDateTime'] = entry['startedDateTime'][:-1] + "+00:00"
            date_string = datetime.fromisoformat(entry['startedDateTime'][:-1] + "+00:00")
            request_dict['startTimestamp'] = datetime.timestamp(date_string)
            request_dict['startTimestamp'] = request_dict['startTimestamp']*1000 
            request_dict['timings'] = entry['timings']
            # Taking the request header, response header and response body size as size
    #         request_dict['requestHeaderSize'] = entry['request']['headersSize']
    #         request_dict['requestBodySize'] = entry['request']['bodySize']
    #         request_dict['responseHeaderSize'] = entry['response']['headersSize']
    #         request_dict['responseBodySize'] = entry['response']['bodySize']
            request_dict['transferSize'] = entry['response']['_transferSize']
            request_list.append(request_dict)
        except Exception as e :
            error_request = {}
            error_request['entry'] = entry
            error_request['error'] = e
            error_request['index'] = index
            error_request_list.append(error_request)
    print('Requests Stats : ')
    print('Total Entries {0}'.format(len(entries)))
    print('Correctly Put {0}'.format(len(request_list)))
    print('Error Generated {0}'.format(len(error_request_list)))
    for pair in error_request_list:
        print('{0:10} {1}'.format(pair['index'], pair['error']))
    return request_list, error_request_list

def get_cid_rq_dict(request_list):
    cid_dict = {}
    cid_dict["NaN"] = []
    for rq in request_list:
        rq_cid = rq['cId']
        if rq_cid == "NaN":
            cid_dict["NaN"].append(rq)
            continue
        rq_cid = int(rq['cId'])
        if rq_cid not in cid_dict :
            cid_dict[rq_cid] = []
        cid_dict[rq_cid].append(rq)
    return cid_dict

def get_port_rq_dict(cid_rq_dict, cid_port_mp):
    port_rq_dict = {}
    count = 0
    port_rq_dict["NaN"] = cid_rq_dict["NaN"]
    for cid in cid_rq_dict:
        if cid != "NaN" :
            if cid not in cid_port_mp:
                print(cid, "present in RQ but not in netlog")
            elif cid_port_mp[cid] in port_rq_dict:
                print("This CId {0} is already has a port {1} mapped to it.".format(cid, cid_port_mp[cid]))
            else :
                count+=1
                port_rq_dict[cid_port_mp[cid]] = cid_rq_dict[cid]
    print("{0} cids got mapped to a unique port.".format(count))
    return port_rq_dict

def get_long_url(url, p):
    # A URL is domain + filePath + query/file
    # We want domain + filePath
    # Removing ?
    url = url.split('?')
    if len(url) > 1 :
        return url[0]
    else :
        url = ''.join(url)
    # removing all files
    new_url = url.split('/')
    if '.' in new_url[-1] :
        new_url[-1] = ''
    correct_url = '/'.join(new_url)
    if p == "y":
        print(correct_url)
        print(url)
        print(' ')
    return correct_url

def get_cid_port_mp(events):
    cid_groupid_mp  = {}
    cid_port_mp = {}
    port_groupid_mp = {}
    for event in events:
        if event['source']['type'] == 5 and ("params" in event) :
            if "group_id" in event['params'] :
                cid_groupid_mp[event['source']['id']] = event['params']['group_id']
            elif "host" in event['params'] :
                cid_groupid_mp[event['source']['id']] = event['params']['host']
        elif event['source']['type'] == 6 and ("params" in event) :
            if "group_id" in event['params'] :
                cid_groupid_mp[event['source']['id']] = event['params']['group_id']
            elif "host" in event['params'] :
                cid_groupid_mp[event['source']['id']] = event['params']['host']
        elif event['source']['type'] == 7 and ("params" in event) :
            if "source_dependency" in event['params']:
                if event['params']['source_dependency']['type'] in [5,6] :
                    t_cid = event['params']['source_dependency']['id']
                    group_id = "NaN"
                    if t_cid in cid_groupid_mp :
                        group_id = cid_groupid_mp[t_cid]
                    cid = event["source"]["id"]
                    cid_groupid_mp[cid] = group_id
            elif "local_address" in event['params']: 
                ip_port_tp = event['params']['local_address']
                port = int(ip_port_tp.split(":")[-1])
                cid = event['source']['id']
                cid_port_mp[cid] = port
    return cid_port_mp, cid_groupid_mp
    
def get_port_rq_summary(port_rq_dict,cid_port_mp,cid_groupid_mp, flows):
    # The size is in Kbs
    port_rq_sum_mp = {}
    for port in port_rq_dict:
        port_rq_sum_mp[port] = {}
        port_rq_sum_mp[port]['RQ'] = 1
        res_type_set = set()
        ser_type_set = set()
        con_type_set = set()
        long_urls = set()
        http_set = set()
        con_size = 0
        cid = set()
        ip = set()
        for rq in port_rq_dict[port]:
            http_set.add(rq['httpVersion'])
            res_type_set.add(rq['resourceType'])
            ser_type_set.add(rq['serverType'])
            con_type_set.add(rq['contentType'])
            long_urls.add((get_long_url(rq['url'], "n"),rq['contentType'], rq['status']))
            con_size += float(rq['contentSize'])/1000
            ip.add(rq['serverIP'])
            cid.add(rq['cId'])
        port_rq_sum_mp[port]['resourceType'] = list(res_type_set)
        port_rq_sum_mp[port]['serverType'] = list(ser_type_set)
        port_rq_sum_mp[port]['contentType'] = list(con_type_set)
        port_rq_sum_mp[port]['longUrls'] = list(long_urls)
        port_rq_sum_mp[port]['contentSize'] = con_size
        port_rq_sum_mp[port]['httpVersions'] = list(http_set)
        port_rq_sum_mp[port]['cidSet'] = list(cid)
        port_rq_sum_mp[port]['serverIPSet'] = list(ip)
        if port != "NaN" :
            port_rq_sum_mp[port]['nebbySize'] = int(flows[str(port)]['last_ack'])/1000
        else :
            port_rq_sum_mp[port]['nebbySize'] = "NaN"
    for key in flows.keys():
        port = int(key)
        if port not in port_rq_dict :
            port_rq_sum_mp[port] = {}
            port_rq_sum_mp[port]['RQ'] = 0
            cid  = list(cid_port_mp.keys())[list(cid_port_mp.values()).index(port)]
            port_rq_sum_mp[port]['domain'] = cid_groupid_mp[cid]
            port_rq_sum_mp[port]['nebbySize'] = int(flows[str(port)]['last_ack'])/1000
    return port_rq_sum_mp

