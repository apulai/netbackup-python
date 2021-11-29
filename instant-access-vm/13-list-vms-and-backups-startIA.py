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

export_data = {'nbu_api_baseurl': nbu_api_baseurl,
             'nbu_api_key': nbu_api_key}

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
        for index, item in enumerate(obj):
            print_dict_path(path + '[' + str(index) + ']', item)
    else:
        print(path + " =>", obj)


# Preparing to get VMware assests
#     "/asset-service/workloads/vmware/assets
#     ?page%5Blimit%5D=10
#     &page%5Bdisable%5D=true"

params = {
    'page': {
        'limit': 10,
        'disable': 'true'
    }
}

print("GET vmware assests ...", end=" ")
response = requests.get(nbu_api_baseurl +
                        "/asset-service/workloads/vmware/assets",
                        params=params,
                        verify=False,
                        headers=header_v5)
parsed1 = response.json()
print("done:", end=" ")
print(response.status_code)

if response.status_code != 200:
    print("Error:", response)
    quit(1)
# print(json.dumps(parsed1, indent=4, sort_keys=True))
# print(type(response), type(parsed1))
# print_dict_path('',parsed1)

# print VM assets on screen
for idx, item in enumerate(parsed1['data']):
    if item['attributes']['assetType'] == 'vm':
        print("Index:", idx)
        print("Display name:\t", item['attributes']['commonAssetAttributes']['displayName'])
        print("id (referenced by NBU):\t", item['id'])
        print("instanceUuid:\t", item['attributes']['instanceUuid'])
        print("assetType:\t", item['attributes']['assetType'])
        print("vCenter:\t", item['attributes']['vCenter'])
        print("vmAbsolutePath:\t", item['attributes']['vmAbsolutePath'])
        print("lastDiscoveredTime:\t", item['attributes']['commonAssetAttributes']['detection']['lastDiscoveredTime'])
        print("nicIpAddresses:\t", item['attributes']['nicIpAddresses'])
        print("")

i = int(input("Please enter the idx of the VM: "))

my_display_name = parsed1['data'][i]['attributes']['commonAssetAttributes']['displayName']
my_vcenter = parsed1['data'][i]['attributes']['vCenter']
my_vm_absolutepath = parsed1['data'][i]['attributes']['vmAbsolutePath']
my_id = parsed1['data'][i]['id']

export_data['displayName']=my_display_name
export_data['id']=my_id

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
    'page': {
        'limit': 10,
        'disable': 'true',
        'offset': 0
    },
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
print("done:", end=" ")
print(response.status_code)

if response.status_code != 200:
    print("Error:", response)
    quit(1)
# print(response)

parsed2 = response.json()
# print_dict_path('',parsed2)
if len(parsed2['data']) == 0:
    print("No backups found ...")
    quit(1)


print()
print("Backups:")
for idx, item in enumerate(parsed2['data']):
    print("Index:\t", idx)
    print("Backup time:\t", item['attributes']['backupTime'])
    print("id (referenced by NBU):\t", item['id'])
    print("JobID:\t", item['attributes']['extendedAttributes']['imageAttributes']['jobId'])
    print("copyNumber:\t", item['attributes']['extendedAttributes']['imageAttributes']['fragments'][0]['copyNumber'])
    print("")

idx = int(input("Please enter backup index: (default: 0 for latest) ") or 0)

my_backup_id = parsed2['data'][idx]['id']
my_copy_number = parsed2['data'][idx]['attributes']['extendedAttributes']['imageAttributes']['fragments'][0]['copyNumber']
proposed_name = my_display_name + "-IA-" + t_now.strftime('%Y%m%dT%H%M%SZ')
my_new_name = input("Please enter a new Name of the Instant Access VM: (default: " + proposed_name + ")") or proposed_name
my_power_on = input("PowerOn (True / False): (default: True) ") or "True"
my_remove_eth_cards = input("removeEthCards (True/False): (default: True) ") or "True"

# Preparing to get additional info
params = {
    'include': 'optionalVmwareRecoveryPointInfo,optionalRecoveryPointCopyInfo'
}

print("GET recovery point details ...", end=" ")
response = requests.get(nbu_api_baseurl +
                        "/recovery-point-service/workloads/vmware/recovery-points/" + my_backup_id,
                        params=params,
                        verify=False,
                        headers=header_v6)
print("done:", end=" ")
print(response.status_code)

if response.status_code != 200:
    print("Error:", response)
    quit(1)

parsed3 = response.json()
# print(parsed3)
# print_dict_path('',parsed3)
print()

for idx, item in enumerate(parsed3['included']):
    if item['type'] == 'optionalVmwareRecoveryPointInfo':
        my_esxi_host = item['attributes']['esxiServer']
        my_resourcePoolOrVapp = item['attributes']['resourcePoolOrVapp']

my_esxi_host = input("Please enter a new esxiHost: (default: " + my_esxi_host + ")") or my_esxi_host
my_resourcePoolOrVapp = input(
    "Please enter a new resource-pool or vApp: (default: " + my_resourcePoolOrVapp + ")") or my_resourcePoolOrVapp

# Preparing to POST to start IA machine
my_attributes = {
    "backupId": my_backup_id,
    "copyNumber": my_copy_number,
    "vCenter": my_vcenter,
    "esxiHost": my_esxi_host,
    "resourcePoolOrVapp": my_resourcePoolOrVapp,
    # "192.168.2.50",
    # "resourcePoolOrVapp":"/NBUESX/host/192.168.2.50/Resources"
    "vmName": my_new_name,
    "powerOn": my_power_on,
    "removeEthCards": my_remove_eth_cards,
    "retention": {"value": 4, "unit": "HOURS"}
}

my_data = {
    "type": "instantAccessVmV3",
    "attributes": my_attributes
}

my_obj = {"data": my_data}

export_data['vCenter']=my_vcenter
export_data['esxiHost']=my_esxi_host
export_data['resourcePoolOrVapp']=my_resourcePoolOrVapp
export_data['vmName']=my_new_name
export_data['powerOn']=my_power_on
export_data['removeEthCards']=my_remove_eth_cards

print("POST request to start IA ... )
print("header:", header_v3)
print("body:", my_obj)
response = requests.post(nbu_api_baseurl +
                         "/recovery/workloads/vmware/instant-access-vms",
                         verify=False,
                         headers=header_v3,
                         json=my_obj)
print("done:", end=" ")
print(response.status_code)
print(response)
parsed = response.json()
print(json.dumps(parsed, indent=4, sort_keys=True))
print("Exporting data for scheduled runs...")
print(json.dumps(export_data, indent=4, sort_keys=True))

with open('exports/vm_'+my_id+'.txt', 'w') as data_file:
         data_file.write(json.dumps(export_data))
print(" done.")
