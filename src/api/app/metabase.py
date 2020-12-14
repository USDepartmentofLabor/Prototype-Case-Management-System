import sys
import traceback
import flask
from app import helpers, models


def insert_user(user):
    try:
        metabase = helpers.get_metabase_connection()

        metabase_user = {
            'first_name': user['username'],
            'last_name': '',
            'email': user['email'],
            'password': user['password'],
            'group_ids': None,
            'login_attributes': None
        }

        resp, ok = metabase.add_user(metabase_user)

        if ok:
            return resp.id
        else:
            flask.current_app.logger.warning(f'Failed to insert user to metabase with response: {resp}')
    except:
        e = sys.exc_info()[0]
        flask.current_app.logger.error(f"Error trying to connect to Metabase: {e}")
    return None


def update_user(user_id, updates):
    try:
        metabase = helpers.get_metabase_connection()

        metabase_updates = {}

        if 'username' in updates:
            metabase_updates['first_name'] = updates['username']

        if 'email' in updates:
            metabase_updates['email'] = updates['email']

        if 'password' in updates:
            metabase_updates['password'] = updates['password']

        resp, ok = metabase.update_user(user_id, metabase_updates)

        if not ok:
            flask.current_app.logger.warning(f'Failed to update metabase user with response: {resp}')
    except:
        e = sys.exc_info()[0]
        flask.current_app.logger.error(f"Error trying to connect to Metabase: {e}")


def deactivate_user(user_id):
    try:
        metabase = helpers.get_metabase_connection()

        resp, ok = metabase.deactivate_user(user_id)

        if not ok:
            flask.current_app.logger.warning(f'Failed to deactivate metabase user with response: {resp}')
    except:
        e = sys.exc_info()[0]
        flask.current_app.logger.error(f"Error trying to connect to Metabase: {e}")


def reactivate_user(user_id):
    try:
        metabase = helpers.get_metabase_connection()

        resp, ok = metabase.reactivate_user(user_id)

        if not ok:
            flask.current_app.logger.warning(f'Failed to reactivate metabase user with response: {resp}')
    except:
        e = sys.exc_info()[0]
        flask.current_app.logger.error(f"Error trying to connect to Metabase: {e}")


def get_dashboards():
    dashboards_response = []

    try:
        default_dashboard = models.EPSProperty.query.filter_by(property='default_dashboard_id').first()

        if default_dashboard:
            default_dashboard_id = default_dashboard.value_as_int()
        else:
            default_dashboard_id = None

        metabase = helpers.get_metabase_connection()

        dashboards = metabase.get_all_dashboards()

        for dashboard in dashboards:
            dashboards_response.append({
                'id': dashboard.id,
                'name': dashboard.name,
                'description': dashboard.description,
                'is_default_dashboard': default_dashboard_id == dashboard.id
            })

    except:
        flask.current_app.logger.error(f"Error trying to connect to Metabase: {traceback.format_exc()}")

    return dashboards_response
