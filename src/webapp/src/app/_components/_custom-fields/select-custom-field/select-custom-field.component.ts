import { Component, OnInit, Input, Output, EventEmitter } from "@angular/core";

import { CustomField, Selection } from "app/_models/customField";

@Component({
  selector: "app-select-custom-field",
  templateUrl: "./select-custom-field.component.html",
  styleUrls: ["./select-custom-field.component.css"],
})
export class SelectCustomFieldComponent implements OnInit {
  @Input() public field: CustomField;
  @Output() fieldChanged = new EventEmitter<CustomField>();
  fieldName: string;
  selectedObject: Selection;

  constructor() {}

  ngOnInit() {
    this.fieldName = `__${this.field.field_type}_cf_${this.field.id}`;
    if (this.field.value) {
      this.selectedObject = this.field.selections.find(
        (el) => el.id.toString() === this.field.value.toString()
      );
    }
  }

  onValueChange() {
    this.field.value = this.selectedObject.id.toString();
    this.fieldChanged.emit(this.field);
  }
}
