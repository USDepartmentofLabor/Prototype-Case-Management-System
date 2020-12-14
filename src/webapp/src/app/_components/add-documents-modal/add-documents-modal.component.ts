import { Component, Output, EventEmitter, ViewChild } from '@angular/core';
import { NgbActiveModal } from '@ng-bootstrap/ng-bootstrap';
import { Utils } from '../../_helpers';
import {
    FormBuilder,
    FormGroup,
    Validators
} from '@angular/forms';


@Component({
    selector: 'app-add-documents-modal',
    templateUrl: './add-documents-modal.component.html',
    styleUrls: ['./add-documents-modal.component.css']
})
export class AddDocumentsModalComponent {
    @Output() passNewDocData: EventEmitter<EventListener> = new EventEmitter();
    @ViewChild('inputRef') inputRef: HTMLInputElement;
    newDocForm: FormGroup;
    isSavingNewDoc: boolean;
    submitted = false;

    constructor(
        public activeModal: NgbActiveModal,
        private formBuilder: FormBuilder,
        private utils: Utils
    ) {
        this.newDocForm = this.formBuilder.group({
            name: ['', [Validators.required]],
            is_required: [false, []]
        });
    }


    get form() {
        return this.newDocForm.controls;
    }

    public capitalizeInput(str: string): string {
        return this.utils.generateCapitalizeString(str);
    }

    public generateSaveDocBtnTxt(): string {
        return this.isSavingNewDoc ? 'Adding Document...' : 'Add Document';
    }

    public submit(): void {
        this.isSavingNewDoc = true;
        this.submitted = true;

        if (this.newDocForm.invalid) {
            this.isSavingNewDoc = false;
        } else {
            this.passNewDocData.emit(this.newDocForm.value);
            setTimeout(() => {
                this.activeModal.close(this.newDocForm.value);
            }, 1000);
        }
    }
}
