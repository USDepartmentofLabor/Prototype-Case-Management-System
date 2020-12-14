import { Component, Input, OnInit } from "@angular/core";
import * as moment from "moment";
import { HistoryItem, HistoryItemAPI } from "app/_models";
import { HistoryAction } from "app/_models/history";

@Component({
  selector: "app-history",
  templateUrl: "./history.component.html",
  styleUrls: ["./history.component.css"],
})
export class HistoryComponent implements OnInit {
  @Input() history: HistoryItemAPI[];
  @Input("history-on") historyOn: string;
  historyItems: HistoryItem[] = [];
  HistoryAction: HistoryAction;

  constructor() {}

  ngOnInit() {
    this.convertHistory();
  }

  public formatDate(theDate: Date): string {
    return moment.utc(theDate).fromNow();
  }

  private convertHistory(): void {
    const propertiesSkipped = [
      "updated_at",
      "updated_location_dt",
      "updated_by_id",
    ];
    this.historyItems = [];
    this.history.forEach((historyItem) => {
      const historyAction: HistoryAction = this.getHistoryAction(
        historyItem.action
      );

      if (historyAction == HistoryAction.Insert) {
        this.historyItems.push({
          action: historyAction,
          description: this.getHistoryDescription(historyAction),
          newValue: null,
          oldValue: null,
          propertyChanged: null,
          dateChanged: new Date(historyItem.date_performed + "Z"),
          performedBy: {
            id: historyItem.performed_by.id,
            name: historyItem.performed_by.name,
            username: historyItem.performed_by.username,
            email: historyItem.performed_by.email,
            color: historyItem.performed_by.color,
          },
        });
      } else {
        historyItem.changes.forEach((change) => {
          if (!propertiesSkipped.includes(change.property_changed)) {
            this.historyItems.push({
              action: historyAction,
              description: this.getHistoryDescription(historyAction),
              newValue: change.new_value,
              oldValue: change.old_value,
              propertyChanged: change.property_changed,
              dateChanged: new Date(historyItem.date_performed + "Z"),
              performedBy: {
                id: historyItem.performed_by.id,
                name: historyItem.performed_by.name,
                username: historyItem.performed_by.username,
                email: historyItem.performed_by.email,
                color: historyItem.performed_by.color,
              },
            });
          }
        });
      }
    });
    this.historyItems.sort((a, b) =>
      a.dateChanged.getTime() > b.dateChanged.getTime() ? 1 : -1
    );
  }

  private getHistoryAction(action: string): HistoryAction {
    let historyAction: HistoryAction;
    if (action === "insert") {
      historyAction = HistoryAction.Insert;
    } else if (action === "update") {
      historyAction = HistoryAction.Update;
    } else if (action === "delete") {
      historyAction = HistoryAction.Delete;
    } else {
      historyAction = HistoryAction.Unknown;
    }
    return historyAction;
  }

  private getHistoryDescription(action: HistoryAction): string {
    let description = "";
    switch (action) {
      case HistoryAction.Insert:
        description = `created the ${this.historyOn}`;
        break;
      case HistoryAction.Update:
        description = `updated the ${this.historyOn}`;
        break;
      case HistoryAction.Delete:
        description = `deleted the ${this.historyOn}`;
        break;
      default:
        description = `changed the ${this.historyOn}`;
        break;
    }
    return description;
  }
}
