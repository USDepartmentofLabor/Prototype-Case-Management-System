import { Component, OnInit } from "@angular/core";
import {
  FormBuilder,
  FormGroup,
  FormControl,
  FormArray,
  Validators,
} from "@angular/forms";
import { concatMap, mergeMap, switchMap, tap } from "rxjs/operators";
//import 'rxjs/add/operator/switchMap';
import {
  NgbModal,
  NgbModalOptions,
  ModalDismissReasons,
} from "@ng-bootstrap/ng-bootstrap";
import {
  AddDocumentsModalComponent,
  DialogComponent,
} from "../../../_components";
import { Router, ActivatedRoute } from "@angular/router";
import { Utils } from "../../../_helpers";
import { SurveyService, CaseService } from "../../../_services";
import {
  Document,
  CustomField,
  Survey,
  CaseDefinition,
  DialogOptions,
  ActivityDefinitionResponse,
  PostCustomField,
  PostActivityDefinition,
} from "../../../_models";
import * as _ from "lodash";
import { Location } from "@angular/common";
import { ActivityService } from "app/_services/activity.service";
import { ActivityDefinitionFormMode } from "../../../activities/activity_definitions/activity-definition-form/activity-definition-form.component";

@Component({
  selector: "app-new-case-definition",
  templateUrl: "./new-case-definition.component.html",
  styleUrls: ["./new-case-definition.component.css"],
})
export class NewCaseDefinitionComponent implements OnInit {
  newCaseDefinitonForm: FormGroup;
  surveyOptions: Survey[];
  closeResult: string;
  submitted = false;
  isSavingCaseDef = false;
  isSurveysLoading = false;
  documents: Document[] = [];
  surveys: Survey[] = [];
  errorMsg: string;
  caseDefinitionData: CaseDefinition;
  caseDefinitionId: number;
  customFields: CustomField[];
  title: string;
  isLoading = false;
  isEditMode = false;
  saveChanges = false;
  primaryDialogOptions: NgbModalOptions = {
    backdrop: "static",
  };
  activityDefinitionFormMode: ActivityDefinitionFormMode;
  activityDefinitions: ActivityDefinitionResponse[] = [];
  isEditingActivityDefinition = false;
  selectedActivityDefinition: ActivityDefinitionResponse;

  constructor(
    private formBuilder: FormBuilder,
    private surveyService: SurveyService,
    private caseService: CaseService,
    private modalService: NgbModal,
    private router: Router,
    private utils: Utils,
    private route: ActivatedRoute,
    private location: Location,
    private activtyService: ActivityService
  ) {
    this.newCaseDefinitonForm = this.formBuilder.group({
      name: new FormControl(null, [
        Validators.required,
        Validators.minLength(6),
      ]),
      caseKey: new FormControl(null, [
        Validators.required,
        Validators.minLength(2),
      ]),
      description: new FormControl(null, []),
      surveyOptionsCheckBoxes: new FormArray([]),
    });

    this.route.params.subscribe((_params) => {
      this.caseDefinitionId = _params.id || null;
    });
  }

  ngOnInit() {
    this.isLoading = true;
    this.caseDefinitionId ? this.initEditMode() : this.initCreateNewMode();
    this.activityDefinitionFormMode = this.isEditMode
      ? ActivityDefinitionFormMode.edit
      : ActivityDefinitionFormMode.create;
  }

  get form() {
    return this.newCaseDefinitonForm.controls;
  }

  public back(): void {
    this.location.back();
  }

  private initEditMode() {
    this.title = "Edit Case Type";
    this.isEditMode = true;
    this.getCaseDefinitionDetails();
  }

  private initCreateNewMode() {
    this.title = "New Case Type";
    this.isEditMode = false;
    this.getSurveyOptions();
  }

  private getCaseDefinitionDetails(): void {
    this.caseService
      .getCaseDefinition(this.caseDefinitionId)
      .subscribe((data) => {
        this.isLoading = false;
        this.caseDefinitionData = data;
        this.newCaseDefinitonForm.patchValue({
          name: this.caseDefinitionData.name,
          caseKey: this.caseDefinitionData.key,
          description: this.caseDefinitionData.description,
        });
        this.caseDefinitionData.surveys = <[]>(
          this.caseDefinitionData.surveys.map((obj) => {
            return obj.name;
          })
        );
        this.newCaseDefinitonForm.controls["caseKey"].disable();
        this.getSurveyOptions();
        this.documents = this.caseDefinitionData.documents;
        this.customFields = this.caseDefinitionData.custom_fields;
        this.activityDefinitions = this.caseDefinitionData.activity_definitions
          ? this.caseDefinitionData.activity_definitions
          : [];
      });
  }

  private getSurveyOptions(): void {
    this.isSurveysLoading = true;
    this.surveyService.getAllSurveys().subscribe((surveyOptions) => {
      this.surveyOptions = surveyOptions;
      this.addSurveyOptionCheckboxes();
      this.isSurveysLoading = false;
      this.isLoading = false;
    });
  }

  private addSurveyOptionCheckboxes(): void {
    this.surveyOptions.map((survey: any) => {
      const control = this.isEditMode
        ? new FormControl(this.caseDefinitionData.surveys.includes(survey.name))
        : new FormControl();
      (this.newCaseDefinitonForm.controls
        .surveyOptionsCheckBoxes as FormArray).push(control);
    });
  }

  private addDocumentToList(_document: Document): void {
    this.documents.push(_document);
  }

  private getSelectedSurveysOptions(): Survey[] {
    const selectedSurveyOptions = [];
    const selectedSurveycb = this.form.surveyOptionsCheckBoxes as FormArray;
    selectedSurveycb.controls.forEach((checkbox, index) => {
      if (checkbox.value) {
        selectedSurveyOptions.push(this.surveyOptions[index].id);
      }
    });

    return selectedSurveyOptions;
  }

  public removeDocumentFromDocumentsList(_document: Document): void {
    this.documents = this.documents.filter(
      (doc: Document) => doc !== _document
    );
  }

  public generateDocumentRequiredTxt(_option: boolean): string {
    return _option === true ? " -(Required)" : "";
  }

  public generateSaveNewCaseDefinitionBtnTxt(): string {
    if (this.isEditMode) {
      return this.isSavingCaseDef
        ? "Saving Case Type..."
        : "Save Changes to Case Type";
    }
    return this.isSavingCaseDef
      ? "Saving New Case Type..."
      : "Save New Case Type";
  }

  public documentsAdded(): boolean {
    return _.isEmpty(this.documents);
  }

  public capitalizeInput(_str: string): string {
    return this.utils.generateCapitalizeString(_str);
  }

  public upperCaseInput(_str: string): string {
    return this.utils.generateUppercaseString(_str);
  }

  private getCustomFieldsFromTempStorage(): CustomField[] {
    return JSON.parse(localStorage.getItem("customFields")) || [];
  }

  private clearCustomFieldsFromTempStorage(): void {
    localStorage.removeItem("customFields");
  }

  public onCreateNewCaseDefinition(): void {
    this.isSavingCaseDef = true;
    this.submitted = true;

    const newCaseDefinition: CaseDefinition = {
      name: this.newCaseDefinitonForm.value.name,
      key: this.newCaseDefinitonForm.value.caseKey,
      description: this.newCaseDefinitonForm.value.description,
      surveys: this.getSelectedSurveysOptions(),
      custom_fields: this.getCustomFieldsFromTempStorage(),
      documents: this.documents,
      activity_definitions: this.activityDefinitions,
    };

    if (this.newCaseDefinitonForm.invalid) {
      this.isSavingCaseDef = false;
    } else {
      if (this.isEditMode) {
        this.caseService
          .updateCaseDefinition(newCaseDefinition, this.caseDefinitionId)
          .pipe(
            tap((res) =>
              console.log(`case defn save result ${JSON.stringify(res)}`)
            )
          )
          .subscribe(
            (caseDefnResponse) => {
              this.activityDefinitions.forEach((actDefn) => {
                console.log(`ACT DEFN ID = ${actDefn.id}`);
                if (actDefn.id > 0) {
                  // update existing activity definition
                  console.log("UPDATING ACT DEFN");
                  this.activtyService
                    .updateActivityDefinition(actDefn.id, actDefn)
                    .subscribe(
                      () => {
                        console.log(
                          "[NewCaseDefinitionComponent.onCreateNewCaseDefinition()] activity definition successfully updated"
                        );
                        actDefn.custom_fields.forEach((customField) => {
                          if (customField.id) {
                            this.activtyService
                              .updateCustomField(
                                actDefn.id,
                                customField.id.toString(),
                                {
                                  id: customField.id.toString(),
                                  name: customField.name,
                                  field_type: customField.field_type,
                                  selections: customField.selections,
                                  validation_rules: null,
                                  custom_section_id: null,
                                  help_text: customField.help_text,
                                  sort_order: customField.sort_order,
                                }
                              )
                              .subscribe(
                                (res) => {
                                  console.log(
                                    `[NewCaseDefinitionComponent.onCreateNewCaseDefinition()] custom field ${res.id} successfully updated`
                                  );
                                  //console.table(res);
                                },
                                (error) => {
                                  this.errorMsg = error.message;
                                  this.isSavingCaseDef = false;
                                }
                              );
                          } else {
                            const newCustomField: PostCustomField = {
                              name: customField.name,
                              field_type: customField.field_type,
                              selections: customField.selections,
                              validation_rules: null,
                              custom_section_id: null,
                              help_text: customField.help_text,
                              sort_order: customField.sort_order,
                            };
                            this.activtyService
                              .createCustomField(actDefn.id, newCustomField)
                              .subscribe(
                                (res) => {
                                  console.log(
                                    `[NewCaseDefinitionComponent.onCreateNewCaseDefinition()] custom field ${res.id} successfully created`
                                  );
                                  //console.table(res);
                                },
                                (error) => {
                                  this.errorMsg = error.message;
                                  this.isSavingCaseDef = false;
                                }
                              );
                          }
                        });
                      },
                      (error) => {
                        this.errorMsg = error.message;
                        this.isSavingCaseDef = false;
                      }
                    );
                } else {
                  // add new activity definition
                  console.log("CREATE NEW ACT DEFN");
                  const postData: PostActivityDefinition = {
                    name: actDefn.name,
                    description: actDefn.description,
                    case_definition_id: caseDefnResponse.id,
                    surveys: actDefn.surveys.map((s) => {
                      return s.id;
                    }),
                    documents: actDefn.documents,
                    custom_fields: actDefn.custom_fields
                      ? actDefn.custom_fields.map((cf) => {
                          return {
                            name: cf.name,
                            field_type: cf.fieldType,
                            selections: cf.selections,
                            validation_rules: [],
                            custom_section_id: null,
                            help_text: cf.help_text,
                            sort_order: cf.sort_order,
                          };
                        })
                      : [],
                  };

                  this.activtyService
                    .createActivityDefinition(postData)
                    .subscribe(
                      () => {
                        console.log(
                          "[NewCaseDefinitionComponent.onCreateNewCaseDefinition()] !!!!!activity definition successfully created"
                        );
                      },
                      (error) => {
                        console.log(
                          `saving new activity definition error: ${error.message}`
                        );
                        this.errorMsg = error.message;
                        this.isSavingCaseDef = false;
                      }
                    );
                }
              });
              this.utils.generateSuccessToastrMsg(
                "New Case Definition successfully created!",
                ""
              );
              this.isSavingCaseDef = false;
              this.onSuccess();
            },
            (error) => {
              this.errorMsg = error.message;
              this.isSavingCaseDef = false;
            }
          );
      } else {
        this.caseService.createNewCaseDefinition(newCaseDefinition).subscribe(
          () => {
            this.utils.generateSuccessToastrMsg(
              "New Case Definition successfully created!",
              ""
            );
            this.isSavingCaseDef = false;
            this.onSuccess();
          },
          (error) => {
            this.errorMsg = error.message;
            this.isSavingCaseDef = false;
          }
        );
      }
    }
  }

  private deleteCaseDefinition(_caseDefId: number): void {
    this.caseService.deleteCaseDefinition(_caseDefId).subscribe((data) => {
      if (data) {
        this.utils.generateSuccessToastrMsg(
          "Case Definition was Successfully Deleted",
          ""
        );
        this.router.navigate(["/cases-definitions"]);
      }
    });
  }

  private onSuccess(): void {
    this.onCancel();
    this.clearCustomFieldsFromTempStorage();

    // wait a few sec before redirect user to a new view
    setTimeout(() => {
      this.router.navigate(["/cases-definitions"]);
    }, 2500);
  }

  private onCancel(): void {
    if (this.isSavingCaseDef) {
      this.isSavingCaseDef = false;
    }
    this.documents = [];
    this.newCaseDefinitonForm.reset();
    this.submitted = false;
    this.errorMsg = null;
    this.back();
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

  public openDeleteDialogPrompt(): void {
    const dialogOptions: DialogOptions = {
      headerText: "Delete Case Definition",
      bodyText: "Are you sure you want to delete this Case Definition?",
      primaryActionText: "Yes, Delete",
      cancelBtnText: "Cancel",
      btnClass: "danger",
      saveChanges: false,
    };

    const dialog = this.modalService.open(
      DialogComponent,
      this.primaryDialogOptions
    );
    dialog.componentInstance.dialogOptions = dialogOptions;
    dialog.componentInstance.passEntry.subscribe((choice: boolean) => {
      if (choice) {
        this.deleteCaseDefinition(this.caseDefinitionId);
      }
    });
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

  public onNewActivityDefinition() {
    if (this.isEditingActivityDefinition) {
      this.isEditingActivityDefinition = false;
    }
    this.isEditingActivityDefinition = true;
    this.activityDefinitionFormMode = ActivityDefinitionFormMode.create;
    this.selectedActivityDefinition = {
      id: this.getNewActivityDefinitionId(),
      name: null,
      description: null,
      case_definition: {
        id: null,
        key: null,
        name: null,
      },
      custom_fields: [],
      created_at: null,
      updated_at: null,
      created_by: {
        color: null,
        email: null,
        id: null,
        name: null,
        username: null,
      },
      updated_by: {
        color: null,
        email: null,
        id: null,
        name: null,
        username: null,
      },
      documents: [],
      surveys: [],
    };
  }

  public onActivityDefinitionSelected(
    activityDefinition: ActivityDefinitionResponse
  ) {
    if (this.isEditingActivityDefinition) {
      this.isEditingActivityDefinition = false;
    }
    this.isEditingActivityDefinition = true;
    this.activityDefinitionFormMode = ActivityDefinitionFormMode.edit;
    this.selectedActivityDefinition = activityDefinition;
  }

  public onCancelActivityDefinitionChange(didCancel: boolean) {
    console.log(
      "[NewCaseDefinitionComponent] chancel activity definition change received"
    );
    this.isEditingActivityDefinition = false;
    this.selectedActivityDefinition = null;
  }

  public onActivityDefinitionChanged(
    activityDefinition: ActivityDefinitionResponse
  ) {
    console.log(
      "[NewCaseDefinitionComponent] activity definition changed received"
    );
    console.log(JSON.stringify(activityDefinition));
    this.isEditingActivityDefinition = false;
    const idx = this.activityDefinitions.findIndex(
      (x) => x.id === activityDefinition.id
    );
    console.log(`idx = ${idx}`);
    if (idx !== -1) {
      this.activityDefinitions[idx] = activityDefinition;
    } else {
      this.activityDefinitions.push(activityDefinition);
    }
  }

  private getNewActivityDefinitionId(): number {
    const activityDefinitionIds = this.activityDefinitions.map((a) => {
      return a.id;
    });
    if (activityDefinitionIds.includes(-1)) {
      return Math.min(...activityDefinitionIds) - 1;
    } else {
      return -1;
    }
  }
}
