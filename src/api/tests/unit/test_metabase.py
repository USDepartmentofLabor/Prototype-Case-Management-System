from unittest import mock
from app import models
from tests import test_helpers
import json


def test_metabase_rescan_triggered(test_client, test_db):
    user = models.User.query.filter_by(username='admin').first()
    new_survey = models.Survey(
        name='test',
        reporting_table_name='test',
        structure={},
        created_by=user,
        updated_by=user
    )

    with mock.patch('app.surveys.views.models.helpers') as helpers_mock:
        test_db.session.add(new_survey)
        test_db.session.commit()

        helpers_mock.metabase_rescan.assert_called_once()

        helpers_mock.reset_mock()

        survey = models.Survey.query.get_or_404(1)

        survey.name = 'test_2'
        survey.mongo_collection_name = 'test_2'
        test_db.session.commit()

        helpers_mock.metabase_rescan.assert_called_once()

        helpers_mock.reset_mock()

        test_db.session.delete(survey)
        test_db.session.commit()

        helpers_mock.metabase_rescan.assert_called_once()


def test_no_rescan_on_case_definition_add_survey(test_client, test_db):
    with mock.patch('app.surveys.views.models.helpers.metabase_rescan', autospec=True) as rescan_mock:
        case_definition = {
            "name": "test_name",
            "key": "TCD1",
            "description": "test_desc",
            "surveys": [],
            "documents": []
        }

        survey = {'name': 'test survey', 'structure': {}}

        access_token = test_helpers.get_access_token(test_client)
        headers = {'Content-Type': 'application/json', 'Authorization': f"Bearer {access_token}"}

        resp = test_client.post(
            "/surveys/", data=json.dumps(survey),
            headers=headers
        )
        assert resp.status_code == 200

        survey_id = resp.json['id']

        resp = test_client.post(
            "/case_definitions/", data=json.dumps(case_definition),
            headers=headers
        )
        assert resp.status_code == 200

        case_defn_id = resp.json['id']

        resp = test_client.get(
            f'/case_definitions/{case_defn_id}',
            headers=headers
        )
        assert resp.status_code == 200
        assert resp.json['surveys'] == []

        rescan_mock.assert_called()
        rescan_mock.reset_mock()

        case_defn = resp.json
        case_defn['surveys'] = [survey_id]

        resp = test_client.put(
            f'/case_definitions/{case_defn_id}',
            data=json.dumps(case_defn),
            headers=headers
        )
        assert resp.status_code == 200

        rescan_mock.assert_not_called()

        case_defn['surveys'] = []
        resp = test_client.put(
            f'/case_definitions/{case_defn_id}',
            data=json.dumps(case_defn),
            headers=headers
        )
        assert resp.status_code == 200

        rescan_mock.assert_not_called()


def test_insert_metabase_user(test_client, test_db):
    with mock.patch('app.users.views.metabase', autospeck=True) as metabase_mock:
        access_token = test_helpers.get_access_token(test_client)
        headers = {'Content-Type': 'application/json', 'Authorization': f"Bearer {access_token}"}

        new_user = {
            'email': test_helpers.fake.email(),
            'username': test_helpers.fake.user_name(),
            'role_id': 2,
            'name': test_helpers.fake.name(),
            'location': test_helpers.fake.address()
        }

        metabase_mock.insert_user.return_value = 1

        resp = test_client.post(
            '/users/',
            data=json.dumps(new_user),
            headers=headers
        )
        assert resp.status_code == 200

        metabase_mock.insert_user.assert_called_once()

        assert resp.json['metabase_user_id'] == 1


def test_update_metabase_user(test_client, test_db):
    with mock.patch('app.users.views.metabase', autospeck=True) as metabase_mock:
        access_token = test_helpers.get_access_token(test_client)
        headers = {'Content-Type': 'application/json', 'Authorization': f"Bearer {access_token}"}

        new_user = {
            'email': test_helpers.fake.email(),
            'username': test_helpers.fake.user_name(),
            'role_id': 2,
            'name': test_helpers.fake.name(),
            'location': test_helpers.fake.address()
        }

        metabase_mock.insert_user.return_value = 1

        resp = test_client.post(
            '/users/',
            data=json.dumps(new_user),
            headers=headers
        )
        assert resp.status_code == 200

        user_id = resp.json['id']

        updates = {
            'email': 'test_email_update@example.com',
            'username': 'test_username_update'
        }

        resp = test_client.put(
            f'/users/{user_id}',
            data=json.dumps({
                'id': user_id,
                **updates
            }),
            headers=headers
        )
        assert resp.status_code == 200

        metabase_mock.update_user.assert_called_once_with(1, updates)
        metabase_mock.deactivate_user.assert_not_called()
        metabase_mock.reactivate_user.assert_not_called()


def test_change_password_update_metabase_user(test_client, test_db):
    with mock.patch('app.users.views.metabase', autospeck=True) as metabase_mock:
        access_token = test_helpers.get_access_token(test_client)
        headers = {'Content-Type': 'application/json', 'Authorization': f"Bearer {access_token}"}

        new_user = {
            'email': test_helpers.fake.email(),
            'username': test_helpers.fake.user_name(),
            'role_id': 2,
            'name': test_helpers.fake.name(),
            'location': test_helpers.fake.address()
        }

        metabase_mock.insert_user.return_value = 1

        resp = test_client.post(
            '/users/',
            data=json.dumps(new_user),
            headers=headers
        )
        assert resp.status_code == 200

        user_id = resp.json['id']

        updates = {
            'new_password': 'password_update',
            'confirm_password': 'password_update'
        }

        resp = test_client.post(
            f'/users/{user_id}/change-password',
            data=json.dumps(updates),
            headers=headers
        )
        assert resp.status_code == 200

        metabase_mock.update_user.assert_called_once_with(1, {'password': updates['new_password']})


def test_delete_metabase_user(test_client, test_db):
    with mock.patch('app.users.views.metabase', autospeck=True) as metabase_mock:
        access_token = test_helpers.get_access_token(test_client)
        headers = {'Content-Type': 'application/json', 'Authorization': f"Bearer {access_token}"}

        new_user = {
            'email': test_helpers.fake.email(),
            'username': test_helpers.fake.user_name(),
            'role_id': 2,
            'name': test_helpers.fake.name(),
            'location': test_helpers.fake.address()
        }

        metabase_mock.insert_user.return_value = 1

        resp = test_client.post(
            '/users/',
            data=json.dumps(new_user),
            headers=headers
        )
        assert resp.status_code == 200

        user_id = resp.json['id']

        resp = test_client.delete(
            f'/users/{user_id}',
            headers=headers
        )
        assert resp.status_code == 200

        metabase_mock.deactivate_user.assert_called_once_with(1)


def test_reactivate_user(test_client, test_db):
    with mock.patch('app.users.views.metabase', autospeck=True) as metabase_mock:
        access_token = test_helpers.get_access_token(test_client)
        headers = {'Content-Type': 'application/json', 'Authorization': f"Bearer {access_token}"}

        new_user = {
            'email': test_helpers.fake.email(),
            'username': test_helpers.fake.user_name(),
            'role_id': 2,
            'name': test_helpers.fake.name(),
            'location': test_helpers.fake.address()
        }

        metabase_mock.insert_user.return_value = 1

        resp = test_client.post(
            '/users/',
            data=json.dumps(new_user),
            headers=headers
        )
        assert resp.status_code == 200

        user_id = resp.json['id']

        updates = {
            'is_active': False
        }

        resp = test_client.put(
            f'/users/{user_id}',
            data=json.dumps({
                'id': user_id,
                **updates
            }),
            headers=headers
        )
        assert resp.status_code == 200

        metabase_mock.deactivate_user.assert_called_once_with(1)
        metabase_mock.reactivate_user.assert_not_called()

        metabase_mock.reset_mock()

        updates = {
            'is_active': True
        }

        resp = test_client.put(
            f'/users/{user_id}',
            data=json.dumps({
                'id': user_id,
                **updates
            }),
            headers=headers
        )
        assert resp.status_code == 200

        metabase_mock.reactivate_user.assert_called_once_with(1)
        metabase_mock.deactivate_user.assert_not_called()
