import os
import psycopg2
import flask
from ..test_helpers import get_access_token


def test_can_access_default_route(test_client):
    response = test_client.get('/')
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['message']
    assert json_data['message'] == "I'm here"


def test_can_access_default_secure_route(test_client, test_db):
    access_token = get_access_token(test_client)
    response = test_client.get('/secure', headers={'Authorization': 'Bearer ' + access_token})
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['message']
    assert json_data['message'] == "Hi ilabtoolkit@gmail.com"


def test_can_get_lookup_values(test_client, test_db):
    # test_db included because test relies on DB being initialized
    access_token = get_access_token(test_client)
    response = test_client.get('/lookups', headers={'Authorization': 'Bearer ' + access_token})
    assert response.status_code == 200
    json_data = response.get_json()
    assert len(json_data) > 0
    assert len(json_data['roles']) > 0
    assert len(json_data['survey_response_statuses']) > 0
    assert len(json_data['case_statuses']) > 0
    assert len(json_data['permissions']) > 0
    assert json_data['permissions'][0] == {'code': 'ADMIN', 'name': 'Administrator', 'value': 1}


def test_can_get_configuration(test_client, test_db):
    from flask import current_app
    access_token = get_access_token(test_client)
    response = test_client.get('/configuration', headers={'Authorization': 'Bearer ' + access_token})
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['metabase_url'] == current_app.config['METABASE_URL']
    assert json_data['api_version'] == current_app.config['API_VERSION']
    valid_properties = ['metabase_url', 'api_version']
    # validate that only expected properties are being returned
    assert not [e for e in json_data.keys() if e not in '\n'.join(valid_properties)]


def test_can_get_dashboards(test_client):
    access_token = get_access_token(test_client)
    response = test_client.get('/dashboards', headers={'Authorization': 'Bearer ' + access_token})
    assert response.status_code == 200


def test_can_get_deleted(test_client, test_db):
    # insert data
    structure = {
        "pages": [
            {
                "name": "page1",
                "elements": [
                    {"type": "text", "name": "question1"}
                ]
            }
        ],
        "title": "Test Survey"
    }

    access_token = get_access_token(test_client)
    response = test_client.post(
        '/surveys/',
        data=flask.json.dumps({'name': 'test survey', 'structure': structure}),
        headers={'Content-Type': 'application/json', 'Authorization': f"Bearer {access_token}"}
    )

    survey_response_structure = {
        "structure": {"question1": "bb"}, "status_id": 1
    }

    survey_id = response.json['id']

    response = test_client.post(
        f"/surveys/{survey_id}/responses",
        data=flask.json.dumps(survey_response_structure),
        headers={'Content-Type': 'application/json', 'Authorization': f"Bearer {access_token}"}
    )

    survey_response_id = response.json['id']

    case_definition = {
        "name": "Test Case Definition 6",
        "key": "TCD1",
        "description": "This is a description of the test case definition 6",
        "surveys": [survey_id],
        "documents": [{
            "name": "Birth Certificate",
            "description": "blah blah",
            "is_required": True
        }, {
            "name": "Document 2",
            "description": "blah blah",
            "is_required": False
        }]
    }

    response = test_client.post(
        "/case_definitions/",
        data=flask.json.dumps(case_definition),
        headers={'Content-Type': 'application/json', 'Authorization': f"Bearer {access_token}"}
    )

    case_defn_id = response.json['id']

    case = {
        "name": "Test Case",
        "description": "This is a description of the test case",
        "case_definition_id": case_defn_id,
        "notes": []
    }

    response = test_client.post(
        f"/case_definitions/{case_defn_id}/cases",
        data=flask.json.dumps(case),
        headers={'Content-Type': 'application/json', 'Authorization': f"Bearer {access_token}"}
    )

    case_id = response.json['id']

    # deletes survey and survey_response
    test_client.delete(
        f'/surveys/{survey_id}',
        headers={'Content-Type': 'application/json', 'Authorization': f"Bearer {access_token}"}
    )
    # Delete method not implemented
    # test_client.delete(f'/case_definitions/{case_defn_id}')
    test_client.delete(
        f'/cases/{case_id}',
        headers={'Content-Type': 'application/json', 'Authorization': f"Bearer {access_token}"}
    )

    response = test_client.get(
        '/deleted',
        headers={'Content-Type': 'application/json', 'Authorization': f"Bearer {access_token}"}
    )
    assert response.status_code == 200
    assert len(response.json['surveys']) == 1
    assert len(response.json['responses']) == 1
    assert len(response.json['cases']) == 1
    assert all(item['id'] == survey_id for item in response.json['surveys'])
    assert all(item['id'] == survey_response_id for item in response.json['responses'])
    assert all(item['id'] == case_id for item in response.json['cases'])


def test_get_deleted_date_filter(test_client, test_db):
    # insert data
    structure = {
        "pages": [
            {
                "name": "page1",
                "elements": [
                    {"type": "text", "name": "question1"}
                ]
            }
        ],
        "title": "Test Survey"
    }

    access_token = get_access_token(test_client)
    response = test_client.post(
        '/surveys/',
        data=flask.json.dumps({'name': 'test survey', 'structure': structure}),
        headers={'Content-Type': 'application/json', 'Authorization': f"Bearer {access_token}"}
    )

    survey_response_structure = {
        "structure": {"question1": "bb"}, "status_id": 1
    }

    survey_id = response.json['id']

    response = test_client.post(
        f"/surveys/{survey_id}/responses",
        data=flask.json.dumps(survey_response_structure),
        headers={'Content-Type': 'application/json', 'Authorization': f"Bearer {access_token}"}
    )

    survey_response_id = response.json['id']

    case_definition = {
        "name": "Test Case Definition 6",
        "key": "TCD1",
        "description": "This is a description of the test case definition 6",
        "surveys": [survey_id],
        "documents": [{
            "name": "Birth Certificate",
            "description": "blash blah",
            "is_required": True
        }, {
            "name": "Document 2",
            "description": "blash blah",
            "is_required": False
        }]
    }

    response = test_client.post(
        "/case_definitions/",
        data=flask.json.dumps(case_definition),
        headers={'Content-Type': 'application/json', 'Authorization': f"Bearer {access_token}"}
    )

    case_defn_id = response.json['id']

    case = {
        "name": "Test Case",
        "description": "This is a description of the test case",
        "case_definition_id": case_defn_id,
        "notes": []
    }

    response = test_client.post(
        f"/case_definitions/{case_defn_id}/cases",
        data=flask.json.dumps(case),
        headers={'Content-Type': 'application/json', 'Authorization': f"Bearer {access_token}"}
    )

    case_id = response.json['id']

    # deletes survey and survey_response
    test_client.delete(
        f'/surveys/{survey_id}',
        headers={'Content-Type': 'application/json', 'Authorization': f"Bearer {access_token}"}
    )
    # Delete method not implemented
    # test_client.delete(f'/case_definitions/{case_defn_id}')

    import time
    import datetime
    from werkzeug import http
    time.sleep(2)
    timestamp = datetime.datetime.utcnow()

    test_client.delete(
        f'/cases/{case_id}',
        headers={'Content-Type': 'application/json', 'Authorization': f"Bearer {access_token}"}
    )

    response = test_client.get(
        f'/deleted?deleted_since={http.http_date(timestamp)}',
        headers={'Content-Type': 'application/json', 'Authorization': f"Bearer {access_token}"}
    )
    assert response.status_code == 200
    assert len(response.json['surveys']) == 0
    assert len(response.json['responses']) == 0
    assert len(response.json['cases']) == 1
    assert all(item['id'] == case_id for item in response.json['cases'])


def test_reset_reporting(test_client, test_db):
    """
    The test database will always have one table; spatial_ref_sys which is used by PostGIS. This
    test has been updated to allow for that.
    """
    structure = {
        "pages": [
            {
                "name": "page1",
                "elements": [
                    {"type": "text", "name": "question1"}
                ]
            }
        ],
        "title": "Test Survey"
    }

    access_token = get_access_token(test_client)
    _ = test_client.post(
        '/surveys/',
        data=flask.json.dumps({'name': 'test survey', 'structure': structure}),
        headers={'Content-Type': 'application/json', 'Authorization': f"Bearer {access_token}"}
    )

    check_num_tables_sql = 'select count(tablename) as num_tables from pg_tables where schemaname = current_schema();'
    data_db_conn = psycopg2.connect(os.environ.get('DATA_DB_URI', 'postgresql:///data_test_pg'))
    data_db_cursor = data_db_conn.cursor()

    # check if survey table was created
    data_db_cursor.execute(check_num_tables_sql)
    data_db_result = data_db_cursor.fetchone()
    assert data_db_result[0] == 2

    # create a table manually
    data_db_cursor.execute('create table extra_table (name varchar);')
    data_db_cursor.execute(check_num_tables_sql)
    data_db_result = data_db_cursor.fetchone()
    assert data_db_result[0] == 3

    data_db_conn.commit()

    # call /reset-reporting endpoint
    response = test_client.post(
        '/reset-reporting',
        data='',
        headers={'Content-Type': 'application/json', 'Authorization': f"Bearer {access_token}"}
    )

    assert response.status_code == 204

    # check that only the survey table exists + PostGIS table
    data_db_cursor.execute(check_num_tables_sql)
    data_db_result = data_db_cursor.fetchone()
    assert data_db_result[0] == 2

    data_db_cursor.close()
    data_db_conn.close()
