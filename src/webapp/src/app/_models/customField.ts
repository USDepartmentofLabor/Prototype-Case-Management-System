export interface CustomFieldValue {
  value: string | number[] | { id: number; rank: number };
}

export interface CustomField {
  id: number;
  name: string;
  fieldType?: string;
  field_type: string;
  selections: Selection[];
  helpText?: string;
  help_text: string;
  placeholder?: string;
  value?: string;
  sort_order?: number;
  model_id?: number;
}

export interface Selection {
  id?: number;
  value: string;
}

export interface Field {
  id?: number;
  value: string;
  displayName: string;
}

export interface CustomFieldListOption {
  width: string;
  height: string;
}

export interface ModalOptions {
  mode: string;
  customField: CustomField;
  cancelTxt: string;
}

export interface PostCustomField {
  name: string;
  field_type: string;
  selections: Selection[];
  validation_rules: string[];
  custom_section_id: string;
  help_text: string;
  sort_order: number;
}

export interface PutCustomField extends PostCustomField {
  id?: string;
}
