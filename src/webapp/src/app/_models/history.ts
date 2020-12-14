export interface HistoryItemAPI {
  action: string;
  changes: {
    new_value: any;
    old_value: any;
    property_changed: string;
  }[];
  date_performed: string;
  performed_by: {
    id: number;
    name: string;
    username: string;
    email: string;
    color: string;
  };
}

export enum HistoryAction {
  Unknown,
  Insert,
  Update,
  Delete,
}

export interface HistoryItem {
  action: HistoryAction;
  description: string;
  newValue: any;
  oldValue: any;
  propertyChanged: string;
  dateChanged: Date;
  performedBy: {
    id: number;
    name: string;
    username: string;
    email: string;
    color: string;
  };
}
