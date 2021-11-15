import json
import requests
from datetime import datetime, timedelta

# This call will disable invalid https certificate disable_warnings
requests.urllib3.disable_warnings()

NBU_API_KEY = "A8fmNjyB5DvvzAN1CnRWblMv160U1Vt5hs5P2fqj81pJh9224HRus-w9YuXnwSMa"
nbu_api_hostname = "nbumaster.lab.local"
nbu_api_baseurl = "https://" + nbu_api_hostname + ":1556/netbackup"
asset_id = "84ba26e1-bd89-45c6-9ad4-196b0d8f9287"

nbu_api_content_typev6 = "application/vnd.netbackup+json;version=6.0"
nbu_api_content_typev5 = "application/vnd.netbackup+json;version=5.0;charset=UTF-8"
nbu_api_content_typev3 = "application/vnd.netbackup+json;version=3.0"

headerv6 = {'Accept': nbu_api_content_typev6,
            'Authorization': NBU_API_KEY,
            'Content-Type': nbu_api_content_typev6}

headerv5 = {'Accept': nbu_api_content_typev5,
            'Authorization': NBU_API_KEY,
            'Content-Type': nbu_api_content_typev5}

headerv3 = {'Accept': nbu_api_content_typev3,
            'Authorization': NBU_API_KEY,
            'Content-Type': nbu_api_content_typev3}


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
                        headers=headerv5)
parsed1 = response.json()
print("done:", end=" ")
print(response.status_code)

if response.status_code != 200:
    print("Error:", response)
    quit(-1)
# print(json.dumps(parsed1, indent=4, sort_keys=True))
# print(type(response), type(parsed1))
# print_dict_path('',parsed1)

# print VM assets on screen
for idx, item in enumerate(parsed1['data']):
    if (item['attributes']['assetType'] == 'vm'):
        print("Index:", idx)
        print("Displayname:\t", item['attributes']['commonAssetAttributes']['displayName'])
        print("id (referenced by NBU):", item['id'])
        print("instanceUuid:", item['attributes']['instanceUuid'])
        print("assetType:", item['attributes']['assetType'])
        print("vCenter:", item['attributes']['vCenter'])
        print("vmAbsolutePath:", item['attributes']['vmAbsolutePath'])
        print("lastDiscoveredTime:", item['attributes']['commonAssetAttributes']['detection']['lastDiscoveredTime'])
        print("nicIpAddresses:", item['attributes']['nicIpAddresses'])
        print("")

i = int(input("Please enter the idx of the VM: "))

mydisplayname = parsed1['data'][i]['attributes']['commonAssetAttributes']['displayName']
myvcenter = parsed1['data'][i]['attributes']['vCenter']
myvmabsolutepath = parsed1['data'][i]['attributes']['vmAbsolutePath']

tnow = datetime.now()
t30dayago = tnow - timedelta(days=30)
# print(tnow.strftime('%Y-%m-%dT%H:%M:%SZ'), t30dayago.strftime('%Y-%m-%dT%H:%M:%SZ'))

print()
print("Listing backups for the last 30 days:")
print("Machine index: ", i)
print("Displayname: ", parsed1['data'][i]['attributes']['commonAssetAttributes']['displayName'])
assted_id = parsed1['data'][i]['id']
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
    'filter': "assetId eq '" + asset_id + "' and (backupTime ge " + t30dayago.strftime('%Y-%m-%dT%H:%M:%SZ') + ")",
    'include': 'optionalVmwareRecoveryPointInfo'
}

print("GET vmware recovery points ...", end=" ")
response = requests.get(nbu_api_baseurl +
                        "/recovery-point-service/workloads/vmware/recovery-points",
                        params=params,
                        verify=False,
                        headers=headerv5)
print("done:", end=" ")
print(response.status_code)

if response.status_code != 200:
    print("Error:", response)
    quit(-1)
# print(response)

parsed2 = response.json()
# print_dict_path('',parsed2)

print()
print("Backups:")
for idx, item in enumerate(parsed2['data']):
    print("Index:", idx)
    print("BackupTime:\t", item['attributes']['backupTime'])
    print("id (referenced by NBU):", item['id'])
    print("JobID:", item['attributes']['extendedAttributes']['imageAttributes']['jobId'])
    print("copyNumber:", item['attributes']['extendedAttributes']['imageAttributes']['fragments'][0]['copyNumber'])
    print("")

idx = int(input("Please enter backup index: (default: 0 for latest) ") or 0)

mybackupid = parsed2['data'][idx]['id']
mycopynumber = parsed2['data'][idx]['attributes']['extendedAttributes']['imageAttributes']['fragments'][0]['copyNumber']
proposedname = mydisplayname + "-IA-" + tnow.strftime('%Y%m%dT%H%M%SZ')
mynewname = input("Please enter a new Name of the Instant Access VM: (deafult: " + proposedname + ")") or proposedname
mypoweron = input("PowerOn (True / False): (default: True) ") or "True"
myremoveethcards = input("removeEthCards (True/False): (default: True) ") or "True"

# Preparing to get additional info
params = {
    'include': 'optionalVmwareRecoveryPointInfo,optionalRecoveryPointCopyInfo'
}

print("GET recovery point details ...", end=" ")
response = requests.get(nbu_api_baseurl +
                        "/recovery-point-service/workloads/vmware/recovery-points/" + mybackupid,
                        params=params,
                        verify=False,
                        headers=headerv6)
print("done:", end=" ")
print(response.status_code)

if response.status_code != 200:
    print("Error:", response)
    quit(-1)

parsed3 = response.json()
# print(parsed3)
# print_dict_path('',parsed3)
print()

for idx, item in enumerate(parsed3['included']):
    if item['type'] == 'optionalVmwareRecoveryPointInfo':
        myesxiHost = item['attributes']['esxiServer']
        myresourcePoolOrVapp = item['attributes']['resourcePoolOrVapp']

myesxiHost = input("Please enter a new esxiHost: (deafult: " + myesxiHost + ")") or myesxiHost
myresourcePoolOrVapp = input(
    "Please enter a new resource-pool or vApp: (deafult: " + myresourcePoolOrVapp + ")") or myresourcePoolOrVapp

# Preparing to POST to start IA machine
myattributes = {
    "backupId": mybackupid,
    "copyNumber": mycopynumber,
    "vCenter": myvcenter,
    "esxiHost": myesxiHost,
    "resourcePoolOrVapp": myresourcePoolOrVapp,
    # "192.168.2.50",
    # "resourcePoolOrVapp":"/NBUESX/host/192.168.2.50/Resources"
    "vmName": mynewname,
    "powerOn": mypoweron,
    "removeEthCards": myremoveethcards,
    "retention": {"objue": 4, "unit": "HOURS"}
}

mydata = {
    "type": "instantAccessVmV3",
    "attributes": myattributes
}

myobj = {"data": mydata}

print("POST IA start ... ")
print("header:", headerv3)
print("body:", myobj)
response = requests.post(nbu_api_baseurl +
                         "/recovery/workloads/vmware/instant-access-vms",
                         verify=False,
                         headers=headerv3,
                         json=myobj)
print("done:", end=" ")
print(response.status_code)
print(response)
parsed = response.json()
print(json.dumps(parsed, indent=4, sort_keys=True))
