import { Component, OnInit, Input, EventEmitter, Output } from '@angular/core';
import { CustomField } from 'app/_models/customField';

@Component({
    selector: 'app-date-custom-field',
    templateUrl: './date-custom-field.component.html',
    styleUrls: ['./date-custom-field.component.css']
})
export class DateCustomFieldComponent implements OnInit {
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
