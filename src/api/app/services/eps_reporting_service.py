import psycopg2
import sqlalchemy
from flask import current_app
from ascend_survey_js_parser.form_parser import SurveyJsonParser
from ascend_survey_js_parser.response_parser import SurveyResponseParser
from ascend_survey_js_parser.utils import pg_utils
from app.libs.case_reporting_table_ddl_generator import CaseReportingTableDDLGenerator


class EPSReportingServiceException(Exception):
    pass


class EPSReportingService:

    def __init__(self, db_uri):
        self.db_uri = db_uri
        self.data_db = sqlalchemy.create_engine(self.db_uri)

    def _get_coordinate(self, location):
        if location['latitude'] and location['longitude']:
            return location['latitude'], location['longitude']
        else:
            return None

    def create_survey(self, survey, db_user):
        pg_table_name = pg_utils.get_pg_friendly_name(survey.name)
        form = SurveyJsonParser().parse(survey.structure, pg_table_name)
        create_statements = form.get_create_statements(db_user)
        session = self.data_db.connect()
        for statement in create_statements:
            session.execute(statement)
        session.close()
        return pg_table_name

    # TODO: add change survey

    def delete_survey(self, survey_name):
        pg_table_name = pg_utils.get_pg_friendly_name(survey_name)
        sql = f"DROP TABLE IF EXISTS {pg_table_name} CASCADE;"
        session = self.data_db.connect()
        session.execute(sql)
        session.close()

    def create_response(self, survey, response):
        created_location = self._get_coordinate(response.__getstate__()['created_location'])
        updated_location = self._get_coordinate(response.__getstate__()['updated_location'])

        pg_table_name = pg_utils.get_pg_friendly_name(survey.name)
        if response.case:
            case_id = response.case.id
            case_name = response.case.name
            source_type = 'Case'
        else:
            case_id = None
            case_name = None
            source_type = 'Standalone'

        insert_statements_rtn = SurveyResponseParser().parse_response(form_json=survey.structure,
                                                                      form_title=pg_table_name,
                                                                      response_json=response.structure,
                                                                      response_id=response.id, case_id=case_id,
                                                                      case_name=case_name, source_type=source_type,
                                                                      created_location=created_location,
                                                                      updated_location=updated_location,
                                                                      created_by=response.created_by.username,
                                                                      last_updated_by=response.updated_by.username)
        session = self.data_db.connect()
        for statement in insert_statements_rtn:
            session.execute(statement)
        session.close()

    # TODO: add change response
    # TODO: add delete response

    # TODO: add new case survey
    # TODO: add change case survey
    # TODO: add delete case survey
    # TODO: add change case response
    # TODO: add delete case response

    def create_case_table(self, case_definition):

        generator = CaseReportingTableDDLGenerator(self.db_uri)
        pg_table_name, *statements = generator.generate_case_table_ddl(case_definition, 'metabase_pg_user')

        session = self.data_db.connect()
        for statement in statements:
            session.execute(statement)
        session.close()

        return pg_table_name

    def delete_case_table(self, case_table_name):
        if not case_table_name:
            raise EPSReportingServiceException("Case table name to delete cannot be null")

        drop_sql = f"DROP TABLE IF EXISTS {case_table_name} CASCADE;"

        session = self.data_db.connect()
        session.execute(drop_sql)
        session.close()

    # TODO: update case definition -> update case reporting table, change table structure

    def add_case_row(self, case):
        created_location = self._get_coordinate(case.__getstate__()['created_location'])
        updated_location = self._get_coordinate(case.__getstate__()['updated_location'])

        generator = CaseReportingTableDDLGenerator(self.db_uri)
        insert_sql, insert_params = generator.generate_case_insert_ddl(case, created_location, updated_location)
        self._run_query(insert_sql, insert_params)

    def delete_case_row(self, case_table_name, case_id):
        if not case_table_name:
            raise EPSReportingServiceException("Case table name cannot be null")

        if not case_id:
            raise EPSReportingServiceException("Case record id cannot be null")

        delete_sql = f"delete from {case_table_name} where case_id = {case_id};"

        session = self.data_db.connect()
        session.execute(delete_sql)
        session.close()

    def update_case_row(self, case):
        updated_location = self._get_coordinate(case.__getstate__()['updated_location'])
        generator = CaseReportingTableDDLGenerator(self.db_uri)
        update_sql, update_params = generator.generate_case_update_ddl(case, updated_location)
        current_app.logger.info(f"update_sql = {update_sql}, update_params = {update_params}")
        self._run_query(update_sql, update_params)

    def delete_all(self):

        data_db_conn = psycopg2.connect(self.db_uri)
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

    def _run_query(self, sql, params):
        data_db_conn = psycopg2.connect(self.db_uri)
        cur = data_db_conn.cursor()
        cur.execute(sql, params)
        data_db_conn.commit()
        cur.close()
        data_db_conn.close()
