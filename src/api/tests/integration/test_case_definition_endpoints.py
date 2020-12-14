import json
import pytest
from flask_jwt_extended import create_access_token
from app.models import User, Survey, CaseDefinition, CustomField
from ..test_helpers import setup_user_with_no_permissions, get_access_token
from unittest import mock
import io


def test_post_valid_case_definition(test_client, test_db):
    num_definitions_before = test_db.session.query(CaseDefinition).count()
    user = User.query.filter_by(username='admin').first()
    survey = Survey(name='Test Survey', reporting_table_name='test_survey',
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
        }],
        "custom_fields": [
            {
                "name": "Household Long Text",
                "field_type": "textarea",
                "selections": None,
                "validation_rules": None,
                "custom_section_id": None,
                "help_text": "This is for longer answers",
                "sort_order": 1
            },
            {
                "name": "Household Selection Field",
                "field_type": "select",
                "selections": [
                    {
                        "id": "1",
                        "value": "Household Selection Option A"
                    },
                    {
                        "id": "2",
                        "value": "Household Selection Option B"
                    },
                    {
                        "id": "3",
                        "value": "Household Selection Option C"
                    }
                ],
                "validation_rules": None,
                "custom_section_id": None,
                "help_text": "This is for a single selection among many",
                "sort_order": 2
            }
        ]
    }

    access_token = create_access_token(identity=user.id)
    response = test_client.post("/case_definitions/", data=json.dumps(case_definition),
                                headers={'Content-Type': 'application/json', 'Authorization': f"Bearer {access_token}"})

    assert response.status_code == 200
    assert (num_definitions_before + 1) == test_db.session.query(CaseDefinition).count()
    json_data = response.get_json()
    assert json_data['id']
    assert len(json_data['surveys']) == 1
    assert len(json_data['documents']) == 2
    assert len(json_data['custom_fields']) == 2
    cd = CaseDefinition.query.get(json_data['id'])
    assert cd
    assert len(cd.surveys.all()) == 1
    assert len(cd.documents) == 2
    assert len(cd.custom_fields) == 2


def test_post_custom_field(test_client, test_db, basic_case_definition):
    access_token = get_access_token(test_client)
    url = f"/case_definitions/{basic_case_definition.id}/custom_fields"
    headers = {'Content-Type': 'application/json', 'Authorization': f"Bearer {access_token}"}
    custom_field_data = {
        "name": "Household Long Text",
        "field_type": "textarea",
        "selections": None,
        "validation_rules": None,
        "custom_section_id": None,
        "help_text": "This is for longer answers",
        "sort_order": 1
    }

    response = test_client.post(url, data=json.dumps(custom_field_data), headers=headers)

    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['id']
    assert CustomField.query.get(json_data['id'])


def test_update_case_definition(test_client, test_db):
    case_definition = {
        "name": "test_name",
        "key": "TCD1",
        "description": "test_desc",
        "surveys": [],
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

    access_token = get_access_token(test_client)
    headers = {'Content-Type': 'application/json', 'Authorization': f"Bearer {access_token}"}

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
    assert resp.json['name'] == 'test_name'
    assert resp.json['description'] == 'test_desc'

    update = {
        'name': 'test_name_2',
        'description': 'test_desc_2'
    }

    resp = test_client.put(
        f'/case_definitions/{case_defn_id}',
        data=json.dumps(update),
        headers=headers
    )
    assert resp.status_code == 200

    resp = test_client.get(
        f'/case_definitions/{case_defn_id}',
        headers=headers
    )
    assert resp.status_code == 200
    assert resp.json['name'] == 'test_name_2'
    assert resp.json['description'] == 'test_desc_2'


def test_put_custom_field(test_client, test_db):
    case_definition = {
        "name": "test_name",
        "key": "TCD1",
        "description": "test_desc"
    }
    access_token = get_access_token(test_client)
    headers = {'Content-Type': 'application/json', 'Authorization': f"Bearer {access_token}"}

    # post CD
    resp = test_client.post(
        "/case_definitions/", data=json.dumps(case_definition),
        headers=headers
    )

    assert resp.status_code == 200

    # post CF
    case_defn_id = resp.json['id']
    custom_field = {
        "name": "Household Numeric Field",
        "field_type": "number",
        "selections": None,
        "validation_rules": None,
        "custom_section_id": None,
        "help_text": "This is for numbers",
        "sort_order": 1
    }

    resp = test_client.post(
        f'/case_definitions/{case_defn_id}/custom_fields',
        data=json.dumps(custom_field),
        headers=headers
    )
    custom_field_id = resp.json['id']

    assert resp.status_code == 200
    assert resp.json['name'] == custom_field['name']
    assert resp.json['field_type'] == custom_field['field_type']
    assert resp.json['selections'] == custom_field['selections']
    assert resp.json['validation_rules'] == []
    assert resp.json['custom_section_id'] == custom_field['custom_section_id']
    assert resp.json['help_text'] == custom_field['help_text']
    assert resp.json['sort_order'] == custom_field['sort_order']

    # update CF
    update = {
        "id": 37,
        "name": "Household Date Field",
        "field_type": "date",
        "selections": None,
        "validation_rules": None,
        "custom_section_id": None,
        "help_text": "This is for a date",
        "sort_order": 3
    }

    resp = test_client.put(
        f'/case_definitions/{case_defn_id}/custom_fields/{custom_field_id}',
        data=json.dumps(update),
        headers=headers
    )

    assert resp.status_code == 200
    assert resp.json['name'] == update['name']
    assert resp.json['field_type'] == update['field_type']
    assert resp.json['selections'] == update['selections']
    assert resp.json['validation_rules'] == []
    assert resp.json['custom_section_id'] == update['custom_section_id']
    assert resp.json['help_text'] == update['help_text']
    assert resp.json['sort_order'] == update['sort_order']


def test_get_case_definitions_no_data(test_client, test_db):
    access_token = get_access_token(test_client)
    response = test_client.get('/case_definitions/', headers={'Content-Type': 'application/json',
                                                              'Authorization': f"Bearer {access_token}"})
    assert response.status_code == 200
    assert len(response.get_json()) == 0


def test_get_case_definitions_one_case_definition(test_client, test_db):
    access_token = get_access_token(test_client)

    user = User.query.filter_by(username='admin').first()
    case_definition = CaseDefinition(key='TCD', name='Test Case Definition', created_by=user, updated_by=user)
    test_db.session.add(case_definition)
    test_db.session.commit()

    response = test_client.get('/case_definitions/', headers={'Content-Type': 'application/json',
                                                              'Authorization': f"Bearer {access_token}"})

    assert response.status_code == 200
    assert len(response.get_json()) == 1


def test_get_case_definitions_n_case_definitions(test_client, test_db):
    user = User.query.filter_by(username='admin').first()
    for x in range(0, 10):
        test_db.session.add(CaseDefinition(key=f"TCD{str(x)}", name=f"Test Case Definition {str(x)}", created_by=user,
                                           updated_by=user))
    test_db.session.commit()

    access_token = get_access_token(test_client)
    response = test_client.get('/case_definitions/', headers={'Content-Type': 'application/json',
                                                              'Authorization': f"Bearer {access_token}"})

    assert response.status_code == 200
    assert len(response.get_json()) == 10


def test_get_case_definition(test_client, test_db):
    user = User.query.filter_by(username='admin').first()
    case_def = CaseDefinition(key='TCD', name="Test Case Definition", created_by=user, updated_by=user)
    test_db.session.add(case_def)
    test_db.session.commit()

    access_token = get_access_token(test_client)
    response = test_client.get(f"/case_definitions/{case_def.id}", headers={'Content-Type': 'application/json',
                                                                            'Authorization': f"Bearer {access_token}"})

    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['id']
    assert json_data['id'] == case_def.id


def test_get_case_definition_fails_with_unknown_case_definition(test_client, test_db):
    access_token = get_access_token(test_client)
    response = test_client.get("/case_definition/99", headers={'Content-Type': 'application/json',
                                                               'Authorization': f"Bearer {access_token}"})

    assert response.status_code == 404


without_permission_test_cases = [
    {
        'id': 'post-case-definitions',
        'url': '/case_definitions/',
        'method': 'POST',
        'response_message': 'You do not have permission to create a case definition.'
    }, {
        'id': 'get-case-definitions',
        'url': '/case_definitions/',
        'method': 'GET',
        'response_message': 'You do not have permission to read case definitions.'
    }, {
        'id': 'get-case-definition',
        'url': '/case_definitions/99',
        'method': 'GET',
        'response_message': 'You do not have permission to read case definitions.'
    }
]

without_permission_test_cases_ids = [case['id'] for case in without_permission_test_cases]


@pytest.mark.parametrize('test_case', without_permission_test_cases, ids=without_permission_test_cases_ids)
def test_case_definitions_fails_without_permission(test_client, test_db, test_case):
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


def test_delete_case_definition(test_client, test_db):
    access_token = get_access_token(test_client)
    headers = {'Content-Type': 'application/json', 'Authorization': f"Bearer {access_token}"}

    # Setup DB

    survey = {
        'name': 'Test Survey',
        'structure': {
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
    }

    response = test_client.post(
        f'/surveys/',
        data=json.dumps(survey),
        headers=headers
    )

    survey_response_structure = {
        "structure": {"question1": "bb"}, "status_id": 1
    }

    survey_id = response.json['id']

    response = test_client.post(
        f"/surveys/{survey_id}/responses",
        data=json.dumps(survey_response_structure),
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
        data=json.dumps(case_definition),
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
        data=json.dumps(case),
        headers={'Content-Type': 'application/json', 'Authorization': f"Bearer {access_token}"}
    )

    case_id = response.json['id']

    response = test_client.delete(
        f'/case_definitions/{case_defn_id}',
        headers={'Content-Type': 'application/json', 'Authorization': f"Bearer {access_token}"}
    )
    assert response.status_code == 200

    response = test_client.get(
        f'/case_definitions/{case_defn_id}',
        headers={'Content-Type': 'application/json', 'Authorization': f"Bearer {access_token}"}
    )
    assert response.status_code == 404

    response = test_client.get(
        f'/cases/{case_id}',
        headers={'Content-Type': 'application/json', 'Authorization': f"Bearer {access_token}"}
    )
    assert response.status_code == 404

    response = test_client.get(
        f'/surveys/{survey_id}/responses/{survey_response_id}',
        headers={'Content-Type': 'application/json', 'Authorization': f"Bearer {access_token}"}
    )
    assert response.status_code == 404


def test_add_doc_to_case_defn(test_client, test_db):
    case_definition = {
        "name": "test_name",
        "key": "TCD1",
        "description": "test_desc",
        "surveys": [],
        "documents": []
    }

    access_token = get_access_token(test_client)
    headers = {'Content-Type': 'application/json', 'Authorization': f"Bearer {access_token}"}

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
    assert resp.json['documents'] == []

    case_defn = resp.json
    doc = {
        "name": "Birth Certificate",
        "description": "blash blah",
        "is_required": True
    }

    case_defn['documents'].append(doc)

    resp = test_client.put(
        f'/case_definitions/{case_defn_id}',
        data=json.dumps(case_defn),
        headers=headers
    )
    assert resp.status_code == 200

    resp = test_client.get(
        f'/case_definitions/{case_defn_id}',
        headers=headers
    )
    assert resp.status_code == 200
    assert resp.json['documents'][0]['name'] == 'Birth Certificate'


def test_remove_doc_from_case_defn(test_client, test_db):
    case_definition = {
        "name": "test_name",
        "key": "TCD1",
        "description": "test_desc",
        "surveys": [],
        "documents": [{
            "name": "Birth Certificate",
            "description": "blash blah",
            "is_required": True
        }]
    }

    access_token = get_access_token(test_client)
    headers = {'Content-Type': 'application/json', 'Authorization': f"Bearer {access_token}"}

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
    assert resp.json['documents'][0]['name'] == 'Birth Certificate'

    case_defn = resp.json
    case_defn['documents'] = []

    resp = test_client.put(
        f'/case_definitions/{case_defn_id}',
        data=json.dumps(case_defn),
        headers=headers
    )
    assert resp.status_code == 200

    resp = test_client.get(
        f'/case_definitions/{case_defn_id}',
        headers=headers
    )
    assert resp.status_code == 200
    assert resp.json['documents'] == []


def test_add_survey_to_case_defn(test_client, test_db):
    case_definition = {
        "name": "test_name",
        "key": "TCD1",
        "description": "test_desc",
        "surveys": [],
        "documents": []
    }

    survey = {'name': 'test survey', 'structure': {}}

    access_token = get_access_token(test_client)
    headers = {'Content-Type': 'application/json', 'Authorization': f"Bearer {access_token}"}

    resp = test_client.post(
        "/surveys/", data=json.dumps(survey),
        headers=headers
    )
    assert resp.status_code == 200

    survey_id = resp.json['id']

    resp = test_client.post(
        "/case_definitions/",
        data=json.dumps(case_definition),
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

    case_defn = resp.json
    case_defn['surveys'] = [1]

    resp = test_client.put(
        f'/case_definitions/{case_defn_id}',
        data=json.dumps(case_defn),
        headers=headers
    )
    assert resp.status_code == 200

    resp = test_client.get(
        f'/case_definitions/{case_defn_id}',
        headers=headers
    )
    assert resp.status_code == 200
    assert resp.json['surveys'][0]['id'] == survey_id


def test_remove_survey_from_case_defn(test_client, test_db):
    case_definition = {
        "name": "test_name",
        "key": "TCD1",
        "description": "test_desc",
        "surveys": [1],
        "documents": []
    }

    survey = {'name': 'test survey', 'structure': {}}

    access_token = get_access_token(test_client)
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
    assert resp.json['surveys'][0]['id'] == survey_id

    case_defn = resp.json
    case_defn['surveys'] = []

    resp = test_client.put(
        f'/case_definitions/{case_defn_id}',
        data=json.dumps(case_defn),
        headers=headers
    )
    assert resp.status_code == 200

    resp = test_client.get(
        f'/case_definitions/{case_defn_id}',
        headers=headers
    )
    assert resp.status_code == 200
    assert resp.json['surveys'] == []


def test_add_unknown_survey_to_case_defn(test_client, test_db):
    case_definition = {
        "name": "test_name",
        "key": "TCD1",
        "description": "test_desc",
        "surveys": [],
        "documents": []
    }

    access_token = get_access_token(test_client)
    headers = {'Content-Type': 'application/json', 'Authorization': f"Bearer {access_token}"}

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

    case_defn = resp.json
    case_defn['surveys'] = [1]

    resp = test_client.put(
        f'/case_definitions/{case_defn_id}',
        data=json.dumps(case_defn),
        headers=headers
    )
    assert resp.status_code == 400

    resp = test_client.get(
        f'/case_definitions/{case_defn_id}',
        headers=headers
    )
    assert resp.status_code == 200
    assert resp.json['surveys'] == []


def test_update_case_defn_docs_preserves_files(test_client, test_db):
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
            }
        ]
    }

    resp = test_client.post(
        '/case_definitions/',
        data=json.dumps(case_definition),
        headers=headers
    )

    assert resp.status_code == 200

    case_defn = resp.json
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

    case_defn['documents'][0]['name'] = 'test_val'

    resp = test_client.put(
        f'/case_definitions/{case_defn_id}',
        data=json.dumps(case_defn),
        headers=headers
    )
    assert resp.status_code == 200

    resp = test_client.get(
        f'/cases/{case_id}',
        headers=headers
    )
    assert resp.status_code == 200

    assert resp.json['documents'][0]['document_id'] == 1
    assert resp.json['documents'][0]['name'] == 'test_val'
    assert resp.json['documents'][0]['id'] == 1
