import os
import logging
import json
import psycopg2
from sqlalchemy.schema import DropTable
from sqlalchemy.ext.compiler import compiles
from faker import Faker
import pytest
from flask_jwt_extended import create_access_token
from flask import current_app
from app import create_app, db, models
from . import factories


@compiles(DropTable, "postgresql")
def _compile_drop_table(element, compiler, **kwargs):
    return compiler.visit_drop_table(element) + " CASCADE"


@pytest.fixture()
def test_client():
    """Flask test client to access the API"""
    eps_api_app = create_app("testing")
    testing_client = eps_api_app.test_client()
    ctx = eps_api_app.app_context()
    ctx.push()
    yield testing_client
    ctx.pop()


@pytest.fixture()
def test_app():
    """Create application for the tests."""
    _app = create_app("testing")
    _app.logger.setLevel(logging.CRITICAL)
    ctx = _app.test_request_context()
    ctx.push()

    yield _app

    ctx.pop()


@pytest.fixture()
def test_db(test_client):
    """Database to use for testing"""
    fake = Faker()

    db.drop_all()
    db.Model.metadata.drop_all(bind=db.engine)
    db.create_all()
    db.session.commit()

    # clear out testing data db
    data_db_conn = psycopg2.connect(os.environ.get('DATA_DB_URI', 'postgresql:///data_test_pg'))
    cur = data_db_conn.cursor()
    sql = """
DO $$ DECLARE
  r RECORD;
BEGIN
  FOR r IN (SELECT tablename FROM pg_tables WHERE schemaname = current_schema() AND tablename <> 'spatial_ref_sys') LOOP
    EXECUTE 'DROP TABLE ' || quote_ident(r.tablename) || ' CASCADE';
  END LOOP;
END $$;
    """
    cur.execute(sql)
    data_db_conn.commit()
    cur.close()
    data_db_conn.close()

    models.Role.insert_roles()
    models.SurveyResponseStatus.insert_survey_response_statuses()
    models.CaseStatus.insert_case_statuses()

    admin_role = models.Role.query.filter_by(name='Admin').first()
    data_reader_role = models.Role.query.filter_by(default=True).first()
    data_collector_role = models.Role.query.filter_by(name='Data Collector').first()
    project_manager_role = models.Role.query.filter_by(name='Project Manager').first()

    admin_user = models.User(
        email='ilabtoolkit@gmail.com',
        username='admin',
        password='admin',
        name='Admin User',
        role=admin_role
    )

    data_reader_user = models.User(
        email=fake.email(),
        username='datareader',
        password='datareader',
        name=fake.name(),
        role=data_reader_role
    )

    data_collector_user = models.User(
        email=fake.email(),
        username='datacollector',
        password='datacollector',
        name=fake.name(),
        role=data_collector_role
    )

    project_manager_user = models.User(
        email=fake.email(),
        username='projectmanager',
        password='projectmanager',
        name=fake.name(),
        role=project_manager_role
    )

    db.session.add(admin_user)
    db.session.add(data_reader_user)
    db.session.add(data_collector_user)
    db.session.add(project_manager_user)
    db.session.commit()

    yield db
    # leave the tables intact after testing in case we want to examine them


@pytest.fixture()
def admin_user():
    """The admin user from the test database"""
    return models.User.query.filter_by(username='admin').first()


@pytest.fixture()
def admin_access_token(admin_user):
    """Access token for the admin user"""
    return create_access_token(identity=admin_user.id)


@pytest.fixture()
def project_manager_user():
    """The project manager from the test database"""
    return models.User.query.filter_by(username='projectmanager').first()


@pytest.fixture()
def data_collector_user():
    """The data collector user from the test database"""
    return models.User.query.filter_by(username='datacollector').first()


@pytest.fixture()
def data_collector_access_token(data_collector_user):
    """Access token for the data collector user"""
    return create_access_token(identity=data_collector_user.id)


@pytest.fixture()
def user_with_no_permissions():
    """A user that has no permissions"""
    fake = Faker()

    role_with_no_permissions = models.Role(name=fake.job(), permissions=0)
    db.session.add(role_with_no_permissions)
    db.session.commit()
    user_with_no_permissions = models.User(email=fake.email(), username=fake.user_name(), password=fake.password(),
                                           name=fake.name(), role=role_with_no_permissions)
    db.session.add(user_with_no_permissions)
    db.session.commit()

    return user_with_no_permissions


@pytest.fixture()
def project_data():
    """Dictionary of project data"""
    return {
        "name": "ADVANCE Brazil",
        "title": "Brazilian ADVANCE Project Eliminating Exploitive Child Labor through Education and Livelihoods",
        "organization": "IMPAQ International",
        "agreement_number": "IL-23979-13-75-K",
        "start_date": "2018-01-01",
        "end_date": "2022-12-31",
        "funding_amount": 10000000,
        "location": "Brasília, Brazil"
    }


@pytest.fixture()
def project_model(project_data, admin_user):
    """Project model with data"""
    return models.Project(name=project_data['name'], title=project_data['title'],
                          organization=project_data['organization'], agreement_number=project_data['agreement_number'],
                          start_date=project_data['start_date'], end_date=project_data['end_date'],
                          funding_amount=project_data['funding_amount'], location=project_data['location'],
                          created_by=admin_user, updated_by=admin_user)


@pytest.fixture()
def basic_test_survey(test_db, admin_user):
    """Basic Survey for testing"""
    survey = models.Survey(name='Basic Test Survey', structure={}, reporting_table_name='basic_test_survey',
                           created_by=admin_user, updated_by=admin_user)
    test_db.session.add(survey)
    test_db.session.commit()
    return survey


@pytest.fixture()
def test_survey(test_client, admin_access_token):
    structure = {"pages": [{"name": "page1", "elements": [{"type": "text", "name": "question1"}]}],
                 "name": "Test Survey"}
    response = test_client.post('/surveys/', data=json.dumps({'name': 'Test Survey', 'structure': structure}),
                                headers={'Content-Type': 'application/json',
                                         'Authorization': f"Bearer {admin_access_token}"})
    return response.get_json()


@pytest.fixture()
def basic_case_definition(test_db, basic_test_survey, admin_user):
    """Basic Case Definition for testing"""
    # example using a factory
    # cd = CaseDefinitionFactory.create(created_by_id=admin_user.id, updated_by_id=admin_user.id)
    cd = models.CaseDefinition(key='BCD', name='Basic Case Definition', created_by=admin_user, updated_by=admin_user)

    cd.surveys.append(basic_test_survey)

    cd.documents.append(models.CaseDefinitionDocument(name='Test Case Definition Document'))

    test_db.session.add(cd)
    test_db.session.commit()

    cd.reporting_table_name = current_app.reporting_service.create_case_table(cd)
    test_db.session.commit()

    return cd


@pytest.fixture()
def basic_case(test_db, basic_case_definition, admin_user):
    """Basic Case for testing"""
    case = models.Case(name='Basic Case', case_definition_id=basic_case_definition.id, created_by=admin_user,
                       updated_by=admin_user)

    test_db.session.add(case)
    test_db.session.commit()

    return case


@pytest.fixture()
def list_of_basic_cases(test_db, basic_case_definition, admin_user):
    """List of 10 basic cases"""
    cases = []

    for idx in range(1, 11):
        case = models.Case(name=f"Basic Case {idx}", case_definition_id=basic_case_definition.id,
                           created_by=admin_user, updated_by=admin_user)

        cases.append(case)
        test_db.session.add(case)
    test_db.session.commit()

    return cases


@pytest.fixture()
def full_case(test_db, basic_test_survey, basic_case_definition, admin_user):
    """Fully filled out case. Object contains case information including all child objects. Records included
        * case
        * case definition
        * survey
        * survey responses
        * uploaded files
        * notes
    """

    case = models.Case(name='Full Case', case_definition_id=basic_case_definition.id, created_by=admin_user,
                       updated_by=admin_user)

    case.responses.append(models.SurveyResponse(survey_id=basic_test_survey.id, structure={}, created_by=admin_user,
                                                updated_by=admin_user))

    test_db.session.add(case)
    test_db.session.commit()

    note = models.Note(
        model_id=case.id,
        model_name='Case',
        note='Test Case Note',
        created_by=admin_user,
        updated_by=admin_user
    )

    # this does actually need to point to a real file. we just need a db record
    file = models.UploadedFile(
        model_id=case.id,
        model_name='Case',
        created_by=admin_user
    )

    test_db.session.add(note)
    test_db.session.add(file)
    test_db.session.commit()

    return case
