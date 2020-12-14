from flask import jsonify, g, current_app
import flask_babel
from app import db
from app import models, helpers
from app.activity_definitions.activity_definitions_service import ActivityDefinitionsService


class CaseDefinitionsService:

    def __init__(self, json_args, _session=None):
        self.json_args = json_args
        self.session = _session or db.session

    def _is_key_unique(self, key):
        return len(self.session.query(models.CaseDefinition).filter(
            models.CaseDefinition.key == key).all()) == 0

    def _is_name_unique(self, name):
        return len(self.session.query(models.CaseDefinition).filter(
            models.CaseDefinition.name == name).all()) == 0

    def _parse_custom_field_from_json(self, custom_field_json):
        validation_rules = []
        if isinstance(custom_field_json.get('validation_rules', None), list):
            for rule in custom_field_json.get('validation_rules'):
                validation_rules.append(rule)
        return {
            'name': custom_field_json.get('name', None),
            'field_type': custom_field_json.get('field_type', None),
            'sort_order': custom_field_json.get('sort_order', None),
            'selections': custom_field_json.get('selections', None),
            'validation_rules': validation_rules,
            'custom_section_id': custom_field_json.get('custom_section_id', None),
            'help_text': custom_field_json.get('help_text', None)
        }

    def _get_validated_custom_field(self, case_definition_id):
        unvalidated_custom_field = self._parse_custom_field_from_json(self.json_args)

        if unvalidated_custom_field['name'] is None:
            return flask_babel.gettext("A name is required for each custom field."), False

        if unvalidated_custom_field['field_type'] is None:
            return flask_babel.gettext("A field type is required for each custom field."), False

        if isinstance(unvalidated_custom_field['selections'], list):
            for s in unvalidated_custom_field['selections']:
                if 'id' not in s:
                    return flask_babel.gettext("An id property is required for custom field selections."), False

        return (models.CustomField(name=unvalidated_custom_field['name'],
                                   field_type=unvalidated_custom_field['field_type'],
                                   selections=unvalidated_custom_field['selections'],
                                   validation_rules=unvalidated_custom_field['validation_rules'],
                                   model_type='CaseDefinition', model_id=case_definition_id,
                                   sort_order=unvalidated_custom_field['sort_order'],
                                   custom_section_id=unvalidated_custom_field['custom_section_id'],
                                   help_text=unvalidated_custom_field['help_text'],
                                   created_by=g.request_user, updated_by=g.request_user),
                True)

    def post(self):
        case_definition_key = self.json_args.get('key', None)

        if not case_definition_key:
            msg = flask_babel.gettext("A key is required for a case definition.")
            return jsonify({"message": msg}), 400

        if not self._is_key_unique(case_definition_key):
            msg = flask_babel.gettext("Case Definition keys must be unique.")
            return jsonify({"message": msg}), 400

        case_definition_name = self.json_args.get('name', None)

        if not case_definition_name:
            msg = flask_babel.gettext("A name is required for a case definition.")
            return jsonify({"message": msg}), 400

        if not self._is_name_unique(case_definition_name):
            msg = flask_babel.gettext("Case Definition names must be unique.")
            return jsonify({"message": msg}), 400

        case_definition_description = self.json_args.get('description', None)
        surveys = self.json_args.get('surveys', [])
        documents = self.json_args.get('documents', [])

        case_definition = models.CaseDefinition(
            key=case_definition_key,
            name=case_definition_name,
            description=case_definition_description,
            created_by=g.request_user,
            updated_by=g.request_user
        )
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
            case_definition_document = models.CaseDefinitionDocument(
                name=doc_name,
                description=doc_description,
                is_required=is_required
            )
            documents_to_add.append(case_definition_document)

        custom_fields = self.json_args.get('custom_fields', [])
        custom_fields_to_add = []
        for cf in custom_fields:
            cf_name = cf.get('name', None)
            if cf_name is None:
                msg = flask_babel.gettext("A name is required for each custom field.")
                return jsonify({"message": msg}), 400

            cf_field_type = cf.get('field_type', None)
            if cf_field_type is None:
                msg = flask_babel.gettext("A field type is required for each custom field.")
                return jsonify({"message": msg}), 400

            cf_sort_order = cf.get('sort_order', None)

            selections = cf.get('selections', None)
            if isinstance(selections, list):
                for s in selections:
                    if 'id' not in s:
                        msg = flask_babel.gettext("An id property is required for custom field selections.")
                        return jsonify({"message": msg}), 400

            validation_rules = []
            vrs = cf.get('validation_rules', None)
            if isinstance(vrs, list):
                for rule in vrs:
                    validation_rules.append(rule)

            model_type = 'CaseDefinition'
            custom_section_id = cf.get('custom_section_id', None)
            help_text = cf.get('help_text', None)

            custom_fields_to_add.append(models.CustomField(name=cf_name, field_type=cf_field_type,
                                                           selections=selections, validation_rules=validation_rules,
                                                           model_type=model_type, sort_order=cf_sort_order,
                                                           custom_section_id=custom_section_id, help_text=help_text,
                                                           created_by=g.request_user, updated_by=g.request_user))

        for survey in surveys_to_add:
            case_definition.surveys.append(survey)

        for document in documents_to_add:
            case_definition.documents.append(document)

        self.session.add(case_definition)
        self.session.commit()

        for cf in custom_fields_to_add:
            cf.model_id = case_definition.id
            self.session.add(cf)
        self.session.commit()

        # process activity definitions
        activity_definitions = self.json_args.get('activity_definitions', [])
        for activity_definition in activity_definitions:
            activity_definition['case_definition_id'] = case_definition.id
            service = ActivityDefinitionsService(json_args=activity_definition)
            _ = service.post()

        case_definition.reporting_table_name = current_app.reporting_service.create_case_table(case_definition)
        helpers.metabase_rescan()

        self.session.commit()

        return jsonify(case_definition.__getstate__()), 200

    def put(self, case_definition_id):

        case_defn = models.CaseDefinition.query.get_or_404(case_definition_id)

        name = self.json_args.get('name')
        description = self.json_args.get('description')

        surveys = self.json_args.get('surveys', [])
        documents = self.json_args.get('documents', [])

        if name:
            case_defn.name = name

        if description:
            case_defn.description = description

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

            # Preserve existing documents
            if 'id' in document:
                matching_docs = [doc for doc in case_defn.documents if doc.id == document['id']]
                for doc in matching_docs:
                    doc.name = doc_name
                    doc.description = doc_description
                    doc.is_required = is_required
                    documents_to_add.append(doc)
            else:
                case_definition_document = models.CaseDefinitionDocument(
                    name=doc_name,
                    description=doc_description,
                    is_required=is_required
                )
                documents_to_add.append(case_definition_document)

        case_defn.surveys = surveys_to_add
        case_defn.documents = documents_to_add

        self.session.commit()
        return jsonify(case_defn.__getstate__()), 200

    def add_custom_field(self, case_definition_id):

        result, is_valid = self._get_validated_custom_field(case_definition_id)

        if not is_valid:
            return jsonify({"message": result}), 400
        else:
            self.session.add(result)
            self.session.commit()

            cd = models.CaseDefinition.query.get(case_definition_id)
            for case in cd.cases:
                case.add_custom_field(result, g.request_user, g.request_user)
            self.session.commit()

            return jsonify(result.__getstate__()), 200

    def update_custom_field(self, case_definition_id, custom_field_id):

        case_definition = models.CaseDefinition.query.get_or_404(case_definition_id, "Case definition not found")
        _ = models.CustomField.query.get_or_404(custom_field_id, "Custom field not found")

        if 'id' not in self.json_args:
            msg = flask_babel.gettext("Custom Field ID is required")
            return jsonify({"message": msg}), 400

        result, is_valid = self._get_validated_custom_field(case_definition_id)

        if not is_valid:
            return jsonify({"message": result}), 400
        else:

            custom_field = models.CustomField.query.get(custom_field_id)
            if 'name' in self.json_args:
                custom_field.name = result.name
            if 'field_type' in self.json_args:
                custom_field.field_type = result.field_type
            if 'sort_order' in self.json_args:
                custom_field.sort_order = result.sort_order
            if 'selections' in self.json_args:
                custom_field.selections = result.selections
            if 'validation_rules' in self.json_args:
                custom_field.validation_rules = result.validation_rules
            if 'custom_section_id' in self.json_args:
                custom_field.custom_section_id = result.custom_section_id
            if 'help_text' in self.json_args:
                custom_field.help_text = result.help_text

            if self.session.is_modified(custom_field):
                custom_field.updated_by = g.request_user

                self.session.commit()

                for case in case_definition.cases:
                    case.update_custom_field(custom_field, g.request_user)
                self.session.commit()

            return jsonify(custom_field.__getstate__()), 200

    def get_custom_fields(self, case_definition_id):

        case_definition = models.CaseDefinition.query.get_or_404(case_definition_id, "Case definition not found")

        return jsonify(case_definition.custom_fields), 200

    def get_custom_field(self, case_definition_id, custom_field_id):

        _ = models.CaseDefinition.query.get_or_404(case_definition_id, "Case definition not found")
        custom_field = models.CustomField.query.get_or_404(custom_field_id, "Custom field not found")

        return jsonify(custom_field.__getstate__()), 200

    def delete_custom_field(self, case_definition_id, custom_field_id):

        case_defn = models.CaseDefinition.query.get_or_404(case_definition_id, "Case definition not found")
        custom_field = models.CustomField.query.get_or_404(custom_field_id, "Custom field not found")

        for case in case_defn.cases:
            case.delete_custom_field_by_case_definition_custom_field_id(custom_field_id)

        self.session.delete(custom_field)
        self.session.commit()

        msg = flask_babel.gettext("Case definition successfully deleted.")
        return jsonify({"message": msg}), 200
