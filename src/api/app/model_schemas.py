from geoalchemy2.types import Geometry

from . import ma, models, db
from marshmallow_sqlalchemy import ModelConverter as BaseModelConverter
from marshmallow import fields


class GeoConverter(BaseModelConverter):
    SQLA_TYPE_MAPPING = BaseModelConverter.SQLA_TYPE_MAPPING.copy()
    SQLA_TYPE_MAPPING.update({
        Geometry: fields.Str
    })


class LocationSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = models.Location
        additional = ['latitude', 'longitude']
        exclude = ['coordinates']


class EPSPropertySchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = models.EPSProperty


class RoleSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = models.Role
        additional = ['permission_codes']


class UserSchema(ma.SQLAlchemyAutoSchema):
    role = ma.Nested(RoleSchema)

    class Meta:
        model = models.User
        model_converter = GeoConverter
        exclude = ['last_login_location_dt', 'last_login_location_coordinates', 'last_login_location_position_accuracy',
                   'last_login_location_altitude', 'last_login_location_altitude_accuracy',
                   'last_login_location_heading', 'last_login_location_speed']

    last_login_location = fields.Method("get_last_login_location")

    def get_last_login_location(self, obj):

        if obj.last_login_location_coordinates is not None:
            latitude = db.session.scalar(obj.last_login_location_coordinates.ST_Y())
            longitude = db.session.scalar(obj.last_login_location_coordinates.ST_X())
        else:
            latitude = None
            longitude = None

        if obj.last_login_location_dt is not None:
            last_login_location_dt_value = obj.last_login_location_dt.isoformat()
        else:
            last_login_location_dt_value = None
        return {
            "latitude": latitude,
            "longitude": longitude,
            "position_accuracy": obj.last_login_location_position_accuracy,
            "altitude": obj.last_login_location_altitude,
            "altitude_accuracy": obj.last_login_location_altitude_accuracy,
            "heading": obj.last_login_location_heading,
            "speed": obj.last_login_location_speed,
            "location_recorded_dt": last_login_location_dt_value
        }


class SurveyResponseStatusSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = models.SurveyResponseStatus


class SurveySchema(ma.SQLAlchemyAutoSchema):
    created_by = ma.Nested(UserSchema, only=['id', 'email', 'username', 'name', 'color'])
    updated_by = ma.Nested(UserSchema, only=['id', 'email', 'username', 'name', 'color'])

    class Meta:
        model = models.Survey


class SurveyResponseSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = models.SurveyResponse
        exclude = ['created_location_coordinates', 'created_location_altitude', 'created_location_altitude_accuracy',
                   'created_location_dt', 'created_location_heading', 'created_location_position_accuracy',
                   'created_location_speed', 'updated_location_coordinates', 'updated_location_altitude',
                   'updated_location_altitude_accuracy', 'updated_location_dt', 'updated_location_heading',
                   'updated_location_position_accuracy', 'updated_location_speed']

    created_by = ma.Nested(UserSchema, only=['id', 'email', 'username', 'name', 'color'])
    updated_by = ma.Nested(UserSchema, only=['id', 'email', 'username', 'name', 'color'])
    status = ma.Nested(SurveyResponseStatusSchema)
    survey = ma.auto_field('survey_id', dump_only=True)
    case_id = ma.auto_field('case_id', dump_only=True)
    activity_id = ma.auto_field('activity_id', dump_only=True)
    created_location = fields.Method('get_created_location')
    updated_location = fields.Method('get_updated_location')

    def get_created_location(self, obj):

        if obj.created_location_coordinates is not None:
            latitude = db.session.scalar(obj.created_location_coordinates.ST_Y())
            longitude = db.session.scalar(obj.created_location_coordinates.ST_X())
        else:
            latitude = None
            longitude = None

        if obj.created_location_dt is not None:
            created_location_dt_value = obj.created_location_dt.isoformat()
        else:
            created_location_dt_value = None
        return {
            "latitude": latitude,
            "longitude": longitude,
            "position_accuracy": obj.created_location_position_accuracy,
            "altitude": obj.created_location_altitude,
            "altitude_accuracy": obj.created_location_altitude_accuracy,
            "heading": obj.created_location_heading,
            "speed": obj.created_location_speed,
            "location_recorded_dt": created_location_dt_value
        }

    def get_updated_location(self, obj):

        if obj.updated_location_coordinates is not None:
            latitude = db.session.scalar(obj.updated_location_coordinates.ST_Y())
            longitude = db.session.scalar(obj.updated_location_coordinates.ST_X())
        else:
            latitude = None
            longitude = None

        if obj.updated_location_dt is not None:
            updated_location_dt_value = obj.updated_location_dt.isoformat()
        else:
            updated_location_dt_value = None
        return {
            "latitude": latitude,
            "longitude": longitude,
            "position_accuracy": obj.updated_location_position_accuracy,
            "altitude": obj.updated_location_altitude,
            "altitude_accuracy": obj.updated_location_altitude_accuracy,
            "heading": obj.updated_location_heading,
            "speed": obj.updated_location_speed,
            "location_recorded_dt": updated_location_dt_value
        }


class CaseDefinitionDocumentSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = models.CaseDefinitionDocument


class CaseDefinitionSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = models.CaseDefinition
        additional = ['custom_fields']

    created_by = ma.Nested(UserSchema, only=['id', 'email', 'username', 'name', 'color'])
    updated_by = ma.Nested(UserSchema, only=['id', 'email', 'username', 'name', 'color'])
    surveys = ma.Nested(SurveySchema, many=True, only=['id', 'name'])
    documents = ma.Nested(CaseDefinitionDocumentSchema, many=True)
    activity_definitions = fields.Method('get_activity_definitions')

    def get_activity_definitions(self, case_def):
        activity_definitions = []
        for activity_definition in case_def.activity_definitions:
            act_def = activity_definition.__getstate__()
            activity_definitions.append(act_def)
        return activity_definitions


class CaseStatusSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = models.CaseStatus


class ProjectSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = models.Project

    created_by = ma.Nested(UserSchema, only=['id', 'email', 'username', 'name', 'color'])
    updated_by = ma.Nested(UserSchema, only=['id', 'email', 'username', 'name', 'color'])


class CustomFieldSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = models.CustomField

    created_by = ma.Nested(UserSchema, only=['id', 'email', 'username', 'name', 'color'])
    updated_by = ma.Nested(UserSchema, only=['id', 'email', 'username', 'name', 'color'])


class ActivityDefinitionDocumentSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = models.ActivityDefinitionDocument


class ActivityDefinitionSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = models.ActivityDefinition

    created_by = ma.Nested(UserSchema, only=['id', 'email', 'username', 'name', 'color'])
    updated_by = ma.Nested(UserSchema, only=['id', 'email', 'username', 'name', 'color'])
    surveys = ma.Nested(SurveySchema, many=True, only=['id', 'name'])
    documents = ma.Nested(ActivityDefinitionDocumentSchema, many=True)
    case_definition = ma.Nested(CaseDefinitionSchema, only=['id', 'key', 'name'])


class NoteSchema(ma.SQLAlchemyAutoSchema):
    created_by = ma.Nested(UserSchema, only=['id', 'email', 'username', 'name', 'color'])
    updated_by = ma.Nested(UserSchema, only=['id', 'email', 'username', 'name', 'color'])

    class Meta:
        model = models.Note


class UploadedFileSchema(ma.SQLAlchemyAutoSchema):
    uploaded_location = ma.Nested(LocationSchema)
    taken_location = ma.Nested(LocationSchema)
    extracted_location = ma.Nested(LocationSchema)
    created_by = ma.Nested(UserSchema, only=['id', 'email', 'username', 'name', 'color'])

    class Meta:
        model = models.UploadedFile
        additional = ['url', 'document_id']


class ActivitySchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = models.Activity
        additional = ['surveys', 'documents', 'history']
        exclude = ['created_location_coordinates', 'created_location_altitude', 'created_location_altitude_accuracy',
                   'created_location_dt', 'created_location_heading', 'created_location_position_accuracy',
                   'created_location_speed', 'updated_location_coordinates', 'updated_location_altitude',
                   'updated_location_altitude_accuracy', 'updated_location_dt', 'updated_location_heading',
                   'updated_location_position_accuracy', 'updated_location_speed']

    activity_definition = ma.Nested(ActivityDefinitionSchema, only=['id', 'name'])
    # case = ma.Nested(CaseSchema)
    created_by = ma.Nested(UserSchema, only=['id', 'email', 'username', 'name', 'color'])
    updated_by = ma.Nested(UserSchema, only=['id', 'email', 'username', 'name', 'color'])
    completed_by = ma.Nested(UserSchema, only=['id', 'email', 'username', 'name', 'color'])
    notes = ma.Nested(NoteSchema, many=True, only=['id', 'note', 'created_at', 'updated_at', 'created_by',
                                                   'updated_by'])
    files = ma.Nested(
        UploadedFileSchema,
        many=True,
        only=['id', 'original_filename', 'remote_filename', 'created_at', 'created_by', 'url']
    )
    created_location = fields.Method('get_created_location')
    updated_location = fields.Method('get_updated_location')
    case = fields.Method('get_case')

    def get_created_location(self, obj):

        if obj.created_location_coordinates is not None:
            latitude = db.session.scalar(obj.created_location_coordinates.ST_Y())
            longitude = db.session.scalar(obj.created_location_coordinates.ST_X())
        else:
            latitude = None
            longitude = None

        if obj.created_location_dt is not None:
            created_location_dt_value = obj.created_location_dt.isoformat()
        else:
            created_location_dt_value = None
        return {
            "latitude": latitude,
            "longitude": longitude,
            "position_accuracy": obj.created_location_position_accuracy,
            "altitude": obj.created_location_altitude,
            "altitude_accuracy": obj.created_location_altitude_accuracy,
            "heading": obj.created_location_heading,
            "speed": obj.created_location_speed,
            "location_recorded_dt": created_location_dt_value
        }

    def get_updated_location(self, obj):

        if obj.updated_location_coordinates is not None:
            latitude = db.session.scalar(obj.updated_location_coordinates.ST_Y())
            longitude = db.session.scalar(obj.updated_location_coordinates.ST_X())
        else:
            latitude = None
            longitude = None

        if obj.updated_location_dt is not None:
            updated_location_dt_value = obj.updated_location_dt.isoformat()
        else:
            updated_location_dt_value = None
        return {
            "latitude": latitude,
            "longitude": longitude,
            "position_accuracy": obj.updated_location_position_accuracy,
            "altitude": obj.updated_location_altitude,
            "altitude_accuracy": obj.updated_location_altitude_accuracy,
            "heading": obj.updated_location_heading,
            "speed": obj.updated_location_speed,
            "location_recorded_dt": updated_location_dt_value
        }

    def get_case(self, obj):
        if obj.case is not None:
            return {
                'id': obj.case.id,
                'key': obj.case.key,
                'name': obj.case.name,
                'definition': {
                    'id': obj.case.case_definition.id,
                    'key': obj.case.case_definition.key,
                    'name': obj.case.case_definition.name
                }
            }
        else:
            return {'id': None,
                    'key': None,
                    'name': None,
                    'definition': {
                        'id': None,
                        'key': None,
                        'name': None
                    }}


class CaseSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = models.Case
        additional = ['surveys', 'documents', 'history']
        exclude = ['created_location_coordinates', 'created_location_altitude', 'created_location_altitude_accuracy',
                   'created_location_dt', 'created_location_heading', 'created_location_position_accuracy',
                   'created_location_speed', 'updated_location_coordinates', 'updated_location_altitude',
                   'updated_location_altitude_accuracy', 'updated_location_dt', 'updated_location_heading',
                   'updated_location_position_accuracy', 'updated_location_speed', 'assigned_at']

    assigned_to = fields.Method('get_assigned_to')
    case_definition = ma.Nested(CaseDefinitionSchema, only=['id', 'key', 'name'])
    created_by = ma.Nested(UserSchema, only=['id', 'email', 'username', 'name', 'color'])
    updated_by = ma.Nested(UserSchema, only=['id', 'email', 'username', 'name', 'color'])
    activities = ma.Nested(ActivitySchema, many=True,
                           only=['id', 'name', 'is_complete', 'completed_at', 'completed_by', 'created_at',
                                 'updated_at'])
    status = ma.Nested(CaseStatusSchema)
    notes = ma.Nested(NoteSchema, many=True, only=['id', 'note', 'created_at', 'updated_at', 'created_by',
                                                   'updated_by'])
    files = ma.Nested(
        UploadedFileSchema,
        many=True,
        only=['id', 'original_filename', 'remote_filename', 'created_at', 'created_by', 'url']
    )
    created_location = fields.Method('get_created_location')
    updated_location = fields.Method('get_updated_location')

    def get_created_location(self, obj):

        if obj.created_location_coordinates is not None:
            latitude = db.session.scalar(obj.created_location_coordinates.ST_Y())
            longitude = db.session.scalar(obj.created_location_coordinates.ST_X())
        else:
            latitude = None
            longitude = None

        if obj.created_location_dt is not None:
            created_location_dt_value = obj.created_location_dt.isoformat()
        else:
            created_location_dt_value = None
        return {
            "latitude": latitude,
            "longitude": longitude,
            "position_accuracy": obj.created_location_position_accuracy,
            "altitude": obj.created_location_altitude,
            "altitude_accuracy": obj.created_location_altitude_accuracy,
            "heading": obj.created_location_heading,
            "speed": obj.created_location_speed,
            "location_recorded_dt": created_location_dt_value
        }

    def get_updated_location(self, obj):

        if obj.updated_location_coordinates is not None:
            latitude = db.session.scalar(obj.updated_location_coordinates.ST_Y())
            longitude = db.session.scalar(obj.updated_location_coordinates.ST_X())
        else:
            latitude = None
            longitude = None

        if obj.updated_location_dt is not None:
            updated_location_dt_value = obj.updated_location_dt.isoformat()
        else:
            updated_location_dt_value = None
        return {
            "latitude": latitude,
            "longitude": longitude,
            "position_accuracy": obj.updated_location_position_accuracy,
            "altitude": obj.updated_location_altitude,
            "altitude_accuracy": obj.updated_location_altitude_accuracy,
            "heading": obj.updated_location_heading,
            "speed": obj.updated_location_speed,
            "location_recorded_dt": updated_location_dt_value
        }

    def get_assigned_to(self, case: models.Case):
        if case.assigned_to_id:
            if case.assigned_at is not None:
                assigned_at = case.assigned_at.isoformat()
            else:
                assigned_at = None
            return {
                'id': case.assigned_to.id,
                'email': case.assigned_to.email,
                'username': case.assigned_to.username,
                'name': case.assigned_to.name,
                'color': case.assigned_to.color,
                'assigned_at': assigned_at
            }
        else:
            return None
