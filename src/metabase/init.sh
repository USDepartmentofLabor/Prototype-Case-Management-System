#!/bin/bash

apk update && apk add curl jq

#"$@" &
#java -jar /app/metabase.jar
#/app/bin/start
/app/run_metabase.sh &
sleep 60

# settings
# TODO: use environment from Dockerfile
admin_username="ilabtoolkit@gmail.com"
admin_password="admin1"
db_username="metabase_pg_user"
db_password="securepassword1"
db_dbname="metabase_pg_user"
db_host="localhost"
db_port="5432"
base_url="http://localhost:3000"

# get the set up token
authz_token=$(curl -s -X GET \
	-H 'Content-Type: application/json' \
	$base_url/api/session/properties \
    | jq -r .setup_token)

echo "AuthZ token is ${authz_token}"

# create the json to send for initial set up
curl -s -X POST \
     -H 'Content-Type: application/json' \
     -d '{
    "token": "'${authz_token}'",
    "user": {
        "first_name": "admin",
        "last_name": "admin",
        "email": "'${admin_username}'",
        "password": "'${admin_password}'"
    },
    "prefs": {
        "allow_tracking": "false",
        "site_name": "mbpoc"
    }
}' \
     $base_url/api/setup/

# auth
authn_token=$(curl -s -X POST \
	-H 'Content-Type: application/json' \
    -d '{
    "username": "'${admin_username}'",
    "password": "'${admin_password}'"
}' \
    $base_url/api/session/ \
    | jq -r .id)

echo "AuthN token is ${authn_token}"

# remove the sample dataset first
curl -s -X DELETE \
	-H 'Content-Type: application/json' \
	-H "X-Metabase-Session: ${authn_token}" \
    $base_url/api/database/1

# add the database to metabase
curl -s -X POST \
	-H 'Content-Type: application/json' \
	-H "X-Metabase-Session: ${authn_token}" \
	-d '{
    "name": "pg_devdb",
    "engine": "postgres",
    "details": {
        "host": "'${db_host}'",
        "port": '${db_port}',
        "dbname": "'${db_username}'",
        "user": "'${db_username}'",
        "password": "'${db_password}'",
        "tunnel-port": 22,
        "ssl": true
    }
}' \
    $base_url/api/database/

# change setting "humanization-strategy" to "none", disable name guessing
curl -s -X PUT \
	-H 'Content-Type: application/json' \
	-H "X-Metabase-Session: ${authn_token}" \
	-d '{"value": "none"}' \
    $base_url/api/setting/humanization-strategy


# See also <https://stackoverflow.com/questions/4824590/propagate-all-arguments-in-a-bash-shell-script>, <https://stackoverflow.com/questions/3811345/how-to-pass-all-arguments-passed-to-my-bash-script-to-a-function-of-mine/3816747>
# End of Docker ENTRYPOINT
# Beginning of Docker CMD
#shift
#"$@"

# TODO: FIXME
while true; do sleep 1000; done
