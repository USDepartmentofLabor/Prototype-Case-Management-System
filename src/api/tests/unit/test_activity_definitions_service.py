from unittest.mock import MagicMock, patch
import pytest
from flask import g
from werkzeug.exceptions import NotFound
from app.activity_definitions.activity_definitions_service import ActivityDefinitionsService
from app import models
from ..factories import UserFactory


def test_can_init():
    session = MagicMock()
    service = ActivityDefinitionsService(json_args={'foo': 'bar'}, _session=session)
    assert service.session is session
    assert service.json_args['foo'] == 'bar'


def test_post_fails_with_duplicate_name(test_app, basic_case_definition):
    activity_definition = {
        "name": "Test Case Definition",
        "case_definition_id": basic_case_definition.id
    }
    session = MagicMock()
    service = ActivityDefinitionsService(json_args=activity_definition, _session=session)
    g.request_user = UserFactory.build()

    with patch.object(service, '_is_name_unique') as _is_name_unique:
        _is_name_unique.return_value = False
        response = service.post()

    response_json = response[0].get_json()
    assert response[1] == 400
    assert response_json['message'] == "Activity Definition names must be unique."


def test_post_fails_with_invalid_case_definition_id(test_app):
    activity_definition = {
        "name": "Test Activity Definition",
        "case_definition_id": 99
    }
    session = MagicMock()
    service = ActivityDefinitionsService(json_args=activity_definition, _session=session)
    g.request_user = UserFactory.build()

    with patch.object(models.CaseDefinition.query, 'get_or_404') as get_or_404:
        get_or_404.side_effect = NotFound
        with pytest.raises(NotFound):
            service.post()


def test_post_valid_activity_definition(test_app, basic_case_definition):
    activity_definition = {
        "name": "Test Activity Definition",
        "case_definition_id": basic_case_definition.id
    }

    session = MagicMock()
    service = ActivityDefinitionsService(json_args=activity_definition, _session=session)
    g.request_user = UserFactory.build()

    response = service.post()
    assert response is not None
    assert isinstance(response, models.ActivityDefinition)


post_without_required_fields_cases = [
    {
        'id': 'name-missing',
        'data': {},
        'response_status': 400,
        'response_message': "A name is required for an activity definition."
    }, {
        'id': 'name-empty',
        'data': {'name': ''},
        'response_status': 400,
        'response_message': "A name is required for an activity definition."
    }, {
        'id': 'name-none',
        'data': {'name': None},
        'response_status': 400,
        'response_message': "A name is required for an activity definition."
    }, {
        'id': 'custom_fields-not-list',
        'data': {'name': 'test name', 'custom_fields': ''},
        'response_status': 400,
        'response_message': "The custom_fields property must be a list."
    }, {
        'id': 'custom_fields-name-missing',
        'data': {'name': 'test name', 'custom_fields': [{}]},
        'response_status': 400,
        'response_message': "A name is required for each custom field."
    }, {
        'id': 'custom_fields-field_type-missing',
        'data': {'name': 'test name', 'custom_fields': [{'name': 'cf name'}]},
        'response_status': 400,
        'response_message': "A field type is required for each custom field."
    }, {
        'id': 'custom_fields-selection-missing-id',
        'data': {'name': 'test name', 'custom_fields': [{'name': 'cf name', 'field_type': 'text', 'selections': [{}]}]},
        'response_status': 400,
        'response_message': "An id property is required for custom field selections."
    }, {
        'id': 'custom_fields-invalid-field_type',
        'data': {'name': 'test name', 'custom_fields': [{'name': 'cf name', 'field_type': 'BAD_TYPE'}]},
        'response_status': 400,
        'response_message': "The custom field refers to an invalid field type."
    }, {
        'id': 'custom_fields-duplicate-ids',
        'data': {'name': 'test name', 'custom_fields': [{'id': '1', 'name': 'cf name 1', 'field_type': 'text'},
                                                        {'id': '2', 'name': 'cf name 2', 'field_type': 'text'}]},
        'response_status': 400,
        'response_message': "Custom field IDs must be unique."
    }
]

post_without_required_fields_cases_ids = \
    [case['id'] for case in post_without_required_fields_cases]


@pytest.mark.parametrize('test_case', post_without_required_fields_cases,
                         ids=post_without_required_fields_cases_ids)
def test_post_fails_with_bad_data(test_app, test_case, basic_case_definition):
    session = MagicMock()
    test_case['data']['case_definition_id'] = basic_case_definition.id
    service = ActivityDefinitionsService(json_args=test_case['data'], _session=session)
    g.request_user = UserFactory.build()

    response = service.post()

    response_json = response[0].get_json()
    assert response[1] == test_case['response_status']
    if test_case['response_message']:
        assert response_json['message'] == test_case['response_message']
