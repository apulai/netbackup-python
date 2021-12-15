import json
import requests
from datetime import datetime, timedelta

# This call will disable invalid https certificate disable_warnings
requests.urllib3.disable_warnings()

nbu_api_key = "A8fmNjyB5DvvzAN1CnRWblMv160U1Vt5hs5P2fqj81pJh9224HRus-w9YuXnwSMa"
nbu_api_hostname = "nbumaster.lab.local"
nbu_api_baseurl = "https://" + nbu_api_hostname + ":1556/netbackup"
asset_id = "84ba26e1-bd89-45c6-9ad4-196b0d8f9287"

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


# Preparing to get VMware assets
#     "/asset-service/workloads/vmware/assets
#     ?page%5Blimit%5D=10
#     &page%5Bdisable%5D=true"
params = {
        'page[limit]': 10,
        'page[offset]': 0
    }


print("GET vmware assets ...", end=" ")
response = requests.get(nbu_api_baseurl +
                        "/asset-service/workloads/vmware/assets",
                        params=params,
                        verify=False,
                        headers=header_v5)
parsed1 = response.json()
print("done:", response.status_code)

if response.status_code != 200:
    print("Error:", response)
    quit(1)
# print(json.dumps(parsed1, indent=4, sort_keys=True))
# print(type(response), type(parsed1))
# print_dict_path('',parsed1)

# print VM assets on screen
for idx, item in enumerate(parsed1['data']):
    if item['attributes']['assetType'] == 'vm':
        print("Index:\t", idx)
        print("Display name:\t", item['attributes']['commonAssetAttributes']['displayName'])
        print("id (referenced by NBU):\t", item['id'])
        print("instanceUuid:\t", item['attributes']['instanceUuid'])
        print("assetType:\t", item['attributes']['assetType'])
        print("vCenter:\t", item['attributes']['vCenter'])
        print("vmAbsolutePath:\t", item['attributes']['vmAbsolutePath'])
        print("lastDiscoveredTime:\t", item['attributes']['commonAssetAttributes']['detection']['lastDiscoveredTime'])
        print("nicIpAddresses:\t", item['attributes']['nicIpAddresses'])
        print("")

i = int(input("Please enter index of the VM: "))

my_display_name = parsed1['data'][i]['attributes']['commonAssetAttributes']['displayName']
my_vcenter = parsed1['data'][i]['attributes']['vCenter']
my_vm_absolutepath = parsed1['data'][i]['attributes']['vmAbsolutePath']

t_now = datetime.now()
t_30_days_ago = t_now - timedelta(days=30)
# print(t_now.strftime('%Y-%m-%dT%H:%M:%SZ'), t_30_days_ago.strftime('%Y-%m-%dT%H:%M:%SZ'))

print()
print("Listing backups for the last 30 days:")
print("Machine index: ", i)
print("Display name: ", parsed1['data'][i]['attributes']['commonAssetAttributes']['displayName'])
asset_id = parsed1['data'][i]['id']
print("NBU asset id: ", asset_id)
print()

# Preparing to list recovery points
# "/recovery-point-service/workloads/vmware/recovery-points",
#          ?page%5Blimit%5D=100&page%5Boffset%5D=0
#           &filter=assetId+eq+%27"+asset_id+"%27+and+%28backupTime+ge+2021-11-01T00%3A00%3A00.000Z%29
#           &include=optionalVmwareRecoveryPointInfo",
params = {
    'page[limit]': 10,
    'page[offset]': 0,
    # 'filter': "assetId eq '"+asset_id+"' and (backupTime ge 2021-11-01T00:00:00.000Z)"
    'filter': "assetId eq '" + asset_id + "' and (backupTime ge " + t_30_days_ago.strftime('%Y-%m-%dT%H:%M:%SZ') + ")",
    'include': 'optionalVmwareRecoveryPointInfo'
}

print("GET vmware recovery points ...", end=" ")
response = requests.get(nbu_api_baseurl +
                        "/recovery-point-service/workloads/vmware/recovery-points",
                        params=params,
                        verify=False,
                        headers=header_v5)
print(" done:", response.status_code)

if response.status_code != 200:
    print("Error:", response)
    quit(1)
# print(response)

parsed2 = response.json()
# print_dict_path('',parsed2)

print()
print("Backups:")
for idx, item in enumerate(parsed2['data']):
    print("Index:\t", idx)
    print("Backup time:\t", item['attributes']['backupTime'])
    print("id (referenced by NBU):\t", item['id'])
    print("JobID:\t", item['attributes']['extendedAttributes']['imageAttributes']['jobId'])
    print("copyNumber:\t", item['attributes']['extendedAttributes']['imageAttributes']['fragments'][0]['copyNumber'])
    print("")
