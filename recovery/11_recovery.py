import json
import requests
from datetime import datetime, timedelta

# This call will disable invalid https certificate disable_warnings
requests.urllib3.disable_warnings()

nbu_api_key = "A8fmNjyB5DvvzAN1CnRWblMv160U1Vt5hs5P2fqj81pJh9224HRus-w9YuXnwSMa"
nbu_api_hostname = "nbuprimary.lab.local"
nbu_api_baseurl = "https://" + nbu_api_hostname + ":1556/netbackup"
asset_id = "84ba26e1-bd89-45c6-9ad4-196b0d8f9287"

nbu_api_content_type_v6 = "application/vnd.netbackup+json;version=6.0"
nbu_api_content_type_v5 = "application/vnd.netbackup+json;version=5.0;charset=UTF-8"
nbu_api_content_type_v3 = "application/vnd.netbackup+json;version=3.0"

nbu_api_multipartform_v5 = "application/vnd.netbackup+form-data;version=5.0;charset=UTF-8"

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


myRecoveryRequest = {
    "data": {
        "type": "physicalFilesFoldersRecoveryRequest",
        "attributes":
            {
                "recoveryPoint": {
                    "client": "nbumedia.lab.local",
                    "policyType": "STANDARD",
                    "startDate": "2024-08-27T13:47:20.000Z",
                    "endDate": "2024-08-27T13:47:20.000Z"
                },
                "recoveryOptions": {
                    "server": "nbuprimary.lab.local",
                    "destinationClient": "nbumedia.lab.local",
                    "overwriteExistingFiles": False,
                    "restrictMountPoints": False,
                    "renameHardLinks": False,
                    "renameSoftLinks": False,
                    "accessControlAttributes": False,
                    "jobPriorityOverride": 90000
                }
            }
    }
}

mySelectionsFile = [
    {
        "path": "/etc/hosts",
        "backupTime": "2024-08-27T13:47:20.000Z"
    }
]

myRenameFile = [
    {
        "from": "/etc/hosts",
        "to": "/tmp/hosts_file_restored"
    }
]

multipart_form_data = {
    "recoveryRequest": ("blob", json.dumps(myRecoveryRequest), nbu_api_multipartform_v5),
    "selectionsFile": ("blob", json.dumps(mySelectionsFile), nbu_api_multipartform_v5),
    "renameFile": ("blob", json.dumps(myRenameFile), nbu_api_multipartform_v5)
}

print("POST to start restore ...", end=" ")
response = requests.post(nbu_api_baseurl +
                         "/recovery/workloads/physical/scenarios/granular-files-folders/recover",
                         files=multipart_form_data,
                         verify=False,
                         headers=header_v5)
parsed1 = response.json()
print(" done:", response.status_code)

if response.status_code != 200:
    print("Error:", response)
    quit(1)
# print(json.dumps(parsed1, indent=4, sort_keys=True))
# print(type(response), type(parsed1))
print_dict_path('', parsed1)

