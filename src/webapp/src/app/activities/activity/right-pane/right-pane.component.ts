import { Component, EventEmitter, Input, OnInit, Output } from "@angular/core";
import { CustomFieldContainerType } from 'app/_components/_custom-fields/render-custom-fields/render-custom-fields.component';
import { CustomField } from 'app/_models';

@Component({
  selector: "app-right-pane",
  templateUrl: "./right-pane.component.html",
  styleUrls: ["./right-pane.component.css"],
})
export class RightPaneComponent implements OnInit {
  @Input() activityID: number;
  @Input() createdBy: {
    email: string;
    id: number;
    name: string;
    username: string;
    color: string;
  };
  @Input() customFields: CustomField[] = [];
  @Input() isComplete: boolean;
  @Output() isCompleteChanged = new EventEmitter<boolean>();
  customFieldContainerType: CustomFieldContainerType = CustomFieldContainerType.Activity;

  constructor() {}

  ngOnInit() {}

  onValueChange(isChecked: boolean) {
    this.isComplete = isChecked;
    this.isCompleteChanged.emit(this.isComplete);
  }
}
