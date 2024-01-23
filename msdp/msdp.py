import json
import requests
from datetime import datetime, timedelta
import time

# This call will disable invalid https certificate   disable_warnings
requests.urllib3.disable_warnings()

nbu_api_key = "A82V50vDyuSMjBzPULKXZH2x5kIxbIxg1IpL1q78R7jhoCm5wKWR5joAX-MgwM1k"
nbu_api_hostname = "nbuprimary.lab.local"
nbu_api_baseurl = "https://" + nbu_api_hostname + ":1556/netbackup"

nbu_api_content_type_v6 = "application/vnd.netbackup+json;version=6.0"
nbu_api_content_type_v5 = "application/vnd.netbackup+json;version=5.0;charset=UTF-8"
nbu_api_content_type_v3 = "application/vnd.netbackup+json;version=3.0"

header_v6 = {'Accept': nbu_api_content_type_v6,
             'Authorization': nbu_api_key,
             'Content-Type': nbu_api_content_type_v6}

header_v5 = {'Accept': nbu_api_content_type_v5,
             'Authorization': nbu_api_key,
             'Content-Type': nbu_api_content_type_v5}

header_v3 = {'Accept': nbu_api_content_type_v3,
             'Authorization': nbu_api_key,
             'Content-Type': nbu_api_content_type_v3}


# This helper function will print the parsed json (dictionary)
# in an easy to use format.
# After a REST query is completed, You have to select the interesting fields
# The aim of this function is to help you with that.
# INPUT: The parsed response from a request (dict or list)
# OUTPUT: objects with full path and values are printed on STDOUT
# RETURN: none

def print_dict_path(path, obj):
    if isinstance(obj, dict):
        for k, v in obj.items():
            print_dict_path(path + "['" + k + "']", v)
    elif isinstance(obj, list):
        for idx, item in enumerate(obj):
            print_dict_path(path + '[' + str(idx) + ']', item)
    else:
        print(path + " =>", obj)


# Preparing to get catalog data
t_now = datetime.now()
t_30_days_ago = t_now - timedelta(days=30)
print(t_now.strftime('%Y-%m-%dT%H:%M:%SZ'), t_30_days_ago.strftime('%Y-%m-%dT%H:%M:%SZ'))

params = {
    'page[limit]': 10,
    'page[offset]': 0,
    #'filter': "(severity eq 'CRITICAL') or (severity eq 'NOTICE')"
    #'filter': "id gt 831"
    #'filter': "createdDateTime gt 2022-02-14T00:00:00.000Z"
    # not good 'filter': "createdDateTime gt 2022-02-14 01:33:00"
    }

while True:
    print("GET msdp server entries (page:",params['page[offset]'],") ...", end=" ")
    response = requests.get(nbu_api_baseurl +
                            "/config/servers/msdp-servers",
                            params=params,
                            verify=False,
                            headers=header_v6)

    print("done:", response.status_code)
    if response.status_code != 200:
        print("Error:", response)
        quit(1)

    parsed1=response.json()
    # print(json.dumps(parsed1, indent=4, sort_keys=True))
    # print(type(response), type(parsed1))
    print_dict_path('',parsed1)

    quit();
    offset = parsed1['meta']['pagination']['offset']

    # print catalog data on screen
    for idx, item in enumerate(parsed1['data']):
        print("Index\t\t:", idx)
        print("Type\t\t:",item['type'])
        print("ID\t\t:",item['id'])
        print("messageKey\t:",item['attributes']['messageKey'])
        print("createdDateTime\t:",item['attributes']['createdDateTime'])
        print("lastUpdatedDateTime\t:",item['attributes']['lastUpdatedDateTime'])
        print()

    mystr = input("(n for next, p for prev, l for last, f for first q for quit): ")
    if mystr == 'q':
        exit(-1)
    if mystr == 'n':
        try:
            params['page[offset]'] = parsed1['meta']['pagination']['next']
            continue
        except KeyError:
            print("Error redoing query")
            continue
    if mystr == 'p':
        try:
            params['page[offset]'] = parsed1['meta']['pagination']['prev']
            continue
        except KeyError:
            print("Error redoing query")
            continue
    if mystr == 'f':
        try:
            params['page[offset]'] = parsed1['meta']['pagination']['first']
            continue
        except KeyError:
            print("Error redoing query")
            continue
    if mystr == 'l':
        try:
            params['page[offset]'] = parsed1['meta']['pagination']['last']
            continue
        except KeyError:
            print("Error redoing query")
            continue

print("process finished")
