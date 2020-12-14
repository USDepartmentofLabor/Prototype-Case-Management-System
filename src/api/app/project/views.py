from flask import jsonify, request, current_app, g
import flask_babel
from . import project
from app import models, db
from app import helpers


def validate_project_submission(request):
    """
    Validates a project submission object
    :param request:
    :return: a two member tuple. The first member is whether the project object is valid. If not the the second
        member is the error message. If it is valid, the second member is a dictionary of the valid values.
    """

    project_name = request.json.get('name', None)

    if not project_name or len(project_name) == 0:
        return False, flask_babel.gettext("A name is required for a project.")

    if len(project_name) > 64:
        return False, flask_babel.gettext("Project names cannot be longer than 64 characters.")

    project_title = request.json.get('title', None)
    project_organization = request.json.get('organization', None)

    if project_organization and len(project_organization) > 64:
        return False, flask_babel.gettext("Project organizations cannot be longer than 64 characters.")

    project_agreement_number = request.json.get('agreement_number', None)

    if project_agreement_number and len(project_agreement_number) > 30:
        return False, flask_babel.gettext("Project agreement numbers cannot be longer than 30 characters.")

    project_start_date = request.json.get('start_date', None)
    project_end_date = request.json.get('end_date', None)
    project_funding_amount = request.json.get('funding_amount', None)
    project_location = request.json.get('location', None)

    return (True, {
        'name': project_name,
        'title': project_title,
        'organization': project_organization,
        'agreement_number': project_agreement_number,
        'start_date': project_start_date,
        'end_date': project_end_date,
        'funding_amount': project_funding_amount,
        'location': project_location
    })


# /project POST
@project.route('', methods=['POST'])
@helpers.jwt_auth
@helpers.role_restrict(
    roles=models.Permission.CREATE_PROJECT,
    message=models.Permission.MSG_CREATE_PROJECT,
)
def post_project():
    current_app.logger.info(f"/project POST accessed by {g.request_user.email}")

    if not request.is_json:
        msg = flask_babel.gettext("Missing JSON in request")
        return jsonify({"message": msg}), 400

    if db.session.query(models.Project).count() > 0:
        msg = flask_babel.gettext('The system already has a project setup.')
        return jsonify({'message': msg}), 400

    (is_valid, data) = validate_project_submission(request)

    if not is_valid:
        return jsonify({"message": data}), 400

    new_project = models.Project(name=data['name'], title=data['title'], organization=data['organization'],
                                 agreement_number=data['agreement_number'], start_date=data['start_date'],
                                 end_date=data['end_date'], funding_amount=data['funding_amount'],
                                 location=data['location'], created_by=g.request_user, updated_by=g.request_user)

    db.session.add(new_project)
    db.session.commit()

    return jsonify(new_project.__getstate__()), 200


# /project GET
@project.route('', methods=['GET'])
@helpers.jwt_auth
@helpers.role_restrict(
    roles=models.Permission.READ_PROJECT,
    message=models.Permission.MSG_READ_PROJECT,
)
def get_project():
    current_app.logger.info(f"/project GET accessed by {g.request_user.email}")

    if db.session.query(models.Project).count() == 0:
        msg = flask_babel.gettext('A project has not been setup.')
        return jsonify({'message': msg}), 400

    p = models.Project.query.order_by(models.Project.id).first()

    return jsonify(p.__getstate__()), 200


# /project PUT
@project.route('', methods=['PUT'])
@helpers.jwt_auth
@helpers.role_restrict(
    roles=models.Permission.UPDATE_PROJECT,
    message=models.Permission.MSG_UPDATE_PROJECT,
)
def put_project():
    current_app.logger.info(f"/project PUT accessed by {g.request_user.email}")

    if not request.is_json:
        msg = flask_babel.gettext("Missing JSON in request")
        return jsonify({"message": msg}), 400

    if db.session.query(models.Project).count() == 0:
        msg = flask_babel.gettext('A project has not been setup.')
        return jsonify({'message': msg}), 400

    p = models.Project.query.order_by(models.Project.id).first()

    if 'name' in request.json.keys():
        pn = request.json.get('name', None)
        if not pn or len(pn) == 0:
            msg = flask_babel.gettext("A name is required for a project.")
            return jsonify({"message": msg}), 400

        if len(pn) > 64:
            msg = flask_babel.gettext("Project names cannot be longer than 64 characters.")
            return jsonify({"message": msg}), 400

        p.name = pn

    if 'title' in request.json.keys():
        p.title = request.json.get('title', p.title)

    if 'organization' in request.json.keys():
        org = request.json.get('organization', None)

        if org and len(org) > 64:
            msg = flask_babel.gettext("Project organizations cannot be longer than 64 characters.")
            return jsonify({"message": msg}), 400

        p.organization = org

    if 'agreement_number' in request.json.keys():
        agreement_number = request.json.get('agreement_number', None)

        if agreement_number and len(agreement_number) > 30:
            msg = flask_babel.gettext("Project agreement numbers cannot be longer than 30 characters.")
            return jsonify({"message": msg}), 400

        p.agreement_number = agreement_number

    if 'start_date' in request.json.keys():
        p.start_date = request.json.get('start_date', p.start_date)

    if 'end_date' in request.json.keys():
        p.end_date = request.json.get('end_date', p.end_date)

    if 'funding_amount' in request.json.keys():
        p.funding_amount = request.json.get('funding_amount', p.funding_amount)

    if 'location' in request.json.keys():
        p.location = request.json.get('location', p.location)

    if db.session.is_modified(p):
        p.updated_by = g.request_user
        db.session.commit()

    return jsonify(p.__getstate__()), 200


# /project DELETE
@project.route('', methods=['DELETE'])
@helpers.jwt_auth
@helpers.role_restrict(
    roles=models.Permission.DELETE_PROJECT,
    message=models.Permission.MSG_DELETE_PROJECT,
)
def delete_project():
    current_app.logger.info(f"/project DELETE accessed by {g.request_user.email}")

    if db.session.query(models.Project).count() == 0:
        msg = flask_babel.gettext('A project has not been setup.')
        return jsonify({'message': msg}), 400

    # even though there should only every be one project, there is nothing on the database preventing it. so
    # we'll just loop through and delete all the project records.
    for p in models.Project.query.all():
        db.session.delete(p)
    db.session.commit()

    msg = flask_babel.gettext("Project successfully deleted.")
    return jsonify({"message": msg}), 200
