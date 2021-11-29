# netbackup-python
Python helpers for Netbackup REST API

The goal of this collection is to help you with Netbackup and REST-API.

The scripts are based on python3 and require the request module to be installed.

instant-access-vm folder:
- 11-list-vms.py: This script will login to NBU master and list the discovered VMware assets
- 12-list-vms-and-backups.py: This script lists VMware assets and backups within the last 30 days
- 13-list-vms-and-backups-startIA: This scripts lists VMware assets, you can select a backup and it will start an Instant Access VM

TODO:
- script 21 to automate IA creation for testing
- script 22 to allow to run a powershell or ssh script

Apulai
