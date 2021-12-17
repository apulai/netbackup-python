import json
import requests
from datetime import datetime, timedelta
import time

# This call will disable invalid https certificate disable_warnings
requests.urllib3.disable_warnings()

nbu_api_key = "A8fmNjyB5DvvzAN1CnRWblMv160U1Vt5hs5P2fqj81pJh9224HRus-w9YuXnwSMa"
nbu_api_hostname = "nbumaster.lab.local"
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
    #'filter': "assetId eq '"+asset_id+"' and (backupTime ge 2021-11-01T00:00:00.000Z)"
    'filter': "scheduleType eq 'FULL' and (backupTime ge " + t_30_days_ago.strftime('%Y-%m-%dT%H:%M:%SZ') + ")"
    #'filter': "scheduleType eq 'FULL' and policyType eq 'MS-SQL-Server' and clientName eq 'TSTCLUSQLEKR02' and (backupTime ge " + t_30_days_ago.strftime('%Y-%m-%dT%H:%M:%SZ') + ")"
    #'filter': "scheduleType eq 'FULL' and policyType eq 'MS-SQL-Server' and (backupTime ge " + t_30_days_ago.strftime('%Y-%m-%dT%H:%M:%SZ') + ")"
    #'filter': "scheduleType eq 'FULL' and policyType eq 'VMware' and (backupTime ge " + t_30_days_ago.strftime('%Y-%m-%dT%H:%M:%SZ') + ")"
}

while True:
    print("GET catalog images (page:",params['page[offset]'],") ...", end=" ")
    response = requests.get(nbu_api_baseurl +
                            "/catalog/images",
                            params=params,
                            verify=False,
                            headers=header_v3)

    print("done:", response.status_code)
    if response.status_code != 200:
        print("Error:", response)
        quit(1)
    parsed1 = response.json()
    # print(json.dumps(parsed1, indent=4, sort_keys=True))
    # print(type(response), type(parsed1))
    #print_dict_path('',parsed1)

    offset = parsed1['meta']['pagination']['offset']

    # print catalog data on screen
    for idx, item in enumerate(parsed1['data']):
        print("Index\t:", idx)
        print("Type\t:",item['type'])
        print("ID\t:",item['id'])
        print("policyName\t:",item['attributes']['policyName'])
        print("policyType\t:",item['attributes']['policyType'])
        print("clientName\t:",item['attributes']['clientName'])
        print("scheduleType\t:",item['attributes']['scheduleType'])
        print("backupTime\t:",item['attributes']['backupTime'])
        print("numFiles\t:",item['attributes']['numFiles'])
        print("kbytes\t\t:",item['attributes']['kbytes'])
        print("numberFragments\t:",item['attributes']['numberFragments'])
        print("contentFile\t:",item['attributes']['contentFile'])
        print("keyword\t\t:",item['attributes']['keyword'])
        print("self href\t:", item['links']['self']['href'] )
        print()

    mystr = input("Please enter index of the backup (n for next, p for prev, l for last, f for first q for quit): ")
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

    i=int(mystr)-offset
    break

print(i)
backupId=parsed1['data'][i]['id']
policyName=parsed1['data'][i]['attributes']['policyName']


print("\nGET getting policy details ",policyName,"  ...", end=" ")

params = {
        'page[limit]': 10,
        'page[offset]': 0
    }

response = requests.get(nbu_api_baseurl +
                        '/config/policies/'+policyName,
                        params=params,
                        verify=False,
                        headers=header_v3)
print("done:", response.status_code)
if not (response.status_code == 200 or response.status_code == 202):
    print("Error:", response, " ... policy not found? No policy details!")
else:
    parsed11 = response.json()
    # print(json.dumps(parsed2, indent=4, sort_keys=True))
    # print(type(response), type(parsed2))
    # print_dict_path('',parsed11)
    for idx,item in enumerate(parsed11['data']['attributes']['policy']['backupSelections']['selections']):
        print(idx,"/t:",item)


print("\nGET generating request id for details ...", end=" ")
response = requests.get(nbu_api_baseurl +
                        '/catalog/images/'+backupId+'/contents',
                        params=params,
                        verify=False,
                        headers=header_v3)
print("done:", response.status_code)
if not (response.status_code == 200 or response.status_code == 202):
    print("Error:", response)
    quit(1)
parsed2 = response.json()
# print(json.dumps(parsed2, indent=4, sort_keys=True))
# print(type(response), type(parsed2))
#print_dict_path('',parsed2)
requestId=parsed2['requestId']

params = {
        'page[limit]': 10,
        'page[offset]': 0
    }


print("------------------------")
print("Printing set details:")
print("------------------------")


urlwithrequestid='/catalog/images/contents/'+requestId

counter=1
while True:
    response = requests.get(nbu_api_baseurl +
                        urlwithrequestid,
                        params=params,
                        verify=False,
                        headers=header_v5)
    if response.status_code != 200 and response.status_code != 202:
        break
    parsed4 = response.json()
    # we have this key usually if policy is standard at least
    try:
        value = parsed4['data'][0]['attributes']['filePath']
        printdetails = 1
    except KeyError:
        printdetails = 0
    except IndexError:
        printdetails = 0


    if printdetails == 1:
        for idx,item in enumerate(parsed4['data']):
            print(counter, ":", item['attributes']['filePath']," : ",item['attributes']['fileSize'])
            counter=counter+1
            #print("Most rawban ugyanaz:")
            #print_dict_path('',parsed4)
    else:
        # print(json.dumps(parsed2, indent=4, sort_keys=True))
        # print(type(response), type(parsed2))
        print_dict_path('',parsed4)

    time.sleep(1)

print("process finished")
