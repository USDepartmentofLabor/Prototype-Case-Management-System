import os
import datetime
import random
import json
from app import models
from ..data_loader_helpers import fake, rebuild_db, make_request, get_unique_name, RequestType, \
    get_occupational_safety_and_health_issues_record, get_wage_and_hour_issues_record, get_inspector_conclusions_record, \
    get_workplace_accidents_record, get_COVID_19_health_checklist_record
from .impaq_dataset import dataset


class IMPAQDatasetLoader:

    def __init__(self, url, application, db):
        self.url = url
        self.application = application
        self.logger = application.logger
        self.db = db

        self.perm_vars = vars(models.Permission)
        self.perm_names = [attr for attr in self.perm_vars if
                           not attr.startswith('__') and not attr.startswith('MSG_') and not attr.startswith(
                               'DESC_') and not attr.startswith('does_have')]

        self.logger.info("data loader created")

    def start_load(self):
        company_names = []

        self.logger.info(f"starting load using URL {self.url}")

        self.logger.info("rebuilding data database")
        rebuild_db(self.db)

        self.logger.info('dropping reporting tables')
        self.application.reporting_service.delete_all()

        self.application.logger.info('loading roles')
        for role in dataset['roles']:
            self.logger.info(f" |-> loading {role['name']}")
            db_role = models.Role.query.filter_by(name=role['name']).first()
            if db_role is None:
                db_role = models.Role(name=role['name'])
            db_role.reset_permissions()
            for perm in role['permissions']:
                db_role.add_permission(self.perm_vars[perm])
            db_role.default = role['default']
            self.db.session.add(db_role)
            self.db.session.commit()
            role['sys_id'] = db_role.id

        admin_role = models.Role.query.filter_by(name='Admin').first()
        project_manager_role = models.Role.query.filter_by(name='Project Manager').first()
        labor_inspector_role = models.Role.query.filter_by(name='Labor Inspector').first()

        self.application.logger.info('loading survey response statuses')
        models.SurveyResponseStatus.insert_survey_response_statuses()

        self.application.logger.info('loading case statuses')

        for status in dataset['case_statuses']:
            db_status = models.CaseStatus.query.get(status['id'])

            if db_status is None:
                db_status = models.CaseStatus(
                    id=status['id'],
                    name=status['name'],
                    default=status['default'],
                    is_final=status['is_final'],
                    color=status['color']
                )
                self.db.session.add(db_status)
        self.db.session.commit()

        self.application.logger.info('loading superadmin')
        superadmin = dataset['superadmin']
        superuser = models.User(email=superadmin['email'],
                                username=superadmin['username'],
                                password=superadmin['password'],
                                name=superadmin['name'],
                                role=admin_role)
        self.db.session.add(superuser)
        self.db.session.commit()
        superadmin['sys_id'] = superuser.id

        self.application.logger.info('loading system properties')
        eps_property = models.EPSProperty(property='default_dashboard_id', value=None)
        self.db.session.add(eps_property)
        self.db.session.commit()

        self.application.logger.info("logging into API")
        url = f"{self.url}/auth/login"
        request_headers = {'Content-type': 'application/json'}
        loc = fake.latlng()
        data = {"login": "admin", "password": superadmin['password'], "latitude": loc[0], "longitude": loc[1]}
        auth_response = make_request(url=url, headers=request_headers, data=data, logger=self.logger,
                                     request_type=RequestType.Post)

        access_token = auth_response['access_token']
        self.application.logger.info(f" |-> successful login, token = {access_token}")

        request_headers = {'Content-type': 'application/json', 'Authorization': f"Bearer {access_token}"}

        self.application.logger.info("loading project information")
        url = f"{self.url}/project"
        data = dataset['project_info']
        _ = make_request(url=url, headers=request_headers, data=data, logger=self.logger, request_type=RequestType.Post)

        data_dir = os.path.join(os.getcwd(), 'data', 'impaq')

        self.application.logger.info("loading surveys")

        for survey in dataset['surveys']:
            self.application.logger.info(f" |-> loading survey {survey['name']}")
            with open(os.path.join(data_dir, survey['file'])) as form_file:
                form_data = json.load(form_file)
                data = {
                    "name": form_data['title'],
                    "structure": form_data
                }
                url = f'{self.url}/surveys/'

                survey_response = make_request(url=url, headers=request_headers, data=data, logger=self.logger,
                                               request_type=RequestType.Post)

                survey['sys_id'] = int(survey_response['id'])

        self.application.logger.info("creating case definitions")

        for case_defn in dataset['case_definitions']:
            self.application.logger.info(f" |-> creating case definition {case_defn['name']}")

            url = f'{self.url}/case_definitions/'
            data = {
                'key': case_defn['key'],
                'name': case_defn['name'],
                'description': case_defn['description'],
                'documents': case_defn['documents'],
                'custom_fields': case_defn['custom_fields']
            }

            case_defn_response = make_request(url=url, headers=request_headers, data=data, logger=self.logger,
                                              request_type=RequestType.Post)
            case_defn['sys_id'] = case_defn_response['id']
            self.application.logger.info("  |-> creating activity definitions")
            dataset_surveys = dataset['surveys']
            url = f'{self.url}/activity_definitions'
            act_defns = []
            for act_defn in case_defn['activity_definitions']:
                self.application.logger.info(f"   |-> creating activity definition {act_defn['name']}")
                act_defn_surveys = []
                for act_defn_survey_name in act_defn['surveys']:
                    found_survey_id = [ds['sys_id'] for ds in dataset_surveys if ds['name'] == act_defn_survey_name]
                    if found_survey_id:
                        act_defn_surveys += found_survey_id
                data = {
                    'name': act_defn['name'],
                    'description': act_defn['description'],
                    'case_definition_id': case_defn['sys_id'],
                    'surveys': act_defn_surveys
                }
                act_defn_response = make_request(url=url, headers=request_headers, data=data, logger=self.logger,
                                                 request_type=RequestType.Post)
                act_defns.append(act_defn_response)
                act_defn['sys_id'] = act_defn_response['id']

            self.application.logger.info("  |-> adding cases")

            for _ in range(random.randint(5, 10)):
                company_name = get_unique_name(fake.company, company_names)
                company_names.append(company_name)
                loc = fake.latlng()

                case_name = f"{company_name} Case"
                self.application.logger.info(f" |-> adding {case_name}")
                url = f"{self.url}/case_definitions/{case_defn['sys_id']}/cases"

                # custom fields
                custom_fields = []
                for custom_field in case_defn_response['custom_fields']:
                    lat, lng, city, *_ = fake.local_latlng()
                    if custom_field['name'] in ['Inspection Type', 'Business Sector', 'Region']:
                        custom_field_value = random.choice(custom_field['selections'])['id']
                    elif custom_field['name'] == 'Business Name':
                        custom_field_value = company_name
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
                    custom_fields.append({
                        'name': custom_field['name'],
                        'field_type': custom_field['field_type'],
                        'selections': custom_field['selections'],
                        'validation_rules': custom_field['selections'],
                        'case_definition_custom_field_id': custom_field['id'],
                        'custom_section_id': None,
                        'help_text': custom_field['help_text'],
                        'sort_order': custom_field['sort_order'],
                        'value': custom_field_value,
                        'model_type': 'Case'
                    })

                data = {
                    "name": case_name,
                    "description": f"This is the case for {company_name}. {' '.join(fake.paragraphs())}",
                    "case_definition_id": {case_defn['sys_id']},
                    "latitude": loc[0],
                    "longitude": loc[1],
                    "custom_fields": custom_fields
                }

                case_response = make_request(url=url, headers=request_headers, data=data, logger=self.logger,
                                             request_type=RequestType.Post)
                case_id = case_response['id']

                url = f'{self.url}/cases/{case_id}'
                data = {
                    'status_id': random.choice([1, 2, 3, 5])
                }
                _ = make_request(url=url, headers=request_headers, data=data, logger=self.logger,
                                 request_type=RequestType.Put)

                # do activities
                activity_names = ['Initial Inspection', 'Re-Inspection #1', 'Re-Inspection #2', 'Re-Inspection #3']
                for activity_name in activity_names:
                    if activity_name == 'Initial Inspection':
                        act_defn = [a for a in act_defns if a['name'] == 'Scheduled Inspection'][0]
                    else:
                        act_defn = [a for a in act_defns if a['name'] == 'Re-Inspection'][0]

                    self.application.logger.info(f"    |-> adding activity {activity_name} for {act_defn['name']}")
                    url = f'{self.url}/activities'
                    data = {
                        "activity_definition_id": act_defn['id'],
                        "case_id": case_id,
                        "name": activity_name,
                        "description": f"This is the {activity_name} for the {case_response['name']} case"
                    }
                    activity_response = make_request(url=url, headers=request_headers, data=data, logger=self.logger,
                                                     request_type=RequestType.Post)

                    if case_response['case_definition']['name'] == 'Occupational Safety and Health':
                        # Occupational Safety and Health Case
                        #   each activity gets on of Occupational Safety and Health Issues and Inspector Conclusions

                        self.application.logger.info(
                            "      |-> adding response for Occupational Safety and Health Issues")

                        loc = fake.latlng()
                        survey_id = [s['sys_id'] for s in dataset['surveys'] if
                                     s['file'] == 'occupational_safety_and_health_issues.json'][0]
                        survey_record = get_occupational_safety_and_health_issues_record()
                        url = f"{self.url}/surveys/{survey_id}/responses"
                        data = {
                            "survey_id": survey_id,
                            "structure": survey_record,
                            "source_type": "Activity",
                            "case_id": case_id,
                            "activity_id": activity_response['id'],
                            "latitude": loc[0],
                            "longitude": loc[1]
                        }
                        _ = make_request(url=url, headers=request_headers, data=data, logger=self.logger,
                                         request_type=RequestType.Post)

                        self.application.logger.info("      |-> adding response for Inspector Conclusions")

                        loc = fake.latlng()
                        survey_id = [s['sys_id'] for s in dataset['surveys'] if
                                     s['file'] == 'inspector_conclusions.json'][0]
                        survey_record = get_inspector_conclusions_record()
                        url = f"{self.url}/surveys/{survey_id}/responses"
                        data = {
                            "survey_id": survey_id,
                            "structure": survey_record,
                            "source_type": "Activity",
                            "case_id": case_id,
                            "activity_id": activity_response['id'],
                            "latitude": loc[0],
                            "longitude": loc[1]
                        }
                        _ = make_request(url=url, headers=request_headers, data=data, logger=self.logger,
                                         request_type=RequestType.Post)

                    elif case_response['case_definition']['name'] == 'Wage and Hour':
                        # Wage and Hour
                        #   each activity gets on of Wage and Hour Issues and Inspector Conclusions

                        self.application.logger.info(
                            "      |-> adding response for Wage and Hour Issues")

                        loc = fake.latlng()
                        survey_id = [s['sys_id'] for s in dataset['surveys'] if
                                     s['file'] == 'wage_and_hour_issues.json'][0]
                        survey_record = get_wage_and_hour_issues_record()
                        url = f"{self.url}/surveys/{survey_id}/responses"
                        data = {
                            "survey_id": survey_id,
                            "structure": survey_record,
                            "source_type": "Activity",
                            "case_id": case_id,
                            "activity_id": activity_response['id'],
                            "latitude": loc[0],
                            "longitude": loc[1]
                        }
                        _ = make_request(url=url, headers=request_headers, data=data, logger=self.logger,
                                         request_type=RequestType.Post)

                        self.application.logger.info("      |-> adding response for Inspector Conclusions")

                        loc = fake.latlng()
                        survey_id = [s['sys_id'] for s in dataset['surveys'] if
                                     s['file'] == 'inspector_conclusions.json'][0]
                        survey_record = get_inspector_conclusions_record()
                        url = f"{self.url}/surveys/{survey_id}/responses"
                        data = {
                            "survey_id": survey_id,
                            "structure": survey_record,
                            "source_type": "Activity",
                            "case_id": case_id,
                            "activity_id": activity_response['id'],
                            "latitude": loc[0],
                            "longitude": loc[1]
                        }
                        _ = make_request(url=url, headers=request_headers, data=data, logger=self.logger,
                                         request_type=RequestType.Post)
                    elif case_response['case_definition']['name'] == 'Workplace Accident':
                        # Workplace Accident
                        #   each activity gets one Workplace Accidents

                        self.application.logger.info("      |-> adding response for Workplace Accidents")

                        loc = fake.latlng()
                        survey_id = [s['sys_id'] for s in dataset['surveys'] if
                                     s['file'] == 'workplace_accidents.json'][0]
                        survey_record = get_workplace_accidents_record()
                        url = f"{self.url}/surveys/{survey_id}/responses"
                        data = {
                            "survey_id": survey_id,
                            "structure": survey_record,
                            "source_type": "Activity",
                            "case_id": case_id,
                            "activity_id": activity_response['id'],
                            "latitude": loc[0],
                            "longitude": loc[1]
                        }
                        _ = make_request(url=url, headers=request_headers, data=data, logger=self.logger,
                                         request_type=RequestType.Post)

                    elif case_response['case_definition']['name'] == 'COVID-19 Health Checklist':
                        # COVID-19 Health Checklist
                        #   each activity gets one COVID-19 Health Checklist

                        self.application.logger.info("      |-> adding response for COVID-19 Health Checklist")

                        loc = fake.latlng()
                        survey_id = [s['sys_id'] for s in dataset['surveys'] if
                                     s['file'] == 'COVID-19_health_checklist.json'][0]
                        survey_record = get_COVID_19_health_checklist_record()
                        url = f"{self.url}/surveys/{survey_id}/responses"
                        data = {
                            "survey_id": survey_id,
                            "structure": survey_record,
                            "source_type": "Activity",
                            "case_id": case_id,
                            "activity_id": activity_response['id'],
                            "latitude": loc[0],
                            "longitude": loc[1]
                        }
                        _ = make_request(url=url, headers=request_headers, data=data, logger=self.logger,
                                         request_type=RequestType.Post)

        self.logger.info("loading complete")
