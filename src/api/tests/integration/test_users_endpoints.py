import json
from flask_jwt_extended import create_access_token
import pytest
from app.models import User, Role, Survey, SurveyResponse, CaseDefinition
from ..test_helpers import get_access_token, setup_user_with_no_permissions, fake


def test_add_new_user(test_client, test_db):
    num_users_before = test_db.session.query(User).count()
    fuser = {
        'email': fake.email(),
        'username': fake.user_name(),
        'role_id': 2,
        'name': fake.name(),
        'location': fake.address()
    }
    access_token = get_access_token(test_client)
    response = test_client.post('/users/',
                                json={
                                    "email": fuser['email'],
                                    "username": fuser['username'],
                                    "role_id": fuser['role_id'],
                                    "name": fuser['name'],
                                    "location": fuser['location']},
                                headers={
                                    'Content-Type': 'application/json', 
                                    'Authorization': f"Bearer {access_token}"})
    assert response.status_code == 200
    json_data = response.get_json()
    # test what was sent was returned
    assert json_data['id']
    assert json_data['email'] == fuser['email']
    assert json_data['username'] == fuser['username']
    assert json_data['name'] == fuser['name']
    assert json_data['location'] == fuser['location']
    assert json_data['role']
    assert json_data['role']['id'] == fuser['role_id']
    assert json_data['color'] in User.supported_user_colors
    # test one more user is system
    assert (num_users_before + 1) == test_db.session.query(User).count()
    # test what was sent was saved to db
    new_user = User.query.get(json_data['id'])
    assert new_user
    assert new_user.email == fuser['email']
    assert new_user.username == fuser['username']
    assert new_user.name == fuser['name']
    assert new_user.location == fuser['location']
    assert new_user.role_id == fuser['role_id']
    assert new_user.color in new_user.supported_user_colors


def test_add_new_user_with_default_role(test_client, test_db):
    num_users_before = test_db.session.query(User).count()
    default_role = Role.query.filter_by(default=True).first()
    fuser = {
        'email': fake.email(),
        'username': fake.user_name(),
        'name': fake.name(),
        'location': fake.address()
    }
    access_token = get_access_token(test_client)
    response = test_client.post('/users/',
                                json={
                                    "email": fuser['email'],
                                    "username": fuser['username'],
                                    "name": fuser['name'],
                                    "location": fuser['location']},
                                headers={
                                    'Content-Type': 'application/json', 
                                    'Authorization': f"Bearer {access_token}"})
    assert response.status_code == 200
    json_data = response.get_json()
    # test what was sent was returned
    assert json_data['id']
    assert json_data['email'] == fuser['email']
    assert json_data['username'] == fuser['username']
    assert json_data['name'] == fuser['name']
    assert json_data['location'] == fuser['location']
    assert json_data['role']
    assert json_data['role']['id'] == default_role.id
    # test one more user is system
    assert (num_users_before + 1) == test_db.session.query(User).count()
    # test what was sent was saved to db
    new_user = User.query.get(json_data['id'])
    assert new_user
    assert new_user.email == fuser['email']
    assert new_user.username == fuser['username']
    assert new_user.name == fuser['name']
    assert new_user.location == fuser['location']
    assert new_user.role_id == default_role.id


post_user_invalid_data_cases = [
    {
        'id': 'email-missing',
        'data': {
            "username": fake.user_name(),
            "name": fake.name(),
            "location": fake.address()
        },
        'response_status': 400,
        'response_message': "Missing email"
    }, {
        'id': 'email-empty',
        'data': {
            "email": '',
            "username": fake.user_name(),
            "name": fake.name(),
            "location": fake.address()
        },
        'response_status': 400,
        'response_message': "Missing email"
    }, {
        'id': 'email-none',
        'data': {
            "email": None,
            "username": fake.user_name(),
            "name": fake.name(),
            "location": fake.address()
        },
        'response_status': 400,
        'response_message': "Missing email"
    }, {
        'id': 'username-missing',
        'data': {
            'email': fake.email(),
            "name": fake.name(),
            "location": fake.address()
        },
        'response_status': 400,
        'response_message': "Missing username"
    }, {
        'id': 'username-empty',
        'data': {
            'email': fake.email(),
            "username": '',
            "name": fake.name(),
            "location": fake.address()
        },
        'response_status': 400,
        'response_message': "Missing username"
    }, {
        'id': 'username-none',
        'data': {
            'email': fake.email(),
            "username": None,
            "name": fake.name(),
            "location": fake.address()
        },
        'response_status': 400,
        'response_message': "Missing username"
    }, {
        'id': 'role_id-non-integer',
        'data': {
            'email': fake.email(),
            "username": fake.user_name(),
            "name": fake.name(),
            "location": fake.address(),
            "role_id": "99"
        },
        'response_status': 400,
        'response_message': "Role id should be a integer number."
    }, {
        'id': 'role_id-invalid',
        'data': {
            'email': fake.email(),
            "username": fake.user_name(),
            "name": fake.name(),
            "location": fake.address(),
            "role_id": 99
        },
        'response_status': 400,
        'response_message': "99 is an invalid role id."
    }
]
post_user_invalid_data_cases_ids = [case['id'] for case in post_user_invalid_data_cases]


@pytest.mark.parametrize('test_case', post_user_invalid_data_cases, ids=post_user_invalid_data_cases_ids)
def test_add_user_fails_with_invalid_data(test_client, test_db, admin_access_token, test_case):

    response = test_client.post('/users/',
                                data=json.dumps(test_case['data']),
                                headers={
                                    'Content-Type': 'application/json', 
                                    'Authorization': f"Bearer {admin_access_token}"})
    assert response.status_code == test_case['response_status']
    json_data = response.get_json()
    assert json_data['message'] == test_case['response_message']


def test_add_users_fails_with_existing_email(test_client, admin_access_token, data_collector_user):
    response = test_client.post('/users/',
                                json={
                                    "email": data_collector_user.email,
                                    "username": fake.user_name(),
                                    "name": fake.name(),
                                    "location": fake.address()},
                                headers={
                                    'Content-Type': 'application/json',
                                    'Authorization': f"Bearer {admin_access_token}"})
    assert response.status_code == 400
    json_data = response.get_json()
    assert json_data['message'] == 'The email address you provided is already in use.'


def test_add_users_fails_with_existing_username(test_client, admin_access_token, data_collector_user):
    response = test_client.post('/users/',
                                json={
                                    "email": fake.email(),
                                    "username": data_collector_user.username,
                                    "name": fake.name(),
                                    "location": fake.address()},
                                headers={
                                    'Content-Type': 'application/json',
                                    'Authorization': f"Bearer {admin_access_token}"})
    assert response.status_code == 400
    json_data = response.get_json()
    assert json_data['message'] == 'The username you provided is already in use.'


def test_add_user_updates_users_seen_at(test_client, test_db):
    admin_user = User.query.filter_by(email='ilabtoolkit@gmail.com').first()
    start_last_seen_at = admin_user.last_seen_at
    fuser = {
        'email': fake.email(),
        'username': fake.user_name(),
        'role_id': 2,
        'name': fake.name(),
        'location': fake.address()
    }
    access_token = get_access_token(test_client)
    response = test_client.post('/users/',
                                json={
                                    "email": fuser['email'],
                                    "username": fuser['username'],
                                    "role_id": fuser['role_id'],
                                    "name": fuser['name'],
                                    "location": fuser['location']},
                                headers={
                                    'Content-Type': 'application/json', 
                                    'Authorization': f"Bearer {access_token}"})
    assert response.status_code == 200
    assert admin_user.last_seen_at > start_last_seen_at


bad_long_password = fake.password(length=65)
change_password_test_cases = [
    {
        'id': 'user-trys-self',
        'request_user_name': 'datareader',
        'change_user_name': 'datareader',
        'new_password': 'datareader12345',
        'confirm_password': 'datareader12345',
        'response_status': 200,
        'response_message': 'Password has been updated'
    }, {
        'id': 'admin-trys-user',
        'request_user_name': 'datareader',
        'change_user_name': 'admin',
        'new_password': 'datareader12345',
        'confirm_password': 'datareader12345',
        'response_status': 200,
        'response_message': 'Password has been updated'
    }, {
        'id': 'user-trys-other-user',
        'request_user_name': 'admin',
        'change_user_name': 'datareader',
        'new_password': 'datareader12345',
        'confirm_password': 'datareader12345',
        'response_status': 401,
        'response_message': 'Not authorized'
    }, {
        'id': 'user-trys-self-without-new_password',
        'request_user_name': 'datareader',
        'change_user_name': 'datareader',
        'new_password': None,
        'confirm_password': 'datareader12345',
        'response_status': 400,
        'response_message': 'Missing new_password'
    }, {
        'id': 'user-trys-self-with-empty-new_password',
        'request_user_name': 'datareader',
        'change_user_name': 'datareader',
        'new_password': '',
        'confirm_password': 'datareader12345',
        'response_status': 400,
        'response_message': 'Missing new_password'
    }, {
        'id': 'user-trys-self-without-confirm_password',
        'request_user_name': 'datareader',
        'change_user_name': 'datareader',
        'new_password': 'datareader12345',
        'confirm_password': None,
        'response_status': 400,
        'response_message': 'Missing confirm_password'
    }, {
        'id': 'user-trys-self-with-empty-confirm_password',
        'request_user_name': 'datareader',
        'change_user_name': 'datareader',
        'new_password': 'datareader12345',
        'confirm_password': '',
        'response_status': 400,
        'response_message': 'Missing confirm_password'
    }, {
        'id': 'user-trys-self-mismatched_new_and_confirm_passwords',
        'request_user_name': 'datareader',
        'change_user_name': 'datareader',
        'new_password': 'datareader12345',
        'confirm_password': 'datareader123456',
        'response_status': 400,
        'response_message': 'Passwords must match.'
    }, {
        'id': 'user-trys-self-password_too_short',
        'request_user_name': 'datareader',
        'change_user_name': 'datareader',
        'new_password': '12345',
        'confirm_password': '12345',
        'response_status': 400,
        'response_message': 'Password must be at least 10 characters long.'
    }, {
        'id': 'user-trys-self-password_too_long',
        'request_user_name': 'datareader',
        'change_user_name': 'datareader',
        'new_password': bad_long_password,
        'confirm_password': bad_long_password,
        'response_status': 400,
        'response_message': 'Password must be less than 64 characters long.'
    }
]

change_password_test_case_ids = [test_case['id'] for test_case in change_password_test_cases]


@pytest.mark.parametrize('test_case', change_password_test_cases, ids=change_password_test_case_ids)
def test_change_password(test_client, test_db, test_case):

    change_user = User.query.filter_by(username=test_case['request_user_name']).first()
    request_user = User.query.filter_by(username=test_case['change_user_name']).first()
    url = f"/users/{change_user.id}/change-password"
    access_token = create_access_token(identity=request_user.id)
    response = test_client.post(url,
                                json={
                                    "new_password": test_case['new_password'],
                                    "confirm_password": test_case['confirm_password']},
                                headers={
                                    'Content-Type': 'application/json', 
                                    'Authorization': f"Bearer {access_token}"})
    assert response.status_code == test_case['response_status']
    json_data = response.get_json()
    assert json_data['message'] == test_case['response_message']


def test_delete_user(test_client, test_db):

    admin_user = User.query.filter_by(username='admin').first()
    user_to_delete = User.query.filter_by(username='projectmanager').first()
    user_to_delete_id = user_to_delete.id

    # add a survey
    survey = Survey(name='test survey', structure={}, created_by=user_to_delete, updated_by=user_to_delete)
    test_db.session.add(survey)
    test_db.session.commit()

    # posts some responses
    survey_response = SurveyResponse(survey_id=survey.id, structure={}, created_by=user_to_delete,
                                     updated_by=user_to_delete)
    test_db.session.add(survey_response)
    survey_response2 = SurveyResponse(survey_id=survey.id, structure={}, created_by=user_to_delete,
                                      updated_by=user_to_delete)
    test_db.session.add(survey_response2)
    test_db.session.commit()

    # add a case definition
    case_definition = CaseDefinition(name="Test Case Definition", key='TCD', created_by=user_to_delete,
                                     updated_by=user_to_delete)
    test_db.session.add(case_definition)
    test_db.session.commit()

    access_token = create_access_token(identity=admin_user.id)
    response = test_client.delete(f"/users/{user_to_delete.id}",
                                  headers={'Content-Type': 'application/json',
                                           'Authorization': f"Bearer {access_token}"})
    assert response.status_code == 200
    # assert all references to user are now admin
    assert survey.created_by.id == admin_user.id
    assert survey.updated_by.id == admin_user.id
    assert survey_response.created_by.id == admin_user.id
    assert survey_response.updated_by.id == admin_user.id
    assert survey_response2.created_by.id == admin_user.id
    assert survey_response2.updated_by.id == admin_user.id
    assert case_definition.created_by.id == admin_user.id
    assert case_definition.updated_by.id == admin_user.id
    # assert user is deleted
    assert len(User.query.filter_by(username='projectmanager').all()) == 0


def test_disable_user(test_client, test_db):
    admin_user = User.query.filter_by(username='admin').first()
    user_to_disable = User.query.filter_by(username='datacollector').first()

    put_stuff = {
        'id': user_to_disable.id,
        'is_active': False
    }
    access_token = create_access_token(identity=admin_user.id)
    response = test_client.put(f"/users/{user_to_disable.id}",
                               data=json.dumps(put_stuff),
                               headers={'Content-Type': 'application/json', 'Authorization': f"Bearer {access_token}"})

    assert response.status_code == 200
    json_data = response.get_json()
    assert not json_data['is_active']
    user_to_disable = User.query.filter_by(username='datacollector').first()
    assert not user_to_disable.is_active


def test_disable_user_fails_for_admin(test_client, admin_user, admin_access_token):
    put_stuff = {
        'id': admin_user.id,
        'is_active': False
    }

    response = test_client.put(f"/users/{admin_user.id}",
                               data=json.dumps(put_stuff),
                               headers={'Content-Type': 'application/json', 'Authorization': f"Bearer {admin_access_token}"})

    assert response.status_code == 400
    json_data = response.get_json()
    assert json_data['message'] == 'Admin users cannot be disabled.'


def test_disable_user_fails_without_permission(test_client, test_db):

    request_user = setup_user_with_no_permissions(test_db)
    access_token = create_access_token(identity=request_user.id)
    response = test_client.put(f"/users/99", headers={'Content-Type': 'application/json',
                                                      'Authorization': f"Bearer {access_token}"})
    assert response.status_code == 401


def test_get_single_user(test_client, test_db):
    """
    Scenario: Client successfully retrieves an existing user account
        Given the client accesses the API using a valid access code
        And with an account that has permission to read users
        When the client requests an existing user
        Then the API returns a 200 status
        And the full user object
    """
    requested_user = User.query.filter_by(username='datacollector').first()

    access_token = get_access_token(test_client)
    response = test_client.get(f"/users/{requested_user.id}", headers={'Content-Type': 'application/json',
                                                                       'Authorization': f"Bearer {access_token}"})

    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['id'] == requested_user.id
    assert json_data['username'] == requested_user.username
    assert json_data['name'] == requested_user.name
    assert json_data['email'] == requested_user.email


def test_put_user(test_client, test_db):
    """
    Scenario: Client successfully updates a user with the API
        Given the client accesses the API with a valid access code
        And using an account that has permission to update a user
        When the client submits a valid update to an existing user
        Then the API returns a 200 status
        And the updated user object
    """
    test_user = User.query.filter_by(username='datacollector').first()
    new_name = fake.name()
    submission_data = {
        'id': test_user.id,
        'name': new_name,
        'color': 'grey'
    }
    access_token = get_access_token(test_client)
    response = test_client.put(f"/users/{test_user.id}",
                               data=json.dumps(submission_data),
                               headers={'Content-Type': 'application/json', 'Authorization': f"Bearer {access_token}"})
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['name'] == new_name
    test_user = User.query.filter_by(username='datacollector').first()
    assert test_user.name == new_name
    assert test_user.color == 'grey'


test_put_disable_admin_test_cases = [
    {
        'id': 'try-to-disable-admin',
        'data': {'id': '', 'name': fake.name(), 'is_active': False},
        'status_code': 400,
        'status_message': 'Admin users cannot be disabled.'
    }, {
        'id': 'dont-send-is-active',
        'data': {'id': '', 'name': fake.name()},
        'status_code': 200,
        'status_message': ''
    }, {
        'id': 'send-null-is-active',
        'data': {'id': '', 'name': fake.name(), 'is_active': None},
        'status_code': 200,
        'status_message': ''
    }, {
        'id': 'send-empty-is-active',
        'data': {'id': '', 'name': fake.name(), 'is_active': ''},
        'status_code': 200,
        'status_message': ''
    }
]

test_put_disable_admin_test_cases_ids = [case['id'] for case in test_put_disable_admin_test_cases]


@pytest.mark.parametrize('test_case', test_put_disable_admin_test_cases, ids=test_put_disable_admin_test_cases_ids)
def test_put_disable_admin(test_client, test_db, admin_user, test_case):
    access_token = get_access_token(test_client)
    test_case['data']['id'] = admin_user.id

    response = test_client.put(f"/users/{admin_user.id}",
                               data=json.dumps(test_case['data']),
                               headers={'Content-Type': 'application/json', 'Authorization': f"Bearer {access_token}"})
    assert response.status_code == test_case['status_code']
    if test_case['status_code'] != 200:
        json_data = response.get_json()
        assert json_data['message'] == test_case['status_message']


put_users_invalid_data_test_cases = [
    {
        'id': 'no-system-id',
        'data': {'name': fake.name()},
        'status_code': 400,
        'status_message': 'You must provide a user id in your put object.'
    }, {
        'id': 'mismatched-ids',
        'data': {'id': 99999999, 'name': fake.name()},
        'status_code': 400,
        'status_message': 'The user id in the URL does not match the user id in your put object.'
    },
    {
        'id': 'invalid-color',
        'data': {'id': '<user_id>', 'color': 'green'},
        'status_code': 400,
        'status_message': 'You provided an unsupported color'
    }
]

put_users_invalid_data_test_cases_ids = [case['id'] for case in put_users_invalid_data_test_cases]


@pytest.mark.parametrize('test_case', put_users_invalid_data_test_cases, ids=put_users_invalid_data_test_cases_ids)
def test_put_user_fails_with_invalid_data(test_client, test_db, test_case):
    """
    Scenario: Client attempts to submit a user object without the user's system id in the object
      Given the client accesses the API with a valid access code
      And using an account that has permission to update a user
      When the client submits a an update that does not contain the user's system id
      Then the API returns a 400 status
      And the message "You must provide a user id in your put object."

    Scenario: Client attempts to submit a user object whose id does not match the request URL
      Given the client accesses the API with a valid access code
      And using an account that has permission to update a user
      When the client submits a user object to update
      And the user's system id does not match the user id in the request URL
      Then the API returns a 400 status
      And the message "The user id in the URL does not match the user id in your put object."
    """
    test_user = User.query.filter_by(username='datacollector').first()
    access_token = get_access_token(test_client)

    if test_case['data'].get('id') == '<user_id>':
        test_case['data']['id'] = test_user.id

    response = test_client.put(f"/users/{test_user.id}",
                               data=json.dumps(test_case['data']),
                               headers={'Content-Type': 'application/json', 'Authorization': f"Bearer {access_token}"})
    assert response.status_code == test_case['status_code']
    json_data = response.get_json()
    assert json_data['message'] == test_case['status_message']


def test_put_user_fails_with_existing_email(test_client, test_db):
    test_user = User.query.filter_by(username='datacollector').first()
    other_user = User.query.filter_by(username='datareader').first()
    data = {
               'id': test_user.id,
               'email': other_user.email
           }
    access_token = get_access_token(test_client)
    response = test_client.put(f"/users/{test_user.id}",
                               data=json.dumps(data),
                               headers={'Content-Type': 'application/json', 'Authorization': f"Bearer {access_token}"})
    assert response.status_code == 400
    json_data = response.get_json()
    assert json_data['message'] == 'The email address you provided is already in use.'


def test_put_user_fails_with_empty_email(test_client, test_db):

    test_user = User.query.filter_by(username='datacollector').first()
    data = {
               'id': test_user.id,
               'email': ''
           }
    access_token = get_access_token(test_client)
    response = test_client.put(f"/users/{test_user.id}",
                               data=json.dumps(data),
                               headers={'Content-Type': 'application/json', 'Authorization': f"Bearer {access_token}"})
    assert response.status_code == 400
    json_data = response.get_json()
    assert json_data['message'] == "User's email addresses cannot be null or empty."


def test_put_user_fails_with_none_email(test_client, test_db):

    test_user = User.query.filter_by(username='datacollector').first()
    data = {
               'id': test_user.id,
               'email': None
           }
    access_token = get_access_token(test_client)
    response = test_client.put(f"/users/{test_user.id}",
                               data=json.dumps(data),
                               headers={'Content-Type': 'application/json', 'Authorization': f"Bearer {access_token}"})
    assert response.status_code == 400
    json_data = response.get_json()
    assert json_data['message'] == "User's email addresses cannot be null or empty."


def test_put_user_fails_with_existing_username(test_client, test_db):
    test_user = User.query.filter_by(username='datacollector').first()
    other_user = User.query.filter_by(username='datareader').first()
    data = {
               'id': test_user.id,
               'username': other_user.username
           }
    access_token = get_access_token(test_client)
    response = test_client.put(f"/users/{test_user.id}",
                               data=json.dumps(data),
                               headers={'Content-Type': 'application/json', 'Authorization': f"Bearer {access_token}"})
    assert response.status_code == 400
    json_data = response.get_json()
    assert json_data['message'] == 'The username you provided is already in use.'


def test_put_user_fails_with_empty_username(test_client, test_db):

    test_user = User.query.filter_by(username='datacollector').first()
    data = {
               'id': test_user.id,
               'username': ''
           }
    access_token = get_access_token(test_client)
    response = test_client.put(f"/users/{test_user.id}",
                               data=json.dumps(data),
                               headers={'Content-Type': 'application/json', 'Authorization': f"Bearer {access_token}"})
    assert response.status_code == 400
    json_data = response.get_json()
    assert json_data['message'] == "Usernames cannot be null or empty."


def test_put_user_fails_with_none_username(test_client, test_db):

    test_user = User.query.filter_by(username='datacollector').first()
    data = {
               'id': test_user.id,
               'username': None
           }
    access_token = get_access_token(test_client)
    response = test_client.put(f"/users/{test_user.id}",
                               data=json.dumps(data),
                               headers={'Content-Type': 'application/json', 'Authorization': f"Bearer {access_token}"})
    assert response.status_code == 400
    json_data = response.get_json()
    assert json_data['message'] == "Usernames cannot be null or empty."


def test_put_user_fails_with_invalid_role_id(test_client, test_db):

    test_user = User.query.filter_by(username='datacollector').first()
    data = {
               'id': test_user.id,
               'role_id': 0
           }
    access_token = get_access_token(test_client)
    response = test_client.put(f"/users/{test_user.id}",
                               data=json.dumps(data),
                               headers={'Content-Type': 'application/json', 'Authorization': f"Bearer {access_token}"})
    assert response.status_code == 400
    json_data = response.get_json()
    assert json_data['message'] == "The provided role id is not a valid role id."


def test_put_users_fails_with_change_in_active_without_permission(test_client, test_db):

    test_user = User.query.filter_by(username='datacollector').first()
    submission_data = {
        'id': test_user.id,
        'is_active': False
    }
    access_token = create_access_token(identity=test_user.id)

    response = test_client.put(f"/users/{test_user.id}",
                               data=json.dumps(submission_data),
                               headers={'Content-Type': 'application/json', 'Authorization': f"Bearer {access_token}"})
    assert response.status_code == 401
    json_data = response.get_json()
    assert json_data['message'] == "You do not have permission to change someone's active flag."


users_without_permission_test_cases = [
    {
        'id': 'put-user',
        'url': "/users/1",
        'method': 'PUT',
        'response_message': 'You do not have permission to update users.'
    }, {
        'id': 'get-user',
        'url': "/users/1",
        'method': 'GET',
        'response_message': 'You do not have permission to read users.'
    }, {
        'id': 'get-users',
        'url': '/users/',
        'method': 'GET',
        'response_message': 'You do not have permission to read users.'
    }, {
        'id': 'post-user',
        'url': '/users/',
        'method': 'POST',
        'response_message': 'You do not have permission to add a user to the system.'
    }, {
        'id': 'delete-user',
        'url': "/users/1",
        'method': 'DELETE',
        'response_message': 'You do not have permission to delete users.'
    }
]

users_without_permission_test_cases_ids = [case['id'] for case in users_without_permission_test_cases]


@pytest.mark.parametrize('test_case', users_without_permission_test_cases, ids=users_without_permission_test_cases_ids)
def test_users_fails_without_permission(test_client, test_db, test_case):
    test_user = setup_user_with_no_permissions(test_db)
    access_token = create_access_token(identity=test_user.id)
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


unknown_user_test_cases = [
    {
        'id': 'delete-user',
        'url': "/users/99",
        'method': 'DELETE'
    }, {
        'id': 'get-user',
        'url': "/users/99",
        'method': 'GET'
    }, {
        'id': 'put-user',
        'url': "/users/99",
        'method': 'PUT'
    }
]

unknown_user_test_cases_ids = [case['id'] for case in unknown_user_test_cases]


@pytest.mark.parametrize('test_case', unknown_user_test_cases, ids=unknown_user_test_cases_ids)
def test_users_fails_with_unknown_user(test_client, test_db, test_case):
    request_user = User.query.filter_by(username='admin').first()
    access_token = create_access_token(identity=request_user.id)
    headers = {'Content-Type': 'application/json', 'Authorization': f"Bearer {access_token}"}
    if test_case['method'] == 'POST':
        response = test_client.post(test_case['url'], headers=headers)
    elif test_case['method'] == 'PUT':
        response = test_client.put(test_case['url'], headers=headers)
    elif test_case['method'] == 'DELETE':
        response = test_client.delete(test_case['url'], headers=headers)
    else:
        response = test_client.get(test_case['url'], headers=headers)

    assert response.status_code == 404


get_users_filter_test_cases = [
    {
        'id': 'default-only-active',
        'url': '/users/',
        'response_status': 200,
        'response_length': 4
    }, {
        'id': 'only-active',
        'url': '/users/?status=active',
        'response_status': 200,
        'response_length': 4
    }, {
        'id': 'only-inactive',
        'url': '/users/?status=inactive',
        'response_status': 200,
        'response_length': 5
    }, {
        'id': 'all',
        'url': '/users/?status=any',
        'response_status': 200,
        'response_length': 9
    }
]

get_users_filter_test_case_ids = [case['id'] for case in get_users_filter_test_cases]


@pytest.mark.parametrize('test_case', get_users_filter_test_cases, ids=get_users_filter_test_case_ids)
def test_get_users_filter(test_client, test_db, test_case):
    # There are already 4 active users in the test DB. Adding 5 inactive users
    for x in range(0, 5):
        test_db.session.add(User(email=fake.email(), username=fake.user_name(), password=fake.password(),
                                 name=fake.name(), is_active=False))
    test_db.session.commit()

    access_token = get_access_token(test_client)
    response = test_client.get(test_case['url'], headers={'Content-Type': 'application/json',
                                                          'Authorization': f"Bearer {access_token}"})

    assert response.status_code == test_case['response_status']
    assert len(response.get_json()) == test_case['response_length']


def test_get_single_user_returns_inactive_user(test_client, test_db):

    requested_user = User(email=fake.email(), username=fake.user_name(), password=fake.password(),
                          name=fake.name(), is_active=False)
    test_db.session.add(requested_user)
    test_db.session.commit()

    access_token = get_access_token(test_client)
    response = test_client.get(f"/users/{requested_user.id}", headers={'Content-Type': 'application/json',
                                                                       'Authorization': f"Bearer {access_token}"})

    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['id'] == requested_user.id
    assert json_data['username'] == requested_user.username
    assert json_data['name'] == requested_user.name
    assert json_data['email'] == requested_user.email


def test_resend_welcome_fails_without_permission(test_client, test_db):

    request_user = setup_user_with_no_permissions(test_db)
    access_token = create_access_token(identity=request_user.id)
    response = test_client.post(f"/users/99/resend-welcome", headers={'Content-Type': 'application/json',
                                                                      'Authorization': f"Bearer {access_token}"})
    assert response.status_code == 401
    json_data = response.get_json()
    assert json_data['message'] == "You do not have permission to resend a welcome email to a user."


def test_resend_welcome_fails_without_userid(test_client, test_db):

    access_token = get_access_token(test_client)
    response = test_client.post("/users//resend-welcome", headers={'Content-Type': 'application/json',
                                                                   'Authorization': f"Bearer {access_token}"})
    assert response.status_code == 404


def test_resend_welcome_fails_with_unknown_userid(test_client, test_db):
    access_token = get_access_token(test_client)
    response = test_client.post("/users/99/resend-welcome", headers={'Content-Type': 'application/json',
                                                                     'Authorization': f"Bearer {access_token}"})
    assert response.status_code == 404


def test_resend_welcome(test_client, test_db):

    admin_user = User.query.filter_by(username='admin').first()
    resend_user = User.query.filter_by(username='datacollector').first()

    access_token = create_access_token(identity=admin_user.id)
    response = test_client.post(f"/users/{resend_user.id}/resend-welcome",
                                headers={'Content-Type': 'application/json', 'Authorization': f"Bearer {access_token}"})
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['message'] == "The welcome email was sent to the user."

