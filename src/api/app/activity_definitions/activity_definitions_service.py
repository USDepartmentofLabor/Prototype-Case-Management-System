from datetime import datetime

from flask import jsonify, g, current_app
import flask_babel
from app import db
from app import models, helpers


class ActivityDefinitionsService:

    def __init__(self, json_args={}, _session=None):
        self.json_args = json_args
        self.session = _session or db.session

    def _is_name_unique(self, name, case_definition_id):
        return len(self.session.query(models.ActivityDefinition).filter(
            models.ActivityDefinition.case_definition_id == case_definition_id,
            models.ActivityDefinition.name == name).all()) == 0

    def post(self):
        name = self.json_args.get('name', None)

        case_definition_id = self.json_args.get('case_definition_id', None)

        if not case_definition_id:
            msg = flask_babel.gettext("A case definition id is required.")
            return jsonify({"message": msg}), 400

        models.CaseDefinition.query.get_or_404(case_definition_id)

        if not name:
            msg = flask_babel.gettext("A name is required for an activity definition.")
            return jsonify({"message": msg}), 400

        if not self._is_name_unique(name, case_definition_id):
            msg = flask_babel.gettext("Activity Definition names must be unique.")
            return jsonify({"message": msg}), 400

        description = self.json_args.get('description', None)
        surveys = self.json_args.get('surveys', [])
        documents = self.json_args.get('documents', [])

        activity_definition = models.ActivityDefinition(name=name, description=description,
                                                        case_definition_id=case_definition_id,
                                                        created_by=g.request_user,
                                                        updated_by=g.request_user)

        surveys_to_add = []
        for survey_id in surveys:
            survey = models.Survey.query.get(survey_id)
            if not survey:
                msg = flask_babel.gettext("Invalid survey ID submitted.")
                return jsonify({"message": msg}), 400
            surveys_to_add.append(survey)

        documents_to_add = []
        for document in documents:
            doc_name = document.get('name', None)
            if not doc_name:
                msg = flask_babel.gettext("A name is required for each case definition document.")
                return jsonify({"message": msg}), 400
            doc_description = document.get('description', None)
            is_required = document.get('is_required', False)
            activity_definition_document = models.ActivityDefinitionDocument(
                name=doc_name,
                description=doc_description,
                is_required=is_required
            )
            documents_to_add.append(activity_definition_document)

        for survey in surveys_to_add:
            activity_definition.surveys.append(survey)

        for document in documents_to_add:
            activity_definition.documents.append(document)

        if 'custom_fields' in self.json_args:
            if isinstance(self.json_args.get('custom_fields'), list):
                for custom_field in self.json_args.get('custom_fields'):

                    if 'name' not in custom_field:
                        msg = flask_babel.gettext("A name is required for each custom field.")
                        return jsonify({"message": msg}), 400

                    if 'field_type' not in custom_field:
                        msg = flask_babel.gettext("A field type is required for each custom field.")
                        return jsonify({"message": msg}), 400

                    if custom_field['field_type'] not in ['textarea', 'date', 'check_box', 'text', 'select',
                                                          'rank_list', 'number', 'radio_button']:
                        msg = flask_babel.gettext("The custom field refers to an invalid field type.")
                        return jsonify({"message": msg}), 400

                    selections = custom_field.get('selections', None)
                    if isinstance(selections, list):
                        for s in selections:
                            if 'id' not in s:
                                msg = flask_babel.gettext("An id property is required for custom field selections.")
                                return jsonify({"message": msg}), 400

                    if models.User.query.get(custom_field.get('created_by_id', 0)):
                        created_by = models.User.query.get(custom_field.get('created_by_id', 0))
                    else:
                        created_by = g.request_user
                    if models.User.query.get(custom_field.get('updated_by_id', 0)):
                        updated_by = models.User.query.get(custom_field.get('updated_by_id', 0))
                    else:
                        updated_by = g.request_user

                    created_at = custom_field.get('created_at', datetime.utcnow().isoformat())
                    updated_at = custom_field.get('updated_at', datetime.utcnow().isoformat())
                    try:
                        activity_definition.add_custom_field(custom_field=custom_field, created_by=created_by,
                                                             updated_by=updated_by, created_at=created_at,
                                                             updated_at=updated_at)
                    except KeyError:
                        msg = flask_babel.gettext("Custom field IDs must be unique.")
                        return jsonify({"message": msg}), 400

            else:
                msg = flask_babel.gettext("The custom_fields property must be a list.")
                return jsonify({"message": msg}), 400

        self.session.add(activity_definition)
        self.session.commit()

        return activity_definition

    def get_all(self):
        return jsonify([ad.__getstate__() for ad in models.ActivityDefinition.query.all()]), 200

    def put(self, activity_definition_id):
        activity_definition = models.ActivityDefinition.query.get_or_404(activity_definition_id)

        name = self.json_args.get('name')
        description = self.json_args.get('description')

        surveys = self.json_args.get('surveys', [])
        documents = self.json_args.get('documents', [])

        if name:
            activity_definition.name = name

        if description:
            activity_definition.description = description

        surveys_to_add = []
        for survey in surveys:
            survey = models.Survey.query.get(survey['id'])
            if not survey:
                msg = flask_babel.gettext("Invalid survey ID submitted.")
                return jsonify({"message": msg}), 400
            surveys_to_add.append(survey)

        documents_to_add = []
        for document in documents:
            doc_name = document.get('name', None)

            if not doc_name:
                msg = flask_babel.gettext("A name is required for each activity definition document.")
                return jsonify({"message": msg}), 400

            doc_description = document.get('description', None)
            is_required = document.get('is_required', False)

            # Preserve existing documents
            if 'id' in document:
                matching_docs = [doc for doc in activity_definition.documents if doc.id == document['id']]
                for doc in matching_docs:
                    doc.name = doc_name
                    doc.description = doc_description
                    doc.is_required = is_required
                    documents_to_add.append(doc)
            else:
                activity_definition_document = models.ActivityDefinitionDocument(
                    name=doc_name,
                    description=doc_description,
                    is_required=is_required
                )
                documents_to_add.append(activity_definition_document)

        activity_definition.surveys = surveys_to_add
        activity_definition.documents = documents_to_add

        self.session.commit()
        return jsonify(activity_definition.__getstate__()), 200

    def get(self, activity_definition_id):
        activity_definition = models.ActivityDefinition.query.get_or_404(activity_definition_id)
        return jsonify(activity_definition.__getstate__()), 200

    def delete(self, activity_definition_id):
        activity_definition = models.ActivityDefinition.query.get_or_404(activity_definition_id)

        # try:
        #     current_app.reporting_service.delete_case_table(case_defn.reporting_table_name)
        #     helpers.metabase_rescan()
        # except EPSReportingServiceException as ex:
        #     current_app.logger.error(f"error deleting reporting table: {ex}")

        for survey in activity_definition.surveys:
            for survey_resp in survey.responses:
                db.session.delete(survey_resp)

        for doc in activity_definition.documents:
            db.session.delete(doc)

        for activity in activity_definition.activities:
            for note in activity.notes:
                db.session.delete(note)

            db.session.delete(activity)

        self.session.delete(activity_definition)
        self.session.commit()
        msg = flask_babel.gettext("Activity definition successfully deleted.")
        return jsonify({"message": msg}), 200

    def get_all_custom_fields(self, activity_definition_id):
        activity_definition = models.ActivityDefinition.query.get_or_404(activity_definition_id)
        return jsonify(activity_definition.custom_fields), 200

    def get_custom_field(self, activity_definition_id, custom_field_id):

        activity_definition = models.ActivityDefinition.query.get_or_404(activity_definition_id,
                                                                         "Activity Definition not found")
        return jsonify(activity_definition.get_custom_field(custom_field_id)), 200

    def delete_custom_field(self, activity_definition_id, custom_field_id):

        activity_definition = models.ActivityDefinition.query.get_or_404(activity_definition_id,
                                                                         "Activity definition not found")

        activity_definition.delete_custom_field(custom_field_id)
        self.session.commit()

        msg = flask_babel.gettext("Activity definition successfully deleted.")
        return jsonify({"message": msg}), 200

    def put_custom_field(self, activity_definition_id, custom_field_id):

        activity_definition = models.ActivityDefinition.query.get_or_404(activity_definition_id,
                                                                         "Activity definition not found")
        activity_definition.update_custom_field(self.json_args, g.request_user)

        self.session.commit()

        for activity in activity_definition.activities:
            for cf in activity.custom_fields:
                if cf['activity_definition_custom_field_id'] == custom_field_id:
                    activity.update_custom_field(cf['id'], self.json_args, g.request_user)
                    self.session.commit()

        return jsonify(activity_definition.get_custom_field(custom_field_id)), 200

    def post_custom_field(self, activity_definition_id):

        activity_definition = models.ActivityDefinition.query.get_or_404(activity_definition_id,
                                                                         "Activity definition not found")
        custom_field_id = activity_definition.add_custom_field(self.json_args, g.request_user, g.request_user)
        self.session.commit()

        return jsonify(activity_definition.get_custom_field(custom_field_id)), 200
