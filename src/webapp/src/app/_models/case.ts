import { ActivityDefinitionResponse, ActivitySummaryAPI, PostActivityDefinition } from './activity';
import { PostCustomField } from './customField';
import {Document, Survey, CreatedBy, UpdatedBy, CustomField, HistoryItemAPI} from './index';

export interface CaseDefinition {
    id?: number;
    name: string;
    key: string;
    description?: string;
    cases?: number[];
    created_at?: string;
    created_by?: CreatedBy;
    documents?: Document[];
    surveys?: Survey[];
    custom_fields?: CustomField[];
    activity_definitions?: ActivityDefinitionResponse[];
    updated_at?: string;
    updated_by?: UpdatedBy;
}

export interface PostCaseDefinitionDocument {
    name: string;
    description: string;
    is_required: boolean;
}

export interface PostCaseDefinition {
    name: string;
    key: string;
    description: string;
    surveys: number[];
    documents: PostCaseDefinitionDocument[];
    custom_fields: PostCustomField[];
    activity_definitions: PostActivityDefinition[];
}

export interface AssignedToAPI {
    id: number;
    name: string;
    username: string;
    email: string;
    color: string;
    assigned_at: string;
}

export interface Case {
    id?: number;
    key?: string;
    name: string;
    description?: string;
    notes?: Note[];
    documents?: Document[];
    custom_fields?: CustomField[];
    created_at?: string;
    created_by?: CreatedBy;
    status?: CaseStatus;
    assigned_to?: AssignedToAPI;
    case_definition?: {
        id: number;
        key: string;
        name: string;
    },
    activities?: ActivitySummaryAPI[];
    history?: HistoryItemAPI[];
    updated_at?: string;
}

export interface Note {
    created_at?: string;
    created_by?: CreatedBy;
    id?: number;
    note: string;
    updated_at: string;
    updated_by?: UpdatedBy;
}

export interface CaseStatus {
    id: number;
    name: string;
    default: true;
    is_final: boolean;
    color: string;
}
