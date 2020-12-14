from flask import jsonify, request, current_app, g
from . import activity_definitions
from app import helpers, models
from app.activity_definitions.activity_definitions_service import ActivityDefinitionsService


@activity_definitions.route('', methods=['POST'])
@helpers.jwt_auth
@helpers.role_restrict(
    roles=models.Permission.CREATE_ACTIVITY_DEFINITION,
    message=models.Permission.MSG_CREATE_ACTIVITY_DEFINITION
)
def post_activity_definition():
    current_app.logger.info(f"/activity_definitions POST accessed by {g.request_user.email}")
    service = ActivityDefinitionsService(json_args=request.get_json())
    activity_definition = service.post()
    return jsonify(activity_definition.__getstate__()), 200


@activity_definitions.route('', methods=['GET'])
@helpers.jwt_auth
@helpers.role_restrict(
    roles=models.Permission.READ_ACTIVITY_DEFINITION,
    message=models.Permission.MSG_READ_ACTIVITY_DEFINITION
)
def get_activity_definitions():
    current_app.logger.info(f"/activity_definitions GET accessed by {g.request_user.email}")
    service = ActivityDefinitionsService()
    return service.get_all()


@activity_definitions.route('/<int:activity_definition_id>', methods=['GET'])
@helpers.jwt_auth
@helpers.role_restrict(
    roles=models.Permission.READ_ACTIVITY_DEFINITION,
    message=models.Permission.MSG_READ_ACTIVITY_DEFINITION
)
def get_activity_definition(activity_definition_id):
    current_app.logger.info(f"/activity_definitions/{activity_definition_id} GET accessed by {g.request_user.email}")
    service = ActivityDefinitionsService()
    return service.get(activity_definition_id)


@activity_definitions.route('/<int:activity_definition_id>', methods=['PUT'])
@helpers.jwt_auth
@helpers.role_restrict(
    roles=models.Permission.UPDATE_ACTIVITY_DEFINITION,
    message=models.Permission.MSG_UPDATE_ACTIVITY_DEFINITION
)
def put_activity_definition(activity_definition_id):
    current_app.logger.info(f"/activity_definitions/{activity_definition_id} PUT accessed by {g.request_user.email}")
    service = ActivityDefinitionsService(json_args=request.get_json())
    return service.put(activity_definition_id)


@activity_definitions.route('/<int:activity_definition_id>', methods=['DELETE'])
@helpers.jwt_auth
@helpers.role_restrict(
    roles=models.Permission.DELETE_ACTIVITY_DEFINITION,
    message=models.Permission.MSG_DELETE_ACTIVITY_DEFINITION
)
def delete_activity_definition(activity_definition_id):
    current_app.logger.info(f"/activity_definitions/{activity_definition_id} DELETE accessed by {g.request_user.email}")
    service = ActivityDefinitionsService()
    return service.delete(activity_definition_id)


@activity_definitions.route('/<int:activity_definition_id>/custom_fields', methods=['GET'])
@helpers.jwt_auth
@helpers.role_restrict(
    roles=models.Permission.READ_ACTIVITY_DEFINITION,
    message=models.Permission.MSG_READ_ACTIVITY_DEFINITION
)
def get_custom_fields(activity_definition_id):
    current_app.logger.info(
        f"/activity_definitions/{activity_definition_id}/custom_fields GET accessed by {g.request_user.email}")
    service = ActivityDefinitionsService()
    return service.get_all_custom_fields(activity_definition_id)


@activity_definitions.route('/<int:activity_definition_id>/custom_fields/<string:custom_field_id>', methods=['GET'])
@helpers.jwt_auth
@helpers.role_restrict(
    roles=models.Permission.READ_ACTIVITY_DEFINITION,
    message=models.Permission.MSG_READ_ACTIVITY_DEFINITION
)
def get_custom_field(activity_definition_id, custom_field_id):
    current_app.logger.info(
        f"/activity_definitions/{activity_definition_id}/custom_fields/{custom_field_id} GET accessed by {g.request_user.email}")
    service = ActivityDefinitionsService()
    return service.get_custom_field(activity_definition_id, custom_field_id)


@activity_definitions.route('/<int:activity_definition_id>/custom_fields/<string:custom_field_id>', methods=['DELETE'])
@helpers.jwt_auth
@helpers.role_restrict(
    roles=models.Permission.DELETE_ACTIVITY_DEFINITION,
    message=models.Permission.MSG_DELETE_ACTIVITY_DEFINITION
)
def delete_custom_field(activity_definition_id, custom_field_id):
    current_app.logger.info(
        f"/activity_definitions/{activity_definition_id}/custom_fields/{custom_field_id} DELETE accessed by {g.request_user.email}")
    service = ActivityDefinitionsService()
    return service.delete_custom_field(activity_definition_id, custom_field_id)


@activity_definitions.route('/<int:activity_definition_id>/custom_fields/<string:custom_field_id>', methods=['PUT'])
@helpers.jwt_auth
@helpers.role_restrict(
    roles=models.Permission.UPDATE_ACTIVITY_DEFINITION,
    message=models.Permission.MSG_UPDATE_ACTIVITY_DEFINITION
)
def put_custom_field(activity_definition_id, custom_field_id):
    current_app.logger.info(
        f"/activity_definitions/{activity_definition_id}/custom_fields/{custom_field_id} PUT accessed by {g.request_user.email}")
    service = ActivityDefinitionsService(json_args=request.get_json())
    return service.put_custom_field(activity_definition_id, custom_field_id)


@activity_definitions.route('/<int:activity_definition_id>/custom_fields', methods=['POST'])
@helpers.jwt_auth
@helpers.role_restrict(
    roles=models.Permission.UPDATE_ACTIVITY_DEFINITION,
    message=models.Permission.MSG_UPDATE_ACTIVITY_DEFINITION
)
def post_custom_field(activity_definition_id):
    current_app.logger.info(
        f"/activity_definitions/{activity_definition_id}/custom_fields POST accessed by {g.request_user.email}")
    service = ActivityDefinitionsService(json_args=request.get_json())
    return service.post_custom_field(activity_definition_id)
