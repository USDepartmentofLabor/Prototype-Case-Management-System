from datetime import datetime
import secrets
import string
import random
import uuid
import copy
from collections import namedtuple
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.ext import hybrid
from sqlalchemy import event, and_
from sqlalchemy_continuum import Operation
from geoalchemy2 import Geometry
from flask_continuum import VersioningMixin
from flask import current_app, session
from . import db
from app import helpers
import flask_babel

GeoLocation = namedtuple('GeoLocation',
                         'latitude longitude position_accuracy altitude altitude_accuracy heading speed location_dt')
ServiceResponse = namedtuple('ServiceResponse', 'message status_code')


class Permission:
    ADMIN = 1 << 0
    DESC_ADMIN = flask_babel.lazy_gettext('Administrator')
    INSTALL_SYSTEM = 1 << 1
    DESC_INSTALL_SYSTEM = flask_babel.lazy_gettext('System Installation')
    CONFIGURE_SYSTEM = 1 << 2
    DESC_CONFIGURE_SYSTEM = flask_babel.lazy_gettext('System Configuration')
    MSG_CONFIGURE_SYSTEM = flask_babel.lazy_gettext('You do not have permission to configure the system.')
    CREATE_ACCOUNT = 1 << 3
    DESC_CREATE_ACCOUNT = flask_babel.lazy_gettext('Create Account')
    READ_ACCOUNT = 1 << 4
    DESC_READ_ACCOUNT = flask_babel.lazy_gettext('View Account')
    UPDATE_ACCOUNT = 1 << 5
    DESC_UPDATE_ACCOUNT = flask_babel.lazy_gettext('Change Account')
    DELETE_ACCOUNT = 1 << 6
    DESC_DELETE_ACCOUNT = flask_babel.lazy_gettext('Delete Account')
    CREATE_ROLE = 1 << 7
    DESC_CREATE_ROLE = flask_babel.lazy_gettext('Create Role')
    READ_ROLE = 1 << 8
    DESC_READ_ROLE = flask_babel.lazy_gettext('View Role')
    UPDATE_ROLE = 1 << 9
    DESC_UPDATE_ROLE = flask_babel.lazy_gettext('Change Role')
    DELETE_ROLE = 1 << 10
    DESC_DELETE_ROLE = flask_babel.lazy_gettext('Delete Role')
    CREATE_SURVEY = 1 << 11
    DESC_CREATE_SURVEY = flask_babel.lazy_gettext('Create Data Collection Form')
    READ_SURVEY = 1 << 12
    DESC_READ_SURVEY = flask_babel.lazy_gettext('View Data Collection Form')
    UPDATE_SURVEY = 1 << 13
    DESC_UPDATE_SURVEY = flask_babel.lazy_gettext('Change Data Collection Form')
    DELETE_SURVEY = 1 << 14
    DESC_DELETE_SURVEY = flask_babel.lazy_gettext('Delete Data Collection Form')
    SUBMIT_SURVEY = 1 << 15
    DESC_SUBMIT_SURVEY = flask_babel.lazy_gettext('Submit Data Collection Form')
    ARCHIVE_SURVEY = 1 << 16
    DESC_ARCHIVE_SURVEY = flask_babel.lazy_gettext('Archive Data Collection Form')
    READ_REPORT = 1 << 17
    DESC_READ_REPORT = flask_babel.lazy_gettext('View Report')
    CREATE_CASE_DEFINITION = 1 << 18
    DESC_CREATE_CASE_DEFINITION = flask_babel.lazy_gettext('Create Case Definition')
    READ_CASE_DEFINITION = 1 << 19
    DESC_READ_CASE_DEFINITION = flask_babel.lazy_gettext('View Case Definition')
    UPDATE_CASE_DEFINITION = 1 << 20
    DESC_UPDATE_CASE_DEFINITION = flask_babel.lazy_gettext('Change Case Definition')
    DELETE_CASE_DEFINITION = 1 << 21
    DESC_DELETE_CASE_DEFINITION = flask_babel.lazy_gettext('Delete Case Definition')
    CREATE_CASE = 1 << 22
    DESC_CREATE_CASE = flask_babel.lazy_gettext('Create Case')
    READ_CASE = 1 << 23
    DESC_READ_CASE = flask_babel.lazy_gettext('Read Case')
    UPDATE_CASE = 1 << 24
    DESC_UPDATE_CASE = flask_babel.lazy_gettext('Change Case')
    DELETE_CASE = 1 << 25
    DESC_DELETE_CASE = flask_babel.lazy_gettext('Delete Case')
    ASSIGN_TO_CASE = 1 << 26
    DESC_ASSIGN_TO_CASE = flask_babel.lazy_gettext('Assign to a Case')
    ASSIGNABLE_TO_CASE = 1 << 27
    DESC_ASSIGNABLE_TO_CASE = flask_babel.lazy_gettext('Assignable to a Case')
    RESET_REPORTING = 1 << 28
    DESC_RESET_REPORTING = flask_babel.lazy_gettext('Reset Reporting Database')
    CREATE_PROJECT = 1 << 29
    DESC_CREATE_PROJECT = flask_babel.lazy_gettext('Create Project Information')
    READ_PROJECT = 1 << 30
    DESC_READ_PROJECT = flask_babel.lazy_gettext('View Project Information')
    UPDATE_PROJECT = 1 << 31
    DESC_UPDATE_PROJECT = flask_babel.lazy_gettext('Change Project Information')
    DELETE_PROJECT = 1 << 32
    DESC_DELETE_PROJECT = flask_babel.lazy_gettext('Delete Project Information')
    CREATE_ACTIVITY_DEFINITION = 1 << 33
    DESC_CREATE_ACTIVITY_DEFINITION = flask_babel.lazy_gettext('Create Activity Definition')
    READ_ACTIVITY_DEFINITION = 1 << 34
    DESC_READ_ACTIVITY_DEFINITION = flask_babel.lazy_gettext('View Activity Definition')
    UPDATE_ACTIVITY_DEFINITION = 1 << 35
    DESC_UPDATE_ACTIVITY_DEFINITION = flask_babel.lazy_gettext('Change Activity Definition')
    DELETE_ACTIVITY_DEFINITION = 1 << 36
    DESC_DELETE_ACTIVITY_DEFINITION = flask_babel.lazy_gettext('Delete Activity Definition')
    CREATE_ACTIVITY = 1 << 37
    DESC_CREATE_ACTIVITY = flask_babel.lazy_gettext('Create Activity')
    READ_ACTIVITY = 1 << 38
    DESC_READ_ACTIVITY = flask_babel.lazy_gettext('View Activity')
    UPDATE_ACTIVITY = 1 << 39
    DESC_UPDATE_ACTIVITY = flask_babel.lazy_gettext('Change Activity')
    DELETE_ACTIVITY = 1 << 40
    DESC_DELETE_ACTIVITY = flask_babel.lazy_gettext('Delete Activity')
    ALLOW_TO_STATUS = 1 << 41
    DESC_ALLOW_TO_STATUS = flask_babel.lazy_gettext('Change Status')

    MSG_CREATE_ACCOUNT = flask_babel.lazy_gettext("You do not have permission to add a user to the system.")
    MSG_READ_ACCOUNT = flask_babel.lazy_gettext("You do not have permission to read users.")
    MSG_UPDATE_ACCOUNT = flask_babel.lazy_gettext("You do not have permission to update users.")
    MSG_DELETE_ACCOUNT = flask_babel.lazy_gettext("You do not have permission to delete users.")

    MSG_CREATE_ROLE = flask_babel.lazy_gettext("You do not have permission to add a role.")
    MSG_READ_ROLE = flask_babel.lazy_gettext("You do not have permission to view roles.")
    MSG_UPDATE_ROLE = flask_babel.lazy_gettext("You do not have permission to update a role.")
    MSG_DELETE_ROLE = flask_babel.lazy_gettext("You do not have permission to delete a role.")

    MSG_CREATE_CASE_DEFINITION = flask_babel.lazy_gettext("You do not have permission to create a case definition.")
    MSG_READ_CASE_DEFINITION = flask_babel.lazy_gettext("You do not have permission to read case definitions.")
    MSG_UPDATE_CASE_DEFINITION = flask_babel.lazy_gettext("You do not have permission to update case definitions.")
    MSG_DELETE_CASE_DEFINITION = flask_babel.lazy_gettext("You do not have permission to delete case definitions.")
    MSG_CREATE_CASE = flask_babel.lazy_gettext("You do not have permission to create a case.")
    MSG_READ_CASE = flask_babel.lazy_gettext("You do not have permission to read cases.")
    MSG_UPDATE_CASE = flask_babel.lazy_gettext("You do not have permission to update cases.")
    MSG_DELETE_CASE = flask_babel.lazy_gettext("You do not have permission to delete cases.")
    MSG_CREATE_SURVEY = flask_babel.lazy_gettext("You do not have permission to create a survey.")
    MSG_READ_SURVEY = flask_babel.lazy_gettext("You do not have permission to read surveys.")
    MSG_UPDATE_SURVEY = flask_babel.lazy_gettext("You do not have permission to update surveys.")
    MSG_DELETE_SURVEY = flask_babel.lazy_gettext("You do not have permission to delete surveys.")
    MSG_SUBMIT_SURVEY = flask_babel.lazy_gettext("You do not have permission to submit a survey.")

    MSG_RESET_REPORTING = flask_babel.lazy_gettext("You do not have permission to reset mongo.")

    MSG_CREATE_PROJECT = flask_babel.lazy_gettext("You do not have permission to create a project.")
    MSG_READ_PROJECT = flask_babel.lazy_gettext("You do not have permission to read a project.")
    MSG_UPDATE_PROJECT = flask_babel.lazy_gettext("You do not have permission to update a project.")
    MSG_DELETE_PROJECT = flask_babel.lazy_gettext("You do not have permission to delete a project.")

    MSG_CREATE_ACTIVITY_DEFINITION = flask_babel.lazy_gettext(
        "You do not have permission to create an activity definition.")
    MSG_READ_ACTIVITY_DEFINITION = flask_babel.lazy_gettext(
        "You do not have permission to read an activity definition.")
    MSG_UPDATE_ACTIVITY_DEFINITION = flask_babel.lazy_gettext(
        "You do not have permission to update an activity definition.")
    MSG_DELETE_ACTIVITY_DEFINITION = flask_babel.lazy_gettext(
        "You do not have permission to delete an activity definition.")

    MSG_CREATE_ACTIVITY = flask_babel.lazy_gettext(
        "You do not have permission to create an activity.")
    MSG_READ_ACTIVITY = flask_babel.lazy_gettext(
        "You do not have permission to read an activity.")
    MSG_UPDATE_ACTIVITY = flask_babel.lazy_gettext(
        "You do not have permission to update an activity.")
    MSG_DELETE_ACTIVITY = flask_babel.lazy_gettext(
        "You do not have permission to delete an activity.")

    @staticmethod
    def does_have(permissions, permission):
        return permissions & permission == permission

    @staticmethod
    def get_as_list():
        perm_vars = vars(Permission)
        perm_names = [attr for attr in perm_vars if
                      not attr.startswith('__') and not attr.startswith('MSG_') and not attr.startswith(
                          'DESC_') and not attr.startswith('does_have') and not attr.startswith('get_as_list')]
        return [{'code': perm, 'value': perm_vars[perm], 'name': perm_vars['DESC_' + perm]} for perm in
                       perm_names]


def history(self):
    hist = []

    for version in self.versions:
        op_type = None
        if version.operation_type == Operation.INSERT:
            op_type = 'insert'
        if version.operation_type == Operation.UPDATE:
            op_type = 'update'
        if version.operation_type == Operation.DELETE:
            op_type = 'delete'

        changes = []
        for k, v in version.changeset.items():
            if isinstance(v[0], datetime):
                v[0] = v[0].isoformat()
            if isinstance(v[1], datetime):
                v[1] = v[1].isoformat()
            c = {
                'property_changed': k,
                'old_value': v[0],
                'new_value': v[1],
            }
            changes.append(c)

        h = {
            'action': op_type,
            'date_performed': version.updated_at.isoformat(),
            'performed_by': {
                'id': version.updated_by.id,
                'email': version.updated_by.email,
                'username': version.updated_by.username,
                'name': version.updated_by.name,
                'color': version.updated_by.color,
            },
            'changes': changes,
        }
        hist.append(h)

    hist.reverse()
    return hist


class Role(db.Model, VersioningMixin):
    __tablename__ = 'roles'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)
    default = db.Column(db.Boolean, default=False, index=True, nullable=False)
    permissions = db.Column(db.BigInteger, nullable=False)
    users = db.relationship('User', backref='role', lazy='dynamic')

    @hybrid.hybrid_property
    def permission_codes(self):
        permission_list = [perm['code'] for perm in Permission.get_as_list() if self.has_permission(perm['value'])]
        # for perm in Permission.get_as_list():
        #     if self.has_permission(perm['value']):
        #         permission_list.append(perm['code'])
        return permission_list

    def __init__(self, **kwargs):
        super(Role, self).__init__(**kwargs)
        if self.permissions is None:
            self.permission = 0

    @staticmethod
    def insert_roles():
        roles = {
            'Admin': [Permission.ADMIN, Permission.INSTALL_SYSTEM, Permission.CONFIGURE_SYSTEM,
                      Permission.CREATE_ACCOUNT, Permission.READ_ACCOUNT, Permission.UPDATE_ACCOUNT,
                      Permission.DELETE_ACCOUNT, Permission.CREATE_ROLE, Permission.READ_ROLE, Permission.UPDATE_ROLE,
                      Permission.DELETE_ROLE, Permission.CREATE_SURVEY, Permission.READ_SURVEY,
                      Permission.UPDATE_SURVEY, Permission.DELETE_SURVEY, Permission.SUBMIT_SURVEY,
                      Permission.ARCHIVE_SURVEY, Permission.READ_REPORT,
                      Permission.CREATE_CASE_DEFINITION, Permission.READ_CASE_DEFINITION,
                      Permission.UPDATE_CASE_DEFINITION, Permission.DELETE_CASE_DEFINITION, Permission.CREATE_CASE,
                      Permission.UPDATE_CASE, Permission.READ_CASE, Permission.DELETE_CASE, Permission.RESET_REPORTING,
                      Permission.CREATE_PROJECT, Permission.READ_PROJECT, Permission.UPDATE_PROJECT,
                      Permission.DELETE_PROJECT, Permission.CREATE_ACTIVITY_DEFINITION,
                      Permission.READ_ACTIVITY_DEFINITION, Permission.UPDATE_ACTIVITY_DEFINITION,
                      Permission.DELETE_ACTIVITY_DEFINITION, Permission.CREATE_ACTIVITY,
                      Permission.READ_ACTIVITY, Permission.UPDATE_ACTIVITY,
                      Permission.DELETE_ACTIVITY, Permission.ASSIGNABLE_TO_CASE, Permission.ASSIGN_TO_CASE,
                      Permission.ALLOW_TO_STATUS],
            'Project Manager': [Permission.CONFIGURE_SYSTEM, Permission.READ_ACCOUNT, Permission.UPDATE_ACCOUNT,
                                Permission.CREATE_SURVEY, Permission.READ_SURVEY, Permission.UPDATE_SURVEY,
                                Permission.DELETE_SURVEY, Permission.SUBMIT_SURVEY,
                                Permission.ARCHIVE_SURVEY, Permission.READ_REPORT,
                                Permission.CREATE_CASE_DEFINITION, Permission.READ_CASE_DEFINITION,
                                Permission.UPDATE_CASE_DEFINITION, Permission.DELETE_CASE_DEFINITION,
                                Permission.CREATE_CASE, Permission.UPDATE_CASE, Permission.READ_CASE,
                                Permission.DELETE_CASE, Permission.CREATE_PROJECT, Permission.READ_PROJECT,
                                Permission.UPDATE_PROJECT, Permission.DELETE_PROJECT,
                                Permission.CREATE_ACTIVITY_DEFINITION,
                                Permission.READ_ACTIVITY_DEFINITION, Permission.UPDATE_ACTIVITY_DEFINITION,
                                Permission.DELETE_ACTIVITY_DEFINITION, Permission.CREATE_ACTIVITY,
                                Permission.READ_ACTIVITY, Permission.UPDATE_ACTIVITY,
                                Permission.DELETE_ACTIVITY, Permission.ASSIGNABLE_TO_CASE, Permission.ASSIGN_TO_CASE,
                                Permission.ALLOW_TO_STATUS],
            'Data Collector': [Permission.READ_ACCOUNT, Permission.UPDATE_ACCOUNT, Permission.READ_SURVEY,
                               Permission.SUBMIT_SURVEY, Permission.UPDATE_SURVEY,
                               Permission.CREATE_CASE, Permission.UPDATE_CASE, Permission.READ_CASE,
                               Permission.READ_PROJECT, Permission.CREATE_ACTIVITY,
                               Permission.READ_ACTIVITY, Permission.UPDATE_ACTIVITY, Permission.ASSIGNABLE_TO_CASE,
                               Permission.ALLOW_TO_STATUS],
            'Data Reader': [Permission.READ_ACCOUNT, Permission.UPDATE_ACCOUNT, Permission.READ_SURVEY,
                            Permission.READ_REPORT, Permission.READ_CASE,
                            Permission.READ_PROJECT, Permission.READ_ACTIVITY, Permission.ASSIGNABLE_TO_CASE],
        }
        default_role = 'Data Reader'
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.reset_permissions()
            for perm in roles[r]:
                role.add_permission(perm)
            role.default = (role.name == default_role)
            db.session.add(role)
        db.session.commit()

    def add_permission(self, perm):
        if not self.has_permission(perm):
            self.permissions += perm

    def remove_permission(self, perm):
        if self.has_permission(perm):
            self.permissions -= perm

    def reset_permissions(self):
        self.permissions = 0

    def has_permission(self, perm):
        return self.permissions & perm == perm

    def __repr__(self):
        return '<Role %r>' % self.name

    def __getstate__(self):
        from .model_schemas import RoleSchema
        return RoleSchema().dump(self)


class User(db.Model, VersioningMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    metabase_user_id = db.Column(db.Integer, nullable=True, unique=True)
    email = db.Column(db.String(64), unique=True, index=True, nullable=False)
    username = db.Column(db.String(64), unique=True, index=True, nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    password_hash = db.Column(db.String(128), nullable=False)
    name = db.Column(db.String(64))
    location = db.Column(db.Text())
    last_seen_at = db.Column(db.DateTime(), default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    color = db.Column(db.String(16))
    last_login_location_coordinates = db.Column(Geometry(geometry_type="POINT"))
    last_login_location_position_accuracy = db.Column(db.Float)
    last_login_location_altitude = db.Column(db.Float)
    last_login_location_altitude_accuracy = db.Column(db.Float)
    last_login_location_heading = db.Column(db.Float)
    last_login_location_speed = db.Column(db.Float)
    last_login_location_dt = db.Column(db.DateTime())
    created_at = db.Column(db.DateTime(), index=True, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime(), index=True, default=datetime.utcnow, nullable=False)

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            self.role = Role.query.filter_by(default=True).first()

        if self.color is None:
            self.color = random.choice(self.supported_user_colors)

    @hybrid.hybrid_property
    def supported_user_colors(self):
        return [
            'light-green',
            'light-blue ',
            'blue-grey',
            'indigo',
            'pink',
            'brown',
            'grey',
            'teal',
            'cyan'
        ]

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_reset_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'reset': self.id}).decode('utf-8')

    @staticmethod
    def reset_password(token, new_password):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token.encode('utf-8'))
        except:
            return False
        user = User.query.get(data.get('reset'))
        if user is None:
            return False
        if session:
            session['current_user_id'] = user.id
        user.password = new_password
        db.session.add(user)
        return True

    def generate_email_change_token(self, new_email, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps(
            {'change_email': self.id, 'new_email': new_email}).decode('utf-8')

    def change_email(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token.encode('utf-8'))
        except:
            return False
        if data.get('change_email') != self.id:
            return False
        new_email = data.get('new_email')
        if new_email is None:
            return False
        if self.query.filter_by(email=new_email).first() is not None:
            return False
        self.email = new_email
        db.session.add(self)
        return True

    def can(self, perm):
        return self.role is not None and self.role.has_permission(perm)

    def is_admin(self):
        return self.can(Permission.ADMIN)

    def ping(self):
        self.last_seen_at = datetime.utcnow()
        db.session.add(self)

    @staticmethod
    def generate_password():
        alphabet = string.ascii_letters + string.digits + string.punctuation
        return ''.join(secrets.choice(alphabet) for i in range(20))

    def __repr__(self):
        return '<User %r>' % self.username

    def __getstate__(self):
        from .model_schemas import UserSchema
        return UserSchema(exclude=['password_hash']).dump(self)


@event.listens_for(User, "after_update")
def update_survey_metabase_rescan(mapped_class, connection, instance):
    change_keys = set(instance.changeset.keys())
    if change_keys and change_keys != {'last_seen_at'}:
        instance.updated_at = datetime.utcnow()


class EPSProperty(db.Model, VersioningMixin):
    __tablename__ = 'eps_properties'

    property = db.Column(db.String(64), primary_key=True)
    value = db.Column(db.Text)

    def value_as_int(self):
        try:
            return int(self.value)
        except:
            return None

    def __repr__(self):
        return f"<EPSProperty {self.property} = {self.value}>"

    def __getstate__(self):
        from .model_schemas import EPSPropertySchema
        return EPSPropertySchema().dump(self)


class Survey(db.Model, VersioningMixin):
    __tablename__ = 'surveys'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, index=True, unique=True, nullable=False)
    structure = db.Column(JSON)
    is_archived = db.Column(db.Boolean, default=False, nullable=False)
    reporting_table_name = db.Column(db.String(128))
    created_at = db.Column(db.DateTime(), index=True, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime(), index=True, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    updated_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # relationships
    responses = db.relationship('SurveyResponse', backref='survey', lazy='dynamic')
    created_by = db.relationship('User', foreign_keys=[created_by_id])
    updated_by = db.relationship('User', foreign_keys=[updated_by_id])

    def __repr__(self):
        return f"<Survey {self.name}>"

    def __getstate__(self):
        from .model_schemas import SurveySchema
        return SurveySchema(exclude=['reporting_table_name']).dump(self)


@event.listens_for(Survey, "after_insert")
def insert_survey_metabase_rescan(mapper, connection, target):
    data_table_name = current_app.reporting_service.create_survey(target, 'metabase_pg_user')
    helpers.metabase_rescan()


@event.listens_for(Survey, "after_update")
def update_survey_metabase_rescan(mapped_class, connection, survey):
    keys = set(survey.changeset.keys())
    if keys and keys != {'case_definitions'}:
        helpers.metabase_rescan()


@event.listens_for(Survey, "after_delete")
def delete_survey_metabase_rescan(mapper, connection, target):
    current_app.reporting_service.delete_survey(target.name)
    helpers.metabase_rescan()


class SurveyResponse(db.Model, VersioningMixin):
    __tablename__ = "survey_responses"

    id = db.Column(db.Integer, primary_key=True)
    structure = db.Column(JSON)
    survey_id = db.Column(db.Integer, db.ForeignKey('surveys.id'), nullable=False)
    status_id = db.Column(db.Integer, db.ForeignKey('survey_response_statuses.id'), nullable=False)
    is_archived = db.Column(db.Boolean, default=False, nullable=False)
    source_type = db.Column(db.String, nullable=False, default='Standalone')
    case_id = db.Column(db.Integer, db.ForeignKey('cases.id'))
    activity_id = db.Column(db.Integer, db.ForeignKey('activities.id'))
    created_at = db.Column(db.DateTime(), index=True, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime(), index=True, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    created_location_coordinates = db.Column(Geometry(geometry_type="POINT"))
    created_location_position_accuracy = db.Column(db.Float)
    created_location_altitude = db.Column(db.Float)
    created_location_altitude_accuracy = db.Column(db.Float)
    created_location_heading = db.Column(db.Float)
    created_location_speed = db.Column(db.Float)
    created_location_dt = db.Column(db.DateTime())
    updated_location_coordinates = db.Column(Geometry(geometry_type="POINT"))
    updated_location_position_accuracy = db.Column(db.Float)
    updated_location_altitude = db.Column(db.Float)
    updated_location_altitude_accuracy = db.Column(db.Float)
    updated_location_heading = db.Column(db.Float)
    updated_location_speed = db.Column(db.Float)
    updated_location_dt = db.Column(db.DateTime())
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    updated_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # relationships
    status = db.relationship('SurveyResponseStatus', foreign_keys=[status_id])
    created_by = db.relationship('User', foreign_keys=[created_by_id])
    updated_by = db.relationship('User', foreign_keys=[updated_by_id])

    def __init__(self, **kwargs):
        super(SurveyResponse, self).__init__(**kwargs)
        if self.status is None:
            default_status = SurveyResponseStatus.query.filter_by(default=True).first()
            self.status = default_status
            self.status_id = default_status.id

    def __repr__(self):
        return f"<SurveyResponse {self.structure}>"

    def __getstate__(self):
        from .model_schemas import SurveyResponseSchema
        return SurveyResponseSchema().dump(self)


class SurveyResponseStatus(db.Model):
    __tablename__ = 'survey_response_statuses'

    id = db.Column(db.Integer, primary_key=True, autoincrement=False)
    name = db.Column(db.String, nullable=False)
    default = db.Column(db.Boolean, default=False, index=True)

    @staticmethod
    def insert_survey_response_statuses():
        statuses = [
            (1, 'Draft', False),
            (2, 'Submitted', True)
        ]
        for status in statuses:
            db_status = SurveyResponseStatus.query.get(status[0])
            if db_status is None:
                db_status = SurveyResponseStatus(id=status[0], name=status[1], default=status[2])
                db.session.add(db_status)
        db.session.commit()

    @staticmethod
    def is_valid_status(check_status_id):
        return check_status_id in [s.id for s in SurveyResponseStatus.query.all()]

    def __repr_(self):
        return f"<SurveyResponseStatus {self.id} - {self.name}"

    def __getstate__(self):
        from .model_schemas import SurveyResponseStatusSchema
        return SurveyResponseStatusSchema().dump(self)


case_definitions_surveys = db.Table('case_definitions_surveys', db.Model.metadata,
                                    db.Column('case_definition_id', db.Integer, db.ForeignKey('case_definitions.id'),
                                              nullable=False, index=True, primary_key=True),
                                    db.Column('survey_id', db.Integer, db.ForeignKey('surveys.id'), nullable=False,
                                              index=True, primary_key=True))


class CaseDefinition(db.Model, VersioningMixin):
    __tablename__ = 'case_definitions'

    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String, unique=True, nullable=False)
    name = db.Column(db.String, unique=True, nullable=False)
    description = db.Column(db.Text)
    reporting_table_name = db.Column(db.String(64))
    created_at = db.Column(db.DateTime(), index=True, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime(), index=True, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    updated_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # relationships
    surveys = db.relationship("Survey", secondary=case_definitions_surveys, backref='case_definitions', lazy='dynamic')
    documents = db.relationship("CaseDefinitionDocument")
    cases = db.relationship('Case', backref='case_definition', lazy='dynamic')
    activity_definitions = db.relationship('ActivityDefinition', backref='case_definition', lazy='dynamic')
    created_by = db.relationship('User', foreign_keys=[created_by_id])
    updated_by = db.relationship('User', foreign_keys=[updated_by_id])

    @hybrid.hybrid_property
    def custom_fields(self):
        custom_fields = CustomField.query.filter(and_(CustomField.model_type == 'CaseDefinition',
                                                      CustomField.model_id == self.id))

        custom_field_list = []
        for cf in custom_fields:
            custom_field_list.append(cf.__getstate__())

        return custom_field_list

    def __repr__(self):
        return f"<CaseDefinition {self.name}>"

    def __getstate__(self):
        from .model_schemas import CaseDefinitionSchema
        return CaseDefinitionSchema().dump(self)


class CaseDefinitionDocument(db.Model, VersioningMixin):
    __tablename__ = 'case_definition_documents'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.Text)
    is_required = db.Column(db.Boolean, default=False, nullable=False)
    case_definition_id = db.Column(db.Integer, db.ForeignKey('case_definitions.id'))

    def __repr__(self):
        return f"<CaseDefinitionDocument {self.name}>"

    def __getstate__(self):
        from .model_schemas import CaseDefinitionDocumentSchema
        return CaseDefinitionDocumentSchema().dump(self)


class Case(db.Model, VersioningMixin):
    __versioned__ = {
        'exclude': [
            'created_location_coordinates',
            'updated_location_coordinates'
        ]
    }
    __tablename__ = 'cases'

    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String, unique=True, nullable=False)
    name = db.Column(db.String, unique=True, nullable=False)
    description = db.Column(db.Text)
    case_definition_id = db.Column(db.Integer, db.ForeignKey('case_definitions.id'), nullable=False)
    assigned_to_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    assigned_at = db.Column(db.DateTime())
    custom_fields = db.Column(JSON)
    created_location_coordinates = db.Column(Geometry(geometry_type="POINT"))
    created_location_position_accuracy = db.Column(db.Float)
    created_location_altitude = db.Column(db.Float)
    created_location_altitude_accuracy = db.Column(db.Float)
    created_location_heading = db.Column(db.Float)
    created_location_speed = db.Column(db.Float)
    created_location_dt = db.Column(db.DateTime())
    updated_location_coordinates = db.Column(Geometry(geometry_type="POINT"))
    updated_location_position_accuracy = db.Column(db.Float)
    updated_location_altitude = db.Column(db.Float)
    updated_location_altitude_accuracy = db.Column(db.Float)
    updated_location_heading = db.Column(db.Float)
    updated_location_speed = db.Column(db.Float)
    updated_location_dt = db.Column(db.DateTime())
    created_at = db.Column(db.DateTime(), index=True, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime(), index=True, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    updated_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    status_id = db.Column(db.Integer, db.ForeignKey('case_statuses.id'), nullable=False)

    # relationships
    assigned_to = db.relationship('User', foreign_keys=[assigned_to_id])
    responses = db.relationship('SurveyResponse', backref='case', lazy='dynamic')
    activities = db.relationship('Activity', backref='case', lazy='dynamic')
    created_by = db.relationship('User', foreign_keys=[created_by_id])
    updated_by = db.relationship('User', foreign_keys=[updated_by_id])
    status = db.relationship('CaseStatus', foreign_keys=[status_id])

    def __init__(self, **kwargs):
        super(Case, self).__init__(**kwargs)
        if self.key is None:
            self.key = Case.generate_key(self.case_definition_id)

        if self.status is None:
            default_status = CaseStatus.query.filter_by(default=True).first()
            self.status = default_status
            self.status_id = default_status.id

        if self.custom_fields is None:
            self.custom_fields = []

    def __repr__(self):
        return f"<Case {self.key} : {self.name}>"

    def __getstate__(self):
        from .model_schemas import CaseSchema
        result = CaseSchema().dump(self)
        return result

    @hybrid.hybrid_property
    def notes(self):
        return Note.query.filter(and_(Note.model_name == 'Case'), Note.model_id == self.id)

    @hybrid.hybrid_property
    def files(self):
        return UploadedFile.query.filter(and_(UploadedFile.model_name == 'Case'), UploadedFile.model_id == self.id)

    def add_custom_field(self, custom_field, created_by, updated_by, custom_field_id=None, created_at=None,
                         updated_at=None):
        if custom_field_id is None:
            custom_field_id = str(uuid.uuid4())
        if created_at is None:
            created_at = datetime.utcnow().isoformat()
        if updated_at is None:
            updated_at = datetime.utcnow().isoformat()

        current_app.logger.info(f"adding custom field ID : {custom_field_id}")
        if custom_field_id in [cf['id'] for cf in self.custom_fields]:
            raise KeyError('Custom field IDs must be unique')
        _custom_fields = copy.deepcopy(self.custom_fields)
        _custom_fields.append({
            'id': custom_field_id,
            'name': custom_field.name,
            'field_type': custom_field.field_type,
            'selections': custom_field.selections,
            'validation_rules': custom_field.validation_rules,
            'model_type': "Case",
            'case_definition_custom_field_id': custom_field.id,
            'custom_section_id': custom_field.custom_section_id,
            'help_text': custom_field.help_text,
            'sort_order': custom_field.sort_order,
            'value': None,
            'created_at': created_at,
            'created_by': {
                'email': created_by.email,
                'id': created_by.id,
                'username': created_by.username,
                'name': created_by.name
            },
            'updated_at': updated_at,
            'updated_by': {
                'email': updated_by.email,
                'id': updated_by.id,
                'username': updated_by.username,
                'name': updated_by.name
            }
        })
        self.custom_fields = _custom_fields

    def update_custom_field_value(self, custom_field, updated_by, updated_at=datetime.utcnow().isoformat()):
        _custom_fields = copy.deepcopy(self.custom_fields)
        new_custom_fields = []
        for cf in _custom_fields:
            if cf['id'] == custom_field['id']:
                cf['value'] = custom_field['value']
                cf['updated_at'] = updated_at
                cf['updated_by']['email'] = updated_by.email
                cf['updated_by']['id'] = updated_by.id
                cf['updated_by']['username'] = updated_by.username
                cf['updated_by']['name'] = updated_by.name
            new_custom_fields.append(cf)
        self.custom_fields = new_custom_fields
        db.session.commit()

    def delete_custom_field_by_case_definition_custom_field_id(self, custom_field_id):
        print(f"deleting custom field ID {custom_field_id} for case ID {self.id}")
        _custom_fields = copy.deepcopy(self.custom_fields)
        new_custom_fields = []
        for cf in _custom_fields:
            if cf['case_definition_custom_field_id'] != custom_field_id:
                new_custom_fields.append(cf)
        self.custom_fields = new_custom_fields

    def get_custom_field(self, custom_field_id):
        for cf in self.custom_fields:
            if cf['id'] == str(custom_field_id):
                return cf

    def has_custom_field(self, custom_field_id):
        for cf in self.custom_fields:
            if cf['id'] == str(custom_field_id):
                return True
        return False

    def update_custom_field(self, custom_field, updated_by):
        print(f"updating custom field ID {custom_field.id} for case ID {self.id}")
        _custom_fields = copy.deepcopy(self.custom_fields)
        new_custom_fields = []
        for cf in _custom_fields:
            if cf['case_definition_custom_field_id'] == custom_field.id:
                cf['name'] = custom_field.name
                cf['field_type'] = custom_field.field_type
                cf['selections'] = custom_field.selections
                cf['validation_rules'] = custom_field.validation_rules
                cf['custom_section_id'] = custom_field.custom_section_id
                cf['help_text'] = custom_field.help_text
                cf['sort_order'] = custom_field.sort_order
                cf['value'] = None
                cf['updated_at'] = datetime.utcnow().isoformat()
                cf['updated_by']['email'] = updated_by.email
                cf['updated_by']['id'] = updated_by.id
                cf['updated_by']['username'] = updated_by.username
                cf['updated_by']['name'] = updated_by.name
            new_custom_fields.append(cf)
        self.custom_fields = new_custom_fields

    @staticmethod
    def generate_key(case_definition_id):
        cd = CaseDefinition.query.get(case_definition_id)
        cases_for_cd = Case.query.filter_by(case_definition_id=case_definition_id).all()
        if len(cases_for_cd) > 0:
            next_case_id = max([c.id for c in cases_for_cd]) + 1
        else:
            next_case_id = 1

        return f"{cd.key}-{next_case_id}"

    @hybrid.hybrid_property
    def surveys(self):
        case_defn = CaseDefinition.query.get(self.case_definition_id)

        surveys_list = []
        for survey in case_defn.surveys:
            responses_count = len(survey.responses.filter_by(case_id=self.id).all())
            item = {
                'id': survey.id,
                'name': survey.name,
                'responses_count': responses_count
            }
            surveys_list.append(item)

        return surveys_list

    @hybrid.hybrid_property
    def documents(self):
        case_defn = CaseDefinition.query.get(self.case_definition_id)
        files = self.files

        attachment_list = []
        for document in case_defn.documents:
            doc_files = [file for file in files if file.document_id == document.id]

            for file in doc_files:
                insert = document.__getstate__()
                insert.update(file.__getstate__())
                attachment_list.append(insert)

            if not doc_files:
                doc = document.__getstate__()
                insert = {
                    **doc,
                    'document_id': doc['id'],
                    'id': None,
                    'original_filename': None,
                    'remote_filename': None,
                    'url': None,
                }
                attachment_list.append(insert)

        independent_files = filter(lambda f: not any(f.document_id == d.id for d in case_defn.documents), files)

        for file in independent_files:
            insert = {
                'name': None,
                'description': None,
                'is_required': None,
                **file.__getstate__()
            }
            attachment_list.append(insert)

        return attachment_list

    @hybrid.hybrid_property
    def history(self):
        return history(self)


class CaseStatus(db.Model):
    __tablename__ = 'case_statuses'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    default = db.Column(db.Boolean, default=False, index=True)
    is_final = db.Column(db.Boolean, default=False)
    color = db.Column(db.String(16))

    @staticmethod
    def insert_case_statuses():
        statuses = [
            (1, 'TODO', True, False, '#B3B6B7'),
            (2, 'In Progress', False, False, '#0000FF'),
            (3, 'Done', False, True, '#00FF00')
        ]

        for status in statuses:
            db_status = CaseStatus.query.get(status[0])

            if db_status is None:
                db_status = CaseStatus(
                    name=status[1],
                    default=status[2],
                    is_final=status[3],
                    color=status[4],
                )
                db.session.add(db_status)

        db.session.commit()

    @staticmethod
    def is_valid_status(check_status_id):
        return check_status_id in [s.id for s in CaseStatus.query.all()]

    @staticmethod
    def supported_colors():
        return [
            'light-green',
            'light-blue ',
            'blue-grey',
            'indigo',
            'pink',
            'brown',
            'grey',
            'teal',
            'cyan'
        ]

    def __repr_(self):
        return f"<CaseStatus {self.id} - {self.name}"

    def __getstate__(self):
        from .model_schemas import CaseStatusSchema
        return CaseStatusSchema().dump(self)


class Project(db.Model, VersioningMixin):
    __tablename__ = 'projects'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True, nullable=False)
    title = db.Column(db.Text)
    organization = db.Column(db.String(64))
    agreement_number = db.Column(db.String(30))
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    funding_amount = db.Column(db.Float)
    location = db.Column(db.Text)
    created_at = db.Column(db.DateTime, index=True, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, index=True, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    updated_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # relationships
    created_by = db.relationship('User', foreign_keys=[created_by_id])
    updated_by = db.relationship('User', foreign_keys=[updated_by_id])

    def __repr__(self):
        return f"<Project {self.name}>"

    def __getstate__(self):
        from .model_schemas import ProjectSchema
        return ProjectSchema().dump(self)


class CustomField(db.Model):
    __tablename__ = 'custom_fields'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, nullable=False)
    field_type = db.Column(db.String(16), nullable=False)
    selections = db.Column(JSON)
    validation_rules = db.Column(db.ARRAY(db.Text))
    model_type = db.Column(db.String, nullable=False)
    model_id = db.Column(db.Integer)
    custom_section_id = db.Column(db.Integer)
    help_text = db.Column(db.Text)
    sort_order = db.Column(db.Integer, nullable=False, default=0)
    created_at = db.Column(db.DateTime, index=True, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, index=True, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    updated_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # relationships
    created_by = db.relationship('User', foreign_keys=[created_by_id])
    updated_by = db.relationship('User', foreign_keys=[updated_by_id])

    def __repr__(self):
        return f"<CustomField {self.name}>"

    def __getstate__(self):
        from .model_schemas import CustomFieldSchema
        return CustomFieldSchema().dump(self)


class Location(db.Model, VersioningMixin):
    __tablename__ = "locations"

    id = db.Column(db.Integer, primary_key=True)
    coordinates = db.Column(Geometry(geometry_type="POINT"))
    position_accuracy = db.Column(db.Float)
    altitude = db.Column(db.Float)
    altitude_accuracy = db.Column(db.Float)
    heading = db.Column(db.Float)
    location_speed = db.Column(db.Float)
    location_dt = db.Column(db.DateTime())

    @property
    def latitude(self):
        if self.coordinates is not None:
            return db.session.scalar(self.coordinates.ST_Y())
        else:
            return None

    @property
    def longitude(self):
        if self.coordinates is not None:
            return db.session.scalar(self.coordinates.ST_X())
        else:
            return None

    def __repr__(self):
        return f"<Location ({self.latitude}, {self.longitude})>"

    def __getstate__(self):
        from .model_schemas import LocationSchema
        return LocationSchema().dump(self)


activity_definitions_surveys = db.Table('activity_definitions_surveys', db.Model.metadata,
                                        db.Column('activity_definition_id', db.Integer,
                                                  db.ForeignKey('activity_definitions.id'),
                                                  nullable=False, index=True, primary_key=True),
                                        db.Column('survey_id', db.Integer, db.ForeignKey('surveys.id'), nullable=False,
                                                  index=True, primary_key=True))


class ActivityDefinition(db.Model, VersioningMixin):
    __tablename__ = 'activity_definitions'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.Text)
    case_definition_id = db.Column(db.Integer, db.ForeignKey('case_definitions.id'), nullable=False)
    custom_fields = db.Column(JSON)
    # reporting_table_name = db.Column(db.String(64))
    created_at = db.Column(db.DateTime(), index=True, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime(), index=True, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    updated_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # relationships
    surveys = db.relationship("Survey", secondary=activity_definitions_surveys, backref='activity_definitions',
                              lazy='dynamic')
    documents = db.relationship("ActivityDefinitionDocument")
    activities = db.relationship('Activity', backref='activity_definition', lazy='dynamic')
    created_by = db.relationship('User', foreign_keys=[created_by_id])
    updated_by = db.relationship('User', foreign_keys=[updated_by_id])

    def __init__(self, **kwargs):
        super(ActivityDefinition, self).__init__(**kwargs)

        if self.custom_fields is None:
            self.custom_fields = []

    def __repr__(self):
        return f"<ActivityDefinition {self.name}>"

    def __getstate__(self):
        from .model_schemas import ActivityDefinitionSchema
        return ActivityDefinitionSchema().dump(self)

    def get_custom_field(self, custom_field_id):
        for cf in self.custom_fields:
            if cf['id'] == str(custom_field_id):
                return cf

    def delete_custom_field(self, custom_field_id):

        _custom_fields = copy.deepcopy(self.custom_fields)
        new_custom_fields = []
        for cf in _custom_fields:
            if cf['id'] != custom_field_id:
                new_custom_fields.append(cf)
        self.custom_fields = new_custom_fields

    def update_custom_field(self, custom_field, updated_by):

        _custom_fields = copy.deepcopy(self.custom_fields)
        new_custom_fields = []
        for cf in _custom_fields:
            if cf['id'] == custom_field['id']:
                cf['name'] = custom_field['name']
                cf['field_type'] = custom_field['field_type']
                cf['selections'] = custom_field['selections']
                cf['validation_rules'] = custom_field['validation_rules']
                cf['custom_section_id'] = custom_field['custom_section_id']
                cf['help_text'] = custom_field['help_text']
                cf['sort_order'] = custom_field['sort_order']
                cf['value'] = None
                cf['updated_at'] = datetime.utcnow().isoformat()
                cf['updated_by']['email'] = updated_by.email
                cf['updated_by']['id'] = updated_by.id
                cf['updated_by']['username'] = updated_by.username
                cf['updated_by']['name'] = updated_by.name
            new_custom_fields.append(cf)
        self.custom_fields = new_custom_fields

    def add_custom_field(self, custom_field, created_by, updated_by, created_at=None,
                         updated_at=None):

        custom_field_id = custom_field.get('id', str(uuid.uuid4()))
        if created_at is None:
            created_at = datetime.utcnow().isoformat()
        if updated_at is None:
            updated_at = datetime.utcnow().isoformat()

        if custom_field_id in [cf['id'] for cf in self.custom_fields]:
            raise KeyError('Custom field IDs must be unique')
        _custom_fields = copy.deepcopy(self.custom_fields)
        _custom_fields.append({
            'id': custom_field_id,
            'name': custom_field['name'],
            'field_type': custom_field['field_type'],
            'selections': custom_field['selections'],
            'validation_rules': custom_field.get('validation_rules', []),
            'model_type': type(self).__name__,
            'parent_id': custom_field.get('parent_id'),
            'custom_section_id': custom_field.get('custom_section_id'),
            'help_text': custom_field['help_text'],
            'sort_order': custom_field['sort_order'],
            'value': None,
            'created_at': created_at,
            'created_by': {
                'email': created_by.email,
                'id': created_by.id,
                'username': created_by.username,
                'name': created_by.name
            },
            'updated_at': updated_at,
            'updated_by': {
                'email': updated_by.email,
                'id': updated_by.id,
                'username': updated_by.username,
                'name': updated_by.name
            }
        })
        self.custom_fields = _custom_fields
        return custom_field_id


class ActivityDefinitionDocument(db.Model, VersioningMixin):
    __tablename__ = 'activity_definition_documents'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.Text)
    is_required = db.Column(db.Boolean, default=False, nullable=False)
    activity_definition_id = db.Column(db.Integer, db.ForeignKey('activity_definitions.id'))

    def __repr__(self):
        return f"<ActivityDefinitionDocument {self.name}>"

    def __getstate__(self):
        from .model_schemas import ActivityDefinitionDocumentSchema
        return ActivityDefinitionDocumentSchema().dump(self)


class Activity(db.Model, VersioningMixin):
    __versioned__ = {
        'exclude': [
            'created_location_coordinates',
            'updated_location_coordinates'
        ]
    }
    __tablename__ = 'activities'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.Text)
    activity_definition_id = db.Column(db.Integer, db.ForeignKey('activity_definitions.id'), nullable=False)
    case_id = db.Column(db.Integer, db.ForeignKey('cases.id'), nullable=False)
    custom_fields = db.Column(JSON)
    is_complete = db.Column(db.Boolean, default=False, nullable=False)
    completed_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    completed_at = db.Column(db.DateTime())
    created_location_coordinates = db.Column(Geometry(geometry_type="POINT"))
    created_location_position_accuracy = db.Column(db.Float)
    created_location_altitude = db.Column(db.Float)
    created_location_altitude_accuracy = db.Column(db.Float)
    created_location_heading = db.Column(db.Float)
    created_location_speed = db.Column(db.Float)
    created_location_dt = db.Column(db.DateTime())
    updated_location_coordinates = db.Column(Geometry(geometry_type="POINT"))
    updated_location_position_accuracy = db.Column(db.Float)
    updated_location_altitude = db.Column(db.Float)
    updated_location_altitude_accuracy = db.Column(db.Float)
    updated_location_heading = db.Column(db.Float)
    updated_location_speed = db.Column(db.Float)
    updated_location_dt = db.Column(db.DateTime())
    created_at = db.Column(db.DateTime(), index=True, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime(), index=True, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    updated_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # relationships
    responses = db.relationship('SurveyResponse', backref='activity', lazy='dynamic')
    completed_by = db.relationship('User', foreign_keys=[completed_by_id])
    created_by = db.relationship('User', foreign_keys=[created_by_id])
    updated_by = db.relationship('User', foreign_keys=[updated_by_id])

    @hybrid.hybrid_property
    def notes(self):
        return Note.query.filter(and_(Note.model_name == 'Activity'), Note.model_id == self.id)

    @hybrid.hybrid_property
    def files(self):
        return UploadedFile.query.filter(and_(UploadedFile.model_name == 'Activity'), UploadedFile.model_id == self.id)

    @hybrid.hybrid_property
    def surveys(self):
        act_defn = ActivityDefinition.query.get(self.activity_definition_id)

        surveys_list = []
        for survey in act_defn.surveys:
            responses_count = len(survey.responses.filter_by(activity_id=self.id).all())
            item = {
                'id': survey.id,
                'name': survey.name,
                'responses_count': responses_count
            }
            surveys_list.append(item)

        return surveys_list

    @hybrid.hybrid_property
    def documents(self):
        act_defn = ActivityDefinition.query.get(self.activity_definition_id)
        files = self.files

        attachment_list = []
        for document in act_defn.documents:
            doc_files = [file for file in files if file.document_id == document.id]

            for file in doc_files:
                insert = document.__getstate__()
                insert.update(file.__getstate__())
                attachment_list.append(insert)

            if not doc_files:
                doc = document.__getstate__()
                insert = {
                    **doc,
                    'document_id': doc['id'],
                    'id': None,
                    'original_filename': None,
                    'remote_filename': None,
                    'url': None,
                }
                attachment_list.append(insert)

        independent_files = filter(lambda f: not any(f.document_id == d.id for d in act_defn.documents), files)

        for file in independent_files:
            insert = {
                'name': None,
                'description': None,
                'is_required': None,
                **file.__getstate__()
            }
            attachment_list.append(insert)

        return attachment_list

    def __init__(self, **kwargs):
        super(Activity, self).__init__(**kwargs)

        if self.custom_fields is None:
            self.custom_fields = []

    def __repr__(self):
        return f"<Activity {self.id} : {self.name}>"

    def __getstate__(self):
        from .model_schemas import ActivitySchema
        result = ActivitySchema().dump(self)
        return result

    def add_custom_field(self, custom_field, created_by, updated_by, custom_field_id=None, created_at=None,
                         updated_at=None):

        if custom_field_id is None:
            custom_field_id = str(uuid.uuid4())
        if created_at is None:
            created_at = datetime.utcnow().isoformat()
        if updated_at is None:
            updated_at = datetime.utcnow().isoformat()

        if custom_field_id in [cf['id'] for cf in self.custom_fields]:
            raise KeyError('Custom field IDs must be unique')
        _custom_fields = copy.deepcopy(self.custom_fields)
        _custom_fields.append({
            'id': custom_field_id,
            'name': custom_field['name'],
            'field_type': custom_field['field_type'],
            'selections': custom_field['selections'],
            'validation_rules': custom_field['validation_rules'],
            'model_type': 'Activity',
            'activity_definition_custom_field_id': custom_field['id'],
            'custom_section_id': custom_field['custom_section_id'],
            'help_text': custom_field['help_text'],
            'sort_order': custom_field['sort_order'],
            'value': None,
            'created_at': created_at,
            'created_by': {
                'email': created_by.email,
                'id': created_by.id,
                'username': created_by.username,
                'name': created_by.name
            },
            'updated_at': updated_at,
            'updated_by': {
                'email': updated_by.email,
                'id': updated_by.id,
                'username': updated_by.username,
                'name': updated_by.name
            }
        })
        self.custom_fields = _custom_fields

    def get_custom_field(self, custom_field_id):
        for cf in self.custom_fields:
            if cf['id'] == str(custom_field_id):
                return cf

    def has_custom_field(self, custom_field_id):
        for cf in self.custom_fields:
            if cf['id'] == str(custom_field_id):
                return True
        return False

    def update_custom_field_value(self, custom_field, updated_by, updated_at=datetime.utcnow().isoformat()):
        _custom_fields = copy.deepcopy(self.custom_fields)
        new_custom_fields = []
        for cf in _custom_fields:
            if cf['id'] == custom_field['id']:
                cf['value'] = custom_field['value']
                cf['updated_at'] = updated_at
                cf['updated_by']['email'] = updated_by.email
                cf['updated_by']['id'] = updated_by.id
                cf['updated_by']['username'] = updated_by.username
                cf['updated_by']['name'] = updated_by.name
            new_custom_fields.append(cf)
        self.custom_fields = new_custom_fields

    def update_custom_field(self, custom_field_id, updated_custom_field, updated_by,
                            updated_at=datetime.utcnow().isoformat()):

        _custom_fields = copy.deepcopy(self.custom_fields)
        new_custom_fields = []
        for cf in _custom_fields:
            if cf['id'] == custom_field_id:
                new_cf = {
                    'id': cf['id'],
                    'name': updated_custom_field['name'],
                    'field_type': updated_custom_field['field_type'],
                    'selections': updated_custom_field['selections'],
                    'validation_rules': updated_custom_field['validation_rules'],
                    'model_type': 'Activity',
                    'activity_definition_custom_field_id': updated_custom_field['id'],
                    'custom_section_id': updated_custom_field['custom_section_id'],
                    'help_text': updated_custom_field['help_text'],
                    'sort_order': updated_custom_field['sort_order'],
                    'value': None,
                    'created_at': cf['created_at'],
                    'created_by': {
                        'email': cf['created_by']['email'],
                        'id': cf['created_by']['id'],
                        'username': cf['created_by']['username'],
                        'name': cf['created_by']['name']
                    },
                    'updated_at': updated_at,
                    'updated_by': {
                        'email': updated_by.email,
                        'id': updated_by.id,
                        'username': updated_by.username,
                        'name': updated_by.name
                    }
                }
                new_custom_fields.append(new_cf)
            else:
                new_custom_fields.append(cf)
            self.custom_fields = new_custom_fields

    @hybrid.hybrid_property
    def history(self):
        return history(self)


class Note(db.Model, VersioningMixin):
    __tablename__ = 'notes'

    id = db.Column(db.Integer, primary_key=True)
    model_name = db.Column(db.String, nullable=False)
    model_id = db.Column(db.Integer, nullable=False)
    note = db.Column(db.Text)
    created_at = db.Column(db.DateTime(), index=True, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime(), index=True, default=datetime.utcnow, onupdate=datetime.utcnow,
                           nullable=False)
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    updated_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # relationships
    created_by = db.relationship('User', foreign_keys=[created_by_id])
    updated_by = db.relationship('User', foreign_keys=[updated_by_id])

    def __repr__(self):
        return f"<Notes {self.id : self.note}>"

    def __getstate__(self):
        from .model_schemas import NoteSchema
        return NoteSchema().dump(self)


class UploadedFile(db.Model, VersioningMixin):
    __tablename__ = 'uploaded_files'

    id = db.Column(db.Integer, primary_key=True)
    model_name = db.Column(db.String, nullable=False)
    model_id = db.Column(db.Integer, nullable=False)
    document_id = db.Column(db.Integer, nullable=True)
    original_filename = db.Column(db.Text)
    remote_filename = db.Column(db.Text)
    uploaded_location_id = db.Column(db.Integer, db.ForeignKey('locations.id'))
    taken_location_id = db.Column(db.Integer, db.ForeignKey('locations.id'))
    extracted_location_id = db.Column(db.Integer, db.ForeignKey('locations.id'))
    created_at = db.Column(db.DateTime(), index=True, default=datetime.utcnow, nullable=False)
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # relationships
    created_by = db.relationship('User', foreign_keys=[created_by_id])
    uploaded_location = db.relationship('Location', foreign_keys=[uploaded_location_id])
    taken_location = db.relationship('Location', foreign_keys=[taken_location_id])
    extracted_location = db.relationship('Location', foreign_keys=[extracted_location_id])

    def __repr__(self):
        return f"<UploadedFile {self.id} : {self.original_filename}>"

    def __getstate__(self):
        from .model_schemas import UploadedFileSchema
        return UploadedFileSchema().dump(self)

    @hybrid.hybrid_property
    def url(self):
        if self.model_name == 'Activity':
            return f'/activities/files/{self.id}/download'
        else:
            return f'/files/{self.id}/download'
