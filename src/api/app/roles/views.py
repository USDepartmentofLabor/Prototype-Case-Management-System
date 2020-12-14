from datetime import datetime

import flask
import flask_babel
from app import roles
from app import models
from app import helpers
import app
from app.services import notification_service


@roles.roles.route('', methods=['POST'])
@helpers.jwt_auth
@helpers.role_restrict(
    roles=models.Permission.CREATE_ROLE,
    message=models.Permission.MSG_CREATE_ROLE,
    admin_allowed=True
)
def post_role():
    name = flask.request.json.get('name')
    default = flask.request.json.get('default') or False
    permissions = flask.request.json.get('permissions') or 0

    if not name:
        msg = flask_babel.gettext("Roles are required to have a name.")
        return flask.jsonify({'message': msg}), 400

    elif len(name) > 64:
        msg = flask_babel.gettext("Role names can not be longer than 64 characters.")
        return flask.jsonify({'message': msg}), 400

    if default:
        default_exists = models.Role.query.filter_by(default=True).first()
        if default_exists:
            msg = flask_babel.gettext("A default role already exists.")
            return flask.jsonify({'message': msg}), 400

    role = models.Role(
        name=name,
        default=default,
        permissions=permissions
    )

    app.db.session.add(role)
    app.db.session.commit()
    return flask.jsonify(role.__getstate__()), 200


@roles.roles.route('', methods=['GET'])
@helpers.jwt_auth
@helpers.role_restrict(
    roles=models.Permission.READ_ROLE,
    message=models.Permission.MSG_READ_ROLE,
    admin_allowed=True
)
def fetch_all_roles():
    role_list = models.Role.query.all()
    return flask.jsonify([role.__getstate__() for role in role_list]), 200


@roles.roles.route('/<int:role_id>', methods=['GET'])
@helpers.jwt_auth
@helpers.role_restrict(
    roles=models.Permission.READ_ROLE,
    message=models.Permission.MSG_READ_ROLE,
    admin_allowed=True
)
def fetch_role(role_id):
    role = models.Role.query.get_or_404(role_id)
    return flask.jsonify(role.__getstate__()), 200


@roles.roles.route('/<int:role_id>', methods=['PUT'])
@helpers.jwt_auth
@helpers.role_restrict(
    roles=models.Permission.UPDATE_ROLE,
    message=models.Permission.MSG_UPDATE_ROLE,
    admin_allowed=True
)
def update_role(role_id):
    name = flask.request.json.get('name')
    default = flask.request.json.get('default')
    permissions = flask.request.json.get('permissions')

    if name and len(name) > 64:
        msg = flask_babel.gettext("Role names can not be longer than 64 characters.")
        return flask.jsonify({'message': msg}), 400

    role = models.Role.query.get_or_404(role_id)

    if name:
        role.name = name

    if default is not None:
        if default:
            default_role = models.Role.query.filter_by(default=True).first()
            if default_role and default_role.id != role_id:
                msg = flask_babel.gettext("A default role already exists.")
                return flask.jsonify({'message': msg}), 400

        role.default = default

    if permissions is not None:
        # if previous permission contains ASSIGNABLE_TO_CASE and new permissions does not
        # then unassigned all cases for all users that have that role and notify all admins
        # users of the case that were affected.
        if models.Permission.does_have(role.permissions,
                                       models.Permission.ASSIGNABLE_TO_CASE) and not models.Permission.does_have(
                permissions, models.Permission.ASSIGNABLE_TO_CASE):
            cases_updated = []
            for user in role.users:
                for case in models.Case.query.filter_by(assigned_to_id=user.id).all():
                    case.assigned_to_id = None
                    case.assigned_at = datetime.utcnow()
                    cases_updated.append(case)
            if len(cases_updated) > 0:
                notification_service.notify_assignable_permission_removed_from_role(role, cases_updated)

        role.permissions = permissions

    app.db.session.commit()
    return flask.jsonify(role.__getstate__()), 200


@roles.roles.route('/<int:role_id>', methods=['DELETE'])
@helpers.jwt_auth
@helpers.role_restrict(
    roles=models.Permission.DELETE_ROLE,
    message=models.Permission.MSG_DELETE_ROLE,
    admin_allowed=True
)
def delete_role(role_id):
    role = models.Role.query.get_or_404(role_id)

    if role.name == 'Admin':
        msg = flask_babel.gettext("Cannot delete the admin role.")
        return flask.jsonify({'message': msg}), 400

    if role.default:
        msg = flask_babel.gettext("Cannot delete the default role.")
        return flask.jsonify({'message': msg}), 400

    default_role = models.Role.query.filter_by(default=True).first()

    for user_with_role in models.User.query.filter_by(role_id=role_id).all():
        user_with_role.role = default_role
        if role.has_permission(models.Permission.ASSIGNABLE_TO_CASE) and not default_role.has_permission(
                models.Permission.ASSIGNABLE_TO_CASE):
            affected_cases = []
            for case in models.Case.query.filter_by(assigned_to_id=user_with_role.id):
                case.assigned_to_id = None
                case.assigned_at = datetime.utcnow()
                affected_cases.append(case)

            if len(affected_cases) > 0:
                notification_service.notify_role_deleted_with_assigned_permission(role, affected_cases)

    app.db.session.delete(role)
    app.db.session.commit()
    msg = flask_babel.gettext('The role has been successfully deleted.')
    return flask.jsonify({'message': msg}), 200
