import { CreatedBy } from "./survey";

export interface Document {
  name?: string;
  is_required?: boolean;
  id?: number;
  created_by?: CreatedBy;
  created_at?: string;
  description?: string;
  original_filename?: string;
  remote_filename?: string;
  url?: string;
  case?: number;
}

export interface FileAPI {
  created_at: string;
  created_by: {
    email: string;
    id: number;
    name: string;
    username: string;
  };
  id: number;
  original_filename: string;
  remote_filename: string;
  url: string;
}
