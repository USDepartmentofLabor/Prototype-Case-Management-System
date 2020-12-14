import {
  Component,
  EventEmitter,
  Input,
  OnChanges,
  OnInit,
  Output,
} from "@angular/core";
import {
  FormArray,
  FormBuilder,
  FormControl,
  FormGroup,
  Validators,
} from "@angular/forms";
import {
  NgbModal,
  NgbModalOptions,
  ModalDismissReasons,
} from "@ng-bootstrap/ng-bootstrap";
import {
  AddDocumentsModalComponent,
} from "../../../_components";
import * as _ from "lodash";
import { Utils } from "app/_helpers";
import {
  ActivityDefinitionDocumentResponse,
  ActivityDefinitionResponse,
  CustomField,
  Survey,
} from "app/_models";

export enum ActivityDefinitionFormMode {
  create,
  edit,
}

@Component({
  selector: "app-activity-definition-form",
  templateUrl: "./activity-definition-form.component.html",
  styleUrls: ["./activity-definition-form.component.css"],
})
export class ActivityDefinitionFormComponent implements OnInit, OnChanges {
  @Input() activityDefinition: ActivityDefinitionResponse;
  @Input() surveyOptions: Survey[];
  @Input() mode: ActivityDefinitionFormMode = ActivityDefinitionFormMode.create;
  @Output() activityDefinitionChanged = new EventEmitter<
    ActivityDefinitionResponse
  >();
  @Output() changeCancelled = new EventEmitter<boolean>();

  activityDefinitonForm: FormGroup;
  primaryDialogOptions: NgbModalOptions = {
    backdrop: "static",
  };
  closeResult: string;
  headerLabel: string;
  submitted = false;

  constructor(
    private formBuilder: FormBuilder,
    private utils: Utils,
    private modalService: NgbModal
  ) {
    this.activityDefinitonForm = this.formBuilder.group({
      name: new FormControl(null, [
        Validators.required,
        Validators.minLength(6),
      ]),
      description: new FormControl(null, []),
      surveyOptionsCheckBoxes: new FormArray(
        []
      ),
    });
  }

  ngOnInit() {
    this.initializeForm();
  }

  ngOnChanges() {
    this.initializeForm();
  }

  get form() {
    return this.activityDefinitonForm.controls;
  }

  public onCustomFieldsChanged(customFields: CustomField[]) {
    console.log(
      "[ActivityDefinitionFormComponent] received custom fields changed"
    );
    this.activityDefinition.custom_fields = customFields;
  }

  public onSaveActivityDefinition() {
    console.log("[ActivityDefinitionFormComponent] saving activity definition");
    this.submitted = true;

    if (this.activityDefinitonForm.valid) {
      this.activityDefinition.name = this.activityDefinitonForm.value.name;
      this.activityDefinition.description = this.activityDefinitonForm.value.description;
      this.activityDefinition.surveys = this.getSelectedSurveysOptions();
      this.activityDefinitionChanged.emit(this.activityDefinition);
    }
  }

  public onCancel() {
    console.log(
      "[ActivityDefinitionFormComponent] cancel activity definition change"
    );
    this.changeCancelled.emit(true);
  }

  public openAddDocumentsModal(): void {
    const modalRef = this.modalService.open(
      AddDocumentsModalComponent,
      this.primaryDialogOptions
    );
    modalRef.result.then(
      (result) => {
        if (result) {
          _.isEmpty(result)
            ? console.log("No new obj")
            : this.addDocumentToList(result);
        }
      },
      (reason) => {
        this.closeResult = `Dismissed ${this.getDismissReason(reason)}`;
      }
    );
  }

  public documentsAdded(): boolean {
    return _.isEmpty(this.activityDefinition.documents);
  }

  public removeDocumentFromDocumentsList(
    document: ActivityDefinitionDocumentResponse
  ): void {
    this.activityDefinition.documents = this.activityDefinition.documents.filter(
      (doc: ActivityDefinitionDocumentResponse) => doc !== document
    );
  }

  public generateDocumentRequiredTxt(option: boolean): string {
    return option === true ? " -(Required)" : "";
  }

  public surveyOptionCheckBoxControls() {
    return (this.activityDefinitonForm.controls.surveyOptionsCheckBoxes as FormArray).controls;
  }

  private initializeForm(): void {
    if (this.mode === ActivityDefinitionFormMode.edit) {
      this.headerLabel = "Update Activity Type";
    } else {
      this.headerLabel = "Create Activity Type";
    }
    this.activityDefinitonForm.patchValue({
      name: this.activityDefinition.name,
      description: this.activityDefinition.description,
    });

    const surveyNames = this.activityDefinition.surveys.map((s) => s.name);
    this.activityDefinitonForm.controls.surveyOptionsCheckBoxes = new FormArray(
      []
    );
    this.surveyOptions.map((survey: any) => {
      const control = new FormControl(surveyNames.includes(survey.name));
      (this.activityDefinitonForm.controls
        .surveyOptionsCheckBoxes as FormArray).push(control);
    });
  }

  private addDocumentToList(
    document: ActivityDefinitionDocumentResponse
  ): void {
    this.activityDefinition.documents.push(document);
  }

  private getDismissReason(reason: any): string {
    if (reason === ModalDismissReasons.ESC) {
      return "by pressing ESC";
    } else if (reason === ModalDismissReasons.BACKDROP_CLICK) {
      return "by clicking on a backdrop";
    } else {
      return `with: ${reason}`;
    }
  }

  private getSelectedSurveysOptions(): { id: number; name: string }[] {
    const selectedSurveyOptions = [];
    const selectedSurveycb = this.form.surveyOptionsCheckBoxes as FormArray;
    selectedSurveycb.controls.forEach((checkbox, index) => {
      if (checkbox.value) {
        selectedSurveyOptions.push({
          id: this.surveyOptions[index].id,
          name: this.surveyOptions[index].name,
        });
      }
    });

    return selectedSurveyOptions;
  }
}
