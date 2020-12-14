import psycopg2
from dateutil import parser
from flask import current_app
from ascend_survey_js_parser.utils import pg_utils


class CustomFieldParseException(Exception):
    pass


class CaseReportingTableDDLGenerator:

    def __init__(self, db_uri):
        self.db_uri = db_uri

    def _mogrify_sql(self, sql):
        data_db_conn = psycopg2.connect(self.db_uri)
        cur = data_db_conn.cursor()

        return cur.mogrify(sql)

        cur.close()
        data_db_conn.close()

    def _find_selection(self, selections, search_id):
        try:
            return next((option for option in selections if option['id'] == int(search_id)), None)
        except:
            return None

    def _generate_ddl_for_custom_field(self, custom_field):
        column_name = pg_utils.get_pg_friendly_name(custom_field['name'])

        if custom_field['field_type'] in ['text', 'textarea', 'radio_button', 'select']:
            return f"{column_name} text"
        elif custom_field['field_type'] in ['check_box', 'rank_list']:
            return f"{column_name} text[]"
        elif custom_field['field_type'] == 'date':
            return f"{column_name} date"
        elif custom_field['field_type'] == 'number':
            return f"{column_name} float"
        else:
            raise CustomFieldParseException(f"Unknown custom field type: {custom_field['field_type']}")

    def _get_custom_field_value(self, custom_field):
        current_app.logger.info(f"custom_field = {custom_field}")

        if custom_field['field_type'] in ['text', 'textarea', 'number']:
            return custom_field['value']
        elif custom_field['field_type'] in ['radio_button', 'select']:
            selected = self._find_selection(custom_field['selections'], custom_field['value'])
            if selected:
                return f"({selected['id']}) {selected['value']}"
            else:
                return None
        elif custom_field['field_type'] == 'check_box':
            if custom_field['value']:
                checked_values = []
                for value in custom_field['value']:
                    selected = self._find_selection(custom_field['selections'], value)
                    if selected:
                        checked_values.append(f"({selected['id']}) {selected['value']}")
                return checked_values
            else:
                return None
        elif custom_field['field_type'] == 'rank_list':
            if custom_field['value']:
                ranked_values = []
                for value in sorted(custom_field['value'], key=lambda i: i['rank']):
                    selected = self._find_selection(custom_field['selections'], value['id'])
                    if selected:
                        ranked_values.append(f"({selected['id']}) {selected['value']}")
                return ranked_values
            else:
                return None
        elif custom_field['field_type'] == 'date':
            if custom_field['value']:
                try:
                    date_value = parser.parse(custom_field['value'])
                    return date_value
                except ValueError as ve:
                    print(f"error parsing date value: {ve}")
                    return None
            else:
                return None
            pass
        else:
            raise CustomFieldParseException(f"Unknown custom field type: {custom_field['field_type']}")

    def _get_case_table_name(self, case_definition_name):
        return f"{pg_utils.get_pg_friendly_name(case_definition_name)}_cases"

    # table generated from case definition
    def generate_case_table_ddl(self, case_definition, database_user_to_grant):
        case_table_name = self._get_case_table_name(case_definition.name)
        table_sql = (f"CREATE TABLE IF NOT EXISTS {case_table_name} (id SERIAL, "
                     "case_id integer not null, key varchar not null, "
                     "name varchar not null, description text, "
                     "status_id integer not null, status varchar not null, "
                     "case_type_id integer not null, "
                     "case_type_name varchar not null, "
                     "assigned_to varchar(64), ")
        for custom_field in case_definition.custom_fields:
            custom_field_ddl = self._generate_ddl_for_custom_field(custom_field)
            table_sql += f"{custom_field_ddl}, "
        table_sql += ("created_at timestamp without time zone not null, "
                      "created_by varchar(64) not null, "
                      "updated_at timestamp without time zone not null, "
                      "updated_by varchar(64) not null, "
                      "created_location_latitude double precision, "
                      "created_location_longitude double precision, "
                      "updated_location_latitude double precision, "
                      "updated_location_longitude double precision, PRIMARY KEY (id));")
        grant_sql = f"GRANT SELECT ON TABLE {case_table_name} TO {database_user_to_grant};"

        return case_table_name, table_sql, grant_sql

    def generate_case_insert_ddl(self, case, created_location, updated_location):
        """generate ddl plus tuple of values"""
        case_table_name = case.case_definition.reporting_table_name
        if case.assigned_to:
            assigned_to = case.assigned_to.name
        else:
            assigned_to = None
        params = [case.id, case.key, case.name, case.description, case.status_id, case.status.name,
                  case.case_definition.id, case.case_definition.name, assigned_to]

        insert_sql = (f"insert into {case_table_name} (case_id, key, name, description, status_id, status, "
                      "case_type_id, case_type_name, assigned_to, ")

        # add custom field column names
        for custom_field in case.custom_fields:
            column_name = pg_utils.get_pg_friendly_name(custom_field['name'])
            insert_sql += f"{column_name}, "

            params.append(self._get_custom_field_value(custom_field))

        custom_field_placeholders = ', '.join(['%s'] * len(case.custom_fields))
        insert_sql += ('created_at, created_by, updated_at, updated_by, created_location_latitude, '
                       'created_location_longitude, updated_location_latitude, updated_location_longitude) '
                       'values (%s, %s, %s, %s, %s, %s, %s, %s, %s, ')
        if custom_field_placeholders:
            insert_sql += f'{custom_field_placeholders}, '
        insert_sql += '%s, %s, %s, %s, %s, %s, %s, %s);'
        params += [case.created_at, case.created_by.username, case.updated_at, case.updated_by.username]
        if created_location:
            params += [created_location[0], created_location[1]]
        else:
            params += [None, None]
        if updated_location:
            params += [updated_location[0], updated_location[1]]
        else:
            params += [None, None]

        return insert_sql, tuple(params)

    def generate_case_update_ddl(self, case, updated_location):
        case_table_name = case.case_definition.reporting_table_name
        if case.assigned_to:
            assigned_to = case.assigned_to.name
        else:
            assigned_to = None

        update_sql = (f"update {case_table_name} set name = %s, description = %s, status_id = %s, status = %s, "
                      "case_type_name = %s, assigned_to = %s, ")
        update_params = [case.name, case.description, case.status_id, case.status.name, case.case_definition.name,
                         assigned_to]

        for custom_field in case.custom_fields:
            column_name = pg_utils.get_pg_friendly_name(custom_field['name'])
            update_sql += f"{column_name} = %s, "

            update_params.append(self._get_custom_field_value(custom_field))

        update_sql += ('updated_at = %s, updated_by = %s, updated_location_latitude = %s, '
                       'updated_location_longitude = %s where case_id = %s;')

        if updated_location:
            updated_latitude = updated_location[0]
            updated_longitude = updated_location[1]
        else:
            updated_latitude = None
            updated_longitude = None

        update_params += [case.updated_at, case.updated_by.username, updated_latitude, updated_longitude, case.id]

        return update_sql, tuple(update_params)
