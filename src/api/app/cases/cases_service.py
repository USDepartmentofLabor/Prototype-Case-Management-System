from datetime import datetime
import itertools

import uuid
from flask import jsonify, g, current_app
import flask_babel
from app import db, helpers
from .. import models
from ..services import notification_service


class CasesService:

    def __init__(self, json_args, _session=None):
        self.json_args = json_args
        self.session = _session or db.session

    def post(self, case_definition):
        case_name = self.json_args.get('name', None)

        if not case_name:
            msg = flask_babel.gettext("A name is required for a case.")
            return jsonify({"message": msg}), 400

        if len(case_name) < 8:
            msg = flask_babel.gettext("Case names must be at least 8 characters long.")
            return jsonify({"message": msg}), 400

        if len(case_name) > 50:
            msg = flask_babel.gettext("Case names cannot be longer than 50 characters.")
            return jsonify({"message": msg}), 400

        name_check = db.session.query(models.Case).filter(
            models.Case.name == case_name).all()
        if len(name_check):
            msg = flask_babel.gettext("Case names must be unique.")
            return jsonify({"message": msg}), 400

        case_description = self.json_args.get('description', None)
        assigned_to_id = self.json_args.get('assigned_to_id', None)
        send_assigned_to_notification = False
        if assigned_to_id is not None:
            try:
                assigned_user = models.User.query.get(assigned_to_id)
                if assigned_user is None:
                    msg = flask_babel.gettext("Cannot assigned case to unknown user id.")
                    return jsonify({"message": msg}), 400

                if not (assigned_user.can(models.Permission.ASSIGNABLE_TO_CASE) or assigned_user.is_admin()):
                    msg = flask_babel.gettext("User does not have permission to be assigned to a case.")
                    return jsonify({"message": msg}), 400
            except:
                msg = flask_babel.gettext("Cannot assigned case to invalid user.")
                return jsonify({"message": msg}), 400

            assigned_at = datetime.utcnow()
            send_assigned_to_notification = True
        else:
            assigned_at = None

        case = models.Case(
            case_definition_id=case_definition.id,
            name=case_name,
            description=case_description,
            assigned_to_id=assigned_to_id,
            assigned_at=assigned_at,
            created_by=g.request_user,
            updated_by=g.request_user
        )

        created_location_data = helpers.parse_gps(self.json_args)
        if created_location_data.longitude is not None and created_location_data.latitude is not None:
            case.created_location_coordinates = \
                f"POINT({created_location_data.longitude} {created_location_data.latitude})"
        case.created_location_position_accuracy = created_location_data.position_accuracy
        case.created_location_altitude = created_location_data.altitude
        case.created_location_altitude_accuracy = created_location_data.altitude_accuracy
        case.created_location_heading = created_location_data.heading
        case.created_location_speed = created_location_data.speed
        case.created_location_dt = created_location_data.location_dt

        if 'custom_fields' in self.json_args:
            if isinstance(self.json_args.get('custom_fields'), list):
                for submitted_custom_field in self.json_args.get('custom_fields'):
                    if not submitted_custom_field.get('id'):
                        submitted_custom_field['id'] = str(uuid.uuid4())
                    current_app.logger.info(f"processing cf : {submitted_custom_field['id']}")

                    if models.CustomField.query.get(submitted_custom_field['case_definition_custom_field_id']):
                        current_app.logger.info('found case defns custom field')
                        cd_cf = models.CustomField.query.get(
                            submitted_custom_field['case_definition_custom_field_id'])
                        if self._validate_custom_field(submitted_custom_field, cd_cf):
                            if 'created_by_id' in submitted_custom_field and models.User.query.get(
                                    submitted_custom_field['created_by_id']):
                                created_by = models.User.query.get(submitted_custom_field['created_by_id'])
                            else:
                                created_by = g.request_user
                            if 'updated_by_id' in submitted_custom_field and models.User.query.get(
                                    submitted_custom_field['updated_by_id']):
                                updated_by = models.User.query.get(submitted_custom_field['updated_by_id'])
                            else:
                                updated_by = g.request_user

                            created_at = submitted_custom_field.get('created_at', datetime.utcnow().isoformat())
                            updated_at = submitted_custom_field.get('updated_at', datetime.utcnow().isoformat())

                            try:
                                case.add_custom_field(custom_field=cd_cf, created_by=created_by,
                                                      custom_field_id=submitted_custom_field.get('id', None),
                                                      updated_by=updated_by, created_at=created_at,
                                                      updated_at=updated_at)
                                if 'value' in submitted_custom_field:
                                    case.update_custom_field_value(custom_field=submitted_custom_field,
                                                                   updated_by=updated_by,
                                                                   updated_at=updated_at)
                            except KeyError:
                                msg = flask_babel.gettext("Submitted custom field IDs must be unique")
                                return jsonify({"message": msg}), 400
                        else:
                            msg = flask_babel.gettext(f"{submitted_custom_field['name']} is invalid.")
                            return jsonify({"message": msg}), 400
                    else:
                        msg = flask_babel.gettext("Unknown case definition custom field ID")
                        return jsonify({"message": msg}), 400

                self._ensure_all_case_definition_custom_fields_were_submitted(case, case_definition)

            else:
                msg = flask_babel.gettext("custom_fields property must be a list")
                return jsonify({"message": msg}), 400
        else:
            for custom_field in case_definition.custom_fields:
                cf = models.CustomField.query.get(custom_field['id'])
                case.add_custom_field(cf, g.request_user, g.request_user)

        self.session.add(case)
        self.session.commit()

        notes = self.json_args.get('notes', [])
        for note in notes:
            if note:
                new_note = models.Note(
                    note=note,
                    model_name='Case',
                    model_id=case.id,
                    created_by=g.request_user,
                    updated_by=g.request_user
                )
                self.session.add(new_note)
        self.session.commit()

        current_app.reporting_service.add_case_row(case)
        if send_assigned_to_notification:
            notification_service.notify_user_they_were_assigned_a_case(case)

        return jsonify(case.__getstate__()), 200

    def update_custom_field(self, case, custom_field_id):

        if "value" in self.json_args:
            custom_field_value = self.json_args.get('value', None)
            case.update_custom_field_value({'id': custom_field_id, 'value': custom_field_value}, g.request_user)
            self._update_case_location(case)
            current_app.reporting_service.update_case_row(case)

        return jsonify(case.get_custom_field(custom_field_id)), 200

    def get_custom_field(self, case, custom_field_id):

        return jsonify(case.get_custom_field(custom_field_id)), 200

    def _do_selections_match(self, field_type, parent_selections, child_selections):

        if field_type in ['text', 'textarea', 'number', 'date']:
            return True
        elif field_type in ['check_box', 'select', 'radio_button', 'rank_list']:
            diff = list(itertools.filterfalse(lambda x: x in parent_selections, child_selections)) + list(
                itertools.filterfalse(lambda x: x in child_selections, parent_selections))

            if diff:
                return False
            else:
                return True

        raise ValueError(f"Unknown custom field field type: {field_type}")

    def _validate_custom_field(self, custom_field, case_definition_custom_field: models.CustomField):

        if custom_field['field_type'] != case_definition_custom_field.field_type:
            return False
        elif custom_field['help_text'] != case_definition_custom_field.help_text:
            return False
        elif custom_field['model_type'] != 'Case':
            return False
        elif custom_field['name'] != case_definition_custom_field.name:
            return False
        elif not self._do_selections_match(custom_field['field_type'], case_definition_custom_field.selections,
                                           custom_field['selections']):
            return False
        return True

    def _ensure_all_case_definition_custom_fields_were_submitted(self, case, case_definition):

        case_defn_custom_field_ids = [cf['id'] for cf in case_definition.custom_fields]
        submitted_case_defn_custom_field_ids = [cf['case_definition_custom_field_id'] for cf in
                                                self.json_args.get('custom_fields')]

        # for all case definition custom fields not submitted
        for unsubmitted_case_defn_custom_field_id in list(
                itertools.filterfalse(lambda x: x in submitted_case_defn_custom_field_ids,
                                      case_defn_custom_field_ids)):
            cf = models.CustomField.query.get(unsubmitted_case_defn_custom_field_id)
            case.add_custom_field(cf, g.request_user, g.request_user)

    def _custom_field_id_not_unique(self, custom_field_id):

        return False

    def _update_case_location(self, case):

        latitude = self.json_args.get('latitude', None)
        longitude = self.json_args.get('longitude', None)
        position_accuracy = self.json_args.get('position_accuracy', None)
        altitude = self.json_args.get('altitude', None)
        altitude_accuracy = self.json_args.get('altitude_accuracy', None)
        heading = self.json_args.get('heading', None)
        speed = self.json_args.get('speed', None)

        got_location_data = False
        if (latitude is not None and helpers.is_number(latitude)) and (
                longitude is not None and helpers.is_number(longitude)):
            case.updated_location_coordinates = f"POINT({longitude} {latitude})"
            got_location_data = True
        if position_accuracy is not None and helpers.is_number(position_accuracy):
            case.updated_location_position_accuracy = position_accuracy
            got_location_data = True
        if altitude is not None and helpers.is_number(altitude):
            case.updated_location_altitude = altitude
            got_location_data = True
        if altitude_accuracy is not None and helpers.is_number(altitude_accuracy):
            case.updated_location_altitude_accuracy = altitude_accuracy
            got_location_data = True
        if heading is not None and helpers.is_number(heading):
            case.updated_location_heading = heading
            got_location_data = True
        if speed is not None and helpers.is_number(speed):
            case.updated_location_speed = speed
            got_location_data = True

        if got_location_data:
            case.updated_location_dt = datetime.utcnow()
            self.session.commit()
