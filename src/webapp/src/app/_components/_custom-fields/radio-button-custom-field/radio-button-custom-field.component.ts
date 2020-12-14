import { Component, OnInit, Input, Output, EventEmitter } from '@angular/core';

import { CustomField } from 'app/_models/customField';

@Component({
    selector: 'app-radio-button-custom-field',
    templateUrl: './radio-button-custom-field.component.html',
    styleUrls: ['./radio-button-custom-field.component.css']
})
export class RadioButtonCustomFieldComponent implements OnInit {
    @Input() public field: CustomField;
    @Output() fieldChanged = new EventEmitter<CustomField>();
    fieldName: string;

    constructor() {
    }

    ngOnInit() {
        this.fieldName = `__${this.field.field_type}_cf_${this.field.id}`;
    }

    isChecked(id: number) {
        const value = parseInt(this.field.value, 10);
        if (isNaN(value)) {
            return false;
        } else {
            return id === value;
        }
    }

    onValueChange(id: number, isChecked: boolean) {
        this.field.value = id.toString();
        this.fieldChanged.emit(this.field);
    }

}
