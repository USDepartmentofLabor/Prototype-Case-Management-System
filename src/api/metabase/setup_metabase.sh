# get the set up token
token=$(curl -s -X GET -H "Content-Type: application/json" http://localhost:3000/api/session/properties | jq '."setup-token"')

echo "set up token is ${token}"

# create the json to send for initial set up
setup_json="'{ \"token\": $token, \"user\": { \"first_name\": \"admin\", \"last_name\": \"admin\", \"email\": \"ilabtoolkit@gmail.com\", \"password\": \"admin1\" }, \"prefs\": { \"allow_tracking\": \"false\", \"site_name\": \"EPS\" } }'"
content_type="'Content-Type:application/json'"
url='http://localhost:3000/api/setup/'
setup_command="curl -X POST $url -H $content_type -d $setup_json"
eval $setup_command

# auth
token2=$(curl -X POST -H "Content-Type: application/json" http://localhost:3000/api/session/ -d "{ \"username\": \"ilabtoolkit@gmail.com\", \"password\": \"admin1\" }" | python2.7 -c 'import sys, json; print json.load(sys.stdin)["id"]' | tail -1)
content_type="'Content-Type:application/json'"
metabase_session="'X-Metabase-Session: "
metabase_session+=$token2
metabase_session+="'"

# remove the sample dataset first
url='http://localhost:3000/api/database/1'
delete_first_database_command="curl -X DELETE $url -H $content_type -H $metabase_session"
eval $delete_first_database_command

# add the database to metabase
add_database_json="'{ \"name\": \"EPS Data (Dev)\", \"engine\": \"postgres\", \"details\": { \"host\": \"localhost\", \"port\": 5432, \"dbname\": \"data_pg\", \"user\": \"metabase_pg_user\", \"password\": \"securepassword1\", \"tunnel-port\": 22, \"ssl\": true } }'"
url='http://localhost:3000/api/database/'
add_database_command="curl -X POST $url -H $content_type -H $metabase_session -d $add_database_json"
eval $add_database_command

# change setting "humanization-strategy" to "none", disable name guessing
change_humanization_setting_json="'{ \"value\": \"none\" }'"
url='http://localhost:3000/api/setting/humanization-strategy'
change_humanization_setting_command="curl -X PUT $url -H $content_type -H $metabase_session -d $change_humanization_setting_json"
eval $change_humanization_setting_command
