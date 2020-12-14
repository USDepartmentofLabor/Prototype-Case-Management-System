import pytest
import json
import flask_jwt_extended
from tests import test_helpers
from app import models


def setup_role(test_client):
    access_token = test_helpers.get_access_token(test_client)
    headers = {'Content-Type': 'application/json', 'Authorization': f"Bearer {access_token}"}
    role = {
        'name': 'test_role',
        'default': False,
        'permissions': 1
    }

    resp = test_client.post('/roles', data=json.dumps(role), headers=headers)
    assert resp.status_code == 200

    return resp.json['id'], headers


def test_post_role(test_client, test_db):
    _, headers = setup_role(test_client)

    role = {
        'name': 'test_role_2',
        'default': False,
        'permissions': 1
    }

    resp = test_client.post('/roles', data=json.dumps(role), headers=headers)
    assert resp.status_code == 200


def test_post_role_invalid(test_client, test_db):
    _, headers = setup_role(test_client)

    role = {
        'name': '',
        'default': False,
        'permissions': 1
    }

    resp = test_client.post('/roles', data=json.dumps(role), headers=headers)
    assert resp.status_code == 400

    role['name'] = '*' * 65

    resp = test_client.post('/roles', data=json.dumps(role), headers=headers)
    assert resp.status_code == 400


def test_fetch_all_roles(test_client, test_db):
    _, headers = setup_role(test_client)

    resp = test_client.get('/roles', headers=headers)
    assert resp.status_code == 200

    assert isinstance(resp.json, list)
    assert len(resp.json) > 0


def test_fetch_role(test_client, test_db):
    role_id, headers = setup_role(test_client)

    resp = test_client.get(f'/roles/{role_id}', headers=headers)
    assert resp.status_code == 200

    assert resp.json['id'] == role_id
    assert resp.json['name'] == 'test_role'
    assert resp.json['default'] is False
    assert resp.json['permissions'] == 1


def test_update_role(test_client, test_db):
    role_id, headers = setup_role(test_client)

    updates = {
        'name': 'test_role_2',
        'default': False,
        'permissions': 1
    }

    resp = test_client.put(f'/roles/{role_id}', data=json.dumps(updates), headers=headers)
    assert resp.status_code == 200

    resp = test_client.get(f'/roles/{role_id}', headers=headers)
    assert resp.status_code == 200

    assert resp.json['id'] == role_id
    assert resp.json['name'] == 'test_role_2'
    assert resp.json['default'] is False
    assert resp.json['permissions'] == 1


def test_update_role_invalid(test_client, test_db):
    role_id, headers = setup_role(test_client)

    updates = {
        'name': '1234567890' * 7,
    }

    resp = test_client.put(f'/roles/{role_id}', data=json.dumps(updates), headers=headers)
    assert resp.status_code == 400


def test_delete_role(test_client, test_db):
    role_id, headers = setup_role(test_client)

    resp = test_client.delete(f'/roles/{role_id}', headers=headers)
    assert resp.status_code == 200

    resp = test_client.get(f'/roles/{role_id}', headers=headers)
    assert resp.status_code == 404


def test_delete_role_reassigns_role_to_default(test_client, test_db):
    role_id, headers = setup_role(test_client)
    default_role = models.Role.query.filter_by(default=True).first()
    test_role = models.Role.query.get(role_id)

    user = models.User(
        email=test_helpers.fake.email(),
        username=test_helpers.fake.user_name(),
        password=test_helpers.fake.password(),
        name=test_helpers.fake.name(),
        role=test_role
    )
    test_db.session.add(user)
    test_db.session.commit()

    resp = test_client.delete(f'/roles/{role_id}', headers=headers)
    assert resp.status_code == 200
    assert user.role_id == default_role.id


def test_delete_admin_role_returns_error(test_client, test_db):
    role_id, headers = setup_role(test_client)
    admin_role = models.Role.query.filter_by(name='Admin').first()
    resp = test_client.delete(f'/roles/{admin_role.id}', headers=headers)
    assert resp.status_code == 400
    json_data = resp.get_json()
    assert json_data['message'] == 'Cannot delete the admin role.'


def test_delete_default_role_returns_error(test_client, test_db):
    role_id, headers = setup_role(test_client)
    default_role = models.Role.query.filter_by(default=True).first()
    resp = test_client.delete(f'/roles/{default_role.id}', headers=headers)
    assert resp.status_code == 400
    json_data = resp.get_json()
    assert json_data['message'] == 'Cannot delete the default role.'


def test_role_auth(test_client, test_db):
    resp = test_client.post('/roles', data={})
    assert resp.status_code == 401

    resp = test_client.get('/roles')
    assert resp.status_code == 401

    resp = test_client.get('/roles/1')
    assert resp.status_code == 401

    resp = test_client.put('/roles/1', data={})
    assert resp.status_code == 401

    resp = test_client.delete('/roles/1')
    assert resp.status_code == 401


permission_test_cases = [
    {
        'id': 'post-role',
        'url': '/roles',
        'method': 'POST',
        'response_message': 'You do not have permission to add a role.'
    }, {
        'id': 'get-role',
        'url': '/roles',
        'method': 'GET',
        'response_message': 'You do not have permission to view roles.'
    }, {
        'id': 'put-role',
        'url': '/roles/1',
        'method': 'PUT',
        'response_message': 'You do not have permission to update a role.'
    }, {
        'id': 'delete-role',
        'url': '/roles/1',
        'method': 'DELETE',
        'response_message': 'You do not have permission to delete a role.'
    }
]
permission_test_cases_ids = [case['id'] for case in permission_test_cases]


@pytest.mark.parametrize('test_case', permission_test_cases, ids=permission_test_cases_ids)
def test_roles_fails_without_permission(test_client, test_db, test_case, user_with_no_permissions):

    access_token = flask_jwt_extended.create_access_token(identity=user_with_no_permissions.id)
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


def test_post_multiple_default_roles_fails(test_client, test_db):
    access_token = test_helpers.get_access_token(test_client)
    headers = {'Content-Type': 'application/json', 'Authorization': f"Bearer {access_token}"}

    role = {
        'name': 'test_role_2',
        'default': True,
        'permissions': 2
    }

    resp = test_client.post('/roles', data=json.dumps(role), headers=headers)
    assert resp.status_code == 400
    assert resp.json['message'] == 'A default role already exists.'


def test_update_default_role(test_client, test_db):
    role_id, headers = setup_role(test_client)

    update = {'default': True}

    resp = test_client.put(
        f'/roles/{role_id}',
        data=json.dumps(update),
        headers=headers
    )
    assert resp.status_code == 400
    assert resp.json['message'] == 'A default role already exists.'
