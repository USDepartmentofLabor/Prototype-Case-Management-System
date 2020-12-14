import flask_babel
from flask import jsonify, current_app, g, request
import app
from app import helpers, models, files, notes
from .activities_service import ActivitiesService
from . import activities


@activities.route('', methods=['POST'])
@helpers.jwt_auth
@helpers.role_restrict(
    roles=models.Permission.CREATE_ACTIVITY,
    message=models.Permission.MSG_CREATE_ACTIVITY,
)
def post_activity():
    current_app.logger.info(f"/activities POST accessed by {g.request_user.email}")
    # return jsonify({"message": "successfully called post_activity()"}), 200

    if 'activity_definition_id' in request.get_json():
        activity_definition = models.ActivityDefinition.query.get(request.get_json().get('activity_definition_id'))
    else:
        activity_definition = None

    service = ActivitiesService(json_args=request.get_json())
    return service.post(activity_definition)


@activities.route('', methods=['GET'])
@helpers.jwt_auth
@helpers.role_restrict(
    roles=models.Permission.READ_ACTIVITY,
    message=models.Permission.MSG_READ_ACTIVITY,
)
def get_activities():
    current_app.logger.info(f"/activities GET accessed by {g.request_user.email}")
    # return jsonify({"message": "successfully called get_activities()"}), 200

    service = ActivitiesService(json_args={})
    return service.get_all()


@activities.route('/<int:activity_id>', methods=['GET'])
@helpers.jwt_auth
@helpers.role_restrict(
    roles=models.Permission.READ_ACTIVITY,
    message=models.Permission.MSG_READ_ACTIVITY,
)
def get_activity(activity_id):
    current_app.logger.info(f"/activities/{activity_id} GET accessed by {g.request_user.email}")
    # return jsonify({"message": "successfully called get_activity()"}), 200
    models.Activity.query.get_or_404(activity_id)
    service = ActivitiesService(json_args={})
    return jsonify(service.get(activity_id).__getstate__()), 200


@activities.route('/<int:activity_id>', methods=['PUT'])
@helpers.jwt_auth
@helpers.role_restrict(
    roles=models.Permission.UPDATE_ACTIVITY,
    message=models.Permission.MSG_UPDATE_ACTIVITY,
)
def put_activity(activity_id):
    current_app.logger.info(f"/activities/{activity_id} PUT accessed by {g.request_user.email}")
    activity = models.Activity.query.get_or_404(activity_id)
    service = ActivitiesService(json_args=request.get_json())
    return jsonify(service.put(activity).__getstate__()), 200


@activities.route('/<int:activity_id>', methods=['DELETE'])
@helpers.jwt_auth
@helpers.role_restrict(
    roles=models.Permission.DELETE_ACTIVITY,
    message=models.Permission.MSG_DELETE_ACTIVITY,
)
def delete_activity(activity_id):
    current_app.logger.info(f"/activities/{activity_id} DELETE accessed by {g.request_user.email}")

    activity = models.Activity.query.get_or_404(activity_id)
    service = ActivitiesService(json_args={})

    if service.delete(activity):
        msg = flask_babel.gettext("Activity successfully deleted.")
        return jsonify({"message": msg}), 200
    else:
        msg = flask_babel.gettext(f"There was an issue deleting the activity.")
        return jsonify({"message": msg}), 400


@activities.route('/<int:activity_id>/custom_fields', methods=['GET'])
@helpers.jwt_auth
@helpers.role_restrict(
    roles=models.Permission.READ_ACTIVITY,
    message=models.Permission.MSG_READ_ACTIVITY,
)
def get_activity_custom_fields(activity_id):
    current_app.logger.info(f"/activities/{activity_id}/custom_fields GET accessed by {g.request_user.email}")
    activity = models.Activity.query.get_or_404(activity_id)
    return jsonify(activity.custom_fields), 200


@activities.route('/<int:activity_id>/custom_fields/<string:custom_field_id>', methods=['GET'])
@helpers.jwt_auth
@helpers.role_restrict(
    roles=models.Permission.READ_ACTIVITY,
    message=models.Permission.MSG_READ_ACTIVITY,
)
def get_activity_custom_field(activity_id, custom_field_id):
    current_app.logger.info(
        f"/activities/{activity_id}/custom_fields/{custom_field_id} GET accessed by {g.request_user.email}")
    activity = models.Activity.query.get_or_404(activity_id)
    return jsonify(activity.get_custom_field(custom_field_id)), 200


@activities.route('/<int:activity_id>/custom_fields/<string:custom_field_id>', methods=['PUT'])
@helpers.jwt_auth
@helpers.role_restrict(
    roles=models.Permission.UPDATE_ACTIVITY,
    message=models.Permission.MSG_UPDATE_ACTIVITY,
)
def put_activity_custom_field_value(activity_id, custom_field_id):
    current_app.logger.info(
        f"/activities/{activity_id}/custom_fields/{custom_field_id} PUT accessed by {g.request_user.email}")

    activity = models.Activity.query.get_or_404(activity_id)

    if activity.has_custom_field(custom_field_id):
        service = ActivitiesService(json_args=request.get_json())
        return jsonify(service.update_custom_field_value(activity, custom_field_id)), 200
    else:
        msg = flask_babel.gettext("The activity's custom field was not found")
        return jsonify({'message': msg}), 404


@activities.route('/<int:activity_id>/add_file', methods=['POST'])
@helpers.jwt_auth
@helpers.role_restrict(
    roles=models.Permission.UPDATE_ACTIVITY,
    message=models.Permission.MSG_UPDATE_ACTIVITY,
)
def post_activity_file(activity_id):
    current_app.logger.info(f"/activities/{activity_id}/add_file POST accessed by {g.request_user.email}")

    activity = models.Activity.query.get_or_404(activity_id)
    return files.post(activity.id, "Activity")


@activities.route('/files/<int:file_id>', methods=['GET'])
@helpers.jwt_auth
@helpers.role_restrict(
    roles=models.Permission.READ_ACTIVITY,
    message=models.Permission.MSG_READ_ACTIVITY,
)
def get_activity_file(file_id):
    current_app.logger.info(f"/activities/files/{file_id} GET accessed by {g.request_user.email}")
    return files.get(file_id)


# TODO DELETE /activities/files/<int: case_file_id>
@activities.route('files/<int:file_id>', methods=['DELETE'])
@helpers.jwt_auth
@helpers.role_restrict(
    roles=models.Permission.UPDATE_ACTIVITY,
    message=models.Permission.MSG_UPDATE_ACTIVITY,
)
def delete_activity_file(file_id):
    current_app.logger.info(f"/activities/files/{file_id} DELETE accessed by {g.request_user.email}")
    return files.delete(file_id)


@activities.route('/files/<int:file_id>/download', methods=['GET'])
@helpers.jwt_auth
@helpers.role_restrict(
    roles=models.Permission.READ_ACTIVITY,
    message=models.Permission.MSG_READ_ACTIVITY,
)
def download_activity_file(file_id):
    current_app.logger.info(f"/activities/files/{file_id}/download GET accessed by {g.request_user.email}")
    return files.download(file_id)


@activities.route('/<int:activity_id>/notes', methods=['POST'])
@helpers.jwt_auth
@helpers.role_restrict(
    roles=models.Permission.UPDATE_ACTIVITY,
    message=models.Permission.MSG_UPDATE_ACTIVITY,
)
def post_activity_note(activity_id):
    current_app.logger.info(f"/activities/{activity_id}/notes POST accessed by {g.request_user.email}")

    activity = models.Activity.query.get_or_404(activity_id)
    return notes.post(activity.id, 'Activity')


@activities.route('/<int:activity_id>/notes', methods=['GET'])
@helpers.jwt_auth
@helpers.role_restrict(
    roles=models.Permission.READ_ACTIVITY,
    message=models.Permission.MSG_READ_ACTIVITY,
)
def get_activity_notes(activity_id):
    current_app.logger.info(f"/activities/{activity_id}/notes GET accessed by {g.request_user.email}")
    activity = models.Activity.query.get_or_404(activity_id)
    return jsonify([n.__getstate__() for n in activity.notes]), 200


@activities.route('/<int:activity_id>/notes/<int:note_id>', methods=['GET'])
@helpers.jwt_auth
@helpers.role_restrict(
    roles=models.Permission.READ_ACTIVITY,
    message=models.Permission.MSG_READ_ACTIVITY,
)
def get_activity_note(activity_id, note_id):
    current_app.logger.info(f"/activities/{activity_id}/notes/{note_id} GET accessed by {g.request_user.email}")
    _ = models.Activity.query.get_or_404(activity_id)
    return notes.get(note_id)


@activities.route('/<int:activity_id>/notes/<int:note_id>', methods=['PUT'])
@helpers.jwt_auth
@helpers.role_restrict(
    roles=models.Permission.UPDATE_ACTIVITY,
    message=models.Permission.MSG_UPDATE_ACTIVITY,
)
def put_activity_note(activity_id, note_id):
    current_app.logger.info(f"/activities/{activity_id}/notes/{note_id} PUT accessed by {g.request_user.email}")
    activity = models.Activity.query.get_or_404(activity_id)

    return notes.put(note_id)


@activities.route('/<int:activity_id>/notes/<int:note_id>', methods=['DELETE'])
@helpers.jwt_auth
@helpers.role_restrict(
    roles=models.Permission.UPDATE_ACTIVITY,
    message=models.Permission.MSG_UPDATE_ACTIVITY,
)
def delete_activity_note(activity_id, note_id):
    current_app.logger.info(f"/activities/{activity_id}/notes/{note_id} DELETE accessed by {g.request_user.email}")

    _ = models.Activity.query.get_or_404(activity_id)
    return notes.delete(note_id)


@activities.route('/<int:activity_id>/surveys/<int:survey_id>/responses', methods=['GET'])
@helpers.jwt_auth
@helpers.role_restrict(
    roles=models.Permission.READ_ACTIVITY,
    message=models.Permission.MSG_READ_ACTIVITY,
)
def get_activity_survey_responses(activity_id, survey_id):
    current_app.logger.info(
        f"/activities/{activity_id}/surveys/{survey_id}/responses GET accessed by {g.request_user.email}")

    survey = models.Survey.query.get_or_404(survey_id)
    responses = survey.responses.filter_by(activity_id=activity_id).all()

    return jsonify([r.__getstate__() for r in responses]), 200
