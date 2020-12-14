import copy
from datetime import datetime

import uuid


class CustomFieldManager:

    def __init__(self, custom_field_object):
        self.custom_field_object = custom_field_object

        setattr(self.custom_field_object, 'add_custom_field', self.add_custom_field)
        setattr(self.custom_field_object, 'update_custom_field', self.update_custom_field)
        setattr(self.custom_field_object, 'update_custom_field_value', self.update_custom_field_value)
        setattr(self.custom_field_object, 'delete_custom_field_by_parent_id', self.delete_custom_field_by_parent_id)
        setattr(self.custom_field_object, 'get_custom_field', self.get_custom_field)
        setattr(self.custom_field_object, 'has_custom_field', self.has_custom_field)
        setattr(self.custom_field_object, 'delete_custom_field', self.delete_custom_field)

    def add_custom_field(self, custom_field, created_by, updated_by, created_at=None,
                         updated_at=None):
        print(f"Adding custom field: {custom_field}")

        custom_field_id = custom_field.get('id', str(uuid.uuid4()))
        if created_at is None:
            created_at = datetime.utcnow().isoformat()
        if updated_at is None:
            updated_at = datetime.utcnow().isoformat()

        if custom_field_id in [cf['id'] for cf in self.custom_field_object.custom_fields]:
            raise KeyError('Custom field IDs must be unique')
        _custom_fields = copy.deepcopy(self.custom_field_object.custom_fields)
        _custom_fields.append({
            'id': custom_field_id,
            'name': custom_field['name'],
            'field_type': custom_field['field_type'],
            'selections': custom_field['selections'],
            'validation_rules': custom_field['validation_rules'],
            'model_type': type(self.custom_field_object).__name__,
            'parent_id': custom_field.get('parent_id'),
            'custom_section_id': custom_field['custom_section_id'],
            'help_text': custom_field['help_text'],
            'sort_order': custom_field['sort_order'],
            'value': None,
            'created_at': created_at,
            'created_by': {
                'email': created_by.email,
                'id': created_by.id,
                'username': created_by.username,
                'name': created_by.name
            },
            'updated_at': updated_at,
            'updated_by': {
                'email': updated_by.email,
                'id': updated_by.id,
                'username': updated_by.username,
                'name': updated_by.name
            }
        })
        self.custom_field_object.custom_fields = _custom_fields

    def update_custom_field(self, custom_field, updated_by):
        print(f"Updating custom field ID {custom_field.id}")
        _custom_fields = copy.deepcopy(self.custom_field_object.custom_fields)
        new_custom_fields = []
        for cf in _custom_fields:
            if cf['id'] == custom_field['id']:
                cf['name'] = custom_field.name
                cf['field_type'] = custom_field.field_type
                cf['selections'] = custom_field.selections
                cf['validation_rules'] = custom_field.validation_rules
                cf['custom_section_id'] = custom_field.custom_section_id
                cf['help_text'] = custom_field.help_text
                cf['sort_order'] = custom_field.sort_order
                cf['value'] = None
                cf['updated_at'] = datetime.utcnow().isoformat()
                cf['updated_by']['email'] = updated_by.email
                cf['updated_by']['id'] = updated_by.id
                cf['updated_by']['username'] = updated_by.username
                cf['updated_by']['name'] = updated_by.name
            new_custom_fields.append(cf)
        self.custom_field_object.custom_fields = new_custom_fields

    def update_custom_field_value(self, custom_field, updated_by, updated_at=datetime.utcnow().isoformat()):
        print(f"Updating the value for custom field id {custom_field['id']}")

        _custom_fields = copy.deepcopy(self.custom_field_object.custom_fields)
        new_custom_fields = []
        for cf in _custom_fields:
            if cf['id'] == custom_field['id']:
                cf['value'] = custom_field['value']
                cf['updated_at'] = updated_at
                cf['updated_by']['email'] = updated_by.email
                cf['updated_by']['id'] = updated_by.id
                cf['updated_by']['username'] = updated_by.username
                cf['updated_by']['name'] = updated_by.name
            new_custom_fields.append(cf)
        self.custom_field_object.custom_fields = new_custom_fields

    def delete_custom_field_by_parent_id(self, parent_id):
        print(f"Deleting custom field for parent id {parent_id}")

        _custom_fields = copy.deepcopy(self.custom_field_object.custom_fields)
        new_custom_fields = []
        for cf in _custom_fields:
            if cf['parent_custom_field_id'] != parent_id:
                new_custom_fields.append(cf)
        self.custom_field_object.custom_fields = new_custom_fields

    def delete_custom_field(self, custom_field_id):
        print(f"Deleting custom field id {custom_field_id}")

        _custom_fields = copy.deepcopy(self.custom_field_object.custom_fields)
        new_custom_fields = []
        for cf in _custom_fields:
            if cf['id'] != custom_field_id:
                new_custom_fields.append(cf)
        self.custom_field_object.custom_fields = new_custom_fields

    def get_custom_field(self, custom_field_id):
        print(f"Getting custom field for id {custom_field_id}")
        for cf in self.custom_field_object.custom_fields:
            if cf['id'] == str(custom_field_id):
                return cf

    def has_custom_field(self, custom_field_id):
        for cf in self.custom_field_object.custom_fields:
            if cf['id'] == str(custom_field_id):
                return True
        return False
