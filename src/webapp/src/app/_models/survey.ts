import { CaseStatus } from './case';

export interface Survey {
  id?: number;
  name: string;
  is_archived: boolean;
  structure: SurveyStructure;
  responses?: number[];
  notes?: string[];
  case_definitions?: number[];
  created_by?: CreatedBy;
  created_at?: string;
  updated_at?: string;
  updated_by?: UpdatedBy;
}

interface SurveyStructure {
  pages?: Elements[];
}

interface Elements {
  inputType: string;
  isRequired: boolean;
  name: string;
  title: string;
  type: string;
}

export interface CreatedBy {
  id: number;
  email: string;
  name?: string;
  username: string;
  first_initial?: string;
  avatarBgColor?: string;
  color: string;
}

export interface UpdatedBy {
  id: number;
  email: string;
  username: string;
}

export interface SurveryResponse {
    case: number; 
    created_at: string; 
    created_by: CreatedBy;
    id: number; 
    is_archived: boolean; 
    source_type: string;
    status: CaseStatus;
    structure: SurveyStructure;
    survey: number;
    updated_at: string;
    updated_by: UpdatedBy;
}