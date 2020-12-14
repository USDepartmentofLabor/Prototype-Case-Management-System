import { CustomField, Document, FileAPI, Note, HistoryItemAPI } from "./index";
import { PostCustomField } from "../_models/customField";

export interface ActivityAPI {
  id: number;
  name: string;
  description: string;
  activity_definition: { id: number; name: string };
  case: {
    id: number;
    key: string;
    name: string;
    definition: {
      id: number;
      key: string;
      name: string;
    };
  };
  completed_at: string;
  completed_by: {
    email: string;
    id: number;
    name: string;
    username: string;
    color: string;
  };
  is_complete: boolean;
  created_at: string;
  created_by: {
    email: string;
    id: number;
    name: string;
    username: string;
    color: string;
  };
  created_location: {
    altitude: number;
    altitude_accuracy: number;
    heading: number;
    latitude: number;
    location_recorded_dt: string;
    longitude: number;
    position_accuracy: number;
    speed: number;
  };
  custom_fields?: CustomField[];
  documents?: Document[];
  files?: FileAPI[];
  notes?: Note[];
  surveys: {
    id: number;
    name: string;
    responses_count: number;
  }[];
  updated_at: string;
  updated_by: {
    email: string;
    id: number;
    name: string;
    username: string;
    color: string;
  };
  updated_location: {
    altitude: number;
    altitude_accuracy: number;
    heading: number;
    latitude: number;
    location_recorded_dt: string;
    longitude: number;
    position_accuracy: number;
    speed: number;
  };
  history: HistoryItemAPI[];
}

export interface ActivityDefinitionDocumentResponse {
  id: number;
  name: string;
  description: string;
  is_required: boolean;
}

export interface AddNoteResponse {
  created_at: string;
  created_by: {
    color: string;
    email: string;
    id: number;
    name: string;
    username: string;
  };
  id: number;
  model_id: number;
  model_name: string;
  note: string;
  updated_at: string;
  updated_by: {
    color: string;
    email: string;
    id: number;
    name: string;
    username: string;
  };
}

export interface PostActivityDefinition {
  name: string;
  description?: string;
  case_definition_id: number;
  surveys: number[];
  documents: {
    name: string;
    description: string;
    is_required?: boolean;
  }[];
  custom_fields: PostCustomField[];
}

export interface ActivityDefinitionResponse {
  id: number;
  name: string;
  description: string;
  case_definition: {
    id: number;
    key: string;
    name: string;
  };
  custom_fields: CustomField[];
  created_at: string;
  updated_at: string;
  created_by: {
    color: string;
    email: string;
    id: number;
    name: string;
    username: string;
  };
  updated_by: {
    color: string;
    email: string;
    id: number;
    name: string;
    username: string;
  };
  documents: ActivityDefinitionDocumentResponse[];
  surveys: {
    id: number;
    name: string;
  }[];
}

export interface ActivitySummaryAPI {
  id: number;
  name: string;
  is_complete: boolean;
  completed_at: string;
  completed_by: {
    color: string;
    email: string;
    id: number;
    name: string;
    username: string;
  };
  created_at: string;
  updated_at: string;
}

export class PostActivity {
  constructor(
    private activity_definition_id: number,
    private case_id: number,
    private name: string,
    private description: string,
    private notes: string[],
    private latitude: number,
    private longitude: number
  ) {}
}
