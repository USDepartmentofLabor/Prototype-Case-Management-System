import json
import pytest
from flask_jwt_extended import create_access_token
from app import models
from ..test_helpers import get_access_token


def test_post_valid_activity_definition(test_client, test_db, basic_case_definition, basic_test_survey):
    count_before = test_db.session.query(models.ActivityDefinition).count()

    activity_definition = {
        "name": "Test Activity Definition",
        "description": "Test Activity Definition Description",
        "case_definition_id": basic_case_definition.id,
        "surveys": [basic_test_survey.id],
        "documents": [{
            "name": "Activity Document 1",
            "description": "Activity Document 1 Description",
            "is_required": True
        }, {
            "name": "Activity Document 2",
            "description": "Activity Document 2 Description",
            "is_required": False
        }],
        "custom_fields": [
            {
                "name": "Household Short Text",
                "field_type": "text",
                "selections": None,
                "validation_rules": None,
                "custom_section_id": None,
                "sort_order": 1,
                "help_text": "This is for short answers"
            },
            {
                "name": "Household Long Text",
                "field_type": "textarea",
                "selections": None,
                "validation_rules": None,
                "custom_section_id": None,
                "help_text": "This is for longer answers",
                "sort_order": 2
            },
            {
                "name": "Household Check Box",
                "field_type": "check_box",
                "selections": [
                    {
                        "id": 1,
                        "value": "Household Check Box Option A"
                    },
                    {
                        "id": 2,
                        "value": "Household Check Box Option B"
                    },
                    {
                        "id": 3,
                        "value": "Household Check Box Option C"
                    }
                ],
                "validation_rules": None,
                "custom_section_id": None,
                "help_text": "This allows for multiple selection of choices among many",
                "sort_order": 3
            },
            {
                "name": "Household Radio Button",
                "field_type": "radio_button",
                "selections": [
                    {
                        "id": 1,
                        "value": "Household Radio Option A"
                    },
                    {
                        "id": 2,
                        "value": "Household Radio Option B"
                    },
                    {
                        "id": 3,
                        "value": "Household Radio Option C"
                    }
                ],
                "validation_rules": None,
                "custom_section_id": None,
                "help_text": "This is for a single selection among many",
                "sort_order": 4
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
                "sort_order": 5
            },
            {
                "name": "Household Numeric Field",
                "field_type": "number",
                "selections": None,
                "validation_rules": None,
                "custom_section_id": None,
                "help_text": "This is for numbers",
                "sort_order": 6
            },
            {
                "name": "Household Date Field",
                "field_type": "date",
                "selections": None,
                "validation_rules": None,
                "custom_section_id": None,
                "help_text": "This is for a date",
                "sort_order": 7
            },
            {
                "name": "Household Rank List",
                "field_type": "rank_list",
                "selections": [
                    {
                        "id": 1,
                        "value": "Household Rank Option A"
                    },
                    {
                        "id": 2,
                        "value": "Household Rank Option B"
                    },
                    {
                        "id": 3,
                        "value": "Household Rank Option C"
                    }
                ],
                "validation_rules": None,
                "custom_section_id": None,
                "help_text": "This is for ranking a list of options",
                "sort_order": 8
            }
        ]
    }

    access_token = get_access_token(test_client)
    response = test_client.post('/activity_definitions', data=json.dumps(activity_definition),
                                headers={'Content-Type': 'application/json', 'Authorization': f"Bearer {access_token}"})

    assert (count_before + 1) == test_db.session.query(models.ActivityDefinition).count()
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['id']
    assert json_data['name'] == activity_definition['name']
    assert len(json_data['surveys']) == 1
    assert len(json_data['documents']) == 2
    assert len(json_data['custom_fields']) == 8
    ad = models.ActivityDefinition.query.get(json_data['id'])
    assert ad
    assert len(ad.surveys.all()) == 1
    assert len(ad.documents) == 2
