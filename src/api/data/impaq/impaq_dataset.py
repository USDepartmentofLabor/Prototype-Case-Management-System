dataset = {
    'roles': [
        {
            'id': 1,
            'name': "Admin",
            'permissions': ['ADMIN'],
            'default': False,
            'sys_id': None,
        },
        {
            'id': 2,
            'name': "Project Manager",
            'permissions': ['CONFIGURE_SYSTEM', 'READ_ACCOUNT', 'UPDATE_ACCOUNT', 'CREATE_SURVEY', 'READ_SURVEY',
                            'UPDATE_SURVEY', 'DELETE_SURVEY', 'SUBMIT_SURVEY', 'ARCHIVE_SURVEY', 'READ_REPORT',
                            'CREATE_CASE_DEFINITION', 'READ_CASE_DEFINITION', 'UPDATE_CASE_DEFINITION',
                            'DELETE_CASE_DEFINITION', 'CREATE_CASE', 'UPDATE_CASE', 'READ_CASE', 'DELETE_CASE',
                            'CREATE_PROJECT', 'READ_PROJECT', 'UPDATE_PROJECT', 'DELETE_PROJECT',
                            'CREATE_ACTIVITY_DEFINITION', 'READ_ACTIVITY_DEFINITION', 'UPDATE_ACTIVITY_DEFINITION',
                            'DELETE_ACTIVITY_DEFINITION', 'CREATE_ACTIVITY', 'READ_ACTIVITY', 'UPDATE_ACTIVITY',
                            'DELETE_ACTIVITY', 'ASSIGNABLE_TO_CASE', 'ASSIGN_TO_CASE'],
            'default': False,
            'sys_id': None,
        },
        {
            'id': 3,
            'name': "Labor Inspector",
            'permissions': ['READ_ACCOUNT', 'UPDATE_ACCOUNT', 'READ_SURVEY', 'SUBMIT_SURVEY', 'UPDATE_SURVEY',
                            'CREATE_CASE', 'UPDATE_CASE', 'READ_CASE', 'READ_PROJECT', 'CREATE_ACTIVITY',
                            'READ_ACTIVITY', 'UPDATE_ACTIVITY', 'ASSIGNABLE_TO_CASE'],
            'default': True,
            'sys_id': None,
        }
    ],
    'superadmin': {
        'sys_id': None,
        'email': "ilabtoolkit@gmail.com",
        'name': "admin",
        'username': "admin",
        'password': "Boo'y9thai6Eiy",
        'role': 1
    },
    "users": [
        {
            "email": "jclements@ascend.network",
            "name": "John Clements",
            "username": "jclements",
            "password": "",
            "role": 1
        },
        {
            "email": "nschoeb@ascend.network",
            "name": "Nick Schoeb",
            "username": "nschoeb",
            "password": "",
            "role": 1
        },
        {
            "email": "tstone@ascend.network",
            "name": "Thomas Stone",
            "username": "tstone",
            "password": "",
            "role": 1
        }
    ],
    "survey_response_statuses": [
        {"id": 1, "name": "Draft", "default": False},
        {"id": 2, "name": "Submitted", "default": True}
    ],
    "case_statuses": [
        {"id": 1, "name": "Initiated", "default": True, "is_final": False, "color": "#0000FF"},
        {"id": 2, "name": "Scheduled", "default": False, "is_final": False, "color": "#FFFF00"},
        {"id": 3, "name": "Delayed", "default": False, "is_final": False, "color": "#FF0000"},
        {"id": 4, "name": "Compliant", "default": False, "is_final": True, "color": "#00FF00"},
        {"id": 5, "name": "Non-Compliant", "default": False, "is_final": False, "color": "#AAAAAA"},
    ],
    "project_info": {
        "name": "ADVANCE Brazil",
        "title": "Brazilian ADVANCE Project Eliminating Exploitive Child Labor through Education and Livelihoods",
        "organization": "IMPAQ International",
        "agreement_number": "IL-23979-13-75-K",
        "start_date": "2018-01-01",
        "end_date": "2022-12-31",
        "funding_amount": 10000000,
        "location": "Brasília, Brazil"
    },
    'surveys': [
        {
            'sys_id': None,
            'name': "Occupational Safety and Health Issues",
            'file': "occupational_safety_and_health_issues.json"
        },
        {
            'sys_id': None,
            'name': "Wage and Hour Issues",
            'file': "wage_and_hour_issues.json"
        },
        {
            'sys_id': None,
            'name': "COVID-19 Health Checklist",
            'file': "COVID-19_health_checklist.json"
        },
        {
            'sys_id': None,
            'name': "Workplace Accidents",
            'file': "workplace_accidents.json"
        },
        {
            'sys_id': None,
            'name': "Inspector Conclusions",
            'file': "inspector_conclusions.json"
        }
    ],
    'case_definitions': [{
        'sys_id': None,
        'key': "OSH",
        'name': "Occupational Safety and Health",
        'description': "Case definition for occupational safety and health cases",
        'documents': [{'name': "Site Picture", 'description': "Picture of worksite", 'is_required': True}],
        'custom_fields': [
            {
                "name": "Inspection Type",
                "field_type": "select",
                "selections": [
                    {
                        "id": 1,
                        "value": "Scheduled"
                    },
                    {
                        "id": 3,
                        "value": "Reactive"
                    }
                ],
                "validation_rules": None,
                "custom_section_id": None,
                "help_text": "Please select an Inspection Type",
                "sort_order": 1
            },
            {
                "name": "Business Name",
                "field_type": "text",
                "selections": None,
                "validation_rules": None,
                "custom_section_id": None,
                "help_text": "Please enter a Business Name",
                "sort_order": 2
            },
            {
                "name": "Business Sector",
                "field_type": "select",
                "selections": [
                    {
                        "id": 1,
                        "value": "Industrial"
                    },
                    {
                        "id": 2,
                        "value": "Agriculture"
                    },
                    {
                        "id": 3,
                        "value": "Services"
                    },
                    {
                        "id": 4,
                        "value": "Manufacturing"
                    }
                ],
                "validation_rules": None,
                "custom_section_id": None,
                "help_text": "Please select a Business Sector",
                "sort_order": 3
            },
            {
                "name": "Region",
                "field_type": "select",
                "selections": [
                    {
                        "id": 1,
                        "value": "Region 1"
                    },
                    {
                        "id": 2,
                        "value": "Region 2"
                    },
                    {
                        "id": 3,
                        "value": "Region 3"
                    },
                    {
                        "id": 4,
                        "value": "Region 4"
                    },
                    {
                        "id": 5,
                        "value": "Region 5"
                    },
                    {
                        "id": 6,
                        "value": "Region 6"
                    },
                    {
                        "id": 7,
                        "value": "Region 7"
                    }
                ],
                "validation_rules": None,
                "custom_section_id": None,
                "help_text": "Please select a Region",
                "sort_order": 4
            },
            {
                "name": "Address",
                "field_type": "textarea",
                "selections": None,
                "validation_rules": None,
                "custom_section_id": None,
                "help_text": "Please enter a street address",
                "sort_order": 5
            },
            {
                "name": "City",
                "field_type": "text",
                "selections": None,
                "validation_rules": None,
                "custom_section_id": None,
                "help_text": "Please enter a City",
                "sort_order": 6
            },
            {
                "name": "Location (GPS) Latitude",
                "field_type": "number",
                "selections": None,
                "validation_rules": None,
                "custom_section_id": None,
                "help_text": "Please enter the latitude",
                "sort_order": 7
            },
            {
                "name": "Location (GPS) Longitude",
                "field_type": "number",
                "selections": None,
                "validation_rules": None,
                "custom_section_id": None,
                "help_text": "Please enter the longitude",
                "sort_order": 8
            },
            {
                "name": "Date Scheduled",
                "field_type": "date",
                "selections": None,
                "validation_rules": None,
                "custom_section_id": None,
                "help_text": "Please enter the date the inspection is scheduled for",
                "sort_order": 9
            }
        ],
        'activity_definitions': [{
            'sys_id': None,
            'name': "Scheduled Inspection",
            'description': "Scheduled Inspection Activity",
            'surveys': ["Occupational Safety and Health Issues", "Inspector Conclusions"]
        }, {
            'sys_id': None,
            'name': "Re-Inspection",
            'description': "Re-Inspection Activity",
            'surveys': ["Occupational Safety and Health Issues", "Inspector Conclusions"]
        }]
    }, {
        'sys_id': None,
        'key': "WH",
        'name': "Wage and Hour",
        'description': "Case definition for wage and hour cases",
        'documents': [],
        'custom_fields': [
            {
                "name": "Inspection Type",
                "field_type": "select",
                "selections": [
                    {
                        "id": 1,
                        "value": "Scheduled"
                    },
                    {
                        "id": 3,
                        "value": "Reactive"
                    }
                ],
                "validation_rules": None,
                "custom_section_id": None,
                "help_text": "Please select an Inspection Type",
                "sort_order": 1
            },
            {
                "name": "Business Name",
                "field_type": "text",
                "selections": None,
                "validation_rules": None,
                "custom_section_id": None,
                "help_text": "Please enter a Business Name",
                "sort_order": 2
            },
            {
                "name": "Business Sector",
                "field_type": "select",
                "selections": [
                    {
                        "id": 1,
                        "value": "Industrial"
                    },
                    {
                        "id": 2,
                        "value": "Agriculture"
                    },
                    {
                        "id": 3,
                        "value": "Services"
                    },
                    {
                        "id": 4,
                        "value": "Manufacturing"
                    }
                ],
                "validation_rules": None,
                "custom_section_id": None,
                "help_text": "Please select a Business Sector",
                "sort_order": 3
            },
            {
                "name": "Region",
                "field_type": "select",
                "selections": [
                    {
                        "id": 1,
                        "value": "Region 1"
                    },
                    {
                        "id": 2,
                        "value": "Region 2"
                    },
                    {
                        "id": 3,
                        "value": "Region 3"
                    },
                    {
                        "id": 4,
                        "value": "Region 4"
                    },
                    {
                        "id": 5,
                        "value": "Region 5"
                    },
                    {
                        "id": 6,
                        "value": "Region 6"
                    },
                    {
                        "id": 7,
                        "value": "Region 7"
                    }
                ],
                "validation_rules": None,
                "custom_section_id": None,
                "help_text": "Please select a Region",
                "sort_order": 4
            },
            {
                "name": "Address",
                "field_type": "textarea",
                "selections": None,
                "validation_rules": None,
                "custom_section_id": None,
                "help_text": "Please enter a street address",
                "sort_order": 5
            },
            {
                "name": "City",
                "field_type": "text",
                "selections": None,
                "validation_rules": None,
                "custom_section_id": None,
                "help_text": "Please enter a City",
                "sort_order": 6
            },
            {
                "name": "Location (GPS) Latitude",
                "field_type": "number",
                "selections": None,
                "validation_rules": None,
                "custom_section_id": None,
                "help_text": "Please enter the latitude",
                "sort_order": 7
            },
            {
                "name": "Location (GPS) Longitude",
                "field_type": "number",
                "selections": None,
                "validation_rules": None,
                "custom_section_id": None,
                "help_text": "Please enter the longitude",
                "sort_order": 8
            },
            {
                "name": "Date Scheduled",
                "field_type": "date",
                "selections": None,
                "validation_rules": None,
                "custom_section_id": None,
                "help_text": "Please enter the date the inspection is scheduled for",
                "sort_order": 9
            }
        ],
        'activity_definitions': [{
            'sys_id': None,
            'name': "Scheduled Inspection",
            'description': "Scheduled Inspection Activity",
            'surveys': ["Wage and Hour Issues", "Inspector Conclusions"]
        }, {
            'sys_id': None,
            'name': "Re-Inspection",
            'description': "Re-Inspection Activity",
            'surveys': ["Wage and Hour Issues", "Inspector Conclusions"]
        }]
    }, {
        'sys_id': None,
        'key': "CHC",
        'name': "COVID-19 Health Checklist",
        'description': "Case definition for COVID-19 Health Checklist cases",
        'documents': [],
        'custom_fields': [
            {
                "name": "Inspection Type",
                "field_type": "select",
                "selections": [
                    {
                        "id": 1,
                        "value": "Scheduled"
                    },
                    {
                        "id": 3,
                        "value": "Reactive"
                    }
                ],
                "validation_rules": None,
                "custom_section_id": None,
                "help_text": "Please select an Inspection Type",
                "sort_order": 1
            },
            {
                "name": "Business Name",
                "field_type": "text",
                "selections": None,
                "validation_rules": None,
                "custom_section_id": None,
                "help_text": "Please enter a Business Name",
                "sort_order": 2
            },
            {
                "name": "Business Sector",
                "field_type": "select",
                "selections": [
                    {
                        "id": 1,
                        "value": "Industrial"
                    },
                    {
                        "id": 2,
                        "value": "Agriculture"
                    },
                    {
                        "id": 3,
                        "value": "Services"
                    },
                    {
                        "id": 4,
                        "value": "Manufacturing"
                    }
                ],
                "validation_rules": None,
                "custom_section_id": None,
                "help_text": "Please select a Business Sector",
                "sort_order": 3
            },
            {
                "name": "Region",
                "field_type": "select",
                "selections": [
                    {
                        "id": 1,
                        "value": "Region 1"
                    },
                    {
                        "id": 2,
                        "value": "Region 2"
                    },
                    {
                        "id": 3,
                        "value": "Region 3"
                    },
                    {
                        "id": 4,
                        "value": "Region 4"
                    },
                    {
                        "id": 5,
                        "value": "Region 5"
                    },
                    {
                        "id": 6,
                        "value": "Region 6"
                    },
                    {
                        "id": 7,
                        "value": "Region 7"
                    }
                ],
                "validation_rules": None,
                "custom_section_id": None,
                "help_text": "Please select a Region",
                "sort_order": 4
            },
            {
                "name": "Address",
                "field_type": "textarea",
                "selections": None,
                "validation_rules": None,
                "custom_section_id": None,
                "help_text": "Please enter a street address",
                "sort_order": 5
            },
            {
                "name": "City",
                "field_type": "text",
                "selections": None,
                "validation_rules": None,
                "custom_section_id": None,
                "help_text": "Please enter a City",
                "sort_order": 6
            },
            {
                "name": "Location (GPS) Latitude",
                "field_type": "number",
                "selections": None,
                "validation_rules": None,
                "custom_section_id": None,
                "help_text": "Please enter the latitude",
                "sort_order": 7
            },
            {
                "name": "Location (GPS) Longitude",
                "field_type": "number",
                "selections": None,
                "validation_rules": None,
                "custom_section_id": None,
                "help_text": "Please enter the longitude",
                "sort_order": 8
            },
            {
                "name": "Date Scheduled",
                "field_type": "date",
                "selections": None,
                "validation_rules": None,
                "custom_section_id": None,
                "help_text": "Please enter the date the inspection is scheduled for",
                "sort_order": 9
            }
        ],
        'activity_definitions': [{
            'sys_id': None,
            'name': "Scheduled Inspection",
            'description': "Scheduled Inspection Activity",
            'surveys': ["COVID-19 Health Checklist"]
        }, {
            'sys_id': None,
            'name': "Re-Inspection",
            'description': "Re-Inspection Activity",
            'surveys': ["COVID-19 Health Checklist"]
        }]
    }, {
        'sys_id': None,
        'key': "WA",
        'name': "Workplace Accident",
        'description': "Case definition for workplace accident cases",
        'documents': [],
        'custom_fields': [
            {
                "name": "Inspection Type",
                "field_type": "select",
                "selections": [
                    {
                        "id": 1,
                        "value": "Scheduled"
                    },
                    {
                        "id": 3,
                        "value": "Reactive"
                    }
                ],
                "validation_rules": None,
                "custom_section_id": None,
                "help_text": "Please select an Inspection Type",
                "sort_order": 1
            },
            {
                "name": "Business Name",
                "field_type": "text",
                "selections": None,
                "validation_rules": None,
                "custom_section_id": None,
                "help_text": "Please enter a Business Name",
                "sort_order": 2
            },
            {
                "name": "Business Sector",
                "field_type": "select",
                "selections": [
                    {
                        "id": 1,
                        "value": "Industrial"
                    },
                    {
                        "id": 2,
                        "value": "Agriculture"
                    },
                    {
                        "id": 3,
                        "value": "Services"
                    },
                    {
                        "id": 4,
                        "value": "Manufacturing"
                    }
                ],
                "validation_rules": None,
                "custom_section_id": None,
                "help_text": "Please select a Business Sector",
                "sort_order": 3
            },
            {
                "name": "Region",
                "field_type": "select",
                "selections": [
                    {
                        "id": 1,
                        "value": "Region 1"
                    },
                    {
                        "id": 2,
                        "value": "Region 2"
                    },
                    {
                        "id": 3,
                        "value": "Region 3"
                    },
                    {
                        "id": 4,
                        "value": "Region 4"
                    },
                    {
                        "id": 5,
                        "value": "Region 5"
                    },
                    {
                        "id": 6,
                        "value": "Region 6"
                    },
                    {
                        "id": 7,
                        "value": "Region 7"
                    }
                ],
                "validation_rules": None,
                "custom_section_id": None,
                "help_text": "Please select a Region",
                "sort_order": 4
            },
            {
                "name": "Address",
                "field_type": "textarea",
                "selections": None,
                "validation_rules": None,
                "custom_section_id": None,
                "help_text": "Please enter a street address",
                "sort_order": 5
            },
            {
                "name": "City",
                "field_type": "text",
                "selections": None,
                "validation_rules": None,
                "custom_section_id": None,
                "help_text": "Please enter a City",
                "sort_order": 6
            },
            {
                "name": "Location (GPS) Latitude",
                "field_type": "number",
                "selections": None,
                "validation_rules": None,
                "custom_section_id": None,
                "help_text": "Please enter the latitude",
                "sort_order": 7
            },
            {
                "name": "Location (GPS) Longitude",
                "field_type": "number",
                "selections": None,
                "validation_rules": None,
                "custom_section_id": None,
                "help_text": "Please enter the longitude",
                "sort_order": 8
            },
            {
                "name": "Date Scheduled",
                "field_type": "date",
                "selections": None,
                "validation_rules": None,
                "custom_section_id": None,
                "help_text": "Please enter the date the inspection is scheduled for",
                "sort_order": 9
            }
        ],
        'activity_definitions': [{
            'sys_id': None,
            'name': "Scheduled Inspection",
            'description': "Scheduled Inspection Activity",
            'surveys': ["Workplace Accidents"]
        }, {
            'sys_id': None,
            'name': "Re-Inspection",
            'description': "Re-Inspection Activity",
            'surveys': ["Workplace Accidents"]
        }]
    }]
}
