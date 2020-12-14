import { Component, OnInit } from "@angular/core";
import {
  FormBuilder,
  FormGroup,
  FormControl,
  Validators,
} from "@angular/forms";
import { Utils } from "../../../_helpers";
import { Router } from "@angular/router";
import { CaseService, UserService } from "../../../_services";
import { Case, CustomField, User } from "../../../_models";
import { Location } from "@angular/common";
import { CaseDefinition } from "../../../_models";
import * as _ from "lodash";
import { CustomFieldContainerType } from "app/_components/_custom-fields/render-custom-fields/render-custom-fields.component";

@Component({
  selector: "app-new-case",
  templateUrl: "./new-case.component.html",
  styleUrls: ["./new-case.component.css"],
})
export class NewCaseComponent implements OnInit {
  newCaseForm: FormGroup;
  caseDefinitions: CaseDefinition[];
  assignableUsers: User[];
  errorMsg: string;
  submitted = false;
  isSavingNewCase = false;
  isCaseDefinitionsLoading = false;
  latitude: number;
  longitude: number;
  customFields: CustomField[] = [];
  areCustomFieldsLoading = false;
  customFieldContainerType: CustomFieldContainerType =
    CustomFieldContainerType.JustSave;

  constructor(
    private formBuilder: FormBuilder,
    private caseService: CaseService,
    private _location: Location,
    private utils: Utils,
    private router: Router,
    private userService: UserService
  ) {
    this.newCaseForm = this.formBuilder.group({
      name: new FormControl(null, [
        Validators.required,
        Validators.minLength(6),
      ]),
      description: new FormControl(null, []),
      assignedTo: new FormControl(null, []),
      note: new FormControl(null, []),
      caseDefinitionRadioGroup: new FormControl(null, [Validators.required]),
    });
  }

  ngOnInit() {
    this.getAllCaseDefinitions();
    this.getAssignableUsers();
    this.getLocation();
  }

  // convenience getter for easy access to form fields
  get form() {
    return this.newCaseForm.controls;
  }

  public back(): void {
    this._location.back();
  }

  public capitalizeInput(_str: string): string {
    return this.utils.generateCapitalizeString(_str);
  }

  public getAllCaseDefinitions(): void {
    this.isCaseDefinitionsLoading = true;
    this.caseService.getAllCaseDefinitions().subscribe(
      (data) => {
        this.caseDefinitions = data;
        this.isCaseDefinitionsLoading = false;
      },
      (error) => {
        console.log(error.message);
      }
    );
  }

  public getAssignableUsers(): void {
    this.userService.getAllUsers().subscribe(
      (data) => {
        this.assignableUsers = [];
        data.forEach((user) => {
          if (this.userService.isUserAssignable(user)) {
            return this.assignableUsers.push(user);
          }
        });
      },
      (error) => {
        console.log(error.message);
      }
    );
  }

  public onCreateNewCase(): void {
    console.log("creating case");
    console.log(`${JSON.stringify(this.customFields)}`);
    console.log(`this.newCaseForm.invalid: ${this.newCaseForm.invalid}`);

    this.isSavingNewCase = true;
    this.submitted = true;

    const caseDefinitionId = this.newCaseForm.value.caseDefinitionRadioGroup;
    const newCaseData: Case = {
      name: this.newCaseForm.value.name,
      description: this.newCaseForm.value.description,
      notes: [this.newCaseForm.value.note],
    };
    const postData = {
      name: newCaseData.name,
      description: newCaseData.description,
      notes: newCaseData.notes,
      latitude: this.latitude,
      longitude: this.longitude,
      assigned_to_id: this.newCaseForm.value.assignedTo
        ? this.newCaseForm.value.assignedTo.id
        : null,
      custom_fields: this.customFields.map((cf) => {
        return {
          name: cf.name,
          field_type: cf.field_type,
          selections: cf.selections,
          validation_rules: cf.selections,
          case_definition_custom_field_id: cf.id,
          custom_section_id: null,
          help_text: cf.help_text,
          sort_order: cf.sort_order,
          value: cf.value,
          model_type: 'Case'
        };
      }),
    };

    if (this.newCaseForm.invalid) {
      this.isSavingNewCase = false;
    } else {
      this.caseService.createNewCase(caseDefinitionId, postData).subscribe(
        (newCase) => {
          this.utils.generateSuccessToastrMsg(
            "New Case successfully created!",
            ""
          );
          this.onSuccess(newCase.id);
        },
        (error) => {
          this.errorMsg = error.message;
          this.isSavingNewCase = false;
        }
      );
    }
  }

  private onSuccess(id: number): void {
    this.onCancel();

    setTimeout(() => {
      this.router.navigate([`/cases/${id}`]);
    }, 2500);
  }

  public onCancel(): void {
    if (this.isSavingNewCase) {
      this.isSavingNewCase = false;
    }
    this.newCaseForm.reset();
    this.submitted = false;
    this.errorMsg = null;
    this.back();
  }

  public generateSaveNewCaseBtnTxt(): string {
    return this.isSavingNewCase ? "Saving New Case..." : "Save New Case";
  }

  public caseDefinitionSelected(id: number, isChecked: boolean) {
    this.areCustomFieldsLoading = true;

    console.log(`case id: ${id}, selected: ${isChecked}`);

    this.caseService.getCaseDefinitionsCustomFields(id).subscribe(
      (customFields) => {
        this.customFields = customFields;
        this.areCustomFieldsLoading = false;
      },
      (error) => {
        console.log(error.message);
        this.areCustomFieldsLoading = false;
      }
    );
  }

  public onCustomFieldsChanged(customFields: CustomField[]) {
    console.log("custom fields changed");
    this.customFields = customFields;
  }

  private getLocation(): void {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          this.latitude = position.coords.latitude;
          this.longitude = position.coords.longitude;
        },
        (err) => {
          this.latitude = null;
          this.longitude = null;
          console.log(`ERROR(${err.code}): ${err.message}`);
        }
      );
    } else {
      this.latitude = null;
      this.longitude = null;
      console.log("No support for geolocation");
    }
  }
}
