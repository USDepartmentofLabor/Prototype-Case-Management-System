import { Component, OnInit, Input, Output, EventEmitter } from '@angular/core';
import {
  FormGroup,
  FormControl,
  FormArray,
  ValidatorFn,
  AbstractControl,
} from '@angular/forms';
import { 
  CustomField, 
  Selection, 
  CustomFieldListOption 
} from '../../../_models';
import { AddCustomFieldModalComponent } from '../add-custom-field-modal/add-custom-field-modal.component';
import { 
  NgbModal, 
  NgbModalOptions, 
  ModalDismissReasons 
} from '@ng-bootstrap/ng-bootstrap';
import * as _ from 'lodash';

@Component({
  selector: 'custom-fields-creator',
  templateUrl: './custom-fields-creator-component.html',
  styleUrls: ['./custom-fields-creator-component.css']
})
export class CustomFieldsCreatorComponent implements OnInit {
  @Input() public customFieldsData: CustomField[];
  @Output() customFieldListChanged = new EventEmitter<CustomField[]>();

  closeResult: string;
  showDetails: boolean
  customFieldTitle: string;
  customFieldBtnTxt: string;
  submitted: boolean = false; 
  currentEditItem: CustomField;
  newCustomFieldForm: FormGroup;
  editingField: boolean = false;
  customFieldFormGroup: FormGroup;
  customFields: CustomField[] = [];
  addingCustomField: boolean = false;
  showSelectOptions: boolean = false;
  showCustomFieldsForm: boolean = false;
  
  listStyle: CustomFieldListOption = {
    width: '300px',
    height: '100%'
  };

  modalOptions:NgbModalOptions = {
    backdrop: 'static'
  }

  constructor(private modalService: NgbModal) {}

  ngOnInit() {
    this.initNewCustomFieldForm();
  }

  // remove
  get form() {
    return this.newCustomFieldForm.controls;
  }

  private initNewCustomFieldForm(): void {
    if(!_.isEmpty(this.customFieldsData)){
      this.customFields = this.customFieldsData;
      this.renderCustomField();
      this.showDetails = false;
    } else {
      this.customFields = [];
      this.showDetails = true;
    }
  }

  private renderCustomField(): void {
    let customFieldGroup = {};
    this.customFields.forEach((_field) => {
      if (['check_box', 'rank_list'].includes(_field.field_type)) {
        customFieldGroup[_field.name] = new FormArray([], this.minSelectedCheckboxes(1));

        this.customFieldFormGroup = new FormGroup(customFieldGroup);

        this.addCheckboxes(
          _field.selections,
          this.customFieldFormGroup.controls[_field.name]
        );
      } else {
        customFieldGroup[_field.name] = new FormControl('');
        this.customFieldFormGroup = new FormGroup(customFieldGroup);

        if(_field.field_type === 'select'){
        this.customFieldFormGroup.controls[_field.name].setValue(_field.selections[0], {
          onlySelf: true
        });
        }
      }
    });
  }

  public listSorted(_customField: CustomField[]):void {
    this.customFields = _customField;
    this.addCustomFieldsInTempStorage();
    //this.customFieldListChanged.emit(this.customFields);
  }

  public deleteCustomFieldFromList(field: CustomField): void {
    this.customFields.splice(
      this.customFields.findIndex((_field: CustomField) => _field.name === field.name),
      1
    );
    this.customFieldListChanged.emit(this.customFields);
  }

  public editCustomFieldFromList(item: CustomField) : void {
    this.currentEditItem = item;
    this.openAddCustomFieldModal('edit');
  }

  public addNewCustomField(
    {
      name, 
      helpText, 
      fieldType, 
      selections, 
      placeholder,
      sort_order
    }: CustomField): void {
    let _id: number;
    this.submitted = true;
    this.addingCustomField = true;

    if (this.editingField) {
      _id = this.currentEditItem.id;
      this.deleteCustomFieldFromList(this.currentEditItem);
    }
    const customField: CustomField = {
      id: this.editingField ? _id : this.generateUniqueId(),
      name: name,
      field_type: fieldType,
      selections: this.generateSelections(fieldType,selections),
      help_text: helpText || '',
      placeholder: placeholder || '',
      sort_order: sort_order || null
    };

    this.customFields.push(customField);
    this.addCustomFieldsInTempStorage();
    this.renderCustomField();
  }

  private addCustomFieldsInTempStorage():void{
    localStorage.setItem('customFields', JSON.stringify(this.customFields));
    this.customFieldListChanged.emit(this.customFields);
  }

  private generateUniqueId(): number {
    if (_.isEmpty(this.customFields)) {
      return 1;
    } else {
      let _ids = this.customFields.map((field) => {
        return field.id;
      });
      let maxId = Math.max(..._ids);
      return maxId + 1;
    }
  }

  private generateSelections(fieldType: string, selections: Selection[]): Selection[] {
    if (['check_box', 'rank_list', 'select','radio_button'].includes(fieldType)) {
      let _id = 1;
      selections.forEach((option) => {
        option.id = _id++;
      });
      return selections;
    } else {
      return [];
    }
  }

  private addCheckboxes(data: Selection[], currControl: AbstractControl): void {
    data.forEach(() => {
      const control = new FormControl();
      (currControl as FormArray).push(control);
    });
  }

  private minSelectedCheckboxes(min = 1) {
    const validator: ValidatorFn = (formArray: FormArray) => {
      const totalSelected = formArray.controls
        // get a list of checkbox values (boolean)
        .map((control) => control.value)
        // total up the number of checked checkboxes
        .reduce((prev, next) => (next ? prev + next : prev), 0);

      // if the total is not greater than the minimum, return the error message
      return totalSelected >= min ? null : { required: true };
    };

    return validator;
  }

  private setMode(mode:string): void{
    this.editingField = (mode == 'new') ? false :true;
  }


  public openAddCustomFieldModal(mode: string): void {
    this.setMode(mode);

    const options = {
      mode: mode,
      customField: mode == 'new' ? {} : this.currentEditItem,
      cancelTxt: 'Cancel'
    };

    const modalRef = this.modalService.open(AddCustomFieldModalComponent, this.modalOptions);
    modalRef.componentInstance.modalOptions = options;
    modalRef.result.then((results) =>{
      if(results){
        _.isEmpty(results) ? console.log('No data..') : this.addNewCustomField(results)
      }
    },
    reason =>{
      this.closeResult = `Dismissed ${this.getDismissReason(reason)}`;
    }) 
  }

  private getDismissReason(reason: any): string {
    if (reason === ModalDismissReasons.ESC) {
      return 'by pressing ESC';
    } else if (reason === ModalDismissReasons.BACKDROP_CLICK) {
      return 'by clicking on a backdrop';
    } else {
      return `with: ${reason}`;
    }
  }
}