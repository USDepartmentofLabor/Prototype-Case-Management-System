import time
import datetime
from werkzeug import http
import flask
import json, copy
from flask_jwt_extended import create_access_token
from app.models import Survey, SurveyResponse, User, SurveyResponseStatus, CaseDefinition
from ..test_helpers import get_access_token, setup_user_with_no_permissions, get_access_token_for_user
from faker import Faker
import pytest

fake = Faker()


def test_get_all_surveys_no_data(test_client, test_db):
    access_token = get_access_token(test_client)
    response = test_client.get('/surveys/', headers={'Content-Type': 'application/json',
                                                     'Authorization': f"Bearer {access_token}"})
    assert response.status_code == 200
    assert len(response.get_json()) == 0


def test_get_all_surveys_one_survey(test_client, test_db, basic_test_survey):
    access_token = get_access_token(test_client)

    response = test_client.get('/surveys/', headers={'Content-Type': 'application/json',
                                                     'Authorization': f"Bearer {access_token}"})

    assert response.status_code == 200
    assert len(response.get_json()) == 1


def test_get_all_surveys_n_surveys(test_client, test_db):
    user = User.query.filter_by(username='admin').first()
    for x in range(0, 10):
        test_db.session.add(Survey(name=f"test survey {x}", structure={}, created_by=user, updated_by=user))
    test_db.session.commit()

    access_token = get_access_token(test_client)
    response = test_client.get('/surveys/', headers={'Content-Type': 'application/json',
                                                     'Authorization': f"Bearer {access_token}"})

    assert response.status_code == 200
    assert len(response.get_json()) == 10


get_surveys_test_cases = [
    {
        'id': 'default-only-not-archived',
        'url': '/surveys/',
        'response_status': 200,
        'response_length': 5
    }, {
        'id': 'only-not-archived',
        'url': '/surveys/?archived=none',
        'response_status': 200,
        'response_length': 5
    }, {
        'id': 'only-archived',
        'url': '/surveys/?archived=all',
        'response_status': 200,
        'response_length': 5
    }, {
        'id': 'all',
        'url': '/surveys/?archived=any',
        'response_status': 200,
        'response_length': 10
    }
]

get_surveys_test_case_ids = [case['id'] for case in get_surveys_test_cases]


@pytest.mark.parametrize('test_case', get_surveys_test_cases, ids=get_surveys_test_case_ids)
def test_get_all_surveys(test_client, test_db, test_case):
    """
    Covers

    Scenario: Archived surveys are not returned by default
      Given the client accesses the API with a valid access code
      And using an account that has permission to read surveys
      When the client requests the list of surveys with no filter
      Then the API returns a status 200
      And and a list of all surveys that are not archived

    Scenario: Client requests only non-archived surveys
      Given the client accesses the API with a valid access code
      And using an account that has permission to read surveys
      When the client requests the list of non-archived surveys
      Then the API returns a status 200
      And a list of all surveys that are not archived

    Scenario: Client requests only archived surveys
      Given the client accesses the API with a valid access code
      And using an account that has permission to read surveys
      When the client requests the list of archived surveys
      Then the API returns a status 200
      And a list of all surveys that are archived
    """
    user = User.query.filter_by(username='admin').first()
    for x in range(0, 10):
        test_db.session.add(Survey(name=f"test survey {x}", structure={}, created_by=user, updated_by=user,
                                   is_archived=(x % 2 == 0)))
    test_db.session.commit()

    access_token = get_access_token(test_client)
    response = test_client.get(test_case['url'], headers={'Content-Type': 'application/json',
                                                          'Authorization': f"Bearer {access_token}"})

    assert response.status_code == test_case['response_status']
    assert len(response.get_json()) == test_case['response_length']


def test_get_survey(test_client, basic_test_survey):
    survey_id = basic_test_survey.id

    access_token = get_access_token(test_client)
    response = test_client.get(f"/surveys/{survey_id}", headers={'Content-Type': 'application/json',
                                                                 'Authorization': f"Bearer {access_token}"})

    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['id']
    assert json_data['id'] == survey_id


def test_get_survey_still_returns_archived_survey(test_client, basic_test_survey):
    """
    Covers

    Scenario: Client requests a survey that is archived
      Given the client accesses the API with a valid access code
      And using an account that has permission to read surveys
      When a client requests a survey that is archived
      Then the API returns a status 200
      And the survey object as JSON
    """

    access_token = get_access_token(test_client)
    response = test_client.get(f"/surveys/{basic_test_survey.id}",
                               headers={'Content-Type': 'application/json',
                                        'Authorization': f"Bearer {access_token}"})

    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['id']
    assert json_data['id'] == basic_test_survey.id


def test_get_survey_fails_with_unknown_survey(test_client, test_db):
    access_token = get_access_token(test_client)
    response = test_client.get("/surveys/99", headers={'Content-Type': 'application/json',
                                                       'Authorization': f"Bearer {access_token}"})

    assert response.status_code == 404


def test_get_survey_responses_with_no_responses(test_client, basic_test_survey):
    """ 0 responses """

    access_token = get_access_token(test_client)
    response = test_client.get(f"/surveys/{basic_test_survey.id}/responses",
                               headers={'Content-Type': 'application/json',
                                        'Authorization': f"Bearer {access_token}"})

    assert response.status_code == 200
    assert len(response.get_json()) == 0


def test_get_survey_responses_with_one_response(test_client, test_db, basic_test_survey, admin_user):
    """ 1 response"""

    response = SurveyResponse(survey_id=basic_test_survey.id, structure={}, created_by=admin_user,
                              updated_by=admin_user)
    test_db.session.add(response)
    test_db.session.commit()

    access_token = get_access_token(test_client)
    response = test_client.get(f"/surveys/{basic_test_survey.id}/responses",
                               headers={'Content-Type': 'application/json',
                                        'Authorization': f"Bearer {access_token}"})

    assert response.status_code == 200
    assert len(response.get_json()) == 1


def test_get_survey_responses_with_n_responses(test_client, test_db, basic_test_survey, admin_user):
    """ n responses """

    for x in range(0, 10):
        test_db.session.add(SurveyResponse(survey_id=basic_test_survey.id, structure={}, created_by=admin_user,
                                           updated_by=admin_user))
    test_db.session.commit()

    access_token = get_access_token(test_client)
    response = test_client.get(f"/surveys/{basic_test_survey.id}/responses",
                               headers={'Content-Type': 'application/json',
                                        'Authorization': f"Bearer {access_token}"})

    assert response.status_code == 200
    assert len(response.get_json()) == 10


get_survey_responses_test_cases = [
    {
        'id': 'default-only-not-archived',
        'url': '/responses',
        'response_status': 200,
        'response_length': 5
    }, {
        'id': 'only-not-archived',
        'url': '/responses?archived=none',
        'response_status': 200,
        'response_length': 5
    }, {
        'id': 'only-archived',
        'url': '/responses?archived=all',
        'response_status': 200,
        'response_length': 5
    }, {
        'id': 'all',
        'url': '/responses?archived=any',
        'response_status': 200,
        'response_length': 10
    }
]

get_survey_responses_test_case_ids = [case['id'] for case in get_survey_responses_test_cases]


@pytest.mark.parametrize('test_case', get_survey_responses_test_cases, ids=get_survey_responses_test_case_ids)
def test_get_all_survey_responses(test_client, test_db, basic_test_survey, admin_user, test_case):
    """ n responses """

    for x in range(0, 10):
        test_db.session.add(SurveyResponse(survey_id=basic_test_survey.id, structure={}, created_by=admin_user,
                                           updated_by=admin_user, is_archived=(x % 2 == 0)))
    test_db.session.commit()

    access_token = get_access_token(test_client)
    response = test_client.get(f"/surveys/{basic_test_survey.id}{test_case['url']}",
                               headers={'Content-Type': 'application/json', 'Authorization': f"Bearer {access_token}"})

    assert response.status_code == test_case['response_status']
    assert len(response.get_json()) == test_case['response_length']


def test_get_survey_responses_fails_with_unknown_survey(test_client, test_db):
    """ 404 """
    access_token = get_access_token(test_client)
    response = test_client.get("/surveys/99/responses", headers={'Content-Type': 'application/json',
                                                                 'Authorization': f"Bearer {access_token}"})

    assert response.status_code == 404


def test_get_survey_response(test_client, test_db, basic_test_survey, admin_user):
    survey_response = SurveyResponse(survey_id=basic_test_survey.id, structure={}, created_by=admin_user,
                                     updated_by=admin_user)
    test_db.session.add(survey_response)
    test_db.session.commit()

    access_token = get_access_token(test_client)
    response = test_client.get(f"/surveys/{basic_test_survey.id}/responses/{survey_response.id}",
                               headers={'Content-Type': 'application/json', 'Authorization': f"Bearer {access_token}"})

    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['id']
    assert json_data['id'] == survey_response.id
    assert json_data['structure'] == survey_response.structure
    assert json_data['survey_id']
    assert json_data['survey_id'] == basic_test_survey.id
    assert json_data['survey_structure'] == basic_test_survey.structure


def test_get_survey_response_still_returns_archived_responses(test_client, test_db, basic_test_survey, admin_user):
    """
    Covers

    Scenario: Client requests a survey response that is archived
      Given the client accesses the API with a valid access code
      And using an account that has permission to read surveys
      When a client requests a survey response that is archived
      Then the API returns a status 200
      And the survey response object as JSON
    """

    survey_response = SurveyResponse(survey_id=basic_test_survey.id, structure={}, created_by=admin_user,
                                     updated_by=admin_user, is_archived=True)
    test_db.session.add(survey_response)
    test_db.session.commit()

    access_token = get_access_token(test_client)
    response = test_client.get(f"/surveys/{basic_test_survey.id}/responses/{survey_response.id}",
                               headers={'Content-Type': 'application/json', 'Authorization': f"Bearer {access_token}"})

    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['id']
    assert json_data['id'] == survey_response.id
    assert json_data['structure'] == survey_response.structure
    assert json_data['survey_id']
    assert json_data['survey_id'] == basic_test_survey.id
    assert json_data['survey_structure'] == basic_test_survey.structure


def test_get_survey_response_fails_with_unknown_survey(test_client, test_db):
    """ 404 bad survey """
    access_token = get_access_token(test_client)
    response = test_client.get("/surveys/99/responses/99",
                               headers={'Content-Type': 'application/json', 'Authorization': f"Bearer {access_token}"})

    assert response.status_code == 404


def test_get_survey_response_fails_with_unknown_response(test_client, test_db, basic_test_survey):
    """ 404 bad response """

    access_token = get_access_token(test_client)
    response = test_client.get(f"/surveys/{basic_test_survey.id}/responses/99",
                               headers={'Content-Type': 'application/json', 'Authorization': f"Bearer {access_token}"})

    assert response.status_code == 404


def test_post_survey(test_client, test_db):
    """
    Covers

    Scenario: Client creates new survey and is_archived is False
      Given the client accesses the API with a valid access code
      And using an account that has permission to create surveys
      When the client submits a new valid survey
      Then the API sets the survey's is_archived to False
      And returns a status 200
      And returns a survey object whose is_archived is False

    """
    num_surveys_before = test_db.session.query(Survey).count()

    structure = {"pages": [{"name": "page1", "elements": [{"type": "text", "name": "question1"}]}],
                 "name": "Test Survey"}

    access_token = get_access_token(test_client)
    response = test_client.post('/surveys/', data=json.dumps({'name': 'Test Survey', 'structure': structure}),
                                headers={'Content-Type': 'application/json', 'Authorization': f"Bearer {access_token}"})

    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['name'] == 'Test Survey'
    assert not json_data['is_archived']
    assert (num_surveys_before + 1) == test_db.session.query(Survey).count()


post_survey_invalid_data_test_cases = [
    {
        'id': 'structure-missing',
        'data': {'name': 'test survey 1'},
        'response_status': 400,
        'message': 'The structure for your survey is missing.'
    }, {
        'id': 'name-missing',
        'data': {'structure': {}},
        'response_status': 400,
        'message': 'The name for your survey is missing.'
    }, {
        'id': 'name-empty',
        'data': {'name': '', 'structure': {}},
        'response_status': 400,
        'message': 'Unable to figure out the name of your survey.'
    }, {
        'id': 'name-starts-with-non-char',
        'data': {'name': '2 test survey', 'structure': {}},
        'response_status': 400,
        'message': "The survey's name must start with a character."
    }
]

post_survey_invalid_data_test_cases_ids = [case['id'] for case in post_survey_invalid_data_test_cases]


@pytest.mark.parametrize('test_case', post_survey_invalid_data_test_cases, ids=post_survey_invalid_data_test_cases_ids)
def test_post_survey_fails_with_invalid_data(test_client, test_db, test_case):
    access_token = get_access_token(test_client)
    response = test_client.post('/surveys/', data=json.dumps(test_case['data']),
                                headers={'Content-Type': 'application/json', 'Authorization': f"Bearer {access_token}"})

    assert response.status_code == test_case['response_status']
    json_data = response.get_json()
    assert json_data['message'] == test_case['message']


def test_post_survey_fails_if_name_is_not_unique(test_client, test_db, basic_test_survey):
    """ name must be unique """

    structure = {
        "pages":
            [
                {
                    "name": "page1",
                    "elements":
                        [
                            {
                                "type": "text",
                                "name": "question1"
                            }
                        ]
                }
            ],
        "title": basic_test_survey.name
    }

    # post survey with the same name
    access_token = get_access_token(test_client)
    response = test_client.post('/surveys/', data=json.dumps({'name': basic_test_survey.name, 'structure': structure}),
                                headers={'Content-Type': 'application/json', 'Authorization': f"Bearer {access_token}"})

    assert response.status_code == 400
    json_data = response.get_json()

    msg = (
        'You have submitted a survey that has the same name as another survey. Survey names must be unique. '
        'Please change the survey name and resubmit.'
    )

    assert json_data['message'] == msg


def test_put_survey_fails_with_unknown_survey(test_client, test_db):
    """
    Scenario: Client submits change survey request for unknown survey
        Given the client access the API without a valid access code
        When the client submits the update for an unknown survey
        The the API returns a 404 status
    """
    access_token = get_access_token(test_client)
    response = test_client.put("/surveys/99",
                               headers={
                                   'Content-Type': 'application/json',
                                   'Authorization': f"Bearer {access_token}"})

    assert response.status_code == 404


def test_put_survey_fails_without_json(test_client, test_db, basic_test_survey):
    """
    Scenario: Client submits change survey request without JSON body
        Given the client accesses the API with a valid access code
        And using an account that has permission to update surveys
        When the client submits the update request
        But does not send the request body on JSON
        Then the API returns a 401 status
        And the message "Missing JSON in request"
    """

    access_token = get_access_token(test_client)
    response = test_client.put(f"/surveys/{basic_test_survey.id}",
                               headers={
                                   'Authorization': f"Bearer {access_token}"})

    assert response.status_code == 400


def test_put_survey(test_client, test_db, basic_test_survey, admin_user):
    """
    Scenario: Client successfully updates a survey definition
        Given the client access the API with a valid access code
        And using an account that has permission to update surveys
        When the client submits the update request
        Then the API returns a 200 status
        And a full survey object
        And any updates to name and structure are applied
        And the surveys updated by is the user the submitted the request
    """

    survey_update = {
        'id': basic_test_survey.id,
        'name': 'New Survey Name',
        'structure': {"pages": [{"name": "page1", "elements": [{"type": "text", "name": "question1"}]}],
                      "title": "Test Survey"}
    }

    access_token = create_access_token(identity=admin_user.id)
    response = test_client.put(f"/surveys/{basic_test_survey.id}", data=json.dumps(survey_update),
                               headers={'Content-Type': 'application/json', 'Authorization': f"Bearer {access_token}"})

    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['name'] == survey_update['name']
    assert not json_data['is_archived']
    assert json_data['updated_by']['id'] == admin_user.id
    updated_survey = Survey.query.get(json_data['id'])
    assert updated_survey.name == survey_update['name']
    assert not updated_survey.is_archived
    assert updated_survey.updated_by_id == admin_user.id


def test_put_survey_updates_is_archived(test_client, test_db, basic_test_survey, admin_user):
    """
    Covers

    Given the client accesses the API with a valid access code
      And using an account that has permission to update surveys
      When the client submits a survey update with is_archived = True
      Then the API sets the survey's is_archived flag to True
      And returns a status 200
      And returns a survey object with is_archived = True
    """
    assert not basic_test_survey.is_archived

    survey_update = {
        'id': basic_test_survey.id,
        'is_archived': True
    }

    access_token = create_access_token(identity=admin_user.id)
    response = test_client.put(f"/surveys/{basic_test_survey.id}", data=json.dumps(survey_update),
                               headers={'Content-Type': 'application/json', 'Authorization': f"Bearer {access_token}"})

    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['is_archived']
    updated_survey = Survey.query.get(json_data['id'])
    assert updated_survey.is_archived
    updated_survey = Survey.query.get(basic_test_survey.id)
    assert updated_survey.is_archived


put_survey_invalid_data_test_cases = [
    {
        'id': 'empty-name',
        'needs_survey_id': True,
        'update_data': {'name': '',
                        'structure': {"pages": [{"name": "page1", "elements": [{"type": "text", "name": "question1"}]}],
                                      "title": "Test Survey"}},
        'response_status': 400,
        'response_message': 'Unable to figure out the name of your survey.'
    }, {
        'id': 'null-name',
        'needs_survey_id': True,
        'update_data': {'name': None,
                        'structure': {"pages": [{"name": "page1", "elements": [{"type": "text", "name": "question1"}]}],
                                      "title": "Test Survey"}},
        'response_status': 400,
        'response_message': 'Unable to figure out the name of your survey.'
    }, {
        'id': 'name-starts-with-non-char',
        'needs_survey_id': True,
        'update_data': {'name': '2 test survey',
                        'structure': {"pages": [{"name": "page1", "elements": [{"type": "text", "name": "question1"}]}],
                                      "title": "Test Survey"}},
        'response_status': 400,
        'response_message': "The survey's name must start with a character."
    }, {
        'id': 'different-survey-id',
        'update_data': {'id': 99, 'name': 'Test Survey',
                        'structure': {"pages": [{"name": "page1", "elements": [{"type": "text", "name": "question1"}]}],
                                      "title": "Test Survey"}},
        'response_status': 400,
        'response_message': 'The survey id in the URL does not match the survey id in your put object.'
    }, {
        'id': 'missing-survey-id',
        'update_data': {'name': 'Test Survey',
                        'structure': {"pages": [{"name": "page1", "elements": [{"type": "text", "name": "question1"}]}],
                                      "title": "Test Survey"}},
        'response_status': 400,
        'response_message': 'You must provide a survey id in your put object.'
    }
]

put_survey_invalid_data_test_cases_ids = [case['id'] for case in put_survey_invalid_data_test_cases]


@pytest.mark.parametrize('test_case', put_survey_invalid_data_test_cases, ids=put_survey_invalid_data_test_cases_ids)
def test_put_survey_fails_with_invalid_data(test_client, test_db, basic_test_survey, admin_user, test_case):
    """
    Scenario: Client submits change survey request with empty survey name
      Given the client access the API with a valid access code
      And using an account that has permission to update surveys
      When the client submits a request with an empty or null survey name
      Then the API returns a 400 status
      And the error code 103

    Scenario: Client attempts to submit a survey object without the surveys's system id in the object
      Given the client accesses the API with a valid access code
      And using an account that has permission to update a survey
      When the client submits an update that does not contain the survey's system id
      Then the API returns a 400 status
      And the message "You must provide a survey id in your put object."

    Scenario: Client attempts to submit a survey object whose id does not match the request URL
      Given the client accesses the API with a valid access code
      And using an account that has permission to update a user
      When the client submits a survey object to update
      And the survey's system id does not match the survey id in the request URL
      Then the API returns a 400 status
      And the message "The survey id in the URL does not match the survey id in your put object."
    """
    update_data = test_case['update_data']
    if test_case.get('needs_survey_id', False):
        update_data['id'] = update_data.get('id', basic_test_survey.id)

    access_token = create_access_token(identity=admin_user.id)
    response = test_client.put(f"/surveys/{basic_test_survey.id}", data=json.dumps(update_data),
                               headers={'Content-Type': 'application/json', 'Authorization': f"Bearer {access_token}"})

    assert response.status_code == test_case['response_status']
    json_data = response.get_json()
    assert json_data['message'] == test_case['response_message']


def test_put_survey_fails_with_duplicate_name(test_client, test_db):
    """
    Scenario: Client submits change survey request with non-unique survey name
      Given the client access the API with a valid access code
      And using an account that has permission to update surveys
      When the client submits a request with a survey name already in use
      Then the API returns a 400 status
      And the error code 100
    """
    user = User.query.filter_by(username='admin').first()
    original_survey = Survey(name='Test Survey 1', structure={}, created_by=user, updated_by=user)
    duplicate_survey = Survey(name='Test Survey 2', structure={}, created_by=user, updated_by=user)
    test_db.session.add(original_survey)
    test_db.session.add(duplicate_survey)
    test_db.session.commit()

    update_data = {'id': original_survey.id, 'name': 'Test Survey 2',
                   'structure': {"pages": [{"name": "page1", "elements": [{"type": "text", "name": "question1"}]}],
                                 "title": "Test Survey 2"}}
    access_token = create_access_token(identity=user.id)
    response = test_client.put(f"/surveys/{original_survey.id}", data=json.dumps(update_data),
                               headers={'Content-Type': 'application/json', 'Authorization': f"Bearer {access_token}"})

    assert response.status_code == 400
    json_data = response.get_json()

    msg = (
        'You have submitted a survey that has the same name as another survey. Survey names must be unique. '
        'Please change the survey name and resubmit.'
    )

    assert json_data['message'] == msg


post_survey_response_test_cases = [
    {
        'id': 'set-default-status',
        'username': 'admin',
        'password': 'admin',
        'survey_structure': {"pages": [{"name": "page1", "elements": [{"type": "text", "name": "question1"}]}],
                             "name": "Test Survey"},
        'response_structure': {"structure": {"question1": "bb"}},
        'response_status': 200,
        'test_status_id': 2
    }, {
        'id': 'pass-status',
        'username': 'admin',
        'password': 'admin',
        'survey_structure': {"pages": [{"name": "page1", "elements": [{"type": "text", "name": "question1"}]}],
                             "name": "Test Survey"},
        'response_structure': {"structure": {"question1": "bb"}, "status_id": 1},
        'response_status': 200,
        'test_status_id': 1
    }
]

post_survey_response_test_cases_ids = [case['id'] for case in post_survey_response_test_cases]


@pytest.mark.parametrize('test_case', post_survey_response_test_cases, ids=post_survey_response_test_cases_ids)
def test_post_survey_response(test_client, test_db, test_survey, test_case):
    """
    Covers

    Scenario: Client creates new survey response and is_archived is False
      Given the client accesses the API with a valid access code
      And using an account that has permission to create survey responses
      When the client submits a new valid survey response
      Then the API sets the survey responses is_archived to False
      And returns a status 200
      And returns a survey response object whose is_archived is False

    """
    survey_id = test_survey['id']
    survey = Survey.query.get(survey_id)

    num_responses_before = len(survey.responses.all())

    response_structure = test_case['response_structure']

    access_token = get_access_token_for_user(test_client, test_case['username'], test_case['password'])
    response = test_client.post(f"/surveys/{survey_id}/responses", data=json.dumps(response_structure),
                                headers={'Content-Type': 'application/json', 'Authorization': f"Bearer {access_token}"})

    user = User.query.filter_by(username=test_case['username']).first()

    assert response.status_code == test_case['response_status']
    assert (num_responses_before + 1) == len(survey.responses.all())
    json_data = response.get_json()
    assert json_data['survey']
    assert json_data['survey'] == survey_id
    assert json_data['id']
    assert json_data['created_by']
    assert json_data['created_by']['id'] == user.id
    assert json_data['updated_by']
    assert json_data['updated_by']['id'] == user.id
    assert json_data['status']
    assert json_data['status']['id'] == test_case['test_status_id']
    assert not json_data['is_archived']
    assert SurveyResponse.query.get(json_data['id'])


post_gps_with_response_test_cases = [
    {
        'id': 'coordinates-saved',
        'username': 'admin',
        'password': 'admin',
        'survey_structure': {"pages": [{"name": "page1", "elements": [{"type": "text", "name": "question1"}]}],
                             "name": "Test Survey"},
        'response_structure': {"structure": {"question1": "bb"}, "latitude": 51.6218595, "longitude": 115.906789},
        'response_status': 200,
        'gps_data_saved': True
    }, {
        'id': 'values-not-sent',
        'username': 'admin',
        'password': 'admin',
        'survey_structure': {"pages": [{"name": "page1", "elements": [{"type": "text", "name": "question1"}]}],
                             "name": "Test Survey"},
        'response_structure': {"structure": {"question1": "bb"}},
        'response_status': 200,
        'gps_data_saved': False
    }, {
        'id': 'null-values-not-saved',
        'username': 'admin',
        'password': 'admin',
        'survey_structure': {"pages": [{"name": "page1", "elements": [{"type": "text", "name": "question1"}]}],
                             "name": "Test Survey"},
        'response_structure': {"structure": {"question1": "bb"}, "latitude": None, "longitude": None},
        'response_status': 200,
        'gps_data_saved': False
    }, {
        'id': 'null-lat-not-saved',
        'username': 'admin',
        'password': 'admin',
        'survey_structure': {"pages": [{"name": "page1", "elements": [{"type": "text", "name": "question1"}]}],
                             "name": "Test Survey"},
        'response_structure': {"structure": {"question1": "bb"}, "latitude": None, "longitude": 115.906789},
        'response_status': 200,
        'gps_data_saved': False
    }, {
        'id': 'null-lon-not-saved',
        'username': 'admin',
        'password': 'admin',
        'survey_structure': {"pages": [{"name": "page1", "elements": [{"type": "text", "name": "question1"}]}],
                             "name": "Test Survey"},
        'response_structure': {"structure": {"question1": "bb"}, "latitude": 51.6218595, "longitude": None},
        'response_status': 200,
        'gps_data_saved': False
    }, {
        'id': 'empty-values-not-saved',
        'username': 'admin',
        'password': 'admin',
        'survey_structure': {"pages": [{"name": "page1", "elements": [{"type": "text", "name": "question1"}]}],
                             "name": "Test Survey"},
        'response_structure': {"structure": {"question1": "bb"}, "latitude": '', "longitude": ''},
        'response_status': 200,
        'gps_data_saved': False
    }, {
        'id': 'empty-lat-not-saved',
        'username': 'admin',
        'password': 'admin',
        'survey_structure': {"pages": [{"name": "page1", "elements": [{"type": "text", "name": "question1"}]}],
                             "name": "Test Survey"},
        'response_structure': {"structure": {"question1": "bb"}, "latitude": '', "longitude": 115.906789},
        'response_status': 200,
        'gps_data_saved': False
    }, {
        'id': 'empty-lon-not-saved',
        'username': 'admin',
        'password': 'admin',
        'survey_structure': {"pages": [{"name": "page1", "elements": [{"type": "text", "name": "question1"}]}],
                             "name": "Test Survey"},
        'response_structure': {"structure": {"question1": "bb"}, "latitude": 51.6218595, "longitude": ''},
        'response_status': 200,
        'gps_data_saved': False
    }
]

post_gps_with_response_test_cases_ids = [case['id'] for case in post_gps_with_response_test_cases]


@pytest.mark.parametrize('test_case', post_gps_with_response_test_cases, ids=post_gps_with_response_test_cases_ids)
def test_post_gps_with_response(test_client, test_db, test_survey, test_case):
    survey_id = test_survey['id']
    survey = Survey.query.get(survey_id)

    num_responses_before = len(survey.responses.all())

    response_structure = test_case['response_structure']

    access_token = get_access_token_for_user(test_client, test_case['username'], test_case['password'])
    response = test_client.post(f"/surveys/{survey_id}/responses", data=json.dumps(response_structure),
                                headers={'Content-Type': 'application/json', 'Authorization': f"Bearer {access_token}"})

    user = User.query.filter_by(username=test_case['username']).first()

    assert response.status_code == test_case['response_status']
    assert (num_responses_before + 1) == len(survey.responses.all())
    json_data = response.get_json()
    assert json_data['survey']
    assert json_data['survey'] == survey_id
    assert json_data['id']
    assert json_data['created_location']
    if test_case['gps_data_saved']:
        assert json_data['created_location']['location_recorded_dt']
        assert json_data['created_location']['latitude'] == test_case['response_structure']['latitude']
        assert json_data['created_location']['longitude'] == test_case['response_structure']['longitude']
    else:
        assert not json_data['created_location']['location_recorded_dt']


post_survey_response_invalid_data_test_cases = [
    {
        'id': 'structure-missing',
        'data': {},
        'response_status': 400,
        'message': 'The structure for your survey response is missing.'
    }, {
        'id': 'structure-empty',
        'data': {"survey_id": 99, "structure": {}},
        'response_status': 400,
        'message': 'The structure for your survey response is missing.'
    }, {
        'id': 'invalid-status',
        'data': {"survey_id": 99, "structure": {"structure": {"question1": "bb"}}, 'status_id': 99},
        'response_status': 400,
        'message': 'The survey response status you provided is invalid.'
    }, {
        'id': 'invalid-source-type',
        'data': {"survey_id": 99, "structure": {"structure": {"question1": "bb"}}, 'source_type': 'BAD_VALUE'},
        'response_status': 400,
        'message': 'The survey response source value you provided is invalid.'
    }
]

post_survey_response_invalid_data_test_cases_ids = [case['id'] for case
                                                    in post_survey_response_invalid_data_test_cases]


@pytest.mark.parametrize('test_case', post_survey_response_invalid_data_test_cases,
                         ids=post_survey_response_invalid_data_test_cases_ids)
def test_post_survey_response_fails_with_invalid_data(test_client, test_db, test_case):
    user = User.query.filter_by(username='admin').first()
    survey = Survey(name='Test Survey',
                    structure={
                        "pages":
                            [
                                {
                                    "name": "page1",
                                    "elements":
                                        [
                                            {
                                                "type": "text",
                                                "name": "question1"
                                            }
                                        ]
                                }
                            ],
                        "title": "Test Survey"
                    }, created_by=user, updated_by=user)

    test_db.session.add(survey)
    test_db.session.commit()
    survey_id = survey.id

    if 'survey_id' in test_case['data']:
        test_case['data']['survey_id'] = survey_id

    access_token = get_access_token(test_client)
    response = test_client.post(f"/surveys/{survey_id}/responses", data=json.dumps(test_case['data']),
                                headers={'Content-Type': 'application/json', 'Authorization': f"Bearer {access_token}"})

    assert response.status_code == test_case['response_status']
    json_data = response.get_json()
    assert json_data['message'] == test_case['message']


def test_post_survey_response_fails_with_unknown_survey(test_client, test_db):
    """ 404 bad survey """
    access_token = get_access_token(test_client)
    response = test_client.post("/surveys/99/responses", headers={'Content-Type': 'application/json',
                                                                  'Authorization': f"Bearer {access_token}"})

    assert response.status_code == 404



put_response_test_cases = [
    {
        'id': 'with-valid-status',
        'create_username': 'admin',
        'put_username': 'datacollector',
        'create_status': 'Draft',
        'put_status': 'Submitted',
        'survey_structure': {"pages": [{"name": "page1", "elements": [{"type": "text", "name": "question1"}]}],
                             "title": "Test Survey"},
        'response_structure': {"structure": {"question1": "bb"}},
        'update_structure': {"structure": {"question1": "bb"}},
        'response_status': 200
    }, {
        'id': 'without-status',
        'create_username': 'admin',
        'put_username': 'datacollector',
        'create_status': 'Draft',
        'put_status': 'Submitted',
        'survey_structure': {"pages": [{"name": "page1", "elements": [{"type": "text", "name": "question1"}]}],
                             "title": "Test Survey"},
        'response_structure': {"structure": {"question1": "bb"}},
        'update_structure': {"structure": {"question1": "bb"}},
        'response_status': 200
    }
]

put_response_test_cases_ids = [case['id'] for case in put_response_test_cases]

@pytest.mark.parametrize('test_case', put_response_test_cases, ids=put_response_test_cases_ids)
def test_put_survey_response(test_client, test_db, test_case):
    create_user = User.query.filter_by(username=test_case['create_username']).first()

    survey = Survey(name='Test Survey', structure=test_case['survey_structure'], created_by=create_user,
                    updated_by=create_user, reporting_table_name='test_survey')
    test_db.session.add(survey)
    test_db.session.commit()
    survey_id = survey.id

    put_user = User.query.filter_by(username=test_case['put_username']).first()
    create_status = SurveyResponseStatus.query.filter_by(name=test_case['create_status']).first()
    put_status = SurveyResponseStatus.query.filter_by(name=test_case['put_status']).first()

    # insert response for survey in db
    survey_response = SurveyResponse(survey_id=survey_id, structure=test_case['response_structure'],
                                     status=create_status, created_by=create_user, updated_by=create_user)
    test_db.session.add(survey_response)
    test_db.session.commit()
    survey_response_id = survey_response.id

    # put updated response
    if put_status:
        put_response_structure = {"structure": {"question1": "aa"}, 'status_id': put_status.id}
    else:
        put_response_structure = {"structure": {"question1": "aa"}}
    access_token = create_access_token(identity=put_user.id)
    response = test_client.put(f"/surveys/{survey_id}/responses/{survey_response_id}",
                               data=json.dumps(put_response_structure),
                               headers={'Content-Type': 'application/json', 'Authorization': f"Bearer {access_token}"})

    # check status 200
    assert response.status_code == 200
    # check structure returned matches
    json_data = response.get_json()
    assert json_data['updated_by']
    assert json_data['updated_by']['id'] == put_user.id
    assert json_data['status']
    if put_status:
        assert json_data['status']['id'] == put_status.id
    else:
        assert json_data['status']['id'] == create_status.id
    assert not json_data['is_archived']


put_gps_with_response_test_cases = [
    {
        'id': 'coordinates-saved',
        'create_username': 'admin',
        'put_username': 'datacollector',
        'survey_structure': {"pages": [{"name": "page1", "elements": [{"type": "text", "name": "question1"}]}],
                             "title": "Test Survey"},
        'response_structure': {"structure": {"question1": "bb"}},
        'update_structure': {"structure": {"question1": "bb"}, "latitude": 51.6218595, "longitude": 115.906789},
        'response_status': 200
    }
]

put_gps_with_response_test_cases_ids = [case['id'] for case in put_gps_with_response_test_cases]

# TODO: Add tests that check that update location is not updated if no or invalid location info is sent
@pytest.mark.parametrize('test_case', put_gps_with_response_test_cases, ids=put_gps_with_response_test_cases_ids)
def test_put_gps_with_response(test_client, test_db, test_case):
    create_user = User.query.filter_by(username=test_case['create_username']).first()

    survey = Survey(name='Test Survey', structure=test_case['survey_structure'], created_by=create_user,
                    updated_by=create_user, reporting_table_name='test_survey')
    test_db.session.add(survey)
    test_db.session.commit()
    survey_id = survey.id

    put_user = User.query.filter_by(username=test_case['put_username']).first()

    # insert response for survey in db
    survey_response = SurveyResponse(survey_id=survey_id, structure=test_case['response_structure'],
                                     created_by=create_user, updated_by=create_user)
    test_db.session.add(survey_response)
    test_db.session.commit()
    survey_response_id = survey_response.id

    access_token = create_access_token(identity=put_user.id)
    response = test_client.put(f"/surveys/{survey_id}/responses/{survey_response_id}",
                               data=json.dumps(test_case['update_structure']),
                               headers={'Content-Type': 'application/json', 'Authorization': f"Bearer {access_token}"})

    # check status 200
    assert response.status_code == 200
    # check structure returned matches
    json_data = response.get_json()
    assert json_data['updated_location']
    assert json_data['updated_location']['latitude'] == test_case['update_structure']['latitude']
    assert json_data['updated_location']['longitude'] == test_case['update_structure']['longitude']


def test_put_survey_response_updates_is_archived(test_client, test_db):
    """
    Covers

    Scenario: Client successfully archives a survey response
      Given the client access the API with a valid access code
      And using an account that has permission to update surveys
      When the client submits a survey response update with is_archived = True
      Then the API sets the survey response's is_archived flag to True
      And returns a status 200
      And returns a survey response object with is_archived = True
    """
    user = User.query.filter_by(username='admin').first()

    survey = Survey(name='Test Survey', reporting_table_name='test_survey',
                    structure={"pages": [{"name": "page1", "elements": [{"type": "text", "name": "question1"}]}],
                               "title": "Test Survey"}, created_by=user, updated_by=user)
    test_db.session.add(survey)
    test_db.session.commit()
    survey_id = survey.id

    # insert response for survey in db
    survey_response = SurveyResponse(survey_id=survey_id, structure={"structure": {"question1": "bb"}},
                                     created_by=user, updated_by=user)
    test_db.session.add(survey_response)
    test_db.session.commit()
    survey_response_id = survey_response.id
    assert not survey_response.is_archived

    put_response_structure = {"structure": {"question1": "aa"}, 'is_archived': True}
    access_token = create_access_token(identity=user.id)
    response = test_client.put(f"/surveys/{survey_id}/responses/{survey_response_id}",
                               data=json.dumps(put_response_structure),
                               headers={'Content-Type': 'application/json', 'Authorization': f"Bearer {access_token}"})

    # check status 200
    assert response.status_code == 200
    # check structure returned matches
    json_data = response.get_json()
    assert json_data['is_archived']
    # check structure in db matches
    survey_response = SurveyResponse.query.get(survey_response_id)
    assert survey_response.is_archived


def test_put_survey_response_fails_with_unknown_survey(test_client, test_db):
    """ 404 bad survey """
    access_token = get_access_token(test_client)
    response = test_client.put("/surveys/99/responses/99",
                               headers={
                                   'Content-Type': 'application/json',
                                   'Authorization': f"Bearer {access_token}"})

    assert response.status_code == 404


def test_put_survey_response_fails_with_unknown_response(test_client, basic_test_survey):
    """ 404 bad response """

    access_token = get_access_token(test_client)
    response = test_client.put(f"/surveys/{basic_test_survey.id}/responses/99",
                               headers={
                                   'Content-Type': 'application/json',
                                   'Authorization': f"Bearer {access_token}"})

    assert response.status_code == 404


put_survey_response_invalid_data_test_cases = [
    {
        'id': 'structure-missing',
        'survey_structure': {"pages": [{"name": "page1", "elements": [{"type": "text", "name": "question1"}]}],
                             "title": "Test Survey"},
        'data': {},
        'response_status': 400,
        'message': 'The structure for your survey response is missing.'
    }, {
        'id': 'invalid-status-code',
        'survey_structure': {"pages": [{"name": "page1", "elements": [{"type": "text", "name": "question1"}]}],
                             "title": "Test Survey"},
        'data': {"structure": {"question1": "bb"}, 'status_id': 99},
        'response_status': 400,
        'message': 'The survey response status you provided is invalid.'
    }, {
        'id': 'invalid-source-type',
        'survey_structure': {"pages": [{"name": "page1", "elements": [{"type": "text", "name": "question1"}]}],
                             "title": "Test Survey"},
        'data': {"structure": {"question1": "bb"}, 'source_type': 'BAD VALUE'},
        'response_status': 400,
        'message': 'The survey response source value you provided is invalid.'
    }
]

put_survey_response_invalid_data_test_cases_ids = [case['id'] for case in put_survey_response_invalid_data_test_cases]


@pytest.mark.parametrize('test_case', put_survey_response_invalid_data_test_cases,
                         ids=put_survey_response_invalid_data_test_cases_ids)
def test_put_survey_response_fails_with_invalid_data(test_client, test_db, test_case):
    user = User.query.filter_by(username='admin').first()

    survey = Survey(name='Test Survey',
                    structure=test_case['survey_structure'], created_by=user, updated_by=user)
    test_db.session.add(survey)
    test_db.session.commit()
    survey_id = survey.id

    # insert response for survey in db
    survey_response = SurveyResponse(survey_id=survey_id, structure={"structure": {"question1": "bb"}}, created_by=user,
                                     updated_by=user)
    test_db.session.add(survey_response)
    test_db.session.commit()
    survey_response_id = survey_response.id

    # put updated response
    response_structure = {}
    access_token = get_access_token(test_client)
    response = test_client.put(f"/surveys/{survey_id}/responses/{survey_response_id}",
                               data=json.dumps(test_case['data']),
                               headers={'Content-Type': 'application/json', 'Authorization': f"Bearer {access_token}"})

    assert response.status_code == test_case['response_status']
    json_data = response.get_json()
    assert json_data['message'] == test_case['message']


def test_delete_survey_fails_with_unknown_survey(test_client, test_db):
    access_token = get_access_token(test_client)
    response = test_client.delete("/surveys/99", headers={'Content-Type': 'application/json',
                                                          'Authorization': f"Bearer {access_token}"})

    assert response.status_code == 404


def test_delete_survey(test_client, test_db):
    user = User.query.filter_by(username='admin').first()
    survey = Survey(name='Test Survey', reporting_table_name='test_survey',
                    structure={"pages": [{"name": "page1", "elements": [{"type": "text", "name": "question1"}]}],
                               "title": "Test Survey"}, created_by=user, updated_by=user)
    test_db.session.add(survey)
    test_db.session.commit()
    survey_id = survey.id

    for x in range(0, 10):
        survey_response = SurveyResponse(survey_id=survey_id, structure={"question1": "bb"}, created_by=user,
                                         updated_by=user)
        test_db.session.add(survey_response)
    test_db.session.commit()

    access_token = get_access_token(test_client)
    response = test_client.delete(f"/surveys/{survey_id}", headers={'Content-Type': 'application/json',
                                                                    'Authorization': f"Bearer {access_token}"})
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['message'] == "Survey successfully deleted."
    assert not Survey.query.get(survey_id)


def test_delete_survey_when_part_of_case_definition(test_client, test_db):
    # add survey
    user = User.query.filter_by(username='admin').first()
    survey = Survey(name='Test Survey', reporting_table_name='test_survey',
                    structure={"pages": [{"name": "page1", "elements": [{"type": "text", "name": "question1"}]}],
                               "title": "Test Survey"}, created_by=user, updated_by=user)
    test_db.session.add(survey)
    test_db.session.commit()
    survey_id = survey.id

    # add case definition with survey
    case_definition = CaseDefinition(key='CD', name='Case Definition', created_by=user, updated_by=user)
    case_definition.surveys.append(survey)
    test_db.session.add(case_definition)
    test_db.session.commit()

    # try to delete survey
    access_token = get_access_token(test_client)
    response = test_client.delete(f"/surveys/{survey_id}", headers={'Content-Type': 'application/json',
                                                                    'Authorization': f"Bearer {access_token}"})
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['message'] == "Survey successfully deleted."
    assert not Survey.query.get(survey_id)


def test_delete_response_fails_with_unknown_survey(test_client, test_db):
    access_token = get_access_token(test_client)
    response = test_client.delete("/surveys/99/responses/99", headers={'Content-Type': 'application/json',
                                                                       'Authorization': f"Bearer {access_token}"})

    assert response.status_code == 404


def test_delete_response_fails_with_unknown_response(test_client, basic_test_survey):
    access_token = get_access_token(test_client)

    response = test_client.delete(f"/surveys/{basic_test_survey.id}/responses/99",
                                  headers={'Content-Type': 'application/json',
                                           'Authorization': f"Bearer {access_token}"})

    assert response.status_code == 404


def test_delete_response(test_client, test_db, basic_test_survey, admin_user):
    survey_response = SurveyResponse(survey_id=basic_test_survey.id, structure={}, created_by=admin_user,
                                     updated_by=admin_user)
    test_db.session.add(survey_response)
    test_db.session.commit()
    survey_response_id = survey_response.id

    access_token = get_access_token(test_client)
    response = test_client.delete(f"/surveys/{basic_test_survey.id}/responses/{survey_response.id}",
                                  headers={'Content-Type': 'application/json',
                                           'Authorization': f"Bearer {access_token}"})
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['message'] == "Survey response successfully deleted."
    assert not SurveyResponse.query.get(survey_response_id)


survey_without_permission_test_cases = [
    {
        'id': 'post-survey',
        'url': '/surveys/',
        'method': 'POST',
        'response_message': 'You do not have permission to create a survey.'
    }, {
        'id': 'get-surveys',
        'url': '/surveys/',
        'method': 'GET',
        'response_message': 'You do not have permission to read surveys.'
    }, {
        'id': 'get-survey',
        'url': '/surveys/99',
        'method': 'GET',
        'response_message': 'You do not have permission to read surveys.'
    }, {
        'id': 'put-survey',
        'url': '/surveys/99',
        'method': 'PUT',
        'response_message': 'You do not have permission to update surveys.'
    }, {
        'id': 'post-survey-response',
        'url': '/surveys/99/responses',
        'method': 'POST',
        'response_message': 'You do not have permission to submit a survey.'
    },
    {
        'id': 'get-survey-responses',
        'url': '/surveys/99/responses',
        'method': 'GET',
        'response_message': 'You do not have permission to read surveys.'
    }, {
        'id': 'get-survey-response',
        'url': '/surveys/99/responses/99',
        'method': 'GET',
        'response_message': 'You do not have permission to read surveys.'
    }, {
        'id': 'put-survey-response',
        'url': '/surveys/99/responses/99',
        'method': 'PUT',
        'response_message': 'You do not have permission to submit a survey.'
    }, {
        'id': 'delete-survey',
        'url': '/surveys/99',
        'method': 'DELETE',
        'response_message': 'You do not have permission to delete surveys.'
    }, {
        'id': 'delete-survey-response',
        'url': '/surveys/99/responses/99',
        'method': 'DELETE',
        'response_message': 'You do not have permission to delete surveys.'
    }
]

survey_without_permission_test_cases_ids = [case['id'] for case in survey_without_permission_test_cases]


@pytest.mark.parametrize('test_case', survey_without_permission_test_cases,
                         ids=survey_without_permission_test_cases_ids)
def test_survey_fails_without_permission(test_client, test_db, test_case):
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


def test_get_survey_updated_since(test_client, test_db):
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
        data=flask.json.dumps({'name': 'Test Survey 1', 'structure': structure}),
        headers={'Content-Type': 'application/json', 'Authorization': f"Bearer {access_token}"}
    )

    survey_1_id = response.json['id']

    time.sleep(2)
    timestamp = http.http_date(datetime.datetime.utcnow())

    structure['title'] = 'Test 2'
    response = test_client.post(
        '/surveys/',
        data=flask.json.dumps({'name': 'Test Survey 2', 'structure': structure}),
        headers={'Content-Type': 'application/json', 'Authorization': f"Bearer {access_token}"}
    )

    survey_2_id = response.json['id']

    response = test_client.get(
        f'/surveys/?updated_since={timestamp}',
        headers={'Content-Type': 'application/json', 'Authorization': f"Bearer {access_token}", },
    )

    assert response.status_code == 200
    assert len(response.json) == 1
    assert response.json[0]['id'] == survey_2_id
