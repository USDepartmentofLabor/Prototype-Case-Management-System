import json
import pytest
from flask_jwt_extended import create_access_token
from app.models import Project
from ..test_helpers import get_access_token


def test_post_valid_project(test_client, test_db, project_data):
    count_before = test_db.session.query(Project).count()

    access_token = get_access_token(test_client)
    response = test_client.post('/project', data=json.dumps(project_data),
                                headers={'Content-Type': 'application/json', 'Authorization': f"Bearer {access_token}"})

    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['id']
    assert json_data['name'] == project_data['name']
    assert (count_before + 1) == test_db.session.query(Project).count()


def test_post_project_fails_when_system_has_project(test_client, test_db, project_data, admin_user):

    p = Project(name=project_data['name'], title=project_data['title'], organization=project_data['organization'],
                agreement_number=project_data['agreement_number'], start_date=project_data['start_date'],
                end_date=project_data['end_date'], funding_amount=project_data['funding_amount'],
                location=project_data['location'], created_by=admin_user, updated_by=admin_user)
    test_db.session.add(p)
    test_db.session.commit()

    access_token = get_access_token(test_client)
    response = test_client.post('/project', data=json.dumps(project_data),
                                headers={'Content-Type': 'application/json', 'Authorization': f"Bearer {access_token}"})

    assert response.status_code == 400
    json_data = response.get_json()
    assert json_data['message'] == 'The system already has a project setup.'


invalid_data_test_cases = [
    {
        'id': 'name-empty',
        'data': {
            "name": "",
            "title": "Brazilian ADVANCE Project Eliminating Exploitive Child Labor through Education and Livelihoods",
            "organization": "IMPAQ International",
            "agreement_number": "IL-23979-13-75-K",
            "start_date": "2018-01-01",
            "end_date": "2022-12-31",
            "funding_amount": 10000000,
            "location": "Brasília, Brazil"
        },
        'response_status': 400,
        'response_message': 'A name is required for a project.'
    }, {
        'id': 'name-null',
        'data': {
            "name": None,
            "title": "Brazilian ADVANCE Project Eliminating Exploitive Child Labor through Education and Livelihoods",
            "organization": "IMPAQ International",
            "agreement_number": "IL-23979-13-75-K",
            "start_date": "2018-01-01",
            "end_date": "2022-12-31",
            "funding_amount": 10000000,
            "location": "Brasília, Brazil"
        },
        'response_status': 400,
        'response_message': 'A name is required for a project.'
    }, {
        'id': 'name-missing',
        'data': {
            "title": "Brazilian ADVANCE Project Eliminating Exploitive Child Labor through Education and Livelihoods",
            "organization": "IMPAQ International",
            "agreement_number": "IL-23979-13-75-K",
            "start_date": "2018-01-01",
            "end_date": "2022-12-31",
            "funding_amount": 10000000,
            "location": "Brasília, Brazil"
        },
        'response_status': 400,
        'response_message': 'A name is required for a project.'
    }, {
        'id': 'name-too-long',
        'data': {
            "name": 'x'*80,
            "title": "Brazilian ADVANCE Project Eliminating Exploitive Child Labor through Education and Livelihoods",
            "organization": "IMPAQ International",
            "agreement_number": "IL-23979-13-75-K",
            "start_date": "2018-01-01",
            "end_date": "2022-12-31",
            "funding_amount": 10000000,
            "location": "Brasília, Brazil"
        },
        'response_status': 400,
        'response_message': 'Project names cannot be longer than 64 characters.'
    }, {
        'id': 'organization-too-long',
        'data': {
            "name": "ADVANCE Brazil",
            "title": "Brazilian ADVANCE Project Eliminating Exploitive Child Labor through Education and Livelihoods",
            "organization": 'x'*80,
            "agreement_number": "IL-23979-13-75-K",
            "start_date": "2018-01-01",
            "end_date": "2022-12-31",
            "funding_amount": 10000000,
            "location": "Brasília, Brazil"
        },
        'response_status': 400,
        'response_message': 'Project organizations cannot be longer than 64 characters.'
    }, {
        'id': 'agreement_number-too-long',
        'data': {
            "name": "ADVANCE Brazil",
            "title": "Brazilian ADVANCE Project Eliminating Exploitive Child Labor through Education and Livelihoods",
            "organization": "IMPAQ International",
            "agreement_number": 'x'*80,
            "start_date": "2018-01-01",
            "end_date": "2022-12-31",
            "funding_amount": 10000000,
            "location": "Brasília, Brazil"
        },
        'response_status': 400,
        'response_message': 'Project agreement numbers cannot be longer than 30 characters.'
    }
]
invalid_data_test_cases_ids = [case['id'] for case in invalid_data_test_cases]


@pytest.mark.parametrize('test_case', invalid_data_test_cases, ids=invalid_data_test_cases_ids)
def test_post_project_fails_with_invalid_data(test_client, test_db, test_case):

    access_token = get_access_token(test_client)
    response = test_client.post('/project', data=json.dumps(test_case['data']),
                                headers={'Content-Type': 'application/json', 'Authorization': f"Bearer {access_token}"})

    assert response.status_code == test_case['response_status']
    json_data = response.get_json()
    assert json_data['message'] == test_case['response_message']
    assert test_db.session.query(Project).count() == 0


# really didn't want to do this. tried to find a way to skip the invalid_data_test_case where
# the id == 'name-missing' since the name is not required for PUTs but no luck.
put_invalid_data_test_cases = [
    {
        'id': 'name-empty',
        'data': {
            "name": "",
            "title": "Brazilian ADVANCE Project Eliminating Exploitive Child Labor through Education and Livelihoods",
            "organization": "IMPAQ International",
            "agreement_number": "IL-23979-13-75-K",
            "start_date": "2018-01-01",
            "end_date": "2022-12-31",
            "funding_amount": 10000000,
            "location": "Brasília, Brazil"
        },
        'response_status': 400,
        'response_message': 'A name is required for a project.'
    }, {
        'id': 'name-null',
        'data': {
            "name": None,
            "title": "Brazilian ADVANCE Project Eliminating Exploitive Child Labor through Education and Livelihoods",
            "organization": "IMPAQ International",
            "agreement_number": "IL-23979-13-75-K",
            "start_date": "2018-01-01",
            "end_date": "2022-12-31",
            "funding_amount": 10000000,
            "location": "Brasília, Brazil"
        },
        'response_status': 400,
        'response_message': 'A name is required for a project.'
    }, {
        'id': 'name-too-long',
        'data': {
            "name": 'x'*80,
            "title": "Brazilian ADVANCE Project Eliminating Exploitive Child Labor through Education and Livelihoods",
            "organization": "IMPAQ International",
            "agreement_number": "IL-23979-13-75-K",
            "start_date": "2018-01-01",
            "end_date": "2022-12-31",
            "funding_amount": 10000000,
            "location": "Brasília, Brazil"
        },
        'response_status': 400,
        'response_message': 'Project names cannot be longer than 64 characters.'
    }, {
        'id': 'organization-too-long',
        'data': {
            "name": "ADVANCE Brazil",
            "title": "Brazilian ADVANCE Project Eliminating Exploitive Child Labor through Education and Livelihoods",
            "organization": 'x'*80,
            "agreement_number": "IL-23979-13-75-K",
            "start_date": "2018-01-01",
            "end_date": "2022-12-31",
            "funding_amount": 10000000,
            "location": "Brasília, Brazil"
        },
        'response_status': 400,
        'response_message': 'Project organizations cannot be longer than 64 characters.'
    }, {
        'id': 'agreement_number-too-long',
        'data': {
            "name": "ADVANCE Brazil",
            "title": "Brazilian ADVANCE Project Eliminating Exploitive Child Labor through Education and Livelihoods",
            "organization": "IMPAQ International",
            "agreement_number": 'x'*80,
            "start_date": "2018-01-01",
            "end_date": "2022-12-31",
            "funding_amount": 10000000,
            "location": "Brasília, Brazil"
        },
        'response_status': 400,
        'response_message': 'Project agreement numbers cannot be longer than 30 characters.'
    }
]
put_invalid_data_test_cases_ids = [case['id'] for case in put_invalid_data_test_cases]


@pytest.mark.parametrize('test_case', put_invalid_data_test_cases, ids=put_invalid_data_test_cases_ids)
def test_put_project_fails_with_invalid_data(test_client, test_db, test_case, project_model):
    test_db.session.add(project_model)
    test_db.session.commit()

    access_token = get_access_token(test_client)
    response = test_client.put('/project', data=json.dumps(test_case['data']),
                               headers={'Content-Type': 'application/json', 'Authorization': f"Bearer {access_token}"})

    assert response.status_code == test_case['response_status']
    json_data = response.get_json()
    assert json_data['message'] == test_case['response_message']


def test_put_project(test_client, test_db, project_model, project_manager_user):
    test_db.session.add(project_model)
    test_db.session.commit()

    project_update = {
        'name': 'New Project Name'
    }

    access_token = create_access_token(project_manager_user.id)
    response = test_client.put('/project', data=json.dumps(project_update),
                               headers={'Content-Type': 'application/json', 'Authorization': f"Bearer {access_token}"})

    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['name'] == project_update['name']
    assert json_data['updated_by']['id'] == project_manager_user.id
    assert test_db.session.query(Project).count() == 1
    updated_project = Project.query.get(json_data['id'])
    assert updated_project.name == project_update['name']
    assert updated_project.updated_by_id == project_manager_user.id


def test_get_project(test_client, test_db, project_model):

    test_db.session.add(project_model)
    test_db.session.commit()

    access_token = get_access_token(test_client)
    response = test_client.get('/project', headers={'Content-Type': 'application/json',
                                                    'Authorization': f"Bearer {access_token}"})

    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['id']


def test_delete_project(test_client, test_db, project_model):

    test_db.session.add(project_model)
    test_db.session.commit()

    access_token = get_access_token(test_client)
    response = test_client.delete('/project', headers={'Content-Type': 'application/json',
                                                    'Authorization': f"Bearer {access_token}"})

    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['message'] == 'Project successfully deleted.'
    assert test_db.session.query(Project).count() == 0


no_project_test_cases = [
    {
        'id': 'get-project',
        'verb': 'GET'
    }, {
        'id': 'put-project',
        'verb': 'PUT'
    }, {
        'id': 'delete-project',
        'verb': 'DELETE'
    }
]
no_project_test_cases_ids = [case['id'] for case in no_project_test_cases]


@pytest.mark.parametrize('test_case', no_project_test_cases, ids=no_project_test_cases_ids)
def test_project_fails_if_no_project(test_client, test_db, test_case):

    access_token = get_access_token(test_client)

    if test_case['verb'] == 'GET':
        response = test_client.get('/project', headers={'Content-Type': 'application/json',
                                                        'Authorization': f"Bearer {access_token}"})
    elif test_case['verb'] == 'PUT':
        response = test_client.put('/project', headers={'Content-Type': 'application/json',
                                                        'Authorization': f"Bearer {access_token}"})
    elif test_case['verb'] == 'DELETE':
        response = test_client.delete('/project', headers={'Content-Type': 'application/json',
                                                           'Authorization': f"Bearer {access_token}"})

    assert response.status_code == 400
    json_data = response.get_json()
    assert json_data['message'] == 'A project has not been setup.'


permission_test_cases = [
    {
        'id': 'post-project',
        'url': '/project',
        'method': 'POST',
        'response_message': 'You do not have permission to create a project.'
    }, {
        'id': 'get-project',
        'url': '/project',
        'method': 'GET',
        'response_message': 'You do not have permission to read a project.'
    }, {
        'id': 'put-project',
        'url': '/project',
        'method': 'PUT',
        'response_message': 'You do not have permission to update a project.'
    }, {
        'id': 'delete-project',
        'url': '/project',
        'method': 'DELETE',
        'response_message': 'You do not have permission to delete a project.'
    }
]
permission_test_cases_ids = [case['id'] for case in permission_test_cases]


@pytest.mark.parametrize('test_case', permission_test_cases, ids=permission_test_cases_ids)
def test_project_fails_without_permission(test_client, test_case, user_with_no_permissions):

    access_token = create_access_token(identity=user_with_no_permissions.id)
    headers = {'Content-Type': 'application/json', 'Authorization': f"Bearer {access_token}"}
    if test_case['method'] == 'POST':
        response = test_client.post(test_case['url'], headers=headers)
    elif test_case['method'] == 'PUT':
        response = test_client.put(test_case['url'], headers=headers)
    elif test_case['method'] == 'DELETE':
        response = test_client.delete(test_case['url'], headers=headers)
    else:
        response = test_client.get(test_case['url'], headers=headers)

    assert response.status_code == 401
    json_data = response.get_json()
    assert json_data['message'] == test_case['response_message']