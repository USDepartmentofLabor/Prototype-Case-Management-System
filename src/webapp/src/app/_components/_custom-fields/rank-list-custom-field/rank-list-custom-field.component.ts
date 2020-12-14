import { Component, OnInit, Input, Output, EventEmitter } from '@angular/core';

import {
    CustomField,
    CustomFieldListOption,
    Selection,
} from 'app/_models/customField';

@Component({
    selector: 'app-rank-list-custom-field',
    templateUrl: './rank-list-custom-field.component.html',
    styleUrls: ['./rank-list-custom-field.component.css'],
})
export class RankListCustomFieldComponent implements OnInit {
    @Input() field: CustomField;
    @Output() fieldChanged = new EventEmitter<CustomField>();
    fieldName: string;
    selections: Selection[];
    listStyle: CustomFieldListOption = {
        width: '300px',
        height: '100%',
    };

    constructor() {
    }

    ngOnInit() {
        this.fieldName = `__${this.field.field_type}_cf_${this.field.id}`;

        if (this.field.value) {
            // sort selections
            // TODO: create model for rank list values
            const values = (this.field.value as any) as {
                id: number;
                rank: number;
            }[];
            values.sort((a, b) => (a.rank > b.rank ? 1 : -1));
            this.selections = [];
            for (let value of values) {
                this.selections.push(
                    this.field.selections.find((s) => s.id === value.id)
                );
            }
        } else {
            this.selections = this.field.selections;
        }
    }

    public onListSorted(sortedSelections: Selection[]): void {

        const values: { id: number; rank: number }[] = [];

        sortedSelections.forEach((s, idx) => {
            values.push({id: s.id, rank: idx + 1});
        });

        (this.field.value as any) = values;
        this.fieldChanged.emit(this.field);
    }
}
