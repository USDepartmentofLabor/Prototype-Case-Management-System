import { Component, OnInit, Input, Output, EventEmitter } from "@angular/core";
import { CustomField } from "app/_models/customField";

@Component({
  selector: "app-text-custom-field",
  templateUrl: "./text-custom-field.component.html",
  styleUrls: ["./text-custom-field.component.css"],
})
export class TextCustomFieldComponent implements OnInit {
  @Input() field: CustomField;
  @Output() fieldChanged = new EventEmitter<CustomField>();
  fieldName: string;

  constructor() {}

  ngOnInit() {
    this.fieldName = `__${this.field.field_type}_cf_${this.field.id}`;
  }

  onChange() {
    this.fieldChanged.emit(this.field);
  }
}
