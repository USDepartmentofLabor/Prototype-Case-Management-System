import json
import pytest
from flask_jwt_extended import create_access_token
from flask import current_app
from app import models
from ..test_helpers import setup_user_with_no_permissions, get_access_token
from unittest import mock
import io
from ..factories import CaseDefinitionFactory


def test_post_valid_case(test_client, test_db, basic_case_definition, admin_user, data_collector_user):
    # cd = CaseDefinitionFactory.create(created_by_id=admin_user.id, updated_by_id=admin_user.id)
    # cd.reporting_table_name = current_app.reporting_service.create_case_table(cd)
    # test_db.session.commit()
    num_cases_before = test_db.session.query(models.Case).count()

    cd_id = basic_case_definition.id

    case = {
        "name": "Test Case",
        "description": "This is a description of the test case",
        "case_definition_id": cd_id,
        "notes": [],
        "latitude": 75.8692385,
        "longitude": -0.428003,
        "assigned_to_id": data_collector_user.id
    }

    access_token = create_access_token(identity=admin_user.id)
    response = test_client.post(f"/case_definitions/{cd_id}/cases", data=json.dumps(case),
                                headers={'Content-Type': 'application/json', 'Authorization': f"Bearer {access_token}"})

    assert response.status_code == 200
    assert (num_cases_before + 1) == test_db.session.query(models.Case).count()
    json_data = response.get_json()
    assert json_data['id']
    assert json_data['created_location']
    assert json_data['created_location']['latitude'] == case['latitude']
    assert json_data['created_location']['longitude'] == case['longitude']
    assert json_data['assigned_to']['id'] == case['assigned_to_id']
    assert json_data['assigned_to']['id'] == case['assigned_to_id']


def test_post_valid_case_with_note(test_client, test_db, basic_case_definition, admin_user):

    num_cases_before = test_db.session.query(models.Case).count()
    cd_id = basic_case_definition.id

    case = {
        "name": "Test Case",
        "description": "This is a description of the test case",
        "case_definition_id": cd_id,
        "notes": ['this is a case note']
    }

    access_token = create_access_token(identity=admin_user.id)
    response = test_client.post(f"/case_definitions/{cd_id}/cases", data=json.dumps(case),
                                headers={'Content-Type': 'application/json', 'Authorization': f"Bearer {access_token}"})

    assert response.status_code == 200
    assert (num_cases_before + 1) == test_db.session.query(models.Case).count()
    json_data = response.get_json()
    assert json_data['id']
    assert len(json_data['notes']) > 0


post_case_invalid_data_cases = [
    {
        'id': 'name-missing',
        'data': {
            "description": "This is a description of the test case",
            "case_definition_id": None,
            "notes": []
        },
        'response_status': 400,
        'response_message': "A name is required for a case."
    }, {
        'id': 'name-empty',
        'data': {
            "name": "",
            "description": "This is a description of the test case",
            "case_definition_id": None,
            "notes": []
        },
        'response_status': 400,
        'response_message': "A name is required for a case."
    }, {
        'id': 'name-none',
        'data': {
            "name": None,
            "description": "This is a description of the test case",
            "case_definition_id": None,
            "notes": []
        },
        'response_status': 400,
        'response_message': "A name is required for a case."
    }, {
        'id': 'name-too-short',
        'data': {
            "name": "Test",
            "description": "This is a description of the test case",
            "case_definition_id": None,
            "notes": []
        },
        'response_status': 400,
        'response_message': "Case names must be at least 8 characters long."
    }, {
        'id': 'name-too-long',
        'data': {
            "name": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
            "description": "This is a description of the test case",
            "case_definition_id": None,
            "notes": []
        },
        'response_status': 400,
        'response_message': "Case names cannot be longer than 50 characters."
    }, {
        'id': 'case-def-id-unknown',
        'data': {
            "name": "Test Case",
            "description": "This is a description of the test case",
            "case_definition_id": None,
            "notes": []
        },
        'test_case_definition_id': 99,
        'response_status': 404,
        'response_message': ""
    }, {
        'id': 'case-unknown-assigned-to',
        'data': {
            "name": "Test Case",
            "description": "This is a description of the test case",
            "case_definition_id": None,
            "assigned_to_id": 99,
            "notes": []
        },
        'response_status': 400,
        'response_message': "Cannot assigned case to unknown user id."
    }
]

post_case_invalid_data_cases_ids = \
    [case['id'] for case in post_case_invalid_data_cases]


@pytest.mark.parametrize('test_case', post_case_invalid_data_cases,
                         ids=post_case_invalid_data_cases_ids)
def test_post_case_fails_with_invalid_data(test_client, test_db, basic_case_definition, admin_user, test_case):

    cd_id = test_case.get('test_case_definition_id', basic_case_definition.id)

    case_data = test_case['data']
    case_data['case_definition_id'] = cd_id

    access_token = create_access_token(identity=admin_user.id)
    response = test_client.post(f"/case_definitions/{cd_id}/cases", data=json.dumps(case_data),
                                headers={'Content-Type': 'application/json', 'Authorization': f"Bearer {access_token}"})

    assert response.status_code == test_case['response_status']
    json_data = response.get_json()
    # 404 response for unknown case def if does not return a JSON response
    if json_data:
        assert json_data['message'] == test_case['response_message']


def test_post_case_fails_with_duplicate_name(test_client, basic_case, admin_user):

    case = {
        "name": basic_case.name,
        "description": "This is a description of the test case",
        "case_definition_id": basic_case.case_definition.id,
        "notes": ['this is a case note']
    }

    access_token = create_access_token(identity=admin_user.id)
    response = test_client.post(f"/case_definitions/{basic_case.case_definition.id}/cases", data=json.dumps(case),
                                headers={'Content-Type': 'application/json', 'Authorization': f"Bearer {access_token}"})

    assert response.status_code == 400
    json_data = response.get_json()
    assert json_data['message'] == 'Case names must be unique.'


get_cases_test_cases = [
    {
        'id': 'no-cases',
        'case_names': [],
        'url': "/cases",
        'response_status': 200,
        'response_count': 0
    }, {
        'id': 'all-cases',
        'case_names': [f"Test Case {x}" for x in range(1, 11)],
        'url': "/cases",
        'response_status': 200,
        'response_count': 10
    }, {
        'id': 'search-match-name',
        'case_names': ["Test Case 1", "Test Case 2", "Another Test Case 1", "Another Test Case 2"],
        'url': "/cases?search_term=Another",
        'response_status': 200,
        'response_count': 2
    }, {
        'id': 'search-match-key',
        'case_names': ["Test Case 1", "Test Case 2", "Another Test Case 1", "Another Test Case 2"],
        'url': "/cases?search_term=BCD-1",
        'response_status': 200,
        'response_count': 1
    }, {
        'id': 'search-match-name-and-key',
        'case_names': ["BCD-1", "BCD-2"],
        'url': "/cases?search_term=BCD-1",
        'response_status': 200,
        'response_count': 1
    }, {
        'id': 'search-no-match',
        'case_names': ["Test Case 1", "Test Case 2", "Another Test Case 1", "Another Test Case 2"],
        'url': "/cases?search_term=Foo",
        'response_status': 200,
        'response_count': 0
    }, {
        'id': 'search-term-not-sent',
        'case_names': [f"Test Case {x}" for x in range(1, 11)],
        'url': "/cases?search_term=",
        'response_status': 200,
        'response_count': 10
    }, {
        'id': 'search-term-contain-space',
        'case_names': ["Test Case 1", "Test Case 2", "Another Test Case 1", "Another Test Case 2"],
        'url': "/cases?search_term=Another Test",
        'response_status': 200,
        'response_count': 2
    }, {
        'id': 'search-mismatched-case-name',
        'case_names': ["Test Case 1", "Test Case 2", "Another Test Case 1", "Another Test Case 2"],
        'url': "/cases?search_term=another",
        'response_status': 200,
        'response_count': 2
    }, {
        'id': 'search-mismatched-case-key',
        'case_names': ["Test Case 1", "Test Case 2", "Another Test Case 1", "Another Test Case 2"],
        'url': "/cases?search_term=bcd-1",
        'response_status': 200,
        'response_count': 1
    }
]
get_cases_test_cases_ids = [case['id'] for case in get_cases_test_cases]


@pytest.mark.parametrize('test_case', get_cases_test_cases,
                         ids=get_cases_test_cases_ids)
def test_get_cases(test_client, test_db, basic_case_definition, admin_user, test_case):
    """ n cases """

    for case_name in test_case['case_names']:
        test_db.session.add(models.Case(name=case_name, case_definition_id=basic_case_definition.id,
                                        created_by=admin_user, updated_by=admin_user))
    test_db.session.commit()

    access_token = create_access_token(identity=admin_user.id)
    response = test_client.get(test_case['url'], headers={'Content-Type': 'application/json',
                                                          'Authorization': f"Bearer {access_token}"})

    assert response.status_code == test_case['response_status']
    assert len(response.get_json()) == test_case['response_count']


def test_get_case(test_client, basic_case, admin_access_token):

    response = test_client.get(f"/cases/{basic_case.id}",
                               headers={'Content-Type': 'application/json',
                                        'Authorization': f"Bearer {admin_access_token}"})

    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['id']
    assert json_data['id'] == basic_case.id


def test_put_case(test_client, basic_case, data_collector_user):

    data = {
        'name': "New Case Name",
        'description': "New Case Description",
        "latitude": 75.8692385,
        "longitude": -0.428003,
        "assigned_to_id": data_collector_user.id
    }

    access_token = create_access_token(identity=data_collector_user.id)
    response = test_client.put(f"/cases/{basic_case.id}", data=json.dumps(data),
                               headers={'Content-Type': 'application/json', 'Authorization': f"Bearer {access_token}"})

    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['name'] == data['name']
    assert json_data['description'] == data['description']
    assert json_data['updated_by']['id'] == data_collector_user.id
    assert json_data['status']['id'] == 1
    assert json_data['status']['name'] == 'TODO'
    assert json_data['updated_location']
    assert json_data['updated_location']['latitude'] == data['latitude']
    assert json_data['updated_location']['longitude'] == data['longitude']
    assert json_data['assigned_to']['id'] == data['assigned_to_id']


put_case_invalid_data_cases = [
   {
        'id': 'name-empty',
        'data': {
            "name": "",
            "description": "This is a description of the test case"
        },
        'response_status': 400,
        'response_message': "A name is required for a case."
    }, {
        'id': 'name-none',
        'data': {
            "name": None,
            "description": "This is a description of the test case"
        },
        'response_status': 400,
        'response_message': "A name is required for a case."
    }, {
        'id': 'name-too-short',
        'data': {
            "name": "Test",
            "description": "This is a description of the test case"
        },
        'response_status': 400,
        'response_message': "Case names must be at least 8 characters long."
    }, {
        'id': 'name-too-long',
        'data': {
            "name": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
            "description": "This is a description of the test case"
        },
        'response_status': 400,
        'response_message': "Case names cannot be longer than 50 characters."
    }, {
        'id': 'invalid-status',
        'data': {
            "status_id": 99,
            "description": "This is a description of the test case"
        },
        'response_status': 400,
        'response_message': "Invalid case status_id: 99"
    }, {
        'id': 'unknown-assigned-to',
        'data': {
            "assigned_to_id": 99,
        },
        'response_status': 400,
        'response_message': "Cannot assigned case to unknown user id."
    }
]
put_case_invalid_data_cases_ids = [case['id'] for case in put_case_invalid_data_cases]


@pytest.mark.parametrize('test_case', put_case_invalid_data_cases,
                         ids=put_case_invalid_data_cases_ids)
def test_put_case_fails_with_invalid_data(test_client, basic_case, admin_user, test_case):

    access_token = create_access_token(identity=admin_user.id)
    response = test_client.put(f"/cases/{basic_case.id}", data=json.dumps(test_case['data']),
                               headers={'Content-Type': 'application/json', 'Authorization': f"Bearer {access_token}"})

    assert response.status_code == test_case['response_status']
    json_data = response.get_json()
    assert json_data['message'] == test_case['response_message']


def test_put_case_fails_with_duplicate_name(test_client, list_of_basic_cases, admin_access_token):

    c = list_of_basic_cases[0]
    c2 = list_of_basic_cases[1]

    case = {
        "name": c.name,
        "description": "This is a description of the test case",
        "case_definition_id": c.case_definition.id,
        "notes": ['this is a case note']
    }

    response = test_client.put(f"/cases/{c2.id}", data=json.dumps(case),
                               headers={'Content-Type': 'application/json',
                                        'Authorization': f"Bearer {admin_access_token}"})

    assert response.status_code == 400
    json_data = response.get_json()
    assert json_data['message'] == 'Case names must be unique.'


def test_put_case_should_succeed_with_same_name(test_client, basic_case, admin_access_token):

    case = {
        "name": "Test Case",
        "description": "This is a description of the test case",
        "case_definition_id": basic_case.case_definition.id,
        "notes": ['this is a case note']
    }

    response = test_client.put(f"/cases/{basic_case.id}", data=json.dumps(case),
                               headers={'Content-Type': 'application/json',
                                        'Authorization': f"Bearer {admin_access_token}"})

    assert response.status_code == 200


def test_put_case_should_allow_empty_description(test_client, basic_case, admin_access_token):

    case = {"description": ""}

    response = test_client.put(f"/cases/{basic_case.id}", data=json.dumps(case),
                               headers={'Content-Type': 'application/json', 'Authorization': f"Bearer {admin_access_token}"})

    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['description'] == ''


def test_delete_case(test_client, full_case, admin_user):

    case_id = full_case.id

    access_token = create_access_token(identity=admin_user.id)
    response = test_client.delete(f"/cases/{case_id}",
                                  headers={'Content-Type': 'application/json',
                                           'Authorization': f"Bearer {access_token}"})

    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['message'] == 'Case successfully deleted.'
    assert not models.Case.query.get(case_id)
    assert not models.Note.query.filter_by(model_id=case_id).all()
    assert not models.SurveyResponse.query.filter_by(case_id=case_id).all()
    assert not models.UploadedFile.query.filter_by(model_id=case_id).all()


without_permission_test_cases = [
    {
        'id': 'post-cases',
        'url': '/case_definitions/99/cases',
        'method': 'POST',
        'response_message': 'You do not have permission to create a case.'
    }, {
        'id': 'get-cases',
        'url': '/cases',
        'method': 'GET',
        'response_message': 'You do not have permission to read cases.'
    }, {
        'id': 'get-case',
        'url': '/cases/99',
        'method': 'GET',
        'response_message': 'You do not have permission to read cases.'
    }, {
        'id': 'put-case',
        'url': '/cases/99',
        'method': 'PUT',
        'response_message': 'You do not have permission to update cases.'
    }, {
        'id': 'delete-case',
        'url': '/cases/99',
        'method': 'DELETE',
        'response_message': 'You do not have permission to delete cases.'
    }
]
without_permission_test_cases_ids = [case['id'] for case in without_permission_test_cases]


@pytest.mark.parametrize('test_case', without_permission_test_cases, ids=without_permission_test_cases_ids)
def test_cases_fails_without_permission(test_client, test_db, user_with_no_permissions, test_case):

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


unknown_case_test_cases = [
    {
        'id': 'get-case',
        'url': '/cases/99',
        'method': 'GET'
    }, {
        'id': 'put-case',
        'url': '/cases/99',
        'method': 'PUT'
    }, {
        'id': 'delete-case',
        'url': '/cases/99',
        'method': 'DELETE'
    }
]
unknown_case_test_cases_ids = [case['id'] for case in unknown_case_test_cases]


@pytest.mark.parametrize('test_case', unknown_case_test_cases, ids=unknown_case_test_cases_ids)
def test_case_with_unknown_case(test_client, admin_access_token, test_case):
    """ 404 """

    headers = {'Content-Type': 'application/json', 'Authorization': f"Bearer {admin_access_token}"}
    if test_case['method'] == 'POST':
        response = test_client.post(test_case['url'], headers=headers)
    elif test_case['method'] == 'PUT':
        response = test_client.put(test_case['url'], headers=headers)
    elif test_case['method'] == 'DELETE':
        response = test_client.delete(test_case['url'], headers=headers)
    else:
        response = test_client.get(test_case['url'], headers=headers)

    assert response.status_code == 404


case_status_test_cases = [
    {
        'id': 'todo',
        'status_id': 1,
        'status_name': 'TODO'
    }, {
        'id': 'inprogress',
        'status_id': 2,
        'status_name': 'In Progress'
    }, {
        'id': 'done',
        'status_id': 3,
        'status_name': 'Done'
    }
]
case_status_test_cases_ids = [case['id'] for case in case_status_test_cases]


@pytest.mark.parametrize('test_case', case_status_test_cases, ids=case_status_test_cases_ids)
def test_put_case_status(test_client, basic_case, data_collector_user, data_collector_access_token, test_case):

    data = {
        'name': "New Case Name",
        'description': "New Case Description",
        'status_id': test_case['status_id']
    }

    response = test_client.put(f"/cases/{basic_case.id}", data=json.dumps(data),
                               headers={'Content-Type': 'application/json',
                                        'Authorization': f"Bearer {data_collector_access_token}"})

    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['name'] == data['name']
    assert json_data['description'] == data['description']
    assert json_data['updated_by']['id'] == data_collector_user.id
    assert json_data['status']['id'] == test_case['status_id']
    assert json_data['status']['name'] == test_case['status_name']


def test_get_case_surveys(test_client, test_db):
    user = models.User.query.filter_by(username='admin').first()
    survey = models.Survey(name='Test Survey', reporting_table_name='test_survey',
                           structure={"pages": [{"name": "page1", "elements": [{"type": "text", "name": "question1"}]}],
                                      "title": "Test Survey"}, created_by=user, updated_by=user)
    test_db.session.add(survey)
    test_db.session.commit()
    survey_id = survey.id

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

    access_token = create_access_token(identity=user.id)
    response = test_client.post("/case_definitions/", data=json.dumps(case_definition),
                                headers={'Content-Type': 'application/json', 'Authorization': f"Bearer {access_token}"})

    assert response.status_code == 200

    case = {
        "name": "Test Case",
        "description": "This is a description of the test case",
        "case_definition_id": 1,
        "notes": []
    }

    access_token = create_access_token(identity=user.id)
    response = test_client.post(f"/case_definitions/1/cases", data=json.dumps(case),
                                headers={'Content-Type': 'application/json', 'Authorization': f"Bearer {access_token}"})
    assert response.status_code == 200

    response_structure = {"structure": {"question1": "bb"}}

    response = test_client.post(
        f"/surveys/{survey_id}/responses", data=json.dumps(response_structure),
        headers={'Content-Type': 'application/json', 'Authorization': f"Bearer {access_token}"}
    )
    assert response.status_code == 200

    response_structure = {"structure": {"question1": "cc"}, 'case_id': 1}

    response = test_client.post(
        f"/surveys/{survey_id}/responses", data=json.dumps(response_structure),
        headers={'Content-Type': 'application/json', 'Authorization': f"Bearer {access_token}"}
    )
    assert response.status_code == 200

    response = test_client.get(
        f"/cases",
        headers={'Content-Type': 'application/json', 'Authorization': f"Bearer {access_token}"}
    )
    assert response.status_code == 200
    assert len(response.json[0]['surveys']) == 1
    assert response.json[0]['surveys'][0] == {'id': 1, 'name': 'Test Survey', 'responses_count': 1}


def test_get_case_surveys_responses(test_client, test_db):
    user = models.User.query.filter_by(username='admin').first()
    survey = models.Survey(name='Test Survey', reporting_table_name='test_survey',
                           structure={"pages": [{"name": "page1", "elements": [{"type": "text", "name": "question1"}]}],
                                      "title": "Test Survey"}, created_by=user, updated_by=user)
    test_db.session.add(survey)
    test_db.session.commit()
    survey_id = survey.id

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

    access_token = create_access_token(identity=user.id)
    response = test_client.post("/case_definitions/", data=json.dumps(case_definition),
                                headers={'Content-Type': 'application/json', 'Authorization': f"Bearer {access_token}"})

    assert response.status_code == 200

    case = {
        "name": "Test Case",
        "description": "This is a description of the test case",
        "case_definition_id": 1,
        "notes": []
    }

    access_token = create_access_token(identity=user.id)
    response = test_client.post(f"/case_definitions/1/cases", data=json.dumps(case),
                                headers={'Content-Type': 'application/json', 'Authorization': f"Bearer {access_token}"})
    assert response.status_code == 200

    response_structure = {"structure": {"question1": "bb"}}

    response = test_client.post(
        f"/surveys/{survey_id}/responses", data=json.dumps(response_structure),
        headers={'Content-Type': 'application/json', 'Authorization': f"Bearer {access_token}"}
    )
    assert response.status_code == 200

    resp = test_client.get(
        f'/cases/1/surveys/{survey_id}/responses',
        headers={'Content-Type': 'application/json', 'Authorization': f"Bearer {access_token}"}
    )

    assert resp.status_code == 200
    assert resp.json == []

    response_structure = {"structure": {"question1": "cc"}, 'case_id': 1}

    response = test_client.post(
        f"/surveys/{survey_id}/responses", data=json.dumps(response_structure),
        headers={'Content-Type': 'application/json', 'Authorization': f"Bearer {access_token}"}
    )
    assert response.status_code == 200

    resp = test_client.get(
        f'/cases/1/surveys/{survey_id}/responses',
        headers={'Content-Type': 'application/json', 'Authorization': f"Bearer {access_token}"}
    )

    assert resp.status_code == 200
    assert len(resp.json) == 1


def _setup_case(test_client):
    access_token = get_access_token(test_client)
    headers = {'Content-Type': 'application/json', 'Authorization': f"Bearer {access_token}"}

    case_definition = {
        "name": "Test Case Definition",
        "key": "TCD1",
        "description": "This is a description of the test case definition",
        "surveys": [],
        "documents": [{
            "name": "Birth Certificate",
            "description": "blash blah",
            "is_required": True
        }]
    }

    resp = test_client.post(
        '/case_definitions/',
        data=json.dumps(case_definition),
        headers=headers
    )

    assert resp.status_code == 200

    case_defn_id = resp.json['id']

    case = {
        "name": "Test Case",
        "description": "This is a description of the test case",
        "case_definition_id": case_defn_id,
        "notes": []
    }

    resp = test_client.post(
        f"/case_definitions/{case_defn_id}/cases",
        data=json.dumps(case),
        headers={'Content-Type': 'application/json', 'Authorization': f"Bearer {access_token}"}
    )

    assert resp.status_code == 200

    case_id = resp.json['id']

    return case_id, case_defn_id, headers


def test_post_case_note(test_client, test_db):
    case_id, _, headers = _setup_case(test_client)

    case_note = {
        'note': 'blah',
        'case_id': case_id
    }
    resp = test_client.post(
        f'/cases/{case_id}/notes',
        data=json.dumps(case_note),
        headers=headers
    )
    assert resp.status_code == 200

    case_note_id = resp.json['id']

    resp = test_client.get(
        f'/cases/{case_id}',
        headers=headers
    )
    assert resp.status_code == 200
    assert resp.json['notes'][0]['id'] == case_note_id


def test_get_case_note(test_client, test_db):
    case_id, _, headers = _setup_case(test_client)

    case_note = {
        'note': 'blah',
        'case_id': case_id
    }
    resp = test_client.post(
        f'/cases/{case_id}/notes',
        data=json.dumps(case_note),
        headers=headers
    )
    assert resp.status_code == 200

    note_1 = resp.json

    resp = test_client.post(
        f'/cases/{case_id}/notes',
        data=json.dumps(case_note),
        headers=headers
    )
    assert resp.status_code == 200

    note_2 = resp.json

    resp = test_client.get(
        f'/cases/{case_id}/notes',
        headers=headers
    )

    assert resp.status_code == 200
    assert resp.json == [note_1, note_2]


def test_get_single_case_note(test_client, test_db):
    case_id, _, headers = _setup_case(test_client)

    case_note = {
        'note': 'blah',
        'case_id': case_id
    }
    resp = test_client.post(
        f'/cases/{case_id}/notes',
        data=json.dumps(case_note),
        headers=headers
    )
    assert resp.status_code == 200

    resp = test_client.post(
        f'/cases/{case_id}/notes',
        data=json.dumps(case_note),
        headers=headers
    )
    assert resp.status_code == 200

    note_2 = resp.json
    note_2_id = note_2['id']

    resp = test_client.get(
        f'/cases/{case_id}/notes/{note_2_id}',
        headers=headers
    )

    assert resp.status_code == 200
    assert resp.json == note_2


def test_put_case_note(test_client, test_db):
    case_id, _, headers = _setup_case(test_client)

    case_note = {
        'note': 'blah',
        'case_id': case_id
    }
    resp = test_client.post(
        f'/cases/{case_id}/notes',
        data=json.dumps(case_note),
        headers=headers
    )
    assert resp.status_code == 200

    case_note_id = resp.json['id']

    resp = test_client.get(
        f'/cases/{case_id}',
        headers=headers
    )
    assert resp.status_code == 200
    assert resp.json['notes'][0]['note'] == 'blah'

    update = {
        'note': 'foo'
    }

    resp = test_client.put(
        f'/cases/{case_id}/notes/{case_note_id}',
        data=json.dumps(update),
        headers=headers
    )
    assert resp.status_code == 200

    resp = test_client.get(
        f'/cases/{case_id}',
        headers=headers
    )
    assert resp.status_code == 200
    assert resp.json['notes'][0]['note'] == 'foo'


def test_delete_case_note(test_client, test_db):
    case_id, _, headers = _setup_case(test_client)

    case_note = {
        'note': 'blah',
        'case_id': case_id
    }
    resp = test_client.post(
        f'/cases/{case_id}/notes',
        data=json.dumps(case_note),
        headers=headers
    )
    assert resp.status_code == 200

    case_note_id = resp.json['id']

    resp = test_client.get(
        f'/cases/{case_id}',
        headers=headers
    )
    assert resp.status_code == 200
    assert resp.json['notes'][0]['id'] == case_note_id

    resp = test_client.delete(
        f'/cases/{case_id}/notes/{case_note_id}',
        headers=headers
    )
    assert resp.status_code == 200

    resp = test_client.get(
        f'/cases/{case_id}',
        headers=headers
    )
    assert resp.status_code == 200
    assert resp.json['notes'] == []


def test_upload_file(test_client, test_db):
    from unittest import mock
    import io

    case_id, _, headers = _setup_case(test_client)

    with mock.patch('app.storage', autospec=True) as storage_mock:
        upload_return = storage_mock.upload.return_value
        upload_return.name = 'test_filename'
        upload_return.url = 'example.com'

        data = {'file': (io.BytesIO(b'foo'), 'test.txt')}

        resp = test_client.post(
            f'/cases/{case_id}/add_file',
            data=data,
            content_type='multipart/form-data',
            headers=headers
        )

        assert resp.status_code == 200

        storage_mock.upload.assert_called_once()

    resp = test_client.get(f'/cases/{case_id}', headers=headers)

    assert resp.status_code == 200
    assert resp.json['files'][0]['original_filename'] == 'test.txt'
    assert resp.json['files'][0]['remote_filename'] == 'test_filename'
    assert resp.json['files'][0]['url'] == '/files/1/download'


def test_reupload_file(test_client, test_db):
    from unittest import mock
    import io

    case_id, _, headers = _setup_case(test_client)

    with mock.patch('app.storage', autospec=True) as storage_mock:
        upload_return = storage_mock.upload.return_value
        upload_return.name = 'test_filename'
        upload_return.url = 'example.com'

        data = {'file': (io.BytesIO(b'foo'), 'test.txt'), 'document_id': 1}

        resp = test_client.post(
            f'/cases/{case_id}/add_file',
            data=data,
            content_type='multipart/form-data',
            headers=headers
        )

        assert resp.status_code == 200

        storage_mock.upload.assert_called_once()

        resp = test_client.get(f'/cases/{case_id}', headers=headers)

        assert resp.status_code == 200

        resp = test_client.get(
            f'/cases/files/1',
            headers=headers
        )

        assert resp.status_code == 200
        assert resp.json['original_filename'] == 'test.txt'
        assert resp.json['remote_filename'] == 'test_filename'
        assert resp.json['url'] == '/files/1/download'

        upload_return.name = 'test_filename_2'

        data = {'file': (io.BytesIO(b'foo'), 'test_2.txt'), 'document_id': 1}

        resp = test_client.post(
            f'/cases/{case_id}/add_file',
            data=data,
            content_type='multipart/form-data',
            headers=headers
        )

        assert resp.status_code == 200
        storage_mock.get.return_value.delete.assert_called_once()

        resp = test_client.get(
            f'/cases/files/2',
            headers=headers
        )

        assert resp.status_code == 200
        assert resp.json['original_filename'] == 'test_2.txt'
        assert resp.json['remote_filename'] == 'test_filename_2'
        assert resp.json['url'] == '/files/2/download'

        resp = test_client.get(
            f'/cases/files/1',
            headers=headers
        )

        assert resp.status_code == 404


def test_fetch_file(test_client, test_db):
    from unittest import mock
    import io

    case_id, _, headers = _setup_case(test_client)

    with mock.patch('app.storage', autospec=True) as storage_mock:
        upload_return = storage_mock.upload.return_value
        upload_return.name = 'test_filename'

        data = {'file': (io.BytesIO(b'foo'), 'test.txt')}

        resp = test_client.post(
            f'/cases/{case_id}/add_file',
            data=data,
            content_type='multipart/form-data',
            headers=headers
        )

        assert resp.status_code == 200

        storage_mock.upload.assert_called_once()

    resp = test_client.get(
        f'/cases/files/1',
        headers=headers
    )

    assert resp.status_code == 200
    assert resp.json['original_filename'] == 'test.txt'
    assert resp.json['remote_filename'] == 'test_filename'
    assert resp.json['url'] == '/files/1/download'


def test_remove_file(test_client, test_db):
    case_id, _, headers = _setup_case(test_client)

    with mock.patch('app.storage', autospec=True) as storage_mock:
        upload_return = storage_mock.upload.return_value
        upload_return.name = 'test_filename'
        upload_return.url = 'example.com'

        data = {'file': (io.BytesIO(b'foo'), 'test.txt')}

        resp = test_client.post(
            f'/cases/{case_id}/add_file',
            data=data,
            content_type='multipart/form-data',
            headers=headers
        )

        assert resp.status_code == 200

        storage_mock.upload.assert_called_once()

        resp = test_client.delete(
            f'/cases/files/1',
            headers=headers
        )

        assert resp.status_code == 200

        storage_mock.get.return_value.delete.assert_called_once()

    resp = test_client.get(f'/cases/{case_id}', headers=headers)

    assert resp.status_code == 200
    assert resp.json['files'] == []


def test_case_document_files(test_client, test_db):
    access_token = get_access_token(test_client)
    headers = {'Content-Type': 'application/json', 'Authorization': f"Bearer {access_token}"}

    case_definition = {
        "name": "Test Case Definition",
        "key": "TCD1",
        "description": "This is a description of the test case definition",
        "surveys": [],
        "documents": [
            {
                "name": "Doc 1",
                "description": "test_desc",
                "is_required": True
            },
            {
                "name": "Doc 2",
                "description": "test_desc_2",
                "is_required": False
            }
        ]
    }

    resp = test_client.post(
        '/case_definitions/',
        data=json.dumps(case_definition),
        headers=headers
    )

    assert resp.status_code == 200

    case_defn_id = resp.json['id']

    case = {
        "name": "Test Case",
        "description": "This is a description of the test case",
        "case_definition_id": case_defn_id,
        "notes": []
    }

    resp = test_client.post(
        f"/case_definitions/{case_defn_id}/cases",
        data=json.dumps(case),
        headers={'Content-Type': 'application/json', 'Authorization': f"Bearer {access_token}"}
    )

    assert resp.status_code == 200

    case_id = resp.json['id']

    with mock.patch('app.storage', autospec=True) as storage_mock:
        upload_return = storage_mock.upload.return_value
        upload_return.name = 'test_filename'

        data = {'file': (io.BytesIO(b'foo'), 'test.txt'), 'document_id': 1}

        resp = test_client.post(
            f'/cases/{case_id}/add_file',
            data=data,
            content_type='multipart/form-data',
            headers=headers
        )

        assert resp.status_code == 200

        data = {'file': (io.BytesIO(b'foo'), 'test_2.txt')}

        resp = test_client.post(
            f'/cases/{case_id}/add_file',
            data=data,
            content_type='multipart/form-data',
            headers=headers
        )

        assert resp.status_code == 200

    resp = test_client.get(
        f'/cases/{case_id}',
        headers=headers
    )

    assert resp.status_code == 200

    case = resp.json

    assert 'documents' in case

    expected = [
        {
            'id': 1,
            'document_id': 1,
            'name': 'Doc 1',
            'description': 'test_desc',
            'original_filename': 'test.txt',
            'remote_filename': 'test_filename',
            'url': '/files/1/download',
            'is_required': True
        },
        {
            'id': None,
            'document_id': 2,
            'name': 'Doc 2',
            'description': 'test_desc_2',
            'original_filename': None,
            'remote_filename': None,
            'url': None,
            'is_required': False
        },
        {
            'id': 2,
            'document_id': None,
            'name': None,
            'description': None,
            'original_filename': 'test_2.txt',
            'remote_filename': 'test_filename',
            'url': '/files/2/download',
            'is_required': None
        },
    ]

    def check_if_subset(d1, d2):
        return all(d1[key] == d2[key] for key in d1.keys())

    assert all(check_if_subset(*i) for i in zip(expected, case['documents']))


def test_file_upload_document_id_empty_string(test_client, test_db):
    case_id, _, headers = _setup_case(test_client)

    with mock.patch('app.storage', autospec=True) as storage_mock:
        upload_return = storage_mock.upload.return_value
        upload_return.name = 'test_filename'
        upload_return.url = 'example.com'

        data = {'file': (io.BytesIO(b'foo'), 'test.txt'), 'document_id': ''}

        resp = test_client.post(
            f'/cases/{case_id}/add_file',
            data=data,
            content_type='multipart/form-data',
            headers=headers
        )

        assert resp.status_code == 200

        storage_mock.upload.assert_called_once()


def test_done_case_status(test_client, test_db):
    access_token = get_access_token(test_client)
    headers = {'Content-Type': 'application/json', 'Authorization': f"Bearer {access_token}"}

    case_definition = {
        "name": "Test Case Definition",
        "key": "TCD1",
        "description": "This is a description of the test case definition",
        "surveys": [],
        "documents": [
            {
                "name": "Doc 1",
                "description": "test_desc",
                "is_required": True
            },
            {
                "name": "Doc 2",
                "description": "test_desc_2",
                "is_required": False
            }
        ]
    }

    resp = test_client.post(
        '/case_definitions/',
        data=json.dumps(case_definition),
        headers=headers
    )
    assert resp.status_code == 200

    case_defn_id = resp.json['id']

    case = {
        "name": "Test Case",
        "description": "This is a description of the test case",
        "case_definition_id": case_defn_id,
        "notes": []
    }

    resp = test_client.post(
        f"/case_definitions/{case_defn_id}/cases",
        data=json.dumps(case),
        headers={'Content-Type': 'application/json', 'Authorization': f"Bearer {access_token}"}
    )

    assert resp.status_code == 200

    case_id = resp.json['id']

    resp = test_client.put(
        f'/cases/{case_id}',
        data=json.dumps({'status_id': 3}),
        headers=headers
    )

    assert resp.status_code == 400
    assert resp.json['message'] == 'All required case documents have not been uploaded.'

    with mock.patch('app.storage', autospec=True) as storage_mock:
        upload_return = storage_mock.upload.return_value
        upload_return.name = 'test_filename'

        data = {'file': (io.BytesIO(b'foo'), 'test.txt'), 'document_id': 1}

        resp = test_client.post(
            f'/cases/{case_id}/add_file',
            data=data,
            content_type='multipart/form-data',
            headers=headers
        )

        assert resp.status_code == 200

    resp = test_client.put(
        f'/cases/{case_id}',
        data=json.dumps({'status_id': 3}),
        headers=headers
    )

    assert resp.status_code == 200


def test_get_case_history(test_client, basic_case, admin_access_token):

    response = test_client.get(f"/cases/{basic_case.id}",
                               headers={'Content-Type': 'application/json',
                                        'Authorization': f"Bearer {admin_access_token}"})

    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['history']
    assert len(json_data['history']) == 1

    history = json_data['history'][0]

    assert history['performed_by']['username'] == 'admin'
    assert history['action'] == 'insert'

    changes = {ch['property_changed']: ch for ch in history['changes']}

    expected_changes = {
        'name': {
            'property_changed': 'name',
            'old_value': None,
            'new_value': 'Basic Case'
        },
        'case_definition_id': {
            'property_changed': 'case_definition_id',
            'old_value': None,
            'new_value': 1
        },
        'id': {
            'property_changed': 'id',
            'old_value': None,
            'new_value': 1
        },
        'created_by_id': {
            'property_changed': 'created_by_id',
            'old_value': None,
            'new_value': 1
        },
        'updated_by_id': {
            'property_changed': 'updated_by_id',
            'old_value': None,
            'new_value': 1
        },
        'custom_fields': {
            'property_changed': 'custom_fields',
            'old_value': None,
            'new_value': []
        },
        'status_id': {
            'property_changed': 'status_id',
            'old_value': None,
            'new_value': 1
        },
        'created_at': {
            'property_changed': 'created_at',
            'old_value': None,
            'new_value': json_data['created_at']
        },
        'updated_at': {
            'property_changed': 'updated_at',
            'old_value': None,
            'new_value': json_data['updated_at']
        },
        'key': {
            'property_changed': 'key',
            'old_value': None,
            'new_value': 'BCD-1'
        }
    }

    assert expected_changes.items() <= changes.items()  # Checks if expected_changes is subset of changes


def test_update_case_history(test_client, basic_case, admin_access_token):
    data = {
        'name': "UPDATE_NAME",
    }
    response = test_client.put(f"/cases/{basic_case.id}", data=json.dumps(data),
                               headers={'Content-Type': 'application/json',
                                        'Authorization': f"Bearer {admin_access_token}"})

    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['history']
    assert len(json_data['history']) == 2

    history = json_data['history'][0]

    assert history['performed_by']['username'] == 'admin'
    assert history['action'] == 'update'

    changes = {ch['property_changed']: ch for ch in history['changes']}

    expected_changes = {
        'name': {
            'property_changed': 'name',
            'old_value': 'Basic Case',
            'new_value': 'UPDATE_NAME'
        },
    }

    assert expected_changes.items() <= changes.items()  # Checks if expected_changes is subset of changes
