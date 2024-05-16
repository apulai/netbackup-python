# Netbackup study script
# Login to NBU 
# Get the login token
# Get list of policies using the token

export apibase="https://nbuprimary.lab.local:1556/netbackup"
export nbu_api_content_type_v6="application/vnd.netbackup+json;version=6.0"

read -p "Username:" Username
echo -n "Password:"
read -s "Password:" Password

#export Username=root
#export Password='We!come10'
export Username
export Password

#export data='{"domaintype": "vx", "domainName": "", "userName": "'${Username}'", "password": "'${Password}'" }'
export data='{ "userName": "'${Username}'", "password": "'${Password}'" }'

echo ${data}

# Login and get token
token=`curl -sS -k \
-H "Accept: ${nbu_api_content_type_v6}" \
-H "Content-type: ${nbu_api_content_type_v6}" \
-X POST ${apibase}/login -d ${data} | jq ".token"`

echo ${token}

# Get policies using token
curl -sS -k \
-H "Accept: ${nbu_api_content_type_v6}" \
-H "Content-type: ${nbu_api_content_type_v6}" \
-H "Cookie: Authorization=${token}"
-X GET ${apibase}/config/policies | jq

# Get policies and filter only their names (.id)
curl -sS -k \
-H "Accept: ${nbu_api_content_type_v6}" \
-H "Content-type: ${nbu_api_content_type_v6}" \
-H "Cookie: Authorization=${token}"
-X GET ${apibase}/config/policies | jq 'recurse | select(has("id")?).id'
