import json
import requests
from datetime import datetime, timedelta
import time
import getpass

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

def print_attrib(name, item):
    try:
        print(name,item)
    except KeyError:
        print(name," no such key ")

username = input("Please enter username: ")
userpassword = getpass.getpass("Please enter password: ")

params = {
    'page[limit]': 10,
    'page[offset]': 0,
    #'filter': "assetId eq '"+asset_id+"' and (backupTime ge 2021-11-01T00:00:00.000Z)"
    #'filter': "scheduleType eq 'FULL' and (backupTime ge " + t_30_days_ago.strftime('%Y-%m-%dT%H:%M:%SZ') + ")"
    #'filter': "scheduleType eq 'FULL' and policyType eq 'MS-SQL-Server' and clientName eq 'TSTCLUSQLEKR02' and (backupTime ge " + t_30_days_ago.strftime('%Y-%m-%dT%H:%M:%SZ') + ")"
    #'filter': "scheduleType eq 'FULL' and policyType eq 'MS-SQL-Server' and (backupTime ge " + t_30_days_ago.strftime('%Y-%m-%dT%H:%M:%SZ') + ")"
    #'filter': "scheduleType eq 'FULL' and policyType eq 'VMware' and (backupTime ge " + t_30_days_ago.strftime('%Y-%m-%dT%H:%M:%SZ') + ")"
}

body = {
  "domainType": "NT",
  "domainName": "lab",
  "userName": username,
  "password": userpassword
}
print(body)

print("POST login info ...", end=" ")
response = requests.post(nbu_api_baseurl +
                        "/login",
                        json=body,
                        verify=False,
                        headers=header_v6)

print("done:", response.status_code)


response1 = response.json()
# print(json.dumps(response1, indent=4, sort_keys=True))
# print(type(response), type(response1))
print_dict_path('',response1)

if response.status_code != 201:
    print("Error:", response)
else:
    jwt =  response1['token']
    print(jwt)

print("process finished")
