from unittest import mock
from tests import test_helpers
import json


def test_insert_multiple_users_no_metabase(test_client, test_db):
    with mock.patch('app.users.views.metabase', autospeck=True) as metabase_mock:
        access_token = test_helpers.get_access_token(test_client)
        headers = {'Content-Type': 'application/json', 'Authorization': f"Bearer {access_token}"}

        new_user_1 = {
            'email': test_helpers.fake.email(),
            'username': test_helpers.fake.user_name(),
            'role_id': 2,
            'name': test_helpers.fake.name(),
            'location': test_helpers.fake.address()
        }

        new_user_2 = {
            'email': test_helpers.fake.email(),
            'username': test_helpers.fake.user_name(),
            'role_id': 2,
            'name': test_helpers.fake.name(),
            'location': test_helpers.fake.address()
        }

        metabase_mock.insert_user.return_value = None  # Pretend metabase is not running

        resp = test_client.post(
            '/users/',
            data=json.dumps(new_user_1),
            headers=headers
        )
        assert resp.status_code == 200

        metabase_mock.insert_user.assert_called_once()

        assert resp.json['metabase_user_id'] is None

        resp = test_client.post(
            '/users/',
            data=json.dumps(new_user_2),
            headers=headers
        )
        assert resp.status_code == 200
        assert resp.json['metabase_user_id'] is None

        # No exception thrown
