import { Component, OnInit, Input, Output, EventEmitter } from "@angular/core";

import { CustomField } from "app/_models/customField";

@Component({
  selector: "app-checkbox-custom-field",
  templateUrl: "./checkbox-custom-field.component.html",
  styleUrls: ["./checkbox-custom-field.component.css"],
})
export class CheckboxCustomFieldComponent implements OnInit {
  @Input() public field: CustomField;
  @Output() fieldChanged = new EventEmitter<CustomField>();
  fieldName: string;

  constructor() {}

  ngOnInit() {
    this.fieldName = `__${this.field.field_type}_cf_${this.field.id}`;
  }

  onValueChange(id: number, isChecked: boolean) {
    const values = this.field.value
      ? ((this.field.value as any) as number[])
      : [];

    if (isChecked) {
      values.push(id);
    } else {
      const idx = values.findIndex((x) => x === id);
      values.splice(idx, 1);
    }

    (this.field.value as any) = values;
    this.fieldChanged.emit(this.field);
  }

  isChecked(id: number) {
    // TODO: update data model for custom field values
    const selectedValue = (this.field.value as any) as number[];
    return selectedValue ? selectedValue.includes(id) : false;
  }
}
