import os
import sys
import json
import requests
from app import create_app, db
from app import models
from app.model_schemas import UserSchema
from flask_migrate import Migrate
import click

application = create_app(os.getenv('FLASK_CONFIG') or 'default')
migrate = Migrate(application, db)


@application.shell_context_processor
def make_shell_context():
    return dict(
        db=db,
        User=models.User,
        Role=models.Role,
        Permission=models.Permission,
        UserSchema=UserSchema,
        Survey=models.Survey,
        SurveyResponse=models.SurveyResponse,
        SurveyResponseStatus=models.SurveyResponseStatus,
        CaseDefinition=models.CaseDefinition,
        Case=models.Case,
        CaseStatus=models.CaseStatus,
        Project=models.Project,
        Location=models.Location,
        EPSProperty=models.EPSProperty
    )


def rebuild_db():
    db.drop_all()
    db.create_all()
    db.session.commit()


def seed_the_db():

    application.logger.info('loading admin account')
    admin_role = models.Role.query.filter_by(name='Admin').first()
    users = [
        {'email': 'ilabtoolkit@gmail.com', 'username': 'admin', 'password': 'admin', 'name': 'Admin User',
         'role': admin_role}
    ]
    for user in users:
        if not len(list(models.User.query.filter_by(email=user['email']))):
            new_user = models.User(
                email=user['email'],
                username=user['username'],
                password=user['password'],
                name=user['name'],
                role=user['role']
            )
            db.session.add(new_user)
            db.session.commit()

    application.logger.info('loading system properties')
    eps_property = models.EPSProperty.query.filter_by(property='default_dashboard_id').first()
    if eps_property is None:
        eps_property = models.EPSProperty(property='default_dashboard_id', value=None)
        db.session.add(eps_property)
        db.session.commit()


@application.cli.command()
def drop_db():
    db.drop_all()


@application.cli.command()
def recreate_db():
    rebuild_db()


@application.cli.command()
def seed_db():
    application.logger.info('seed db')
    seed_the_db()

@application.cli.command("load-impaq-dataset")
@click.argument("base_url")
def load_impaq_dataset_command(base_url="http://localhost:5000"):
    from data.impaq.impaq_dataset_loader import IMPAQDatasetLoader
    dataloader = IMPAQDatasetLoader(url=base_url, application=application, db=db)
    dataloader.start_load()

@application.cli.command("load-dev-dataset")
@click.argument("base_url")
def load_dev_dataset(base_url="http://localhost:5000"):
    import random
    import copy
    from faker import Faker
    fake = Faker()

    def get_random_choices(choices):
        return random.sample(choices, random.randint(1, len(choices)))

    def get_unique_name(gen_func, name_list):
        n = gen_func()
        while n in name_list:
            n = gen_func()
        return n

    application.logger.info("start loading the dev dataset")

    application.logger.info("re-created database")
    rebuild_db()

    application.logger.info('dropping reporting tables')
    application.reporting_service.delete_all()

    application.logger.info('loading roles')
    models.Role.insert_roles()

    application.logger.info('loading survey response statuses')
    models.SurveyResponseStatus.insert_survey_response_statuses()

    application.logger.info('loading case statuses')
    models.CaseStatus.insert_case_statuses()

    application.logger.info("seeding database")
    seed_the_db()

    application.logger.info("logging into API")
    try:
        loc = fake.latlng()
        auth_request_headers = {'Content-type': 'application/json'}
        auth_request = requests.post(
            f'{base_url}/auth/login',
            data=json.dumps({"login": "admin", "password": "admin", "latitude": loc[0], "longitude": loc[1]},
                            default=str),
            headers=auth_request_headers)
        auth_request_status_code = auth_request.status_code

        if auth_request_status_code != 200:
            application.logger.error("Error logging in to the API")
            application.logger.error(f"STATUS CODE = {auth_request_status_code}")
            application.logger.error(json.dumps(auth_request.json(), indent=4, default=str))
            sys.exit(0)

        access_token = auth_request.json()['access_token']

    except requests.exceptions.ConnectionError as ce:
        application.logger.error(f"Error connecting to API: {ce}")
        sys.exit(0)
    except:
        application.logger.error("Unexpected error:", sys.exc_info()[0])
        sys.exit(0)

    data_dir = os.path.join(os.getcwd(), 'data', 'child_labor')

    std_forms = [{
        'filename': 'standard_followup_form.json',
        'db_id': None
    }, {
        'filename': 'standard_household_intake_form.json',
        'db_id': None
    }, {
        'filename': 'standard_intake_form.json',
        'db_id': None
    }, {
        'filename': 'age_and_country_survey.json',
        'db_id': None
    }]

    application.logger.info("creating surveys")

    for std_form in std_forms:
        with open(os.path.join(data_dir, std_form['filename'])) as form_file:
            form_data = json.load(form_file)
            data = {
                "name": form_data['title'],
                "structure": form_data
            }

            request_headers = {'Content-type': 'application/json', 'Authorization': f"Bearer {access_token}"}
            post_survey_request = requests.post(
                f'{base_url}/surveys/',
                data=json.dumps(data, default=str),
                headers=request_headers)
            post_survey_request_status_code = post_survey_request.status_code

            if post_survey_request_status_code != 200:
                application.logger.error("Error posting survey")
                application.logger.error(f"STATUS CODE = {post_survey_request_status_code}")
                application.logger.error(json.dumps(post_survey_request.json(), indent=4, default=str))
                sys.exit(0)

            std_form['db_id'] = int(post_survey_request.json()['id'])

    application.logger.info("successfully created surveys")

    application.logger.info("creating case definition")

    # create case definition
    data = {
        "name": "Household Participant Cases",
        "key": "HPC",
        "description": "Case definition describing child labor household participants.",
        "surveys": [],
        "custom_fields": [
            {
                "name": "Household Short Text",
                "field_type": "text",
                "selections": None,
                "validation_rules": None,
                "custom_section_id": None,
                "help_text": "This is for short answers",
                "sort_order": 1
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
                        "id": 1,
                        "value": "Household Selection Option A"
                    },
                    {
                        "id": 2,
                        "value": "Household Selection Option B"
                    },
                    {
                        "id": 3,
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

    # request_headers = {'Content-type': 'application/json', 'Authorization': f"Bearer {access_token}"}
    post_case_defn_request = requests.post(
        f'{base_url}/case_definitions/',
        data=json.dumps(data, default=str),
        headers=request_headers)
    post_case_defn_request_code = post_case_defn_request.status_code

    if post_survey_request_status_code != 200:
        application.logger.error("Error posting case definition")
        application.logger.error(f"STATUS CODE = {post_case_defn_request_code}")
        application.logger.error(json.dumps(post_case_defn_request.json(), indent=4, default=str))
        sys.exit(0)

    case_defn_id = int(post_case_defn_request.json()['id'])

    application.logger.info(f"successfully created case definition")

    application.logger.info(f"creating activity definitions")

    activity_definitions = [
        {
            "name": "Household Intake",
            "description": "This is the activity for household intakes.",
            "case_definition_id": case_defn_id,
            "surveys": [s['db_id'] for s in std_forms if s['filename'] == 'standard_household_intake_form.json'],
            "documents": [],
            "custom_fields": [
                {
                    "name": "Household Short Text",
                    "field_type": "text",
                    "selections": None,
                    "validation_rules": None,
                    "custom_section_id": None,
                    "help_text": "This is for short answers",
                    "sort_order": 1
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
                            "id": 1,
                            "value": "Household Selection Option A"
                        },
                        {
                            "id": 2,
                            "value": "Household Selection Option B"
                        },
                        {
                            "id": 3,
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
        },
        {
            "name": "Youth Intake",
            "description": "This is the activity for youth intakes.",
            "case_definition_id": case_defn_id,
            "surveys": [s['db_id'] for s in std_forms if s['filename'] == 'standard_intake_form.json'],
            "documents": [],
            "custom_fields": [
                {
                    "name": "Household Short Text",
                    "field_type": "text",
                    "selections": None,
                    "validation_rules": None,
                    "custom_section_id": None,
                    "help_text": "This is for short answers",
                    "sort_order": 1
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
                            "id": 1,
                            "value": "Household Selection Option A"
                        },
                        {
                            "id": 2,
                            "value": "Household Selection Option B"
                        },
                        {
                            "id": 3,
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
        },
        {
            "name": "Youth Followup",
            "description": "This is the activity for youth followup.",
            "case_definition_id": case_defn_id,
            "surveys": [s['db_id'] for s in std_forms if s['filename'] == 'standard_followup_form.json'],
            "documents": [],
            "custom_fields": [
                {
                    "name": "Household Short Text",
                    "field_type": "text",
                    "selections": None,
                    "validation_rules": None,
                    "custom_section_id": None,
                    "help_text": "This is for short answers",
                    "sort_order": 1
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
                            "id": 1,
                            "value": "Household Selection Option A"
                        },
                        {
                            "id": 2,
                            "value": "Household Selection Option B"
                        },
                        {
                            "id": 3,
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
    ]

    hh_intake_act_defn_id = None
    youth_intake_act_defn_id = None
    youth_followup_act_defn_id = None

    for act_defn in activity_definitions:
        application.logger.info(f"creating activity definitions: {act_defn['name']}")

        post_act_defn_request = requests.post(
            f'{base_url}/activity_definitions',
            data=json.dumps(act_defn, default=str),
            headers=request_headers)
        post_act_defn_request_code = post_act_defn_request.status_code

        if post_act_defn_request_code != 200:
            application.logger.error("Error posting activity definition")
            application.logger.error(f"STATUS CODE = {post_act_defn_request_code}")
            application.logger.error(json.dumps(post_act_defn_request.json(), indent=4, default=str))
            sys.exit(0)

        defn_id = int(post_act_defn_request.json()['id'])
        if act_defn['name'] == 'Household Intake':
            hh_intake_act_defn_id = defn_id
        elif act_defn['name'] == 'Youth Intake':
            youth_intake_act_defn_id = defn_id
        elif act_defn['name'] == 'Youth Followup':
            youth_followup_act_defn_id = defn_id

        application.logger.info(f"successfully activity definition created")

    if hh_intake_act_defn_id is None or youth_intake_act_defn_id is None or youth_followup_act_defn_id is None:
        application.logger.error("There was an error setting activity definition IDs")
        application.logger.error(f"   hh_intake_act_defn_id = {hh_intake_act_defn_id}")
        application.logger.error(f"   youth_intake_act_defn_id = {youth_intake_act_defn_id}")
        application.logger.error(f"   youth_followup_act_defn_id = {youth_followup_act_defn_id}")
        sys.exit(0)

    application.logger.info(f"successfully created activity definitions")

    # load cases, responses
    application.logger.info(f"creating cases")
    last_names = []
    for i in range(10):
        hh_last_name = get_unique_name(fake.last_name, last_names)
        last_names.append(hh_last_name)
        loc = fake.latlng()
        data = {
            "name": f"{hh_last_name} Household Case",
            "description": f"This is the case for the {hh_last_name} Household",
            "case_definition_id": case_defn_id,
            "latitude": loc[0],
            "longitude": loc[1]
        }

        assignable_users = models.User.query.filter(models.User.username.in_(['aperkins', 'nbutler'])).all()
        # assign about 50% of cases
        if fake.boolean():
            assignable_user = random.choice(assignable_users)
            data['assigned_to_id'] = assignable_user.id

        # request_headers = {'Content-type': 'application/json', 'Authorization': f"Bearer {access_token}"}
        post_case_request = requests.post(
            f"{base_url}/case_definitions/{case_defn_id}/cases",
            data=json.dumps(data, default=str),
            headers=request_headers)
        post_case_request_code = post_case_request.status_code

        if post_case_request_code != 200:
            application.logger.error("Error posting case")
            application.logger.error(f"STATUS CODE = {post_case_request_code}")
            application.logger.error(json.dumps(post_case_request.json(), indent=4, default=str))
            sys.exit(0)
        case_id = int(post_case_request.json()['id'])

        # creating HH intake activity
        application.logger.info(f"creating HH intake activity")

        act_data = {
            "activity_definition_id": hh_intake_act_defn_id,
            "case_id": case_id,
            "name": f"Intake for {hh_last_name}.",
            "description": f"This is the intake activity for the {hh_last_name} household."
        }
        post_act_request = requests.post(
            f"{base_url}/activities",
            data=json.dumps(act_data, default=str),
            headers=request_headers)
        post_act_request_code = post_act_request.status_code

        if post_act_request_code != 200:
            application.logger.error("Error posting activity")
            application.logger.error(f"STATUS CODE = {post_act_request_code}")
            application.logger.error(json.dumps(post_act_request.json(), indent=4, default=str))
            sys.exit(0)
        act_id = int(post_act_request.json()['id'])

        application.logger.info(f"creating standard household intake response")
        std_hh_intake = next(filter(lambda s: s['filename'] == 'standard_household_intake_form.json', std_forms), None)
        loc = fake.latlng()
        data = {
            "survey_id": std_hh_intake['db_id'],
            "structure": {
                "address_info": fake.text(),
                "address_line_1": f"{fake.building_number()} {fake.street_name()} {fake.street_suffix()}",
                "address_line_2": fake.secondary_address(),
                "adminv_area": fake.state_abbr(),
                "country": fake.country(),
                "dependent_adminv_area": f"{fake.city()} County",
                "dependent_locality": ' '.join(fake.words()).title(),
                "id": f'HH{i + 1:04}',
                "intake_date": "2020-02-14",
                "locality": fake.city(),
                "name": f"{hh_last_name} Household",
                "postal_code": fake.postalcode()
            },
            "source_type": "Activity",
            "activity_id": act_id,
            "latitude": loc[0],
            "longitude": loc[1]
        }

        post_survey_response_request = requests.post(
            f"{base_url}/surveys/{std_hh_intake['db_id']}/responses",
            data=json.dumps(data, default=str),
            headers=request_headers)
        post_survey_response_request_code = post_survey_response_request.status_code

        if post_survey_response_request_code != 200:
            application.logger.error("Error posting household intake survey response")
            application.logger.error(f"STATUS CODE = {post_survey_response_request_code}")
            application.logger.error(json.dumps(post_survey_response_request.json(), indent=4, default=str))
            sys.exit(0)

        application.logger.info(f"creating member intake responses")
        relationships = ["Head of household", "Spouse/partner", "Son/daughter", "Step child", "Adopted/fostered child",
                         "Son-in-law/daughter-in-law", "Grandchild", "Parent", "Parent-in-law", "Grandparent",
                         "Brother/sister", "Brother-in-law/sister-in-law", "Aunt/uncle", "Niece/nephew", "Cousin",
                         "Servant", "Non-relative"]
        hazardous_conditions = ["Dust/fumes", "Fire/gas/flames", "Loud noise or vibration", "Extreme cold or heat",
                                "Dangerous tools (knives, etc.)", "Work underground", "Work at heights",
                                "Work in water/lake/pond/river", "Workplace too dark or confined",
                                "Insufficient ventilation", "Chemicals (pesticides, glues, etc.)", "Explosives"]
        work_activities = [
            "Run or do any kind of business, big or small, for himself/herself or with one or more partners?",
            "Do any work for a wage, salary, commission or any payment in kind?",
            "Do any work as a domestic worker for a wage, salary or any payment in kind?",
            "Help unpaid in a household business of any kind?",
            "Do any work on his/her own or household's plot, farm, food garden, or help in growing farm produce or in looking after animals for the household?",
            "Do any construction or major repair work on his/her own home, plot, or business or those of the household?",
            "Catch any fish, prawns, shells, wild animals, or other food for sale or household food?",
            "Fetch water or collect firewood for household use?",
            "Produce any other good for this household use?",
            "Did not engage in any of the above activities."]
        household_tasks = ["Shopping for household", "Repairing any household equipment",
                           "Cooking cleaning utensils/house", "Washing clothes", "Caring for children/old/sick"]

        std_intake = next(filter(lambda s: s['filename'] == 'standard_intake_form.json', std_forms), None)
        std_followup = next(filter(lambda s: s['filename'] == 'standard_followup_form.json', std_forms), None)

        num_children = random.randint(1, 5)

        for child_idx in range(num_children):
            child_profile = fake.profile()
            loc = fake.latlng()

            # creating youth intake activity
            application.logger.info(f"creating youth intake activity")

            youth_intake_act_data = {
                "activity_definition_id": youth_intake_act_defn_id,
                "case_id": case_id,
                "name": f"Youth Intake for {child_profile['name']}",
                "description": f"This is the youth intake activity for {child_profile['name']}."
            }
            post_act_request = requests.post(
                f"{base_url}/activities",
                data=json.dumps(youth_intake_act_data, default=str),
                headers=request_headers)
            post_act_request_code = post_act_request.status_code

            if post_act_request_code != 200:
                application.logger.error("Error posting case")
                application.logger.error(f"STATUS CODE = {post_act_request_code}")
                application.logger.error(json.dumps(post_act_request.json(), indent=4, default=str))
                sys.exit(0)
            youth_intake_act_id = int(post_act_request.json()['id'])

            data = {
                "survey_id": std_intake['db_id'],
                "structure": {
                    "dob": str(child_profile['birthdate']),
                    "enrolled_in_school": fake.boolean(),
                    "gender": child_profile['sex'],
                    "have_job_returning_to": fake.boolean(),
                    "hazardous_conditions": random.choices(hazardous_conditions),
                    "hours_worked": random.randint(0, 80),
                    "hours_worked_on_housework": random.randint(0, 80),
                    "household_id": f'HH{i + 1:04}',
                    "household_tasks": random.choices(household_tasks),
                    "id": f'HH{i + 1:04}HM{child_idx + 1:04}',
                    "intake_date": fake.date(),
                    "is_birthdate_approximate": fake.boolean(),
                    "name": child_profile['name'],
                    "relationship": random.choice(relationships),
                    "work_activities": random.choices(work_activities)
                },
                "source_type": "Activity",
                "activity_id": youth_intake_act_id,
                "latitude": loc[0],
                "longitude": loc[1]
            }

            post_survey_response_request = requests.post(
                f"{base_url}/surveys/{std_intake['db_id']}/responses",
                data=json.dumps(data, default=str),
                headers=request_headers)
            post_survey_response_request_code = post_survey_response_request.status_code

            if post_survey_response_request_code != 200:
                application.logger.error("Error posting standard intake survey response")
                application.logger.error(f"STATUS CODE = {post_survey_response_request_code}")
                application.logger.error(json.dumps(post_survey_response_request.json(), indent=4, default=str))
                sys.exit(0)

            application.logger.info("member intake responses created")

            application.logger.info("creating followups")
            for i in range(1, 3):
                loc = fake.latlng()
                # creating youth followup activity
                application.logger.info(f"creating youth follow activity")

                youth_followup_act_data = {
                    "activity_definition_id": youth_followup_act_defn_id,
                    "case_id": case_id,
                    "name": f"Youth Follow Up {i} for {child_profile['name']}.",
                    "description": f"This is the {i} youth follow-up activity for {child_profile['name']}."
                }
                post_act_request = requests.post(
                    f"{base_url}/activities",
                    data=json.dumps(youth_followup_act_data, default=str),
                    headers=request_headers)
                post_act_request_code = post_act_request.status_code

                if post_act_request_code != 200:
                    application.logger.error("Error posting activity")
                    application.logger.error(f"STATUS CODE = {post_act_request_code}")
                    application.logger.error(json.dumps(post_act_request.json(), indent=4, default=str))
                    sys.exit(0)
                youth_followup_act_id = int(post_act_request.json()['id'])

                data = {
                    "survey_id": std_followup['db_id'],
                    "structure": {
                        "dob": str(child_profile['birthdate']),
                        "enrolled_in_school": fake.boolean(),
                        "followup_date": fake.date(),
                        "gender": child_profile['sex'],
                        "have_job_returning_to": fake.boolean(),
                        "hazardous_conditions": random.choices(hazardous_conditions),
                        "hours_worked": random.randint(0, 80),
                        "hours_worked_on_housework": random.randint(0, 80),
                        "household_id": f'HH{i + 1:04}',
                        "household_tasks": random.choices(household_tasks),
                        "id": f'HH{i + 1:04}HM{child_idx + 1:04}',
                        "is_birthdate_approximate": fake.boolean(),
                        "name": child_profile['name'],
                        "relationship": random.choice(relationships),
                        "work_activities": random.choices(work_activities)
                    },
                    "source_type": "Activity",
                    "activity_id": youth_followup_act_id,
                    "latitude": loc[0],
                    "longitude": loc[1]
                }

                post_survey_response_request = requests.post(
                    f"{base_url}/surveys/{std_followup['db_id']}/responses",
                    data=json.dumps(data, default=str),
                    headers=request_headers)
                post_survey_response_request_code = post_survey_response_request.status_code

                if post_survey_response_request_code != 200:
                    application.logger.error("Error posting standard followup survey response")
                    application.logger.error(f"STATUS CODE = {post_survey_response_request_code}")
                    application.logger.error(json.dumps(post_survey_response_request.json(), indent=4, default=str))
                    sys.exit(0)

            application.logger.info("followups created")

    application.logger.info("successfully created cases")

    application.logger.info("loading responses for age and country standalone survey")

    survey = next(filter(lambda s: s['filename'] == 'age_and_country_survey.json', std_forms), None)
    countries = ['CN', 'IN', 'US', 'ID', 'PK', 'BR', 'NG', 'BD', 'RU', 'MX']

    for _ in range(100):
        country = random.choice(countries)
        location = fake.local_latlng(country_code=country, coords_only=True)
        data = {
            "survey_id": survey['db_id'],
            "structure": {
                "survey_date": fake.date(),
                "age": random.randint(18, 65),
                "country": country,
                "name": fake.name()
            },
            "latitude": float(location[0]),
            "longitude": float(location[1]),
            "source_type": "Standalone"
        }

        post_survey_response_request = requests.post(
            f"{base_url}/surveys/{survey['db_id']}/responses",
            data=json.dumps(data, default=str),
            headers=request_headers)
        post_survey_response_request_code = post_survey_response_request.status_code

        if post_survey_response_request_code != 200:
            application.logger.error("Error posting age and country survey response")
            application.logger.error(f"STATUS CODE = {post_survey_response_request_code}")
            application.logger.error(json.dumps(post_survey_response_request.json(), indent=4, default=str))
            sys.exit(0)

    application.logger.info("age and country standalone survey responses loaded")

    application.logger.info("start load project information")

    try:
        data = {
            "name": "ADVANCE Brazil",
            "title": "Brazilian ADVANCE Project Eliminating Exploitive Child Labor through Education and Livelihoods",
            "organization": "IMPAQ International",
            "agreement_number": "IL-23979-13-75-K",
            "start_date": "2018-01-01",
            "end_date": "2022-12-31",
            "funding_amount": 10000000,
            "location": "Brasília, Brazil"
        }
        post_project_request = requests.post(
            f"{base_url}/project",
            data=json.dumps(data, default=str),
            headers=request_headers)
        post_project_request_code = post_project_request.status_code

        if post_project_request_code != 200:
            application.logger.error("Error posting project info")
            application.logger.error(f"STATUS CODE = {post_project_request_code}")
            application.logger.error(json.dumps(post_project_request.json(), indent=4, default=str))
            sys.exit(0)

    except requests.exceptions.ConnectionError as ce:
        application.logger.error(f"Error connecting to API: {ce}")
        sys.exit(0)
    except:
        application.logger.error("Unexpected error:", sys.exc_info()[0])
        sys.exit(0)

    application.logger.info("project information loaded")

    # application.logger.info("*" * 80)
    # application.logger.info("LOADING LABOR INSPECTION DATA")
    # application.logger.info("*" * 80)
    #
    # data_dir = os.path.join(os.getcwd(), 'data', 'labor_inspection')
    #
    # labor_inspection_forms = [{
    #     'filename': 'productivity_and_quality.json',
    #     'db_id': None
    # }, {
    #     'filename': 'employee_work_premises.json',
    #     'db_id': None
    # }, {
    #     'filename': 'working_conditions.json',
    #     'db_id': None
    # }, {
    #     'filename': 'health_and_safety.json',
    #     'db_id': None
    # }, {
    #     'filename': 'workplace_fairness.json',
    #     'db_id': None
    # }]
    #
    # application.logger.info("creating surveys")
    #
    # for form in labor_inspection_forms:
    #     with open(os.path.join(data_dir, form['filename'])) as form_file:
    #         form_data = json.load(form_file)
    #         data = {
    #             "name": form_data['title'],
    #             "structure": form_data
    #         }
    #
    #         request_headers = {'Content-type': 'application/json', 'Authorization': f"Bearer {access_token}"}
    #         post_survey_request = requests.post(
    #             f'{base_url}/surveys/',
    #             data=json.dumps(data, default=str),
    #             headers=request_headers)
    #         post_survey_request_status_code = post_survey_request.status_code
    #
    #         if post_survey_request_status_code != 200:
    #             application.logger.error("Error posting survey")
    #             application.logger.error(f"STATUS CODE = {post_survey_request_status_code}")
    #             application.logger.error(json.dumps(post_survey_request.json(), indent=4, default=str))
    #             sys.exit(0)
    #
    #         form['db_id'] = int(post_survey_request.json()['id'])
    #
    # application.logger.info("successfully created surveys")
    #
    # application.logger.info("creating case definition")
    #
    # # create case definition
    # data = {
    #     "name": "Labor Inspection Cases",
    #     "key": "LIC",
    #     "description": "Case definition for labor inspection cases",
    #     "surveys": [s['db_id'] for s in labor_inspection_forms],
    #     "custom_fields": [
    #         {
    #             "name": "Labor Inspection Short Text",
    #             "field_type": "text",
    #             "selections": None,
    #             "validation_rules": None,
    #             "custom_section_id": None,
    #             "help_text": "This is for short answers",
    #             "sort_order": 1
    #         },
    #         {
    #             "name": "Labor Inspection Long Text",
    #             "field_type": "textarea",
    #             "selections": None,
    #             "validation_rules": None,
    #             "custom_section_id": None,
    #             "help_text": "This is for longer answers",
    #             "sort_order": 2
    #         },
    #         {
    #             "name": "Labor Inspection Check Box",
    #             "field_type": "check_box",
    #             "selections": [
    #                 {
    #                     "id": 1,
    #                     "value": "Labor Inspection Check Box Option A"
    #                 },
    #                 {
    #                     "id": 2,
    #                     "value": "Labor Inspection Check Box Option B"
    #                 },
    #                 {
    #                     "id": 3,
    #                     "value": "Labor Inspection Check Box Option C"
    #                 }
    #             ],
    #             "validation_rules": None,
    #             "custom_section_id": None,
    #             "help_text": "This allows for multiple selection of choices among many",
    #             "sort_order": 3
    #         },
    #         {
    #             "name": "Labor Inspection Radio Button",
    #             "field_type": "radio_button",
    #             "selections": [
    #                 {
    #                     "id": 1,
    #                     "value": "Labor Inspection Radio Option A"
    #                 },
    #                 {
    #                     "id": 2,
    #                     "value": "Labor Inspection Radio Option B"
    #                 },
    #                 {
    #                     "id": 3,
    #                     "value": "Labor Inspection Radio Option C"
    #                 }
    #             ],
    #             "validation_rules": None,
    #             "custom_section_id": None,
    #             "help_text": "This is for a single selection among many",
    #             "sort_order": 4
    #         },
    #         {
    #             "name": "Labor Inspection Selection Field",
    #             "field_type": "select",
    #             "selections": [
    #                 {
    #                     "id": 1,
    #                     "value": "Labor Inspection Selection Option A"
    #                 },
    #                 {
    #                     "id": 2,
    #                     "value": "Labor Inspection Selection Option B"
    #                 },
    #                 {
    #                     "id": 3,
    #                     "value": "Labor Inspection Selection Option C"
    #                 }
    #             ],
    #             "validation_rules": None,
    #             "custom_section_id": None,
    #             "help_text": "This is for a single selection among many",
    #             "sort_order": 5
    #         },
    #         {
    #             "name": "Labor Inspection Numeric Field",
    #             "field_type": "number",
    #             "selections": None,
    #             "validation_rules": None,
    #             "custom_section_id": None,
    #             "help_text": "This is for numbers",
    #             "sort_order": 6
    #         },
    #         {
    #             "name": "Labor Inspection Date Field",
    #             "field_type": "date",
    #             "selections": None,
    #             "validation_rules": None,
    #             "custom_section_id": None,
    #             "help_text": "This is for a date",
    #             "sort_order": 7
    #         },
    #         {
    #             "name": "Labor Inspection Rank List",
    #             "field_type": "rank_list",
    #             "selections": [
    #                 {
    #                     "id": 1,
    #                     "value": "Labor Inspection Rank Option A"
    #                 },
    #                 {
    #                     "id": 2,
    #                     "value": "Labor Inspection Rank Option B"
    #                 },
    #                 {
    #                     "id": 3,
    #                     "value": "Labor Inspection Rank Option C"
    #                 }
    #             ],
    #             "validation_rules": None,
    #             "custom_section_id": None,
    #             "help_text": "This is for ranking a list of options",
    #             "sort_order": 8
    #         }
    #     ]
    # }
    #
    # # request_headers = {'Content-type': 'application/json', 'Authorization': f"Bearer {access_token}"}
    # post_case_defn_request = requests.post(
    #     f'{base_url}/case_definitions/',
    #     data=json.dumps(data, default=str),
    #     headers=request_headers)
    # post_case_defn_request_code = post_case_defn_request.status_code
    #
    # if post_survey_request_status_code != 200:
    #     application.logger.error("Error posting case definition")
    #     application.logger.error(f"STATUS CODE = {post_case_defn_request_code}")
    #     application.logger.error(json.dumps(post_case_defn_request.json(), indent=4, default=str))
    #     sys.exit(0)
    #
    # case_defn_id = int(post_case_defn_request.json()['id'])
    #
    # application.logger.info(f"successfully created case definition")
    #
    # # create 30 cases
    # # each case has CF completely filled in
    # # each case has one response to each survey
    # application.logger.info(f"creating cases")
    # company_names = []
    # for i in range(30):
    #     company_name = get_unique_name(fake.company, company_names)
    #     company_names.append(company_name)
    #     loc = fake.latlng()
    #     data = {
    #         "name": f"{company_name} Case",
    #         "description": f"This is the case for {company_name}. {' '.join(fake.paragraphs())}",
    #         "case_definition_id": case_defn_id,
    #         "latitude": loc[0],
    #         "longitude": loc[1]
    #     }
    #
    #     post_case_request = requests.post(
    #         f"{base_url}/case_definitions/{case_defn_id}/cases",
    #         data=json.dumps(data, default=str),
    #         headers=request_headers)
    #     post_case_request_code = post_case_request.status_code
    #
    #     if post_case_request_code != 200:
    #         application.logger.error("Error posting case")
    #         application.logger.error(f"STATUS CODE = {post_case_request_code}")
    #         application.logger.error(json.dumps(post_case_request.json(), indent=4, default=str))
    #         sys.exit(0)
    #     case_id = int(post_case_request.json()['id'])
    #
    #     application.logger.info(f"creating Productivity and Quality response")
    #     survey = next(filter(lambda s: s['filename'] == 'productivity_and_quality.json', labor_inspection_forms), None)
    #     management_response = get_random_choices(['item1', 'item2', 'item3', 'item4'])
    #     if 'item4' in management_response:
    #         management_response_comment = fake.paragraph()
    #     else:
    #         management_response_comment = None
    #     work_area_impact = random.choice(['item1', 'item2', 'item3', 'item4'])
    #     if work_area_impact == 'item4':
    #         work_area_impact_comment = fake.paragraph()
    #     else:
    #         work_area_impact_comment = None
    #     efficient_work = get_random_choices(['item1', 'item2', 'item3', 'item4', 'item5', 'item6', 'item7'])
    #     if 'item7' in efficient_work:
    #         efficient_work_comment = fake.paragraph()
    #     else:
    #         efficient_work_comment = None
    #     loc = fake.latlng()
    #     data = {
    #         "survey_id": survey['db_id'],
    #         "structure": {
    #             "management_response": management_response,
    #             "work_area_impact": work_area_impact,
    #             "efficient_work": efficient_work,
    #             "Feedback": fake.paragraph(),
    #             "management_response-Comment": management_response_comment,
    #             "work_area_impact-Comment": work_area_impact_comment,
    #             "efficient_work-Comment": efficient_work_comment
    #         },
    #         "source_type": "Case",
    #         "case_id": case_id,
    #         "latitude": loc[0],
    #         "longitude": loc[1]
    #     }
    #
    #     post_survey_response_request = requests.post(
    #         f"{base_url}/surveys/{survey['db_id']}/responses",
    #         data=json.dumps(data, default=str),
    #         headers=request_headers)
    #     post_survey_response_request_code = post_survey_response_request.status_code
    #
    #     if post_survey_response_request_code != 200:
    #         application.logger.error("Error posting Productivity and Quality survey response")
    #         application.logger.error(f"STATUS CODE = {post_survey_response_request_code}")
    #         application.logger.error(json.dumps(post_survey_response_request.json(), indent=4, default=str))
    #         sys.exit(0)
    #
    #     application.logger.info(f"creating Employee Work Premises response")
    #     survey = next(filter(lambda s: s['filename'] == 'employee_work_premises.json', labor_inspection_forms), None)
    #     workstation_question = random.choice(["yes", "no"])
    #     floor_question = random.choice(["yes", "no"])
    #     passageways_question = random.choice(["yes", "no"])
    #     exit_question = random.choice(["yes", "no"])
    #     fire_escape = random.choice(["yes", "no"])
    #     fire_route_obstructions = random.choice(["yes", "no"])
    #     fire_extinguisher = random.choice(["yes", "no"])
    #     loc = fake.latlng()
    #     data = {
    #         "survey_id": survey['db_id'],
    #         "structure": {
    #             "workstation_question": workstation_question,
    #             "workstation_comment": fake.paragraph() if workstation_question == 'no' else None,
    #             "floor_question": floor_question,
    #             "floor_comment": fake.paragraph() if floor_question == 'no' else None,
    #             "passageways_question": passageways_question,
    #             "passageways_comment": fake.paragraph() if passageways_question == 'no' else None,
    #             "exit_question": exit_question,
    #             "exit_comment": fake.paragraph() if exit_question == 'no' else None,
    #             "fire_escape": fire_escape,
    #             "fire_route_obstructions": fire_route_obstructions,
    #             "route_comment": fake.paragraph() if fire_route_obstructions == 'no' else None,
    #             "fire_extinguisher": fire_extinguisher,
    #             "general_feedback": fake.paragraph()
    #         },
    #         "source_type": "Case",
    #         "case_id": case_id,
    #         "latitude": loc[0],
    #         "longitude": loc[1]
    #     }
    #
    #     post_survey_response_request = requests.post(
    #         f"{base_url}/surveys/{survey['db_id']}/responses",
    #         data=json.dumps(data, default=str),
    #         headers=request_headers)
    #     post_survey_response_request_code = post_survey_response_request.status_code
    #
    #     if post_survey_response_request_code != 200:
    #         application.logger.error("Error posting Employee Work Premises survey response")
    #         application.logger.error(f"STATUS CODE = {post_survey_response_request_code}")
    #         application.logger.error(json.dumps(post_survey_response_request.json(), indent=4, default=str))
    #         sys.exit(0)
    #
    #     application.logger.info(f"creating Working Conditions response")
    #     survey = next(filter(lambda s: s['filename'] == 'working_conditions.json', labor_inspection_forms), None)
    #     physical_conditions = random.choice(['item1', 'item2', 'item3'])
    #     if physical_conditions == 'item3':
    #         physical_condition_comment = fake.paragraph()
    #     else:
    #         physical_condition_comment = None
    #     work_intensity = random.choice(['item1', 'item2', 'item3'])
    #     if work_intensity == 'item1':
    #         work_intensity_comment = fake.paragraph()
    #     else:
    #         work_intensity_comment = None
    #     supervisor_treatment = random.choice(['item1', 'item2', 'item3'])
    #     if supervisor_treatment == 'item3':
    #         supervisor_treatment_comment = fake.paragraph()
    #     else:
    #         supervisor_treatment_comment = None
    #     job_injury = random.choice(['item1', 'item2', 'item3'])
    #     if job_injury in ['item1', 'item2']:
    #         job_injury_comment = fake.paragraph()
    #     else:
    #         job_injury_comment = None
    #     equal_treatment = random.choice(['yes', 'no'])
    #     if equal_treatment == 'no':
    #         equal_treatment_comment = fake.paragraph()
    #     else:
    #         equal_treatment_comment = None
    #     loc = fake.latlng()
    #     data = {
    #         "survey_id": survey['db_id'],
    #         "structure": {
    #             "physical_conditions": physical_conditions,
    #             "physical_condition_comment": physical_condition_comment,
    #             "work_intensity": work_intensity,
    #             "work_intensity_comment": work_intensity_comment,
    #             "supervisor_treatment": supervisor_treatment,
    #             "supervisor_treatment_comment": supervisor_treatment_comment,
    #             "job_injury": job_injury,
    #             "job_injury_comment": job_injury_comment,
    #             "work_load": get_random_choices(['item1', 'item2', 'item3', 'item4']),
    #             "intensity_continues": random.choice(['item1', 'item2']),
    #             "equal_treatment": equal_treatment,
    #             "equal_treatment_comment": equal_treatment_comment,
    #             "general_feedback": fake.paragraph()
    #         },
    #         "source_type": "Case",
    #         "case_id": case_id,
    #         "latitude": loc[0],
    #         "longitude": loc[1]
    #     }
    #
    #     post_survey_response_request = requests.post(
    #         f"{base_url}/surveys/{survey['db_id']}/responses",
    #         data=json.dumps(data, default=str),
    #         headers=request_headers)
    #     post_survey_response_request_code = post_survey_response_request.status_code
    #
    #     if post_survey_response_request_code != 200:
    #         application.logger.error("Error posting Working Conditions survey response")
    #         application.logger.error(f"STATUS CODE = {post_survey_response_request_code}")
    #         application.logger.error(json.dumps(post_survey_response_request.json(), indent=4, default=str))
    #         sys.exit(0)
    #
    #     application.logger.info(f"creating Health and Safety response")
    #     survey = next(filter(lambda s: s['filename'] == 'health_and_safety.json', labor_inspection_forms), None)
    #     work_environment = random.choice(['always', 'usually', 'sometimes', 'never'])
    #     if work_environment in ['sometimes', 'never']:
    #         work_environment_comment = fake.paragraph()
    #     else:
    #         work_environment_comment = None
    #     ignore_rules = random.choice(['always', 'often', 'sometimes', 'rarely', 'never'])
    #     if ignore_rules in ['always', 'often', 'sometimes', 'rarely']:
    #         ignore_rules_comment = fake.paragraph()
    #     else:
    #         ignore_rules_comment = None
    #     safety_material = random.choice(['yes', 'no'])
    #     if safety_material == 'no':
    #         safety_material_comment = fake.paragraph()
    #     else:
    #         safety_material_comment = None
    #     safety_problems = get_random_choices(['item1', 'item2', 'item3', 'item5', 'item6'])
    #     if "item6" in safety_problems:
    #         safety_problems_comment = fake.paragraph()
    #     else:
    #         safety_problems_comment = None
    #     loc = fake.latlng()
    #     data = {
    #         "survey_id": survey['db_id'],
    #         "structure": {
    #             "work_environment": work_environment,
    #             "work_environment_comment": work_environment_comment,
    #             "ignore_rules": ignore_rules,
    #             "ignore_rules_comment": ignore_rules_comment,
    #             "safety_material": safety_material,
    #             "safety_problems": [
    #                 "item1",
    #                 "item2"
    #             ],
    #             "general_feedback": fake.paragraph(),
    #             "safety_material-Comment": safety_material_comment,
    #             "safety_problems-Comment": safety_problems_comment
    #         },
    #         "source_type": "Case",
    #         "case_id": case_id,
    #         "latitude": loc[0],
    #         "longitude": loc[1]
    #     }
    #
    #     post_survey_response_request = requests.post(
    #         f"{base_url}/surveys/{survey['db_id']}/responses",
    #         data=json.dumps(data, default=str),
    #         headers=request_headers)
    #     post_survey_response_request_code = post_survey_response_request.status_code
    #
    #     if post_survey_response_request_code != 200:
    #         application.logger.error("Error posting Health and Safety survey response")
    #         application.logger.error(f"STATUS CODE = {post_survey_response_request_code}")
    #         application.logger.error(json.dumps(post_survey_response_request.json(), indent=4, default=str))
    #         sys.exit(0)
    #
    #     application.logger.info(f"creating Workplace Fairness response")
    #     survey = next(filter(lambda s: s['filename'] == 'workplace_fairness.json', labor_inspection_forms), None)
    #     wages_rating = random.randint(1, 5)
    #     if wages_rating in [1, 2]:
    #         wages_comment = fake.paragraph()
    #     else:
    #         wages_comment = None
    #     holidays_rating = random.randint(1, 5)
    #     if holidays_rating in [1, 2]:
    #         holiday_comment = fake.paragraph()
    #     else:
    #         holiday_comment = None
    #     vacation_days = random.randint(1, 5)
    #     if vacation_days in [1, 2, 3]:
    #         vacation_days_comment = fake.paragraph()
    #     else:
    #         vacation_days_comment = None
    #     management_assistance = random.randint(1, 5)
    #     if management_assistance in [1, 2, 3]:
    #         management_assistance_comment = fake.paragraph()
    #     else:
    #         management_assistance_comment = None
    #     management_communication = random.randint(1, 5)
    #     if management_communication in [1, 2, 3]:
    #         management_communication_comment = fake.paragraph()
    #     else:
    #         management_communication_comment = None
    #     loc = fake.latlng()
    #     data = {
    #         "survey_id": survey['db_id'],
    #         "structure": {
    #             "wages_rating": wages_rating,
    #             "wages_comment": wages_comment,
    #             "holidays_rating": 2,
    #             "holiday_comment": holiday_comment,
    #             "vacation_days": vacation_days,
    #             "vacation_days_comment": vacation_days_comment,
    #             "management_assistance": management_assistance,
    #             "management_assistance_comment": management_assistance_comment,
    #             "management_communication": management_communication,
    #             "management_communication_comment": management_communication_comment,
    #             "general_feedback": fake.paragraph()
    #         },
    #         "source_type": "Case",
    #         "case_id": case_id,
    #         "latitude": loc[0],
    #         "longitude": loc[1]
    #     }
    #
    #     post_survey_response_request = requests.post(
    #         f"{base_url}/surveys/{survey['db_id']}/responses",
    #         data=json.dumps(data, default=str),
    #         headers=request_headers)
    #     post_survey_response_request_code = post_survey_response_request.status_code
    #
    #     if post_survey_response_request_code != 200:
    #         application.logger.error("Error posting Workplace Fairness survey response")
    #         application.logger.error(f"STATUS CODE = {post_survey_response_request_code}")
    #         application.logger.error(json.dumps(post_survey_response_request.json(), indent=4, default=str))
    #         sys.exit(0)
    #
    # application.logger.info("*" * 80)
    # application.logger.info("LOADING LABOR INSPECTION DATA COMPLETE")
    # application.logger.info("*" * 80)

    application.logger.info("*" * 80)
    application.logger.info("LOADING CUSTOM FIELDS FOR CASES")
    application.logger.info("*" * 80)

    cases_request = requests.get(f"{base_url}/cases", headers=request_headers)

    if cases_request.status_code == 200:
        cases = cases_request.json()
        for activity in cases:
            application.logger.info(f"loading custom field values for ({activity['id']}) {activity['name']}")
            for custom_field in activity['custom_fields']:
                if custom_field['field_type'] == 'text':
                    custom_field_value = fake.sentence()
                elif custom_field['field_type'] == 'textarea':
                    custom_field_value = fake.paragraph()
                elif custom_field['field_type'] == 'check_box':
                    selections = get_random_choices(custom_field['selections'])
                    custom_field_value = [s['id'] for s in selections]
                elif custom_field['field_type'] in ['select', 'radio_button']:
                    custom_field_value = random.choice(custom_field['selections'])['id']
                elif custom_field['field_type'] == 'number':
                    custom_field_value = random.randint(1, 10)
                elif custom_field['field_type'] == 'date':
                    custom_field_value = fake.date()
                elif custom_field['field_type'] == 'rank_list':
                    selections = copy.deepcopy(custom_field['selections'])
                    random.shuffle(selections)
                    custom_field_value = []
                    for i, s in enumerate(selections, start=1):
                        custom_field_value.append({'id': s['id'], 'rank': i})
                else:
                    custom_field_value = None

                url = f"{base_url}/cases/{activity['id']}/custom_fields/{custom_field['id']}"
                data = {"value": custom_field_value}
                custom_field_request = requests.put(url, data=json.dumps(data, default=str), headers=request_headers)
                if custom_field_request.status_code != 200:
                    application.logger.error("Error updating case custom field")
                    application.logger.error(f"STATUS CODE = {custom_field_request.status_code}")
                    application.logger.error(json.dumps(custom_field_request.json(), indent=4, default=str))
    else:
        application.logger.error("Error getting cases")
        application.logger.error(f"STATUS CODE = {cases_request.status_code}")
        application.logger.error(json.dumps(cases_request.json(), indent=4, default=str))

    application.logger.info("*" * 80)
    application.logger.info("LOADING CUSTOM FIELDS FOR CASES COMPLETE")
    application.logger.info("*" * 80)

    application.logger.info("*" * 80)
    application.logger.info("LOADING CUSTOM FIELDS FOR ACTIVITIES")
    application.logger.info("*" * 80)

    activities_request = requests.get(f"{base_url}/activities", headers=request_headers)

    if activities_request.status_code == 200:
        activities = activities_request.json()
        for activity in activities:
            application.logger.info(f"loading custom field values for ({activity['id']}) {activity['name']}")
            for custom_field in activity['custom_fields']:
                if custom_field['field_type'] == 'text':
                    custom_field_value = fake.sentence()
                elif custom_field['field_type'] == 'textarea':
                    custom_field_value = fake.paragraph()
                elif custom_field['field_type'] == 'check_box':
                    selections = get_random_choices(custom_field['selections'])
                    custom_field_value = [s['id'] for s in selections]
                elif custom_field['field_type'] in ['select', 'radio_button']:
                    custom_field_value = random.choice(custom_field['selections'])['id']
                elif custom_field['field_type'] == 'number':
                    custom_field_value = random.randint(1, 10)
                elif custom_field['field_type'] == 'date':
                    custom_field_value = fake.date()
                elif custom_field['field_type'] == 'rank_list':
                    selections = copy.deepcopy(custom_field['selections'])
                    random.shuffle(selections)
                    custom_field_value = []
                    for i, s in enumerate(selections, start=1):
                        custom_field_value.append({'id': s['id'], 'rank': i})
                else:
                    custom_field_value = None

                url = f"{base_url}/activities/{activity['id']}/custom_fields/{custom_field['id']}"
                data = {"value": custom_field_value}
                custom_field_request = requests.put(url, data=json.dumps(data, default=str), headers=request_headers)
                if custom_field_request.status_code != 200:
                    application.logger.error("Error updating case custom field")
                    application.logger.error(f"STATUS CODE = {custom_field_request.status_code}")
                    application.logger.error(json.dumps(custom_field_request.json(), indent=4, default=str))
    else:
        application.logger.error("Error getting activities")
        application.logger.error(f"STATUS CODE = {cases_request.status_code}")
        application.logger.error(json.dumps(cases_request.json(), indent=4, default=str))

    application.logger.info("*" * 80)
    application.logger.info("LOADING CUSTOM FIELDS FOR ACTIVITIES COMPLETE")
    application.logger.info("*" * 80)

    #
    # application.logger.info("start reporting database, rescan metabase")
    # post_rescan_request = requests.post(
    #     f'{base_url}/reset-reporting',
    #     data='',
    #     headers=request_headers)
    # post_rescan_request_code = post_rescan_request.status_code
    #
    # if post_survey_request_status_code != 200:
    #     application.logger.error("Error posting rebuild mongodb, rescan metabase")
    #     application.logger.error(f"STATUS CODE = {post_rescan_request_code}")
    #     application.logger.error(json.dumps(post_rescan_request.json(), indent=4, default=str))
    #     sys.exit(0)
    #
    # application.logger.info("successfully rebuild mongo, rescan metabase")

    application.logger.info("end loading the dev dataset")


@application.cli.command("load-demo-dataset")
@click.argument("base_url")
def load_demo_dataset(base_url="http://localhost:5000"):
    """
    Loads a demo (SGLLE) dataset

    1. seed the database
    2. add the labor inspection surveys
        - Productivity and Quality
        - Employee Work Premises
        - Health and Safety
        - Workplace Fairness
    2. add 'Labor Inspection Case Type`
        - with custom fields
    3. add cases

    :param base_url: The URL of the API to use to load the data
    """
    import random
    import datetime
    from faker import Faker
    fake = Faker(locale='es_MX')

    def get_random_choices(choices):
        return random.sample(choices, random.randint(1, len(choices)))

    def get_unique_name(gen_func, name_list):
        n = gen_func()
        while n in name_list:
            n = gen_func()
        return n

    application.logger.info("start loading the demo dataset")

    application.logger.info("re-created database")
    rebuild_db()

    application.logger.info("seeding database")

    application.logger.info('dropping reporting tables')
    application.reporting_service.delete_all()

    application.logger.info('loading roles')
    roles = {
        'Admin': [models.Permission.ADMIN],
        'Project Manager': [models.Permission.CONFIGURE_SYSTEM, models.Permission.READ_ACCOUNT,
                            models.Permission.UPDATE_ACCOUNT,
                            models.Permission.CREATE_SURVEY, models.Permission.READ_SURVEY,
                            models.Permission.UPDATE_SURVEY,
                            models.Permission.DELETE_SURVEY, models.Permission.SUBMIT_SURVEY,
                            models.Permission.ARCHIVE_SURVEY, models.Permission.READ_REPORT,
                            models.Permission.CREATE_CASE_DEFINITION, models.Permission.READ_CASE_DEFINITION,
                            models.Permission.UPDATE_CASE_DEFINITION, models.Permission.DELETE_CASE_DEFINITION,
                            models.Permission.CREATE_CASE, models.Permission.UPDATE_CASE, models.Permission.READ_CASE,
                            models.Permission.DELETE_CASE, models.Permission.CREATE_PROJECT,
                            models.Permission.READ_PROJECT,
                            models.Permission.UPDATE_PROJECT, models.Permission.DELETE_PROJECT],
        'Labor Inspector': [models.Permission.READ_ACCOUNT, models.Permission.UPDATE_ACCOUNT,
                            models.Permission.READ_SURVEY,
                            models.Permission.SUBMIT_SURVEY, models.Permission.UPDATE_SURVEY,
                            models.Permission.CREATE_CASE, models.Permission.UPDATE_CASE, models.Permission.READ_CASE,
                            models.Permission.READ_PROJECT]
    }
    default_role = 'Labor Inspector'
    for r in roles:
        role = models.Role.query.filter_by(name=r).first()
        if role is None:
            role = models.Role(name=r)
        role.reset_permissions()
        for perm in roles[r]:
            role.add_permission(perm)
        role.default = (role.name == default_role)
        db.session.add(role)
    db.session.commit()

    application.logger.info('loading survey response statuses')
    models.SurveyResponseStatus.insert_survey_response_statuses()

    application.logger.info('loading case statuses')
    case_statuses = [
        (1, 'Initiated', True),
        (2, 'Scheduled', False),
        (3, 'Delayed', False),
        (4, 'Compliant', False),
        (5, 'Non-Compliant', False),
    ]

    for status in case_statuses:
        db_status = models.CaseStatus.query.get(status[0])

        if db_status is None:
            db_status = models.CaseStatus(id=status[0], name=status[1], default=status[2])
            db.session.add(db_status)

    db.session.commit()

    application.logger.info('loading admin and test accounts')
    admin_role = models.Role.query.filter_by(name='Admin').first()
    users = [
        {'email': 'ilabtoolkit@gmail.com', 'username': 'admin', 'password': 'admin', 'name': 'Admin User',
         'role': admin_role},
        {'email': 'jclements@ascend.network', 'username': 'jclements', 'password': 'admin12345',
         'name': 'John Clements', 'role': admin_role},
        {'email': 'nschoeb@ascend.network', 'username': 'nschoeb', 'password': 'admin12345', 'name': 'Nick Schoeb',
         'role': admin_role},
        {'email': 'tstone@ascend.network', 'username': 'tstone', 'password': 'admin12345', 'name': 'Thomas Stone',
         'role': admin_role}
    ]
    for user in users:
        if not len(list(models.User.query.filter_by(email=user['email']))):
            new_user = models.User(
                email=user['email'],
                username=user['username'],
                password=user['password'],
                name=user['name'],
                role=user['role']
            )
            db.session.add(new_user)
            db.session.commit()

    application.logger.info('loading system properties')
    eps_property = models.EPSProperty(property='default_dashboard_id', value=None)
    db.session.add(eps_property)
    db.session.commit()

    application.logger.info("logging into API")

    try:
        loc = fake.latlng()
        auth_request_headers = {'Content-type': 'application/json'}
        auth_request = requests.post(
            f'{base_url}/auth/login',
            data=json.dumps({"login": "admin", "password": "admin", "latitude": loc[0], "longitude": loc[1]},
                            default=str),
            headers=auth_request_headers)
        auth_request_status_code = auth_request.status_code

        if auth_request_status_code != 200:
            application.logger.error("Error logging in to the API")
            application.logger.error(f"STATUS CODE = {auth_request_status_code}")
            application.logger.error(json.dumps(auth_request.json(), indent=4, default=str))
            sys.exit(0)

        access_token = auth_request.json()['access_token']

    except requests.exceptions.ConnectionError as ce:
        application.logger.error(f"Error connecting to API: {ce}")
        sys.exit(0)
    except:
        application.logger.error("Unexpected error:", sys.exc_info()[0])
        sys.exit(0)

    request_headers = {'Content-type': 'application/json', 'Authorization': f"Bearer {access_token}"}

    application.logger.info("*" * 80)
    application.logger.info("LOADING PROJECT INFORMATION")
    application.logger.info("*" * 80)

    try:
        data = {
            "name": "ADVANCE Brazil",
            "title": "Brazilian ADVANCE Project Eliminating Exploitive Child Labor through Education and Livelihoods",
            "organization": "IMPAQ International",
            "agreement_number": "IL-23979-13-75-K",
            "start_date": "2018-01-01",
            "end_date": "2022-12-31",
            "funding_amount": 10000000,
            "location": "Brasília, Brazil"
        }
        post_project_request = requests.post(
            f"{base_url}/project",
            data=json.dumps(data, default=str),
            headers=request_headers)
        post_project_request_code = post_project_request.status_code

        if post_project_request_code != 200:
            application.logger.error("Error posting project info")
            application.logger.error(f"STATUS CODE = {post_project_request_code}")
            application.logger.error(json.dumps(post_project_request.json(), indent=4, default=str))
            sys.exit(0)

    except requests.exceptions.ConnectionError as ce:
        application.logger.error(f"Error loading project information: {ce}")
        sys.exit(0)
    except:
        application.logger.error("Unexpected error:", sys.exc_info()[0])
        sys.exit(0)

    application.logger.info("project information loaded")

    application.logger.info("*" * 80)
    application.logger.info("LOADING LABOR INSPECTION DATA")
    application.logger.info("*" * 80)

    data_dir = os.path.join(os.getcwd(), 'data', 'labor_inspection')

    labor_inspection_forms = [{
        'filename': 'productivity_and_quality.json',
        'db_id': None
    }, {
        'filename': 'employee_work_premises.json',
        'db_id': None
    }, {
        'filename': 'working_conditions.json',
        'db_id': None
    }, {
        'filename': 'health_and_safety.json',
        'db_id': None
    }, {
        'filename': 'workplace_fairness.json',
        'db_id': None
    }]

    application.logger.info("creating surveys")

    for form in labor_inspection_forms:
        with open(os.path.join(data_dir, form['filename'])) as form_file:
            form_data = json.load(form_file)
            data = {
                "name": form_data['title'],
                "structure": form_data
            }

            request_headers = {'Content-type': 'application/json', 'Authorization': f"Bearer {access_token}"}
            post_survey_request = requests.post(
                f'{base_url}/surveys/',
                data=json.dumps(data, default=str),
                headers=request_headers)
            post_survey_request_status_code = post_survey_request.status_code

            if post_survey_request_status_code != 200:
                application.logger.error("Error posting survey")
                application.logger.error(f"STATUS CODE = {post_survey_request_status_code}")
                application.logger.error(json.dumps(post_survey_request.json(), indent=4, default=str))
                sys.exit(0)

            form['db_id'] = int(post_survey_request.json()['id'])

    application.logger.info("successfully created surveys")

    application.logger.info("creating case definition")

    # create case definition
    data = {
        "name": "Labor Inspection Cases",
        "key": "LIC",
        "description": "Case definition for labor inspection cases",
        "surveys": [s['db_id'] for s in labor_inspection_forms],
        "custom_fields": [
            {
                "name": "Inspection Type",
                "field_type": "select",
                "selections": [
                    {
                        "id": 1,
                        "value": "Scheduled"
                    },
                    {
                        "id": 2,
                        "value": "Follow-up"
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
                        "value": "Baja California"
                    },
                    {
                        "id": 2,
                        "value": "Pacific Coastal Lowlands"
                    },
                    {
                        "id": 3,
                        "value": "Mexican Plateau"
                    },
                    {
                        "id": 4,
                        "value": "Sierra Madre Oriental"
                    },
                    {
                        "id": 5,
                        "value": "Sierra Madre Occidental"
                    },
                    {
                        "id": 6,
                        "value": "Cordillera Neo-Volcánica"
                    },
                    {
                        "id": 7,
                        "value": "Gulf Coastal Plain"
                    },
                    {
                        "id": 8,
                        "value": "Southern Highlands"
                    },
                    {
                        "id": 9,
                        "value": "Yucatán Peninsula"
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
        ]
    }

    # request_headers = {'Content-type': 'application/json', 'Authorization': f"Bearer {access_token}"}
    post_case_defn_request = requests.post(
        f'{base_url}/case_definitions/',
        data=json.dumps(data, default=str),
        headers=request_headers)
    post_case_defn_request_code = post_case_defn_request.status_code

    if post_case_defn_request_code != 200:
        application.logger.error("Error posting case definition")
        application.logger.error(f"STATUS CODE = {post_case_defn_request_code}")
        application.logger.error(json.dumps(post_case_defn_request.json(), indent=4, default=str))
        sys.exit(0)

    case_defn_id = int(post_case_defn_request.json()['id'])

    application.logger.info(f"successfully created case definition")

    # create 30 cases
    # each case has CF completely filled in
    # each case has one response to each survey
    application.logger.info(f"creating cases")
    company_names = []
    for i in range(30):
        company_name = get_unique_name(fake.company, company_names)
        company_names.append(company_name)
        loc = fake.latlng()
        data = {
            "name": f"{company_name} Case",
            "description": f"This is the case for {company_name}. {' '.join(fake.paragraphs())}",
            "case_definition_id": case_defn_id,
            "latitude": loc[0],
            "longitude": loc[1]
        }

        post_case_request = requests.post(
            f"{base_url}/case_definitions/{case_defn_id}/cases",
            data=json.dumps(data, default=str),
            headers=request_headers)
        post_case_request_code = post_case_request.status_code

        if post_case_request_code != 200:
            application.logger.error("Error posting case")
            application.logger.error(f"STATUS CODE = {post_case_request_code}")
            application.logger.error(json.dumps(post_case_request.json(), indent=4, default=str))
            sys.exit(0)
        case_id = int(post_case_request.json()['id'])

        # choose a random case status and update
        data = {
            'status_id': random.choice(range(1, 6))
        }
        response = requests.put(f"{base_url}/cases/{case_id}", data=json.dumps(data, default=str),
                                headers=request_headers)

        if response.status_code != 200:
            application.logger.error("Error updating case's status")
            application.logger.error(f"STATUS CODE = {response.status_code}")
            application.logger.error(json.dumps(response.json(), indent=4, default=str))
            sys.exit(0)

        application.logger.info(f"creating Productivity and Quality response")
        survey = next(filter(lambda s: s['filename'] == 'productivity_and_quality.json', labor_inspection_forms), None)
        management_response = get_random_choices(['item1', 'item2', 'item3', 'item4'])
        if 'item4' in management_response:
            management_response_comment = fake.paragraph()
        else:
            management_response_comment = None
        work_area_impact = random.choice(['item1', 'item2', 'item3', 'item4'])
        if work_area_impact == 'item4':
            work_area_impact_comment = fake.paragraph()
        else:
            work_area_impact_comment = None
        efficient_work = get_random_choices(['item1', 'item2', 'item3', 'item4', 'item5', 'item6', 'item7'])
        if 'item7' in efficient_work:
            efficient_work_comment = fake.paragraph()
        else:
            efficient_work_comment = None
        loc = fake.latlng()
        data = {
            "survey_id": survey['db_id'],
            "structure": {
                "management_response": management_response,
                "work_area_impact": work_area_impact,
                "efficient_work": efficient_work,
                "Feedback": fake.paragraph(),
                "management_response-Comment": management_response_comment,
                "work_area_impact-Comment": work_area_impact_comment,
                "efficient_work-Comment": efficient_work_comment
            },
            "source_type": "Case",
            "case_id": case_id,
            "latitude": loc[0],
            "longitude": loc[1]
        }

        post_survey_response_request = requests.post(
            f"{base_url}/surveys/{survey['db_id']}/responses",
            data=json.dumps(data, default=str),
            headers=request_headers)
        post_survey_response_request_code = post_survey_response_request.status_code

        if post_survey_response_request_code != 200:
            application.logger.error("Error posting Productivity and Quality survey response")
            application.logger.error(f"STATUS CODE = {post_survey_response_request_code}")
            application.logger.error(json.dumps(post_survey_response_request.json(), indent=4, default=str))
            sys.exit(0)

        application.logger.info(f"creating Employee Work Premises response")
        survey = next(filter(lambda s: s['filename'] == 'employee_work_premises.json', labor_inspection_forms), None)
        workstation_question = random.choice(["yes", "no"])
        floor_question = random.choice(["yes", "no"])
        passageways_question = random.choice(["yes", "no"])
        exit_question = random.choice(["yes", "no"])
        fire_escape = random.choice(["yes", "no"])
        fire_route_obstructions = random.choice(["yes", "no"])
        fire_extinguisher = random.choice(["yes", "no"])
        loc = fake.latlng()
        data = {
            "survey_id": survey['db_id'],
            "structure": {
                "workstation_question": workstation_question,
                "workstation_comment": fake.paragraph() if workstation_question == 'no' else None,
                "floor_question": floor_question,
                "floor_comment": fake.paragraph() if floor_question == 'no' else None,
                "passageways_question": passageways_question,
                "passageways_comment": fake.paragraph() if passageways_question == 'no' else None,
                "exit_question": exit_question,
                "exit_comment": fake.paragraph() if exit_question == 'no' else None,
                "fire_escape": fire_escape,
                "fire_route_obstructions": fire_route_obstructions,
                "route_comment": fake.paragraph() if fire_route_obstructions == 'no' else None,
                "fire_extinguisher": fire_extinguisher,
                "general_feedback": fake.paragraph()
            },
            "source_type": "Case",
            "case_id": case_id,
            "latitude": loc[0],
            "longitude": loc[1]
        }

        post_survey_response_request = requests.post(
            f"{base_url}/surveys/{survey['db_id']}/responses",
            data=json.dumps(data, default=str),
            headers=request_headers)
        post_survey_response_request_code = post_survey_response_request.status_code

        if post_survey_response_request_code != 200:
            application.logger.error("Error posting Employee Work Premises survey response")
            application.logger.error(f"STATUS CODE = {post_survey_response_request_code}")
            application.logger.error(json.dumps(post_survey_response_request.json(), indent=4, default=str))
            sys.exit(0)

        application.logger.info(f"creating Working Conditions response")
        survey = next(filter(lambda s: s['filename'] == 'working_conditions.json', labor_inspection_forms), None)
        physical_conditions = random.choice(['item1', 'item2', 'item3'])
        if physical_conditions == 'item3':
            physical_condition_comment = fake.paragraph()
        else:
            physical_condition_comment = None
        work_intensity = random.choice(['item1', 'item2', 'item3'])
        if work_intensity == 'item1':
            work_intensity_comment = fake.paragraph()
        else:
            work_intensity_comment = None
        supervisor_treatment = random.choice(['item1', 'item2', 'item3'])
        if supervisor_treatment == 'item3':
            supervisor_treatment_comment = fake.paragraph()
        else:
            supervisor_treatment_comment = None
        job_injury = random.choice(['item1', 'item2', 'item3'])
        if job_injury in ['item1', 'item2']:
            job_injury_comment = fake.paragraph()
        else:
            job_injury_comment = None
        equal_treatment = random.choice(['yes', 'no'])
        if equal_treatment == 'no':
            equal_treatment_comment = fake.paragraph()
        else:
            equal_treatment_comment = None
        loc = fake.latlng()
        data = {
            "survey_id": survey['db_id'],
            "structure": {
                "physical_conditions": physical_conditions,
                "physical_condition_comment": physical_condition_comment,
                "work_intensity": work_intensity,
                "work_intensity_comment": work_intensity_comment,
                "supervisor_treatment": supervisor_treatment,
                "supervisor_treatment_comment": supervisor_treatment_comment,
                "job_injury": job_injury,
                "job_injury_comment": job_injury_comment,
                "work_load": get_random_choices(['item1', 'item2', 'item3', 'item4']),
                "intensity_continues": random.choice(['item1', 'item2']),
                "equal_treatment": equal_treatment,
                "equal_treatment_comment": equal_treatment_comment,
                "general_feedback": fake.paragraph()
            },
            "source_type": "Case",
            "case_id": case_id,
            "latitude": loc[0],
            "longitude": loc[1]
        }

        post_survey_response_request = requests.post(
            f"{base_url}/surveys/{survey['db_id']}/responses",
            data=json.dumps(data, default=str),
            headers=request_headers)
        post_survey_response_request_code = post_survey_response_request.status_code

        if post_survey_response_request_code != 200:
            application.logger.error("Error posting Working Conditions survey response")
            application.logger.error(f"STATUS CODE = {post_survey_response_request_code}")
            application.logger.error(json.dumps(post_survey_response_request.json(), indent=4, default=str))
            sys.exit(0)

        application.logger.info(f"creating Health and Safety response")
        survey = next(filter(lambda s: s['filename'] == 'health_and_safety.json', labor_inspection_forms), None)
        work_environment = random.choice(['always', 'usually', 'sometimes', 'never'])
        if work_environment in ['sometimes', 'never']:
            work_environment_comment = fake.paragraph()
        else:
            work_environment_comment = None
        ignore_rules = random.choice(['always', 'often', 'sometimes', 'rarely', 'never'])
        if ignore_rules in ['always', 'often', 'sometimes', 'rarely']:
            ignore_rules_comment = fake.paragraph()
        else:
            ignore_rules_comment = None
        safety_material = random.choice(['yes', 'no'])
        if safety_material == 'no':
            safety_material_comment = fake.paragraph()
        else:
            safety_material_comment = None
        safety_problems = get_random_choices(['item1', 'item2', 'item3', 'item5', 'item6'])
        if "item6" in safety_problems:
            safety_problems_comment = fake.paragraph()
        else:
            safety_problems_comment = None
        loc = fake.latlng()
        data = {
            "survey_id": survey['db_id'],
            "structure": {
                "work_environment": work_environment,
                "work_environment_comment": work_environment_comment,
                "ignore_rules": ignore_rules,
                "ignore_rules_comment": ignore_rules_comment,
                "safety_material": safety_material,
                "safety_problems": [
                    "item1",
                    "item2"
                ],
                "general_feedback": fake.paragraph(),
                "safety_material-Comment": safety_material_comment,
                "safety_problems-Comment": safety_problems_comment
            },
            "source_type": "Case",
            "case_id": case_id,
            "latitude": loc[0],
            "longitude": loc[1]
        }

        post_survey_response_request = requests.post(
            f"{base_url}/surveys/{survey['db_id']}/responses",
            data=json.dumps(data, default=str),
            headers=request_headers)
        post_survey_response_request_code = post_survey_response_request.status_code

        if post_survey_response_request_code != 200:
            application.logger.error("Error posting Health and Safety survey response")
            application.logger.error(f"STATUS CODE = {post_survey_response_request_code}")
            application.logger.error(json.dumps(post_survey_response_request.json(), indent=4, default=str))
            sys.exit(0)

        application.logger.info(f"creating Workplace Fairness response")
        survey = next(filter(lambda s: s['filename'] == 'workplace_fairness.json', labor_inspection_forms), None)
        wages_rating = random.randint(1, 5)
        if wages_rating in [1, 2]:
            wages_comment = fake.paragraph()
        else:
            wages_comment = None
        holidays_rating = random.randint(1, 5)
        if holidays_rating in [1, 2]:
            holiday_comment = fake.paragraph()
        else:
            holiday_comment = None
        vacation_days = random.randint(1, 5)
        if vacation_days in [1, 2, 3]:
            vacation_days_comment = fake.paragraph()
        else:
            vacation_days_comment = None
        management_assistance = random.randint(1, 5)
        if management_assistance in [1, 2, 3]:
            management_assistance_comment = fake.paragraph()
        else:
            management_assistance_comment = None
        management_communication = random.randint(1, 5)
        if management_communication in [1, 2, 3]:
            management_communication_comment = fake.paragraph()
        else:
            management_communication_comment = None
        loc = fake.latlng()
        data = {
            "survey_id": survey['db_id'],
            "structure": {
                "wages_rating": wages_rating,
                "wages_comment": wages_comment,
                "holidays_rating": 2,
                "holiday_comment": holiday_comment,
                "vacation_days": vacation_days,
                "vacation_days_comment": vacation_days_comment,
                "management_assistance": management_assistance,
                "management_assistance_comment": management_assistance_comment,
                "management_communication": management_communication,
                "management_communication_comment": management_communication_comment,
                "general_feedback": fake.paragraph()
            },
            "source_type": "Case",
            "case_id": case_id,
            "latitude": loc[0],
            "longitude": loc[1]
        }

        post_survey_response_request = requests.post(
            f"{base_url}/surveys/{survey['db_id']}/responses",
            data=json.dumps(data, default=str),
            headers=request_headers)
        post_survey_response_request_code = post_survey_response_request.status_code

        if post_survey_response_request_code != 200:
            application.logger.error("Error posting Workplace Fairness survey response")
            application.logger.error(f"STATUS CODE = {post_survey_response_request_code}")
            application.logger.error(json.dumps(post_survey_response_request.json(), indent=4, default=str))
            sys.exit(0)

    application.logger.info("*" * 80)
    application.logger.info("LOADING LABOR INSPECTION DATA COMPLETE")
    application.logger.info("*" * 80)

    application.logger.info("*" * 80)
    application.logger.info("LOADING CUSTOM FIELDS FOR CASES")
    application.logger.info("*" * 80)

    cases_request = requests.get(f"{base_url}/cases", headers=request_headers)

    if cases_request.status_code == 200:
        cases = cases_request.json()
        for case in cases:
            lat, lng, city, *_ = fake.local_latlng(country_code='MX')
            application.logger.info(f"loading custom field values for ({case['id']}) {case['name']}")
            for custom_field in case['custom_fields']:
                if custom_field['name'] in ['Inspection Type', 'Business Sector', 'Region']:
                    custom_field_value = random.choice(custom_field['selections'])['id']
                elif custom_field['name'] == 'Business Name':
                    custom_field_value = fake.company()
                elif custom_field['name'] == 'Address':
                    custom_field_value = fake.address()
                elif custom_field['name'] == 'City':
                    custom_field_value = city
                elif custom_field['name'] == 'Location (GPS) Latitude':
                    custom_field_value = lat
                elif custom_field['name'] == 'Location (GPS) Longitude':
                    custom_field_value = lng
                elif custom_field['name'] == 'Date Scheduled':
                    custom_field_value = fake.date_between_dates(date_start=datetime.date(2019, 1, 1))
                else:
                    custom_field_value = None

                url = f"{base_url}/cases/{case['id']}/custom_fields/{custom_field['id']}"
                data = {"value": custom_field_value}
                custom_field_request = requests.put(url, data=json.dumps(data, default=str), headers=request_headers)
                if custom_field_request.status_code != 200:
                    application.logger.error("Error updating case custom field")
                    application.logger.error(f"STATUS CODE = {custom_field_request.status_code}")
                    application.logger.error(json.dumps(custom_field_request.json(), indent=4, default=str))
    else:
        application.logger.error("Error getting cases")
        application.logger.error(f"STATUS CODE = {cases_request.status_code}")
        application.logger.error(json.dumps(cases_request.json(), indent=4, default=str))

    application.logger.info("*" * 80)
    application.logger.info("LOADING CUSTOM FIELDS FOR CASES COMPLETE")
    application.logger.info("*" * 80)

    application.logger.info("start reporting database, rescan metabase")
    post_rescan_request = requests.post(
        f'{base_url}/reset-reporting',
        data='',
        headers=request_headers)
    post_rescan_request_code = post_rescan_request.status_code

    if post_survey_request_status_code != 200:
        application.logger.error("Error posting rebuild mongodb, rescan metabase")
        application.logger.error(f"STATUS CODE = {post_rescan_request_code}")
        application.logger.error(json.dumps(post_rescan_request.json(), indent=4, default=str))
        sys.exit(0)

    application.logger.info("successfully rebuild mongo, rescan metabase")

    application.logger.info("end loading the dev dataset")


if __name__ == "__main__":
    application.run()
