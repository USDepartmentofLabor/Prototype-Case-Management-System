import sys
import json
import enum
import random
import requests
from faker import Faker

fake = Faker()


class RequestType(enum.Enum):
    Post = 1
    Put = 2
    Get = 3
    Delete = 4


class YesNoType(enum.Enum):
    YesNo = 1
    YesNoNa = 2


def decision(probability):
    return random.random() < probability


def rebuild_db(db):
    db.drop_all()
    db.create_all()
    db.session.commit()


def make_request(url: str, headers: object, data: object, logger, request_type: RequestType):
    try:
        if request_type == RequestType.Post:
            request = requests.post(
                url=url,
                data=json.dumps(data,
                                default=str),
                headers=headers)
        elif request_type == RequestType.Put:
            request = requests.put(
                url=url,
                data=json.dumps(data,
                                default=str),
                headers=headers)
        else:
            request = requests.get(
                url=url,
                headers=headers)
        request_status_code = request.status_code

        if request_status_code != 200:
            logger.error("Error logging in to the API")
            logger.error(f"STATUS CODE = {request_status_code}")
            if request.json():
                logger.error(json.dumps(request.json(), indent=4, default=str))
            sys.exit(0)

        return request.json()

    except requests.exceptions.ConnectionError as ce:
        logger.error(f"Error connecting to API: {ce}")
        sys.exit(0)
    except:
        logger.error("Unexpected error:", sys.exc_info()[0])
        sys.exit(0)


def get_unique_name(gen_func, name_list):
    n = gen_func()
    while n in name_list:
        n = gen_func()
    return n


def get_occupational_safety_and_health_issues_record():
    health_and_safety_options = ['Repetitive strain injuries', 'Stress related to pressure from supervisors',
                                 'Unsafe equipment', 'Other', 'None', 'Current form']
    record = {'required_safety_devices_exist': random.choice(['yes', 'no', 'na']),
              'dangerous_machines_guarded': random.choice(['yes', 'no']),
              'staff_observing_safety_rules': random.choice(['yes', 'no', 'na']),
              'ppe_used': random.choice(['yes', 'no']),
              'tools_secured': random.choice(['yes', 'no']),
              'ladders_safe': random.choice(['yes', 'no']),
              'scaffolding_safe': random.choice(['yes', 'no']),
              'kept_clean': {
                  'workstation': random.choice(['yes', 'no']),
                  'floors': random.choice(['yes', 'no']),
                  'passageways': random.choice(['yes', 'no']),
              },
              'sufficient_exist_amd_extinguishers': random.choice(['yes', 'no']),
              'exits_marked_unobstructed': random.choice(['yes', 'no']),
              'extinguishers_marked_unobstructed': random.choice(['yes', 'no']),
              'no_evidence_unsafe_work_practices': random.choice(['yes', 'no']),
              'workers_familiar_with_escape_routes': random.choice(['yes', 'no']),
              'routes_unobstructed': random.choice(['yes', 'no']),
              'know_location_nearest_extinguishers': random.choice(['yes', 'no']),
              'supervisors_encourage_follow_safety_rules': random.choice(['yes', 'no']),
              'training_provided': random.choice(['yes', 'no']),
              'health_and_safety_problems': random.choices(health_and_safety_options)}

    # if record['required_safety_devices_exist'] in ['no', 'na']:
    #     record['required_safety_devices_exist_justification'] = fake.paragraph()
    #     # if decision(.3): # True 30% of time
    #     #     record['required_safety_devices_exist_documentation'] = some_kind_of_file

    documentation_properties = [('required_safety_devices_exist', YesNoType.YesNoNa),
                                ('dangerous_machines_guarded', YesNoType.YesNo),
                                ('staff_observing_safety_rules', YesNoType.YesNoNa),
                                ('ppe_used', YesNoType.YesNo),
                                ('tools_secured', YesNoType.YesNo),
                                ('ladders_safe', YesNoType.YesNo),
                                ('scaffolding_safe', YesNoType.YesNo),
                                ('sufficient_exist_amd_extinguishers', YesNoType.YesNo),
                                ('exits_marked_unobstructed', YesNoType.YesNo),
                                ('extinguishers_marked_unobstructed', YesNoType.YesNo),
                                ('no_evidence_unsafe_work_practices', YesNoType.YesNo),
                                ('workers_familiar_with_escape_routes', YesNoType.YesNo),
                                ('routes_unobstructed', YesNoType.YesNo),
                                ('know_location_nearest_extinguishers', YesNoType.YesNo),
                                ('supervisors_encourage_follow_safety_rules', YesNoType.YesNo),
                                ('training_provided', YesNoType.YesNo)
                                ]

    for doc_prop in documentation_properties:
        if doc_prop[1] == YesNoType.YesNoNa:
            check_array = ['no', 'na']
        else:
            check_array = ['no']

        if record[doc_prop[0]] in check_array:
            record[f"{doc_prop[0]}_justification"] = fake.paragraph()
            # if decision(.3): # True 30% of time
            #     record['required_safety_devices_exist_documentation'] = some_kind_of_file

    if any([v == 'no' for v in record['kept_clean'].values()]):
        record['kept_clean_justification'] = fake.paragraph()

    # dangerous_machines_guarded_justification
    # dangerous_machines_guarded_documentation
    # staff_observing_safety_rules_justification
    # staff_observing_safety_rules_documentation
    # ppe_used_justification
    # ppe_used_documentation
    # tools_secured_justification
    # tools_secured_documentation
    # ladders_safe_justification
    # ladders_safe_documentation
    # scaffolding_safe_justification
    # scaffolding_safe_documentation
    # kept_clean_justification
    # kept_clean_documentation
    # sufficient_exist_amd_extinguishers_justification
    # sufficient_exist_amd_extinguishers_documentation
    # exits_marked_unobstructed_documentation
    # extinguishers_marked_unobstructed_justification
    # extinguishers_marked_unobstructed_documentation
    # no_evidence_unsafe_work_practices_justification
    # no_evidence_unsafe_work_practices_documentation
    # workers_familiar_with_escape_routes_justification
    # workers_familiar_with_escape_routes_documentation
    # routes_unobstructed_justification
    # routes_unobstructed_documentation
    # know_location_nearest_extinguishers_justification
    # know_location_nearest_extinguishers_documentation
    # supervisors_encourage_follow_safety_rules_justification
    # supervisors_encourage_follow_safety_rules_documentation
    # training_provided_justification
    # training_provided_documentation

    return record


def get_wage_and_hour_issues_record():
    record = {'written_contracts_issued': random.choice(['yes', 'no']),
              'remuneration_paid': random.choice(['yes', 'no']),
              'paid_proper_intervals': random.choice(['yes', 'no']),
              'deductions_calculated_correctly': random.choice(['yes', 'no']),
              'benefits_paid': random.choice(['yes', 'no']),
              'allowances_paid': random.choice(['yes', 'no']),
              'required_breaks_complied_with': random.choice(['yes', 'no']),
              'overtime_within_legal_limits': random.choice(['yes', 'no']),
              'work_properly_authorized': random.choice(['yes', 'no'])}

    record_keys = list(record.keys())
    for key in record_keys:
        if record[key] == 'no':
            record[f"{key}_justification"] = fake.paragraph()

    # written_contract_issued_justification
    # written_contract_issued_documentation
    # remuneration_paid_justification
    # remuneration_paid_documentation
    # paid_proper_intervals_justification
    # paid_proper_intervals_documentation
    # deductions_calculated_correctly_justification
    # deductions_calculated_correctly_documentation
    # benefits_paid_justification
    # benefits_paid_documentation
    # allowances_paid_justification
    # allowances_paid_documentation
    # required_breaks_complied_with_justification
    # required_breaks_complied_with_documentation
    # overtime_within_legal_limits_justification
    # overtime_within_legal_limits_documentation
    # work_properly_authorized_justification
    # work_properly_authorized_documentation

    return record

def get_inspector_conclusions_record():
    record = {
        'was_inspection_successfully_completed': fake.boolean(),
        'is_worksite_in_compliance': fake.boolean(),
        'was_general_std_of_working_conditions_summarized': fake.boolean(),
        'did_discuss_conditions': fake.boolean(),
        'did_propose_priorities': fake.boolean(),
        'did_state_measures_implemented': fake.boolean(),
        'did_inform_employer': fake.boolean(),
        'did_inform_those_present': fake.boolean()
    }

    record_keys = list(record.keys())
    for key in record_keys:
        if record[key]:
            record[f"{key}_justification"] = fake.paragraph()

    '''
    was_inspection_successfully_completed_justification
    was_inspection_successfully_completed_documentation
    is_worksite_in_compliance_justification
    is_worksite_in_compliance_documentation
    was_general_std_of_working_conditions_summarized_justification
    was_general_std_of_working_conditions_summarized_documentation
    did_discuss_conditions_justification
    did_discuss_conditions_documentation
    did_propose_priorities_justification
    did_propose_priorities_documentation
    did_state_measures_implemented_justification
    did_state_measures_implemented_documentation
    did_inform_employer_justification
    did_inform_employer_documentation
    did_inform_those_present_justification
    did_inform_those_present_documentation
    '''

    return record

def get_COVID_19_health_checklist_record():
    practices_coverage_options = [
        'assessing employee health (e.g., assessing symptoms) prior to and/or upon arrival to work?',
        'what to do when an employee is symptomatic (has symptoms of COVID-19) or has tested positive for the virus that causes COVID-19?',
        'what to do when an employee has been exposed to co-workers or other people (e.g., family or friends) who have symptoms consistent with COVID-19 or who have tested positive for the virus that causes COVID-19?',
        'practices to protect workers at increased risk of severe illness, such as older adults and people of any age with a chronic medical condition?'
    ]
    record = {
        'have_assessment_and_control_plan': fake.boolean(),
        'has_employee_provided_poc': fake.boolean(),
        'has_employer_established_practices': fake.boolean(),
        'practices_coverage': random.choices(practices_coverage_options),
        'have_provided_info_and_training': fake.boolean(),
        'has_employer_posted_flyers': fake.boolean(),
        'has_employer_posted_simple_posters': fake.boolean(),
        'has_employer_made_available_facilities': fake.boolean(),
        'does_employer_have_procedures_for_ppe': fake.boolean(),
        'was_training_provided_for_ppe': fake.boolean(),
        'have_stay_at_home_precedures': fake.boolean(),
        'have_procedures_to_isloate_symptomatic_people': fake.boolean(),
        'have_procedure_for_alt_transpo': fake.boolean(),
        'have_contract_tracing_procedures': fake.boolean(),
        'have_procedures_for_exposure_notification': fake.boolean(),
        'have_workers_contact_info': fake.boolean(),
        'have_procedures_to_clean_used_surfaces': fake.boolean(),
        'do_procedures_include_closing_off_areas': fake.boolean(),
        'do_procedures_include_protecting_cleanup_crew': fake.boolean(),
        'do_procedures_include_vehicle_cleanup': fake.boolean()
    }

    return record

def get_workplace_accidents_record():
    record = {
        'date_occured': fake.date(),
        'location': fake.address(),
        'what_happened': fake.paragraph(),
        'who_injured': fake.name(),
        'contributory_factors': fake.paragraph(),
        'prevention': fake.paragraph(),
        'was_breach_of_law': fake.boolean(),
        'due_to_ignorance_or_carelessness': fake.boolean(),
        'due_to_physical_or_mental_state': fake.boolean()
    }

    return record