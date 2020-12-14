from unittest.mock import MagicMock, patch
import pytest
from flask import g
from app.case_definitions.case_definitions_service import CaseDefinitionsService
from ..factories import UserFactory


def test_can_init():
    session = MagicMock()
    service = CaseDefinitionsService(json_args={'foo': 'bar'}, _session=session)
    assert service.session is session
    assert service.json_args['foo'] == 'bar'


def test_post_fails_with_unknown_survey(test_app):
    case_definition = {
        "name": "Test Case Definition 6",
        "key": "TCD1",
        "surveys": [1, 2, 3]
    }
    session = MagicMock()
    service = CaseDefinitionsService(json_args=case_definition, _session=session)
    g.request_user = UserFactory.build()

    response = service.post()

    response_json = response[0].get_json()
    assert response[1] == 400
    assert response_json['message'] == "Invalid survey ID submitted."


def test_post_case_fails_with_duplicate_name(test_app):
    case_definition = {
        "key": "TCD1",
        "name": "Test Case Definition"
    }
    session = MagicMock()
    service = CaseDefinitionsService(json_args=case_definition, _session=session)
    g.request_user = UserFactory.build()

    with patch.object(service, '_is_name_unique') as _is_name_unique:
        _is_name_unique.return_value = False
        response = service.post()

    response_json = response[0].get_json()
    assert response[1] == 400
    assert response_json['message'] == "Case Definition names must be unique."


def test_post_case_fails_with_duplicate_key(test_app):
    case_definition = {
        "key": "TCD1",
        "name": "Test Case Definition"
    }
    session = MagicMock()
    service = CaseDefinitionsService(json_args=case_definition, _session=session)
    g.request_user = UserFactory.build()

    with patch.object(service, '_is_key_unique') as _is_key_unique:
        _is_key_unique.return_value = False
        response = service.post()

    response_json = response[0].get_json()
    assert response[1] == 400
    assert response_json['message'] == "Case Definition keys must be unique."


post_case_definition_without_required_fields_cases = [
    {
        'id': 'name-missing',
        'data': {'key': 'TCD'},
        'response_status': 400,
        'response_message': "A name is required for a case definition."
    }, {
        'id': 'name-empty',
        'data': {'key': 'TCD', 'name': ''},
        'response_status': 400,
        'response_message': "A name is required for a case definition."
    }, {
        'id': 'name-none',
        'data': {'key': 'TCD', 'name': None},
        'response_status': 400,
        'response_message': "A name is required for a case definition."
    }, {
        'id': 'key-missing',
        'data': {'name': 'Test Case Definition'},
        'response_status': 400,
        'response_message': "A key is required for a case definition."
    }, {
        'id': 'key-empty',
        'data': {'key': '', 'name': 'Test Case Definition'},
        'response_status': 400,
        'response_message': "A key is required for a case definition."
    }, {
        'id': 'key-none',
        'data': {'key': None, 'name': 'Test Case Definition'},
        'response_status': 400,
        'response_message': "A key is required for a case definition."
    }, {
        'id': 'document-name-missing',
        'data': {
            "key": "TCD6",
            "name": "Test Case Definition 6",
            "documents": [{
                "description": "blash blah",
                "is_required": True
            }]
        },
        'response_status': 400,
        'response_message': "A name is required for each case definition document."
    }, {
        'id': 'custom-field-name-missing',
        'data': {
            "key": "TCD6",
            "name": "Test Case Definition 6",
            "custom_fields": [{
                "field_type": "textarea",
                "selections": None,
                "validation_rules": None,
                "custom_section_id": None,
                "help_text": "This is for longer answers",
                "sort_order": 1
            }]
        },
        'response_status': 400,
        'response_message': "A name is required for each custom field."
    }, {
        'id': 'custom-field-field-type-missing',
        'data': {
            "key": "TCD6",
            "name": "Test Case Definition 6",
            "custom_fields": [{
                "name": "Household Long Text",
                "selections": None,
                "validation_rules": None,
                "custom_section_id": None,
                "help_text": "This is for longer answers",
                "sort_order": 1
            }]
        },
        'response_status': 400,
        'response_message': "A field type is required for each custom field."
    }, {
        'id': 'custom-field-selections-id-missing',
        'data': {
            "key": "TCD6",
            "name": "Test Case Definition 6",
            "custom_fields": [{
                "name": "Household Selection Field",
                "field_type": "select",
                "selections": [
                    {
                        "value": "Household Selection Option A"
                    }
                ],
                "validation_rules": None,
                "custom_section_id": None,
                "help_text": "This is for a single selection among many",
                "sort_order": 2
            }]
        },
        'response_status': 400,
        'response_message': "An id property is required for custom field selections."
    }
]

post_case_definition_without_required_fields_cases_ids = \
    [case['id'] for case in post_case_definition_without_required_fields_cases]


@pytest.mark.parametrize('test_case', post_case_definition_without_required_fields_cases,
                         ids=post_case_definition_without_required_fields_cases_ids)
def test_post_case_definition_without_required_fields(test_app, test_case):
    session = MagicMock()
    service = CaseDefinitionsService(json_args=test_case['data'], _session=session)
    g.request_user = UserFactory.build()

    response = service.post()

    response_json = response[0].get_json()
    assert response[1] == test_case['response_status']
    assert response_json['message'] == test_case['response_message']


post_custom_field_with_invalid_data_cases = [
    {
        'id': 'custom-field-name-missing',
        'data': {
            "field_type": "textarea",
            "selections": None,
            "validation_rules": None,
            "custom_section_id": None,
            "help_text": "This is for longer answers",
            "sort_order": 1
        },
        'response_status': 400,
        'response_message': "A name is required for each custom field."
    }, {
        'id': 'custom-field-field-type-missing',
        'data': {
            "name": "Household Long Text",
            "selections": None,
            "validation_rules": None,
            "custom_section_id": None,
            "help_text": "This is for longer answers",
            "sort_order": 1
        },
        'response_status': 400,
        'response_message': "A field type is required for each custom field."
    }, {
        'id': 'custom-field-selections-id-missing',
        'data': {
            "name": "Household Selection Field",
            "field_type": "select",
            "selections": [
                {
                    "value": "Household Selection Option A"
                }
            ],
            "validation_rules": None,
            "custom_section_id": None,
            "help_text": "This is for a single selection among many",
            "sort_order": 2
        },
        'response_status': 400,
        'response_message': "An id property is required for custom field selections."
    }
]

post_custom_field_with_invalid_data_cases_ids = \
    [case['id'] for case in post_custom_field_with_invalid_data_cases]


@pytest.mark.parametrize('test_case', post_custom_field_with_invalid_data_cases,
                         ids=post_custom_field_with_invalid_data_cases_ids)
def test_post_custom_field_with_invalid_data(test_app, test_case):
    session = MagicMock()
    service = CaseDefinitionsService(json_args=test_case['data'], _session=session)
    g.request_user = UserFactory.build()

    response = service.add_custom_field(1)

    response_json = response[0].get_json()
    assert response[1] == test_case['response_status']
    assert response_json['message'] == test_case['response_message']


# TODO: Update this test, need to mock db retrieval of CD
# def test_post_valid_custom_field(test_app):
#     case_definition = CaseDefinitionFactory.build()
#     session = MagicMock()
#     service = CaseDefinitionsService(json_args=case_definition, _session=session)
#     g.request_user = UserFactory.build()
#
#     with patch.object(service, '_get_validated_custom_field') as _get_validated_custom_field:
#         _get_validated_custom_field.return_value = (case_definition, True)
#         response = service.add_custom_field(1)
#
#     assert response[1] == 200

# TODO: Test error unknown CD
# TODO: Test error unknown CF
# TODO: Test validate CF
# TODO: Test only update values if they exist
# TODO: Test update the values to whatever is sent
# TODO: Test accepts valid CF
