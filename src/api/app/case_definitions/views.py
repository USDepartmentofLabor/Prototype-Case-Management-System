from flask import jsonify, request, current_app, g
import flask_babel
from sqlalchemy import and_
from . import case_definitions
from .. import models, db
from app import helpers
from app.case_definitions.case_definitions_service import CaseDefinitionsService
from app.cases.cases_service import CasesService


# /case_definitions POST
from ..services.eps_reporting_service import EPSReportingServiceException


@case_definitions.route('/', methods=['POST'])
@helpers.jwt_auth
@helpers.role_restrict(
    roles=models.Permission.CREATE_CASE_DEFINITION,
    message=models.Permission.MSG_CREATE_CASE_DEFINITION
)
def post_case_definition():
    current_app.logger.info(f"/case_definitions POST accessed by {g.request_user.email}")
    service = CaseDefinitionsService(json_args=request.get_json())
    return service.post()


# /case_definitions GET
@case_definitions.route('/', methods=['GET'])
@helpers.jwt_auth
@helpers.role_restrict(
    roles=models.Permission.READ_CASE_DEFINITION,
    message=models.Permission.MSG_READ_CASE_DEFINITION
)
def get_case_definitions():
    current_app.logger.info(f"/case_definitions GET accessed by {g.request_user.email}")

    return jsonify([cd.__getstate__() for cd in models.CaseDefinition.query.all()]), 200


@case_definitions.route('/<int:case_definition_id>', methods=['GET'])
@helpers.jwt_auth
@helpers.role_restrict(
    roles=models.Permission.READ_CASE_DEFINITION,
    message=models.Permission.MSG_READ_CASE_DEFINITION
)
def get_case_definition(case_definition_id):
    current_app.logger.info(f"/case_definitions/{case_definition_id} GET accessed by {g.request_user.email}")

    case_def = models.CaseDefinition.query.get_or_404(case_definition_id)
    return jsonify(case_def.__getstate__()), 200


@case_definitions.route('/<int:case_definition_id>', methods=['PUT'])
@helpers.jwt_auth
@helpers.role_restrict(
    roles=models.Permission.UPDATE_CASE_DEFINITION,
    message=models.Permission.MSG_UPDATE_CASE_DEFINITION
)
def update_case_definition(case_definition_id):
    current_app.logger.info(f"/case_definitions/{case_definition_id} PUT accessed by {g.request_user.email}")
    service = CaseDefinitionsService(json_args=request.get_json())
    return service.put(case_definition_id)


# /case_definitions/<case_definition_id>/cases POST
@case_definitions.route('/<int:case_definition_id>/cases', methods=['POST'])
@helpers.jwt_auth
@helpers.role_restrict(
    roles=models.Permission.CREATE_CASE,
    message=models.Permission.MSG_CREATE_CASE,
)
def post_case(case_definition_id):
    current_app.logger.info(f"/case_definitions/{case_definition_id}/cases POST accessed by {g.request_user.email}")

    if not request.is_json:
        msg = flask_babel.gettext("Missing JSON in request")
        return jsonify({"message": msg}), 400

    case_defn = models.CaseDefinition.query.get_or_404(case_definition_id)

    service = CasesService(json_args=request.get_json())
    return service.post(case_defn)


@case_definitions.route('/<int:case_definition_id>', methods=['DELETE'])
@helpers.jwt_auth
@helpers.role_restrict(
    roles=models.Permission.DELETE_CASE_DEFINITION,
    message=models.Permission.MSG_DELETE_CASE_DEFINITION,
    admin_allowed=True
)
def delete_case_definition(case_definition_id):
    current_app.logger.info(f"/case_definitions/{case_definition_id} DELETE accessed by {g.request_user.email}")

    case_defn = models.CaseDefinition.query.get_or_404(case_definition_id)

    try:
        current_app.reporting_service.delete_case_table(case_defn.reporting_table_name)
        helpers.metabase_rescan()
    except EPSReportingServiceException as ex:
        current_app.logger.error(f"error deleting reporting table: {ex}")

    for survey in case_defn.surveys:
        for survey_resp in survey.responses:
            db.session.delete(survey_resp)

    for doc in case_defn.documents:
        db.session.delete(doc)

    for case in case_defn.cases:
        for note in case.notes:
            db.session.delete(note)

        db.session.delete(case)

    # have to query for fields here since custom_fields is a hybrid sqlalchemy property
    # and each custom field in the list is disconnected from sqlalchemy tracking.
    custom_fields = models.CustomField.query.filter(and_(models.CustomField.model_type == 'CaseDefinition',
                                                         models.CustomField.model_id == case_definition_id))
    for cf in custom_fields:
        db.session.delete(cf)

    db.session.delete(case_defn)
    db.session.commit()

    msg = flask_babel.gettext("Case definition successfully deleted.")
    return jsonify({"message": msg}), 200


@case_definitions.route('/<int:case_definition_id>/custom_fields', methods=['POST'])
@helpers.jwt_auth
@helpers.role_restrict(
    roles=models.Permission.UPDATE_CASE_DEFINITION,
    message=models.Permission.MSG_UPDATE_CASE_DEFINITION,
    admin_allowed=True
)
def post_custom_field(case_definition_id):
    lmsg = f"/case_definitions/{case_definition_id}/custom_fields POST accessed by {g.request_user.email}"
    current_app.logger.info(lmsg)

    case_defn = models.CaseDefinition.query.get_or_404(case_definition_id)

    service = CaseDefinitionsService(json_args=request.get_json())
    return service.add_custom_field(case_defn.id)


@case_definitions.route('/<int:case_definition_id>/custom_fields/<int:custom_field_id>', methods=['PUT'])
@helpers.jwt_auth
@helpers.role_restrict(
    roles=models.Permission.UPDATE_CASE_DEFINITION,
    message=models.Permission.MSG_UPDATE_CASE_DEFINITION,
    admin_allowed=True
)
def put_custom_field(case_definition_id, custom_field_id):
    lmsg = f"/case_definitions/{case_definition_id}/custom_fields/{custom_field_id} PUT accessed by {g.request_user.email}"
    current_app.logger.info(lmsg)

    service = CaseDefinitionsService(json_args=request.get_json())
    return service.update_custom_field(case_definition_id, custom_field_id)


@case_definitions.route('/<int:case_definition_id>/custom_fields', methods=['GET'])
@helpers.jwt_auth
@helpers.role_restrict(
    roles=models.Permission.READ_CASE_DEFINITION,
    message=models.Permission.MSG_READ_CASE_DEFINITION,
    admin_allowed=True
)
def get_custom_fields(case_definition_id):
    lmsg = f"/case_definitions/{case_definition_id}/custom_fields GET accessed by {g.request_user.email}"
    current_app.logger.info(lmsg)

    service = CaseDefinitionsService(json_args=request.get_json())
    return service.get_custom_fields(case_definition_id)


@case_definitions.route('/<int:case_definition_id>/custom_fields/<int:custom_field_id>', methods=['GET'])
@helpers.jwt_auth
@helpers.role_restrict(
    roles=models.Permission.READ_CASE_DEFINITION,
    message=models.Permission.MSG_READ_CASE_DEFINITION,
    admin_allowed=True
)
def get_custom_field(case_definition_id, custom_field_id):
    lmsg = f"/case_definitions/{case_definition_id}/custom_fields/{custom_field_id} GET accessed by {g.request_user.email}"
    current_app.logger.info(lmsg)

    service = CaseDefinitionsService(json_args=request.get_json())
    return service.get_custom_field(case_definition_id, custom_field_id)


@case_definitions.route('/<int:case_definition_id>/custom_fields/<int:custom_field_id>', methods=['DELETE'])
@helpers.jwt_auth
@helpers.role_restrict(
    roles=models.Permission.UPDATE_CASE_DEFINITION,
    message=models.Permission.MSG_UPDATE_CASE_DEFINITION,
    admin_allowed=True
)
def delete_custom_field(case_definition_id, custom_field_id):
    lmsg = f"/case_definitions/{case_definition_id}/custom_fields/{custom_field_id} DELETE accessed by {g.request_user.email}"
    current_app.logger.info(lmsg)

    service = CaseDefinitionsService(json_args=request.get_json())
    return service.delete_custom_field(case_definition_id, custom_field_id)
