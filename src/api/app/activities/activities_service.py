import itertools
from datetime import datetime

from flask import jsonify, current_app, g
import flask_babel
from app import models, db, helpers, files


class ActivitiesService:

    def __init__(self, json_args, _session=None):
        self.json_args = json_args
        self.session = _session or db.session

    def post(self, activity_definition=None):
        activity_name = self.json_args.get('name', None)

        if not activity_name:
            msg = flask_babel.gettext("A name is required for a activity.")
            return jsonify({"message": msg}), 400

        if len(activity_name) < 8:
            msg = flask_babel.gettext("Activity names must be at least 8 characters long.")
            return jsonify({"message": msg}), 400

        # if len(activity_name) > 50:
        #     msg = flask_babel.gettext("Activity names cannot be longer than 50 characters.")
        #     return jsonify({"message": msg}), 400

        case_id = self.json_args.get('case_id', None)

        name_check = db.session.query(models.Activity).filter(
            models.Activity.case_id == case_id, models.Activity.name == activity_name).all()
        if len(name_check):
            msg = flask_babel.gettext("Activity names must be unique.")
            return jsonify({"message": msg}), 400

        case_description = self.json_args.get('description', None)
        is_complete = self.json_args.get('is_complete', False)
        if is_complete == True:
            completed_by = g.request_user
            completed_at = datetime.utcnow()
        else:
            is_complete = False
            completed_by = None
            completed_at = None

        activity_definition_id = activity_definition.id if activity_definition is not None else None

        activity = models.Activity(
            activity_definition_id=activity_definition_id,
            case_id=case_id,
            name=activity_name,
            description=case_description,
            is_complete=is_complete,
            completed_at=completed_at,
            completed_by=completed_by,
            created_by=g.request_user,
            updated_by=g.request_user,
        )

        created_location_data = helpers.parse_gps(self.json_args)
        if created_location_data.longitude is not None and created_location_data.latitude is not None:
            activity.created_location_coordinates = \
                f"POINT({created_location_data.longitude} {created_location_data.latitude})"
        activity.created_location_position_accuracy = created_location_data.position_accuracy
        activity.created_location_altitude = created_location_data.altitude
        activity.created_location_altitude_accuracy = created_location_data.altitude_accuracy
        activity.created_location_heading = created_location_data.heading
        activity.created_location_speed = created_location_data.speed
        activity.created_location_dt = created_location_data.location_dt

        if 'custom_fields' in self.json_args:
            if isinstance(self.json_args.get('custom_fields'), list):
                for submitted_custom_field in self.json_args.get('custom_fields'):
                    if not submitted_custom_field.get('id'):
                        msg = flask_babel.gettext("IDs cannot not be empty for custom fields")
                        return jsonify({"message": msg}), 400
                    current_app.logger.info(f"processing cf : {submitted_custom_field['id']}")

                    if activity_definition.get_custom_field(
                            submitted_custom_field['activity_definition_custom_field_id']):
                        current_app.logger.info('found activity defns custom field')
                        act_defn_cf = activity_definition.get_custom_field(
                            submitted_custom_field['activity_definition_custom_field_id'])
                        if self._validate_custom_field(submitted_custom_field, act_defn_cf):
                            if models.User.query.get(submitted_custom_field['created_by_id']):
                                created_by = models.User.query.get(submitted_custom_field['created_by_id'])
                            else:
                                created_by = g.request_user
                            if models.User.query.get(submitted_custom_field['updated_by_id']):
                                updated_by = models.User.query.get(submitted_custom_field['updated_by_id'])
                            else:
                                updated_by = g.request_user

                            created_at = submitted_custom_field.get('created_at', datetime.utcnow().isoformat())
                            updated_at = submitted_custom_field.get('updated_at', datetime.utcnow().isoformat())

                            try:
                                activity.add_custom_field(custom_field=act_defn_cf, created_by=created_by,
                                                          custom_field_id=submitted_custom_field['id'],
                                                          updated_by=updated_by, created_at=created_at,
                                                          updated_at=updated_at)
                                activity.update_custom_field_value(custom_field=submitted_custom_field,
                                                                   updated_by=updated_by,
                                                                   updated_at=updated_at)
                            except KeyError:
                                msg = flask_babel.gettext("Submitted custom field IDs must be unique")
                                return jsonify({"message": msg}), 400
                        else:
                            msg = flask_babel.gettext("Invalid custom field")
                            return jsonify({"message": msg}), 400
                    else:
                        msg = flask_babel.gettext("Unknown activity definition custom field ID")
                        return jsonify({"message": msg}), 400

                self._ensure_all_activity_definition_custom_fields_were_submitted(activity, activity_definition)

            else:
                msg = flask_babel.gettext("custom_fields property must be a list")
                return jsonify({"message": msg}), 400
        else:
            if activity_definition and activity_definition.custom_fields:
                for custom_field in activity_definition.custom_fields:
                    activity.add_custom_field(custom_field, g.request_user, g.request_user)

        self.session.add(activity)
        self.session.commit()

        notes = self.json_args.get('notes', [])
        for note in notes:
            if note:
                new_note = models.Note(
                    note=note,
                    model_name='Activity',
                    model_id=activity.id,
                    created_by=g.request_user,
                    updated_by=g.request_user
                )
                self.session.add(new_note)
        self.session.commit()

        # current_app.reporting_service.add_case_row(activity)

        return jsonify(activity.__getstate__()), 200

    def get_all(self):

        return jsonify([a.__getstate__() for a in models.Activity.query.all()]), 200

    def get(self, activity_id):
        return models.Activity.query.get(activity_id)

    def put(self, activity):

        if 'name' in self.json_args.keys():
            an = self.json_args.get('name', None)
            if not an:
                msg = flask_babel.gettext("A name is required for an activity.")
                return jsonify({"message": msg}), 400

            if len(an) == 0:
                msg = flask_babel.gettext("A name is required for an activity.")
                return jsonify({"message": msg}), 400

            if len(an) < 8:
                msg = flask_babel.gettext("Activity names must be at least 8 characters long.")
                return jsonify({"message": msg}), 400

            if len(an) > 50:
                msg = flask_babel.gettext("Activity names cannot be longer than 50 characters.")
                return jsonify({"message": msg}), 400

            name_check = self.session.query(models.Activity).filter(
                models.Activity.name == an, models.Activity.id != activity.id).all()
            if len(name_check):
                msg = flask_babel.gettext("Activity names must be unique.")
                return jsonify({"message": msg}), 400

            activity.name = an

        if 'description' in self.json_args.keys():
            activity.description = self.json_args.get('description', activity.description)

        if 'is_complete' in self.json_args.keys():
            is_complete = self.json_args.get('is_complete', None)

            if is_complete != activity.is_complete:
                # don't want trueish here which can happen with JSON
                if is_complete == True:
                    activity.is_complete = True
                    activity.completed_by = g.request_user
                    activity.completed_at = datetime.utcnow()
                elif is_complete == False:
                    activity.is_complete = False
                    activity.completed_by = None
                    activity.completed_at = None

        location_data = helpers.parse_gps(self.json_args)
        if location_data.location_dt is not None:
            if location_data.longitude is not None and location_data.latitude is not None:
                activity.updated_location_coordinates = \
                    f"POINT({location_data.longitude} {location_data.latitude})"
            activity.updated_location_position_accuracy = location_data.position_accuracy
            activity.updated_location_altitude = location_data.altitude
            activity.updated_location_altitude_accuracy = location_data.altitude_accuracy
            activity.updated_location_heading = location_data.heading
            activity.updated_location_speed = location_data.speed
            activity.updated_location_dt = location_data.location_dt

        if self.session.is_modified(activity):
            activity.updated_by = g.request_user
            self.session.commit()

        # current_app.reporting_service.update_case_row(case)

        return activity

    def delete(self, activity):

        for n in activity.notes:
            self.session.delete(n)

        for f in activity.files:
            self.session.delete(f)
        for r in activity.responses:
            self.session.delete(r)

        self.session.delete(activity)
        self.session.commit()

        return True

    def update_custom_field_value(self, activity, custom_field_id):

        if "value" in self.json_args:
            custom_field_value = self.json_args.get('value', None)
            activity.update_custom_field_value({'id': custom_field_id, 'value': custom_field_value}, g.request_user)
            # current_app.reporting_service.update_case_row(case)
            self.session.commit()

        return activity.get_custom_field(custom_field_id)

    def _ensure_all_activity_definition_custom_fields_were_submitted(self, activity, activity_definition):

        activity_defn_custom_field_ids = [cf['id'] for cf in activity_definition.custom_fields]
        submitted_activity_defn_custom_field_ids = [cf['activity_definition_custom_field_id'] for cf in
                                                    self.json_args.get('custom_fields')]

        # for all activity definition custom fields not submitted
        for unsubmitted_custom_field_id in list(
                itertools.filterfalse(lambda x: x in submitted_activity_defn_custom_field_ids,
                                      activity_defn_custom_field_ids)):
            cf = activity_definition.get_custom_field(unsubmitted_custom_field_id)
            activity.add_custom_field(cf, g.request_user, g.request_user)

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

    def _validate_custom_field(self, custom_field, activity_definition_custom_field):

        if custom_field['field_type'] != activity_definition_custom_field['field_type']:
            return False
        elif custom_field['help_text'] != activity_definition_custom_field['help_text']:
            return False
        elif custom_field['model_type'] != type(models.Activity).__name__:
            return False
        elif custom_field['name'] != activity_definition_custom_field['name']:
            return False
        elif not self._do_selections_match(custom_field['field_type'], activity_definition_custom_field['selections'],
                                           custom_field['selections']):
            return False
        return True
