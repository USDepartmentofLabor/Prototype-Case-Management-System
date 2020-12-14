#!/usr/bin/env python3
from sys import exit
from os import getenv
from requests import request as _request, ConnectionError
from time import sleep


def handle_response(response):
    if not response:
        print("No response")
    if response and not response.ok:
        print((response.content,
               response.status_code))
        raise RuntimeError(response)
    return response


def request(**request_kw):
    request_kw.setdefault('timeout', 5)
    try:
        response = _request(**request_kw)
        error = None
        if response:
            response = handle_response(response)
    except ConnectionError:
        response = None
        error = None
        print("Connecting...")
    except Exception as exc:
        response = None
        error = exc
        print("An exception occurred: ", repr(error))
    return response


def first_request(**request_kw):
    for _ in range(5):
        try:
            response = request(**request_kw)
        except Exception as exc:
            response = None
        if response and response.ok:
            break
        sleep(30)
    return response


# TODO: use environment from Dockerfile
admin_email = str(getenv('ADMIN_EMAIL', 'ilabtoolkit@gmail.com'))
admin_username = str(getenv('ADMIN_USERNAME', 'admin'))
admin_password = str(getenv('ADMIN_PASSWORD', 'admin1'))
db_username = str(getenv('DATA_DB_USER', 'metabase_pg_user'))
db_password = str(getenv('DATA_DB_PASS', 'securepassword1'))
db_dbname = str(getenv('DATA_DB_DBNAME', 'data_pg'))
db_host = str(getenv('DATA_DB_HOST', 'postgresql-db'))
db_port = str(getenv('DATA_DB_PORT', '5432'))
base_url = 'http://localhost:3000'

type_headers = dict([
    ('Accept', 'application/json'),
    ('Content-Type', 'application/json'),
])

authz_token = first_request(
    method='GET',
    url='{base_url}/api/session/properties'.format(base_url=base_url),
    headers=type_headers) \
    .json()['setup_token']

# This will be running in Python 3.6.6
# so we can use formatted F-strings
print('AuthZ token is {authz_token}'.format(authz_token=authz_token))

_ = request(
    method='POST',
    url='{base_url}/api/setup/'.format(base_url=base_url),
    headers=type_headers,
    json={
    "token": authz_token,
    "user": {
        "first_name": admin_username,
        "last_name": admin_username,
        "email": admin_email,
        "password": admin_password,
    },
    "prefs": {
        "allow_tracking": "false",
        "site_name": "mbpoc"
    }
})

authn_token = request(
    method='POST',
    url='{base_url}/api/session/'.format(base_url=base_url),
    headers=type_headers,
    json={
    "username": admin_email,
    "password": admin_password,
}) \
    .json()['id']

print("AuthN token is {authn_token}".format(authn_token=authn_token))

headers=dict(type_headers)
headers.update({'X-Metabase-Session': authn_token})

# check to see if the database exists
databases = request(
    method='GET',
    url='{base_url}/api/database/'.format(base_url=base_url),
    headers=headers,
).json()

# remove the sample dataset
for database in databases:
    if database['name'] == 'Sample Dataset':
        _ = request(
            method='DELETE',
            url='{base_url}/api/database/'.format(base_url=base_url) + str(database['id']),
            headers=headers)

# if it does not exist, then
if len([db for db in databases if db['name'] == db_dbname]) != 1:
    print("Connecting database {}".format(db_dbname))

    # add the database to metabase
    _ = request(
        method='POST',
        url='{base_url}/api/database/'.format(base_url=base_url),
        headers=headers,
        json={
        "name": "pg_devdb",
        "engine": "postgres",
        "details": {
            "host": db_host,
            "port": db_port,
            "dbname": db_dbname,
            "user": db_username,
            "password": db_password,
            "tunnel-port": 22,
            "ssl": True,
        }
    })
else:
    print("Database {} is connected".format(db_dbname))

# change setting "humanization-strategy" to "none", disable name guessing
_ = request(
    method='PUT',
    url='{base_url}/api/setting/humanization-strategy'.format(
        base_url=base_url),
    headers=headers,
    json={"value": "none"})

# enable embedding in other applications
_ = request(
    method='PUT',
    url='{base_url}/api/setting/enable-embedding'.format(
        base_url=base_url),
    headers=headers,
    json={"value": "true"})

embedding_secret_key = str(getenv('METABASE_SECRET_KEY', 'badsecretkey'))

_ = request(
    method='PUT',
    url='{base_url}/api/setting/embedding-secret-key'.format(
        base_url=base_url),
    headers=headers,
    json={"value": embedding_secret_key})
