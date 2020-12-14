from datetime import datetime
from flask import jsonify, request, current_app, g
import flask_babel
from .. import db
from .. import models
from . import users
from ..email import send_email
from app import helpers
from app import metabase
from ..services import notification_service


# /users/<int:id>/change-password
@users.route('/<int:user_id>/change-password', methods=['POST'])
@helpers.jwt_auth
def change_password(user_id):
    current_app.logger.info("change password")

    if not request.is_json:
        msg = flask_babel.gettext("Missing JSON in request")
        return jsonify({"message": msg}), 400

    if g.request_user.id == user_id or g.request_user.is_admin():
        change_user = models.User.query.get_or_404(user_id)

        new_password = request.json.get('new_password', None)
        confirm_password = request.json.get('confirm_password', None)

        if not new_password:
            msg = flask_babel.gettext("Missing new_password")
            return jsonify({"message": msg}), 400
        if not confirm_password:
            msg = flask_babel.gettext("Missing confirm_password")
            return jsonify({"message": msg}), 400
        if not new_password == confirm_password:
            msg = flask_babel.gettext("Passwords must match.")
            return jsonify({"message": msg}), 400
        if len(new_password) < 10:
            msg = flask_babel.gettext("Password must be at least 10 characters long.")
            return jsonify({"message": msg}), 400
        if len(new_password) > 64:
            msg = flask_babel.gettext("Password must be less than 64 characters long.")
            return jsonify({"message": msg}), 400

        change_user.password = new_password

        updates = {'password': new_password}
        metabase.update_user(change_user.metabase_user_id, updates)

        db.session.add(change_user)
        db.session.commit()

        msg = flask_babel.gettext("Password has been updated")
        return jsonify({"message": msg}), 200

    else:
        msg = flask_babel.gettext("Not authorized")
        return jsonify({"message": msg}), 401


# /users/<int:id>/resend-welcome
@users.route('/<int:user_id>/resend-welcome', methods=['POST'])
@helpers.jwt_auth
def resend_welcome(user_id):
    current_app.logger.info(f"/users/{user_id}/resend-welcome POST accessed by {g.request_user.email}")

    if g.request_user.is_admin():
        user = models.User.query.get_or_404(user_id)
        password = models.User.generate_password()

        user.password = password
        db.session.commit()

        send_email(user.email, 'Welcome to EPS',
                   'auth/email/welcome', web_app_url=current_app.config['WEB_APP_URL'], user=user, password=password)

        msg = flask_babel.gettext("The welcome email was sent to the user.")
        return jsonify({"message": msg}), 200

    else:
        msg = flask_babel.gettext("You do not have permission to resend a welcome email to a user.")
        return jsonify({"message": msg}), 401


# /users GET
@users.route('/', methods=['GET'])
@helpers.jwt_auth
@helpers.role_restrict(
    roles=models.Permission.READ_ACCOUNT,
    message=models.Permission.MSG_READ_ACCOUNT,
)
def get_users():
    current_app.logger.info(f"/users (get_users) accessed by {g.request_user.email}")

    status = request.args.get('status', None)
    if request.args.get('assignable', 'false').upper() == 'TRUE':
        assignable = True
    else:
        assignable = False

    if status and status not in ['active', 'inactive', 'any']:
        msg = flask_babel.gettext("Unsupported status filter : %(status)s", status=status)
        return jsonify({'message': msg}), 400

    if not status or status == 'active':
        users = models.User.query.filter_by(is_active=True).all()
    elif status == 'inactive':
        users = models.User.query.filter_by(is_active=False).all()
    elif status == 'any':
        users = models.User.query.all()
    else:
        users = models.User.query.filter_by(is_active=True).all()

    print(f"LEN USERS: {len(users)}")

    if assignable:
        users = list(filter(lambda u: u.can(models.Permission.ASSIGNABLE_TO_CASE), users))

    print(f"LEN USERS: {len(users)}")

    return jsonify([u.__getstate__() for u in users]), 200


# /users POST
@users.route('/', methods=['POST'])
@helpers.jwt_auth
@helpers.role_restrict(
    roles=models.Permission.CREATE_ACCOUNT,
    message=models.Permission.MSG_CREATE_ACCOUNT,
)
def post_user():
    current_app.logger.info(f"/users (add_user) accessed by {g.request_user.email}")

    if not request.is_json:
        msg = flask_babel.gettext("Missing JSON in request")
        return jsonify({"message": msg}), 400

    email = request.json.get('email', None)
    username = request.json.get('username', None)
    role_id = request.json.get('role_id', None)
    name = request.json.get('name', None)
    location = request.json.get('location', None)

    if not email:
        msg = flask_babel.gettext("Missing email")
        return jsonify({"message": msg}), 400
    if models.User.query.filter_by(email=email).all():
        msg = flask_babel.gettext("The email address you provided is already in use.")
        return jsonify({"message": msg}), 400
    if not username:
        msg = flask_babel.gettext("Missing username")
        return jsonify({"message": msg}), 400
    if models.User.query.filter_by(username=username).all():
        msg = flask_babel.gettext("The username you provided is already in use.")
        return jsonify({"message": msg}), 400
    if not role_id:
        role = models.Role.query.filter_by(default=True).first()
    else:
        if not isinstance(role_id, int):
            msg = flask_babel.gettext("Role id should be a integer number.")
            return jsonify({"message": msg}), 400
        if role_id not in [r.id for r in models.Role.query.all()]:
            msg = flask_babel.gettext("%(role_id)s is an invalid role id.", role_id=role_id)
            return jsonify({"message": msg}), 400
        role = models.Role.query.get(role_id)
    password = models.User.generate_password()

    user_data = {
        'email': email,
        'username': username,
        'name': name,
        'role': role,
        'location': location,
        'password': password
    }

    metabase_user_id = metabase.insert_user(user_data)

    user = models.User(
        metabase_user_id=metabase_user_id,
        **user_data
    )

    db.session.add(user)
    db.session.commit()
    send_email(user.email, 'Welcome to EPS',
               'auth/email/welcome', web_app_url=current_app.config['WEB_APP_URL'], user=user, password=password)

    return jsonify(user.__getstate__()), 200


# /users/{user_id} GET
@users.route('/<int:user_id>', methods=['GET'])
@helpers.jwt_auth
@helpers.role_restrict(
    roles=models.Permission.READ_ACCOUNT,
    message=models.Permission.MSG_READ_ACCOUNT,
)
def get_user(user_id):
    current_app.logger.info(f"/users/{user_id} GET accessed by {g.request_user.email}")

    return_user = models.User.query.get_or_404(user_id)
    return jsonify(return_user.__getstate__()), 200


# /users/{user_id} PUT
@users.route('/<int:user_id>', methods=['PUT'])
@helpers.jwt_auth
@helpers.role_restrict(
    roles=models.Permission.UPDATE_ACCOUNT,
    message=models.Permission.MSG_UPDATE_ACCOUNT,
)
def put_user(user_id):
    current_app.logger.info(f"/users/{user_id} PUT accessed by {g.request_user.email}")

    if not request.is_json:
        msg = flask_babel.gettext("Missing JSON in request")
        return jsonify({"message": msg}), 400

    return_user = models.User.query.get_or_404(user_id)

    put_is_active = request.json.get('is_active', return_user.is_active)

    if put_is_active is not None and (put_is_active != return_user.is_active):
        # trying to change is_active_flag
        if not g.request_user.can(models.Permission.DELETE_ACCOUNT):
            msg = flask_babel.gettext("You do not have permission to change someone's active flag.")
            return jsonify({"message": msg}), 401

    # trying to disabled admin
    if return_user.is_admin() and put_is_active is False:
        msg = flask_babel.gettext("Admin users cannot be disabled.")
        return jsonify({"message": msg}), 400

    put_user_id = request.json.get('id', None)
    if not put_user_id:
        msg = flask_babel.gettext("You must provide a user id in your put object.")
        return jsonify({"message": msg}), 400
    if put_user_id != return_user.id:
        msg = flask_babel.gettext("The user id in the URL does not match the user id in your put object.")
        return jsonify({"message": msg}), 400

    requested_email = request.json.get('email', return_user.email)
    if not requested_email:
        msg = flask_babel.gettext("User's email addresses cannot be null or empty.")
        return jsonify({"message": msg}), 400
    if len(models.User.query.filter(models.User.email == requested_email, models.User.id != put_user_id).all()):
        msg = flask_babel.gettext("The email address you provided is already in use.")
        return jsonify({"message": msg}), 400

    requested_username = request.json.get('username', return_user.username)
    if not requested_username:
        msg = flask_babel.gettext("Usernames cannot be null or empty.")
        return jsonify({"message": msg}), 400
    if len(models.User.query.filter(models.User.username == requested_username, models.User.id != put_user_id).all()):
        msg = flask_babel.gettext("The username you provided is already in use.")
        return jsonify({"message": msg}), 400

    if 'role_id' in request.json:
        requested_role_id = request.json.get('role_id')

        if requested_role_id not in [r.id for r in models.Role.query.all()]:
            msg = flask_babel.gettext("The provided role id is not a valid role id.")
            return jsonify({"message": msg}), 400

        new_role = models.Role.query.get(requested_role_id)
        # if the user's current role has ASSIGNABLE_TO_CASE and the new role does not
        # then unassign all their cases and notify admins
        if return_user.can(models.Permission.ASSIGNABLE_TO_CASE) and not new_role.has_permission(
                models.Permission.ASSIGNABLE_TO_CASE):
            cases_updated = []
            for case in models.Case.query.filter_by(assigned_to_id=return_user.id).all():
                case.assigned_to_id = None
                case.assigned_at = datetime.utcnow()
                cases_updated.append(case)
            if len(cases_updated) > 0:
                notification_service.notify_user_role_changed_not_assignable(return_user, cases_updated)

    else:
        requested_role_id = return_user.role_id

    color = request.json.get('color', return_user.color)
    if color not in models.User.supported_user_colors:
        msg = flask_babel.gettext("You provided an unsupported color")
        return jsonify({'message': msg}), 400

    updates = {
        'email': requested_email,
        'username': requested_username,
    }
    metabase.update_user(return_user.metabase_user_id, updates)

    is_active = request.json.get('is_active', return_user.is_active)

    if return_user.is_active and is_active is False:
        metabase.deactivate_user(return_user.metabase_user_id)
    elif return_user.is_active is False and is_active:
        metabase.reactivate_user(return_user.metabase_user_id)

    if is_active is None or is_active == '':
        is_active = return_user.is_active
    else:
        is_active = is_active

    return_user.email = requested_email
    return_user.username = requested_username
    return_user.role_id = requested_role_id
    return_user.name = request.json.get('name', return_user.name)
    return_user.location = request.json.get('location', return_user.location)
    return_user.is_active = is_active
    return_user.color = color
    db.session.commit()

    return jsonify(return_user.__getstate__()), 200


# /users/{user_id} DELETE
@users.route('/<int:user_id>', methods=['DELETE'])
@helpers.jwt_auth
@helpers.role_restrict(
    roles=models.Permission.DELETE_ACCOUNT,
    message=models.Permission.MSG_DELETE_ACCOUNT,
)
def delete_user(user_id):
    current_app.logger.info(f"/users/{user_id} DELETE accessed by {g.request_user.email}")

    if current_app.config['ENV'] == 'production':
        msg = flask_babel.gettext('Endpoint does not exist')
        return jsonify({'message': msg}), 404

    user_to_delete = models.User.query.get_or_404(user_id)

    admin_user = models.User.query.filter_by(username='admin').first()

    for s in models.Survey.query.filter_by(created_by_id=user_to_delete.id):
        s.created_by_id = admin_user.id
    db.session.commit()

    for s in models.Survey.query.filter_by(updated_by_id=user_to_delete.id):
        s.updated_by_id = admin_user.id
    db.session.commit()

    for sr in models.SurveyResponse.query.filter_by(created_by_id=user_to_delete.id):
        sr.created_by_id = admin_user.id
    db.session.commit()

    for sr in models.SurveyResponse.query.filter_by(updated_by_id=user_to_delete.id):
        sr.updated_by_id = admin_user.id
    db.session.commit()

    for cd in models.CaseDefinition.query.filter_by(created_by_id=user_to_delete.id):
        cd.created_by_id = admin_user.id
    db.session.commit()

    for cd in models.CaseDefinition.query.filter_by(updated_by_id=user_to_delete.id):
        cd.updated_by_id = admin_user.id
    db.session.commit()

    # not notifying anyone here because this endpoint is only reachable in dev and test environments
    for c in models.Case.query.filter_by(assigned_to_id=user_to_delete.id):
        c.assigned_to_id = None
        c.assigned_at = datetime.utcnow()

    metabase.deactivate_user(user_to_delete.metabase_user_id)

    db.session.delete(user_to_delete)
    db.session.commit()

    msg = flask_babel.gettext("The user has been deleted.")
    return jsonify({"message": msg}), 200
