from app import models
import pytest
import json


def test_get_case_status(test_client, test_db, admin_access_token):
    case_status_args = {'id': 1, 'name': 'TODO', 'default': True, 'is_final': False, 'color': '#B3B6B7'}

    resp = test_client.get('/case_statuses/1', headers={'Authorization': f'Bearer {admin_access_token}'})

    assert resp.status_code == 200
    assert resp.json == case_status_args


def test_get_case_statuses(test_client, test_db, admin_access_token):
    case_status_args = [
        {'id': 1, 'name': 'TODO', 'default': True, 'is_final': False, 'color': '#B3B6B7'},
        {'id': 2, 'name': 'In Progress', 'default': False, 'is_final': False, 'color': '#0000FF'},
        {'id': 3, 'name': 'Done', 'default': False, 'is_final': True, 'color': '#00FF00'},
    ]

    resp = test_client.get('/case_statuses', headers={'Authorization': f'Bearer {admin_access_token}'})

    assert resp.status_code == 200
    assert resp.json == case_status_args


post_valid_data_case_status = [
    {
        'id': 'Normal Case Status',
        'data': {
            'name': 'NormalStatus',
            'default': False,
            'is_final': False,
            'color': '#FFFFFF'
        },
    },
    {
        'id': 'Default Case Status',
        'data': {
            'name': 'DefaultStatus',
            'default': True,
            'is_final': False,
            'color': '#FFFFFF'
        },
    },
    {
        'id': 'Final Case Status',
        'data': {
            'name': 'FinalStatus',
            'default': False,
            'is_final': True,
            'color': '#FFFFFF'
        },
    },
    {
        'id': 'No Color Case Status',
        'data': {
            'name': 'RandColorStatus',
            'default': False,
            'is_final': False,
        },
    },
    {
        'id': 'No Default Case Status',
        'data': {
            'name': 'NoDefaultStatus',
            'is_final': False,
            'color': '#FFFFFF'
        },
    },
    {
        'id': 'No is_final Case Status',
        'data': {
            'name': 'NoFinalStatus',
            'default': False,
            'color': '#FFFFFF'
        },
    },
]

post_valid_data_case_status_ids = [cs['id'] for cs in post_valid_data_case_status]


@pytest.mark.parametrize('case_status_params', post_valid_data_case_status,
                         ids=post_valid_data_case_status_ids)
def test_post_valid_case_status(test_client, test_db, admin_access_token, case_status_params):
    resp = test_client.post(
        '/case_statuses', data=json.dumps(case_status_params['data']),
        headers={'Content-Type': 'application/json', 'Authorization': f"Bearer {admin_access_token}"}
    )

    assert resp.status_code == 200

    assert case_status_params['data'].items() < resp.json.items()

    if 'default' not in case_status_params['data']:
        assert resp.json['default'] is False

    if 'is_final' not in case_status_params['data']:
        assert resp.json['is_final'] is False

    if 'color' not in case_status_params['data']:
        assert 'color' in resp.json


post_invalid_data_case_status = [
    {
        'id': 'No Name Case Status',
        'data': {
            'default': False,
            'is_final': False,
            'color': '#FFFFFF'
        },
        'message': 'A name is required for a case status.'
    },
    {
        'id': 'Empty Name Case Status',
        'data': {
            'name': '',
            'default': False,
            'is_final': False,
            'color': '#FFFFFF'
        },
        'message': 'A name is required for a case status.'
    },
    {
        'id': 'Long Name Case Status',
        'data': {
            'name': 'Loooooooooooooooooooooooooooooooooooooooooooongname',  # 51 chars
            'default': False,
            'is_final': False,
            'color': '#FFFFFF'
        },
        'message': 'Case status names cannot be longer than 50 characters.'
    },
    {
        'id': 'Duplicate Name Case Status',
        'data': {
            'name': 'TODO',
            'default': False,
            'is_final': False,
        },
        'message': 'Case status names must be unique.'
    },
]

post_invalid_data_case_status_ids = [cs['id'] for cs in post_invalid_data_case_status]


@pytest.mark.parametrize('case_status_params', post_invalid_data_case_status,
                         ids=post_invalid_data_case_status_ids)
def test_post_case_status_invalid_name(test_client, test_db, admin_access_token, case_status_params):
    resp = test_client.post(
        '/case_statuses', data=json.dumps(case_status_params['data']),
        headers={'Content-Type': 'application/json', 'Authorization': f"Bearer {admin_access_token}"}
    )

    assert resp.status_code == 400
    assert resp.json['message'] == case_status_params['message']


def test_post_case_status_new_default(test_client, test_db, admin_access_token):
    data = {
        'name': 'Status',
        'default': True,
        'is_final': False,
        'color': '#FFFFFF'
    }

    resp = test_client.post(
        '/case_statuses', data=json.dumps(data),
        headers={'Content-Type': 'application/json', 'Authorization': f"Bearer {admin_access_token}"}
    )

    assert resp.status_code == 200
    assert resp.json['default'] is True

    default_id = resp.json['id']

    data['name'] = 'Status2'

    resp = test_client.post(
        '/case_statuses', data=json.dumps(data),
        headers={'Content-Type': 'application/json', 'Authorization': f"Bearer {admin_access_token}"}
    )

    assert resp.status_code == 200
    assert resp.json['default'] is True

    resp = test_client.get(
        f'/case_statuses/{default_id}',
        headers={'Content-Type': 'application/json', 'Authorization': f"Bearer {admin_access_token}"}
    )

    assert resp.status_code == 200
    assert resp.json['default'] is False


def test_post_case_status_random_color(test_client, test_db, admin_access_token):
    data = {
        'name': 'Status',
        'default': False,
        'is_final': False,
    }

    resp = test_client.post(
        '/case_statuses', data=json.dumps(data),
        headers={'Content-Type': 'application/json', 'Authorization': f"Bearer {admin_access_token}"}
    )

    assert resp.status_code == 200
    assert 'color' in resp.json
    assert resp.json['color'] in models.CaseStatus.supported_colors()


def test_put_valid_case_status(test_client, test_db, admin_access_token):
    data = {
        'name': 'Status',
        'default': False,
        'is_final': True,
        'color': '#FFFFFF'
    }

    resp = test_client.post(
        '/case_statuses', data=json.dumps(data),
        headers={'Content-Type': 'application/json', 'Authorization': f"Bearer {admin_access_token}"}
    )

    assert resp.status_code == 200
    assert data.items() < resp.json.items()

    update = {
        'name': 'NewStatus',
        'default': True,
        'is_final': False,
        'color': '#000000'
    }

    resp = test_client.put(
        f'/case_statuses/{resp.json["id"]}', data=json.dumps(update),
        headers={'Content-Type': 'application/json', 'Authorization': f"Bearer {admin_access_token}"}
    )

    assert resp.status_code == 200
    assert update.items() < resp.json.items()


put_valid_data_case_status = [
    {
        'id': 'Empty Name Case Status',
        'data': {
            'name': '',
        },
        'message': 'A name is required for a case status.'
    },
    {
        'id': 'Long Name Case Status',
        'data': {
            'name': 'Loooooooooooooooooooooooooooooooooooooooooooongname',  # 51 chars
        },
        'message': 'Case status names cannot be longer than 50 characters.'
    },
    {
        'id': 'Duplicate Name Case Status',
        'data': {
            'name': 'TODO',
        },
        'message': 'Case status names must be unique.'
    },
]

put_valid_data_case_status_ids = [cs['id'] for cs in put_valid_data_case_status]


@pytest.mark.parametrize('case_status_params', put_valid_data_case_status,
                         ids=put_valid_data_case_status_ids)
def test_put_case_status_invalid_name(test_client, test_db, admin_access_token, case_status_params):
    data = {
        'name': 'Status',
        'default': False,
        'is_final': True,
        'color': '#FFFFFF'
    }

    resp = test_client.post(
        '/case_statuses', data=json.dumps(data),
        headers={'Content-Type': 'application/json', 'Authorization': f"Bearer {admin_access_token}"}
    )

    assert resp.status_code == 200

    case_status_id = resp.json["id"]

    resp = test_client.put(
        f'/case_statuses/{case_status_id}', data=json.dumps(case_status_params['data']),
        headers={'Content-Type': 'application/json', 'Authorization': f"Bearer {admin_access_token}"}
    )

    assert resp.status_code == 400
    assert resp.json['message'] == case_status_params['message']

    resp = test_client.get(
        f'/case_statuses/{case_status_id}',
        headers={'Content-Type': 'application/json', 'Authorization': f"Bearer {admin_access_token}"}
    )

    assert resp.status_code == 200
    assert data.items() < resp.json.items()


def test_put_case_status_new_default(test_client, test_db, admin_access_token):
    # Insert default CaseStatus
    data = {
        'name': 'Status',
        'default': True,
        'is_final': False,
        'color': '#FFFFFF'
    }

    resp = test_client.post(
        '/case_statuses', data=json.dumps(data),
        headers={'Content-Type': 'application/json', 'Authorization': f"Bearer {admin_access_token}"}
    )

    assert resp.status_code == 200
    assert resp.json['default'] is True

    default_id = resp.json['id']

    # Insert nondefault CaseStatus
    data = {
        'name': 'Status2',
        'default': False,
        'is_final': False,
        'color': '#FFFFFF'
    }

    resp = test_client.post(
        '/case_statuses', data=json.dumps(data),
        headers={'Content-Type': 'application/json', 'Authorization': f"Bearer {admin_access_token}"}
    )

    assert resp.status_code == 200
    assert resp.json['default'] is False

    update_id = resp.json['id']

    # Verify default CaseStatus is still default
    resp = test_client.get(
        f'/case_statuses/{default_id}',
        headers={'Content-Type': 'application/json', 'Authorization': f"Bearer {admin_access_token}"}
    )

    assert resp.status_code == 200
    assert resp.json['default'] is True

    # Update nondefault CaseStatus to new default
    data = {'default': True}
    resp = test_client.put(
        f'/case_statuses/{update_id}', data=json.dumps(data),
        headers={'Content-Type': 'application/json', 'Authorization': f"Bearer {admin_access_token}"}
    )

    assert resp.status_code == 200
    assert resp.json['default'] is True

    # Old default CaseStatus should no longer be so
    resp = test_client.get(
        f'/case_statuses/{default_id}',
        headers={'Content-Type': 'application/json', 'Authorization': f"Bearer {admin_access_token}"}
    )

    assert resp.status_code == 200
    assert resp.json['default'] is False


def test_delete_case_status(test_client, test_db, admin_access_token):
    data = {
        'name': 'Status',
        'default': False,
        'is_final': False,
        'color': '#FFFFFF'
    }

    resp = test_client.post(
        '/case_statuses', data=json.dumps(data),
        headers={'Content-Type': 'application/json', 'Authorization': f"Bearer {admin_access_token}"}
    )

    assert resp.status_code == 200

    case_status_id = resp.json['id']

    resp = test_client.get(
        f'/case_statuses/{case_status_id}',
        headers={'Content-Type': 'application/json', 'Authorization': f"Bearer {admin_access_token}"}
    )

    assert resp.status_code == 200

    resp = test_client.delete(
        f'/case_statuses/{case_status_id}',
        headers={'Content-Type': 'application/json', 'Authorization': f"Bearer {admin_access_token}"}
    )

    assert resp.status_code == 200

    resp = test_client.get(
        f'/case_statuses/{case_status_id}',
        headers={'Content-Type': 'application/json', 'Authorization': f"Bearer {admin_access_token}"}
    )

    assert resp.status_code == 404
