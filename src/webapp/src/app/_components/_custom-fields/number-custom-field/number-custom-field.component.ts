import { Component, OnInit, Input, Output, EventEmitter } from '@angular/core';

import { CustomField } from 'app/_models/customField';

@Component({
    selector: 'app-number-custom-field',
    templateUrl: './number-custom-field.component.html',
    styleUrls: ['./number-custom-field.component.css']
})
export class NumberCustomFieldComponent implements OnInit {
    @Input() public field: CustomField;
    @Output() fieldChanged = new EventEmitter<CustomField>();
    fieldName: string;

    constructor() {
    }

    ngOnInit() {
        this.fieldName = `__${this.field.field_type}_cf_${this.field.id}`;
    }

    onValueChange() {
        this.fieldChanged.emit(this.field);
    }

}
