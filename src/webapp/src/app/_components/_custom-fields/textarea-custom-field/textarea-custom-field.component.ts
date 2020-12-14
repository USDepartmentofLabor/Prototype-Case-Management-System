import { Component, OnInit, Input, Output, EventEmitter } from '@angular/core';

import { CustomField } from 'app/_models/customField';

@Component({
    selector: 'app-textarea-custom-field',
    templateUrl: './textarea-custom-field.component.html',
    styleUrls: ['./textarea-custom-field.component.css']
})
export class TextareaCustomFieldComponent implements OnInit {
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
