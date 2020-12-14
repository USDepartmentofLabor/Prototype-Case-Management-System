import random
import flask
import http
import flask_babel
from . import case_statuses
import app
from app import models, helpers


@case_statuses.route('', methods=['GET'])
@helpers.jwt_auth
def get_case_statuses():
    flask.current_app.logger.info(f"/case_statuses GET accessed by {flask.g.request_user.email}")
    case_status_list = [cs.__getstate__() for cs in models.CaseStatus.query.all()]
    return flask.jsonify(case_status_list), http.HTTPStatus.OK


@case_statuses.route('/<int:case_status_id>', methods=['GET'])
@helpers.jwt_auth
def get_case_status(case_status_id):
    flask.current_app.logger.info(f"/case_statuses/{case_status_id} GET accessed by {flask.g.request_user.email}")
    case_status = models.CaseStatus.query.get_or_404(case_status_id)
    return flask.jsonify(case_status.__getstate__()), http.HTTPStatus.OK


def validate_name(name):
    """Validates the `name` field for CaseStatus

    Args:
        name: Name being validated

    Returns:
        is_name_valid (bool), flask.Response or None

        If the `name` provided fails validation, is_name_valid will be `False` and a flask response
        detailing the failed validation will be provided.
    """
    # Validate name
    if name is None or name == '':
        msg = flask_babel.gettext("A name is required for a case status.")
        return False, flask.jsonify({"message": msg})

    if len(name) == 0:
        msg = flask_babel.gettext("A name is required for a case status.")
        return False, flask.jsonify({"message": msg})

    if len(name) > 50:
        msg = flask_babel.gettext("Case status names cannot be longer than 50 characters.")
        return False, flask.jsonify({"message": msg})

    name_check = app.db.session.query(models.CaseStatus).filter(models.CaseStatus.name == name).all()
    if len(name_check) > 0:
        msg = flask_babel.gettext("Case status names must be unique.")
        return False, flask.jsonify({"message": msg})

    return True, None


@case_statuses.route('', methods=['POST'])
@helpers.jwt_auth
@helpers.role_restrict(
    roles=models.Permission.CONFIGURE_SYSTEM,
    message=models.Permission.MSG_CONFIGURE_SYSTEM,
)
def post_case_status():
    """POST /case_statuses

    This endpoint will insert a new CaseStatus into the database.
    Arguments are received in a JSON body and the schema is:

    {
      'name': <string>,  # Required
      'default: <boolean>,  # Default False
      'is_final: <boolean>,  # Default False
      'color': <string>,  # Optional
    }

    If `default` is provided and is `True`, any existing CaseStatus with `default=True` will be set to `False`.
    If `color` is not provided, a random color will be generated from a preset list.

    Returns:
        Flask.Response, 200 OK or 400 BAD REQUEST
    """
    flask.current_app.logger.info(f"/case_statuses POST accessed by {flask.g.request_user.email}")

    def random_color():
        return random.choice(models.CaseStatus.supported_colors())

    name = flask.request.json.get('name', None)
    default = flask.request.json.get('default', False)
    is_final = flask.request.json.get('is_final', False)
    color = flask.request.json.get('color', random_color())

    # Validate name
    name_valid, err = validate_name(name)

    if not name_valid:
        return err, http.HTTPStatus.BAD_REQUEST

    # Validate default
    if default:
        models.CaseStatus.query.update({models.CaseStatus.default: False})

    case_status = models.CaseStatus(
        name=name,
        default=default,
        is_final=is_final,
        color=color
    )

    app.db.session.add(case_status)
    app.db.session.commit()

    return flask.jsonify(case_status.__getstate__()), http.HTTPStatus.OK


@case_statuses.route('/<int:case_status_id>', methods=['PUT'])
@helpers.jwt_auth
@helpers.role_restrict(
    roles=models.Permission.CONFIGURE_SYSTEM,
    message=models.Permission.MSG_CONFIGURE_SYSTEM,
)
def put_case_status(case_status_id):
    """PUT /case_statuses/<case_status_id>

        This endpoint will update an existing CaseStatus.
        Arguments are received in a JSON body and the schema is:

        {
          'name': <string>,
          'default: <boolean>,
          'is_final: <boolean>,
          'color': <string>,
        }

        All arguments are optional.
        If `default` is provided and is `True`, any existing CaseStatus with `default=True` will be set to `False`.

        Returns:
            Flask.Response, 200 OK or 400 BAD REQUEST
        """
    flask.current_app.logger.info(f"/case_statuses/{case_status_id} PUT accessed by {flask.g.request_user.email}")

    case_status = models.CaseStatus.query.get_or_404(case_status_id)

    name = flask.request.json.get('name', None)
    default = flask.request.json.get('default', None)
    is_final = flask.request.json.get('is_final', None)
    color = flask.request.json.get('color', None)

    if name is not None:
        # Validate name
        name_valid, err = validate_name(name)

        if not name_valid:
            return err, http.HTTPStatus.BAD_REQUEST

        case_status.name = name

    if default is not None:
        if default:
            models.CaseStatus.query.update({models.CaseStatus.default: False})

        case_status.default = default

    if is_final is not None:
        case_status.is_final = is_final

    if color is not None:
        case_status.color = color

    app.db.session.commit()
    return flask.jsonify(case_status.__getstate__()), http.HTTPStatus.OK


@case_statuses.route('/<int:case_status_id>', methods=['DELETE'])
@helpers.jwt_auth
@helpers.role_restrict(
    roles=models.Permission.CONFIGURE_SYSTEM,
    message=models.Permission.MSG_CONFIGURE_SYSTEM,
)
def delete_case_status(case_status_id):
    flask.current_app.logger.info(f"/case_statuses/{case_status_id} DELETE accessed by {flask.g.request_user.email}")

    case_status = models.CaseStatus.query.get_or_404(case_status_id)

    app.db.session.delete(case_status)
    app.db.session.commit()

    msg = flask_babel.gettext("CaseStatus successfully deleted.")
    return flask.jsonify({"message": msg}), 200
