import { Component, OnInit, Input } from '@angular/core';
import { NgbActiveModal } from '@ng-bootstrap/ng-bootstrap';
import {
    FormGroup,
    FormBuilder,
    FormControl,
    FormArray,
    Validators,
} from '@angular/forms';
import {
    Field,
    ModalOptions,
    Selection,
    CustomField
} from '../../../_models';
import * as _ from 'lodash';

@Component({
    selector: 'app-add-custom-field-modal',
    templateUrl: './add-custom-field-modal.component.html',
    styleUrls: ['./add-custom-field-modal.component.css']
})
export class AddCustomFieldModalComponent implements OnInit {
    @Input() public modalOptions: ModalOptions;
    saveTxt: string;
    headerTxt: string;
    isSavingNewField: boolean;
    submitted = false;
    editingField = false;
    newCustomFieldForm: FormGroup;
    showSelectOptions = false;
    addingCustomField = false;
    showCustomFieldsForm = false;
    errorMsg: string;
    customFieldTitle: string;

    customFieldTypes: Field[] = [
        {value: 'text', displayName: 'Short Text'},
        {value: 'textarea', displayName: 'Long Text'},
        {value: 'check_box', displayName: 'Checkbox'},
        {value: 'radio_button', displayName: 'Radio Button'},
        {value: 'select', displayName: 'Selection Field'},
        {value: 'number', displayName: 'Numeric Field'},
        {value: 'date', displayName: 'Date Field'},
        {value: 'rank_list', displayName: 'Rank List'}
    ];

    constructor(
        private formBuilder: FormBuilder,
        public activeModal: NgbActiveModal
    ) {
    }

    ngOnInit() {
        this.initNewCustomFieldForm();
        if (!_.isEmpty(this.modalOptions.customField)) {
            this.editCustomFieldFromList(this.modalOptions.customField);
        }
        this.generateCustomFieldModalHeaderTxt();
        this.generateSaveButtonTxt();
    }

    get form() {
        return this.newCustomFieldForm.controls;
    }

    private generateCustomFieldModalHeaderTxt(): void {
        this.headerTxt = (this.modalOptions.mode === 'new') ? 'Add New Custom Field' : 'Edit Custom Field';
    }

    private generateSaveButtonTxt(): void {
        if (this.isSavingNewField) {
            this.saveTxt = 'Saving Field...';
        } else {
            this.saveTxt = (this.modalOptions.mode === 'new') ? '+ Add New Field' : 'Save Changes';
        }
    }

    private initNewCustomFieldForm(): void {
        this.newCustomFieldForm = this.formBuilder.group({
            name: new FormControl(null, [Validators.required]),
            helpText: new FormControl(null),
            fieldType: new FormControl(null, [Validators.required]),
            selections: new FormArray([]),
            placeholder: new FormControl(null)
        });
        this.newCustomFieldForm.controls['fieldType'].setValue(this.customFieldTypes[0].value, {
            onlySelf: true
        });
    }

    public onFieldTypeSelection(): void {
        this.showSelectOptions = ['check_box', 'radio_button', 'select', 'rank_list'].includes(
            this.form.fieldType.value
        );
    }

    public addOptionToCustomField(): void {
        const selectionsFormArray = <FormArray>this.newCustomFieldForm.controls['selections'];
        const selectionsFormGroup = new FormGroup({
            value: new FormControl(null, [Validators.required])
        });
        selectionsFormArray.push(selectionsFormGroup);
    }

    public removeOptionFromCustomField(index: number): void {
        const selectionsFormArray = <FormArray>this.newCustomFieldForm.controls['selections'];
        selectionsFormArray.removeAt(index);
    }

    public resetAddCustomFieldForm(): void {
        this.newCustomFieldForm.reset();
        this.initNewCustomFieldForm();
        this.showSelectOptions = false;
        this.showCustomFieldsForm = false;
        this.submitted = false;
        this.addingCustomField = false;
        this.activeModal.close();
    }

    public editCustomFieldFromList(item: CustomField): void {

        if (['check_box', 'radio_button', 'select', 'rank_list'].includes(item.field_type)) {
            this.showSelectOptions = true;
            item.selections.forEach(() => {
                this.addOptionToCustomField();
            });
        }

        this.newCustomFieldForm.patchValue({
            name: item.name,
            fieldType: item.field_type,
            selections: this.generateSelections(item.field_type, item.selections)
        });
    }

    public addNewCustomField(): void {
        this.isSavingNewField = true;
        this.generateSaveButtonTxt();

        this.submitted = true;
        if (this.newCustomFieldForm.invalid) {
            this.isSavingNewField = false;
            this.generateSaveButtonTxt();
        } else {
            setTimeout(() => {
                this.activeModal.close(this.newCustomFieldForm.value);
            }, 1000);
        }
    }

    private generateSelections(fieldType: string, selections: Selection[]): Selection[] {
        if (['check_box', 'rank_list', 'select', 'radio_button'].includes(fieldType)) {
            return selections;
        } else {
            return [];
        }
    }
}
