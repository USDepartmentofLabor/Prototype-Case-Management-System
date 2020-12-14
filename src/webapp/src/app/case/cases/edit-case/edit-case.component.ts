import { Component, OnInit } from "@angular/core";
import { ActivatedRoute, Router } from "@angular/router";
import {
  NgbModal,
  NgbModalOptions,
  ModalDismissReasons,
} from "@ng-bootstrap/ng-bootstrap";
import {
  CaseService,
  AuthenticationService,
  UserService,
} from "../../../_services";
import { Utils } from "../../../_helpers";
import {
  FormBuilder,
  FormGroup,
  FormControl,
  Validators,
} from "@angular/forms";
import {
  UploadDocumentsModalComponent,
  DialogComponent,
  CustomFieldContainerType,
} from "../../../_components/index";
import * as _ from "lodash";
import {
  Case,
  CaseDefinition,
  CaseStatus,
  Note,
  SurveryResponse,
  Document,
  CustomField,
  DialogOptions,
  Survey,
  User,
  ActivityAPI,
  ActivitySummaryAPI,
} from "../../../_models";
import { Location } from "@angular/common";
import { update } from "lodash";
import { NewActivityModalComponent } from "app/activities/new-activity-modal/new-activity-modal.component";
import { ActivityService } from "app/_services/activity.service";

@Component({
  selector: "app-edit-case",
  templateUrl: "./edit-case.component.html",
  styleUrls: ["./edit-case.component.css"],
})
export class EditCaseComponent implements OnInit {
  case: Case;
  caseId: number;
  caseDefinitionID: number;
  isCaseLoading = false;
  caseMode: object;
  caseNameForm: FormGroup;
  caseDescForm: FormGroup;
  caseNoteForm: FormGroup;
  nameFieldEditMode = false;
  descFieldEditMode = false;
  statusFieldEditMode = false;
  caseNoteEditMode = false;
  isSavingName = false;
  isSavingDesc = false;
  isSavingStatus = false;
  isSavingCaseNote = false;
  submitted = false;
  currStatus: string;
  statuses: CaseStatus[];
  lookupData: object[] = JSON.parse(localStorage.getItem("lookupData"));
  currUser: User = this.authService.currentUserValue;
  currCaseName: string;
  newName = false;
  surveyViewMode = false;
  loadingSurveyResponses = false;
  surveyResponse: SurveryResponse;
  caseNotes: Note;
  customFields: CustomField[];
  caseDefinition: CaseDefinition;
  documents: Document[] = [];
  closeResult: string;
  primaryModalOptions: NgbModalOptions = {
    backdrop: "static",
  };
  latitude: number;
  longitude: number;
  assignableUsers: User[];
  assignedTo: { name: string; username: string; color: string } = {
    name: "Unassigned",
    username: "unassigned",
    color: "grey",
  };
  editingAssignee = false;
  customFieldContainerType: CustomFieldContainerType =
    CustomFieldContainerType.Case;

  constructor(
    private caseService: CaseService,
    private formBuilder: FormBuilder,
    public route: ActivatedRoute,
    private authService: AuthenticationService,
    private utils: Utils,
    private modalService: NgbModal,
    private _location: Location,
    private router: Router,
    private userService: UserService,
    private activityService: ActivityService
  ) {
    this.caseNameForm = this.formBuilder.group({
      name: new FormControl(null, [
        Validators.required,
        Validators.minLength(6),
      ]),
    });
    this.caseDescForm = this.formBuilder.group({
      description: new FormControl(null, [Validators.minLength(6)]),
    });
    this.caseNoteForm = this.formBuilder.group({
      note: new FormControl(null, [Validators.required]),
    });
  }

  ngOnInit() {
    this.route.params.subscribe((_params) => {
      this.caseId = _params.id;
      this.getCaseDetails(this.caseId);
      this.currUser.first_initial = this.utils.generateFirstInitalFromUserName(
        this.currUser.username
      );
      this.currUser.avatarBgColor = this.utils.generateRandomBackgroundColorClass();
    });
    this.getAssignableUsers();
    this.getLocation();
  }

  get form() {
    return this.caseNameForm.controls;
  }

  get noteForm() {
    return this.caseNoteForm.controls;
  }

  public back(): void {
    this._location.back();
  }

  public caseHasCustomFields() {
    return !_.isEmpty(this.customFields);
  }

  private getCaseDetails(caseId: number): void {
    this.isCaseLoading = true;
    this.caseService.getCase(caseId).subscribe(
      (data) => {
        this.case = data;
        this.documents = this.case.documents;
        this.currCaseName = this.case.name;
        this.customFields = this.case.custom_fields;
        this.generateStatusDropDownData();
        this.case.notes.map((note) => {
          note.created_by.first_initial = this.utils.generateFirstInitalFromUserName(
            note.created_by.username
          );
          note.created_by.avatarBgColor = note.created_by.color; //this.utils.generateRandomBackgroundColorClass();
        });
        this.case.notes = this.sortCaseNotes(this.case.notes);
        this.case.activities = this.sortActivities(this.case.activities);
        if (this.case.assigned_to) {
          this.assignedTo = {
            name: this.case.assigned_to.name,
            username: this.case.assigned_to.username,
            color: this.case.assigned_to.color,
          };
        } else {
          this.assignedTo = {
            name: "Unassigned",
            username: "unassigned",
            color: "grey",
          };
        }

        this.isCaseLoading = false;
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
        this.assignableUsers.push({
          id: 0,
          name: "Unassigned",
          username: "unassigned",
          color: "grey",
          email: null,
          role: null,
          location: null,
          last_seen_at: null,
          created_at: null,
          updated_at: null,
          confirmed: null,
          confirmed_at: null,
          firstInitial: "U",
          avatarBgColor: "grey",
        });
      },
      (error) => {
        console.log(error.message);
      }
    );
  }

  private deleteCase(_caseId: number): void {
    this.caseService.deleteCase(_caseId).subscribe((responseData) => {
      if (responseData) {
        this.utils.generateSuccessToastrMsg(
          "Document Successfully Deleted",
          ""
        );
        this.router.navigate(["/cases"]);
      }
    });
  }

  public deleteCaseDocument(_docId: number) {
    this.caseService.deleteFile(_docId).subscribe(
      (responseData) => {
        if (responseData) {
          this.getCaseDetails(this.caseId);
          this.utils.generateSuccessToastrMsg(
            "Document Successfully Deleted",
            ""
          );
        }
      },
      (error) => {
        console.log(error.message);
      }
    );
  }

  private deleteActivity(activityId: number): void {
    this.activityService
      .deleteActivity(activityId)
      .subscribe((responseData) => {
        if (responseData) {
          this.getCaseDetails(this.caseId);
          this.utils.generateSuccessToastrMsg(
            "Activity Successfully Deleted",
            ""
          );
        }
      });
  }

  public downloadCaseDocument(_docId: number) {
    this.caseService.downloadFile(_docId).subscribe(
      (responseData) => {
        if (responseData) {
          const _a = document.createElement("a");
          _a.href = responseData["url"];
          _a.setAttribute("target", "_blank");
          _a.click();
          _a.remove();
        }
      },
      (error) => {
        console.log("error accessing file url", error);
      }
    );
  }

  private generateStatusDropDownData(): object[] {
    this.statuses = this.lookupData["case_statuses"];
    this.statuses = this.statuses.filter(
      (status) => status["name"] !== this.case.status.name
    );
    return this.statuses;
  }

  public onDeleteActivity(activityID: number): void {
    console.log(`asking to delete activity id ${activityID}`);

    const dialogOptions: DialogOptions = {
      headerText: "Delete Activity",
      bodyText: "Are you sure you want to delete this Activity?",
      primaryActionText: "Yes, Delete",
      cancelBtnText: "Cancel",
      btnClass: "default",
      saveChanges: false,
    };

    const dialog = this.modalService.open(
      DialogComponent,
      this.primaryModalOptions
    );
    dialog.componentInstance.dialogOptions = dialogOptions;
    dialog.componentInstance.passEntry.subscribe((choice: boolean) => {
      if (choice) {
        this.deleteActivity(activityID);
      }
    });
  }

  public onUpdateStatus(status: CaseStatus) {
    const data = {
      status_id: status.id,
      latitude: this.latitude,
      longitude: this.longitude,
    };
    // status done need better check
    if (status.is_final && !this.checkAllDocsAreUploaded()) {
      this.utils.generateErrorToastrMsg(
        "All documents have not been uploaded",
        ""
      );
      return;
    } else {
      this.caseService.updateCase(this.caseId, data).subscribe(
        (responseData) => {
          this.case = responseData;
          this.documents = this.case.documents;
          this.currCaseName = this.case.name;
          this.customFields = this.case.custom_fields;
          this.generateStatusDropDownData();
          this.case.notes.map((note) => {
            note.created_by.first_initial = this.utils.generateFirstInitalFromUserName(
              note.created_by.username
            );
            note.created_by.avatarBgColor = note.created_by.color; //this.utils.generateRandomBackgroundColorClass();
          });
          this.case.notes = this.sortCaseNotes(this.case.notes);
          this.case.activities = this.sortActivities(this.case.activities);
          if (this.case.assigned_to) {
            this.assignedTo = {
              name: this.case.assigned_to.name,
              username: this.case.assigned_to.username,
              color: this.case.assigned_to.color,
            };
          } else {
            this.assignedTo = {
              name: "Unassigned",
              username: "unassigned",
              color: "grey",
            };
          }

          this.isCaseLoading = false;
          this.generateStatusDropDownData();
          this.utils.generateSuccessToastrMsg(
            "Status Successfully updated!",
            ""
          );
        },
        (error) => {
          console.log(error.message);
        }
      );
    }
  }

  public onEditAssignee(): void {
    this.editingAssignee = true;
  }

  public onChangeAssignee(user: User): void {
    this.assignedTo = {
      name: user.name,
      username: user.username,
      color: user.color,
    };
    this.editingAssignee = false;

    // need to update assignee in three cases
    // 1. The case was unassigned and is being assigned
    // 2. The case was assigned and is not being assigned to a different user
    // 3. The case was assigned and is being unassigned
    if (
      (!this.case.assigned_to && user.id !== 0) ||
      (this.case.assigned_to && user.id !== this.case.assigned_to.id) ||
      (this.case.assigned_to && user.id === 0)
    ) {
      console.log("different assignee");
      let updateUserId: number = null;
      if (user.id !== 0) {
        updateUserId = user.id;
      }
      const data = {
        assigned_to_id: updateUserId,
      };
      this.caseService.updateCase(this.caseId, data).subscribe(
        (responseData) => {
          this.case = responseData;
          this.documents = this.case.documents;
          this.currCaseName = this.case.name;
          this.customFields = this.case.custom_fields;
          this.generateStatusDropDownData();
          this.case.notes.map((note) => {
            note.created_by.first_initial = this.utils.generateFirstInitalFromUserName(
              note.created_by.username
            );
            note.created_by.avatarBgColor = note.created_by.color; //this.utils.generateRandomBackgroundColorClass();
          });
          this.case.notes = this.sortCaseNotes(this.case.notes);
          this.case.activities = this.sortActivities(this.case.activities);
          if (this.case.assigned_to) {
            this.assignedTo = {
              name: this.case.assigned_to.name,
              username: this.case.assigned_to.username,
              color: this.case.assigned_to.color,
            };
          } else {
            this.assignedTo = {
              name: "Unassigned",
              username: "unassigned",
              color: "grey",
            };
          }

          this.isCaseLoading = false;
          this.generateStatusDropDownData();
          this.utils.generateSuccessToastrMsg(
            "Assignee successfully updated!",
            ""
          );
        },
        (error) => {
          console.log(error.message);
        }
      );
    }
  }

  public onCancelAllEdits(): void {
    this.editingAssignee = false;
  }

  private checkAllDocsAreUploaded() {
    const docNotUploaded = this.documents.find(
      (document) => document.is_required && document.remote_filename == null
    );
    return _.isUndefined(docNotUploaded) ? true : false;
  }

  public showResponses(_survey: Survey) {
    this.router.navigate([`cases/${this.caseId}/form-response`, _survey.id]);
  }

  public showSurvey(_survey: Survey) {
    this.router.navigate([`cases/${this.caseId}/form`, _survey.id]);
  }

  // change the mode and update the patch value
  public onChangeMode(_fieldValue: string, _element: string): void {
    switch (_element) {
      case "name":
        this.nameFieldEditMode = !this.nameFieldEditMode;
        this.setNameVal(_fieldValue);
        break;
      case "desc":
        this.descFieldEditMode = !this.descFieldEditMode;
        this.setDescVal(_fieldValue);
        break;
      case "status":
        this.statusFieldEditMode = true;
        break;
      case "note":
        this.caseNoteEditMode = !this.caseNoteEditMode;
        break;
      default:
    }
  }

  public onCaseUpdate(_element: string): void {
    switch (_element) {
      case "name":
        this.saveNameVal();
        break;
      case "desc":
        this.saveDescVal();
        break;
      case "status":
        this.statusFieldEditMode = true;
        break;
      case "note":
        this.saveCaseNoteVal();
        break;
      default:
    }
  }

  public openNewActivityDialog(): void {
    const modalRef = this.modalService.open(
      NewActivityModalComponent,
      this.primaryModalOptions
    );
    modalRef.componentInstance.caseId = this.caseId;
    modalRef.componentInstance.caseDefinitionId = this.case.case_definition.id;
    modalRef.result.then(
      (result) => {
        result ? this.getCaseDetails(this.caseId) : console.log("No new obj");
      },
      (reason) => {
        this.closeResult = `Dismissed ${this.getDismissReason(reason)}`;
      }
    );
  }

  private setNameVal(_nameValue: string): void {
    this.caseNameForm.patchValue({
      name: _nameValue,
    });
  }

  private setDescVal(_descValue: string): void {
    this.caseDescForm.patchValue({
      description: _descValue,
    });
  }

  private saveNameVal(): void {
    this.isSavingName = true;
    this.submitted = true;

    const data = {
      name: this.caseNameForm.value.name,
      latitude: this.latitude,
      longitude: this.longitude,
    };

    if (this.caseNameForm.invalid) {
      this.isSavingName = false;
    } else {
      this.caseService.updateCase(this.caseId, data).subscribe(
        (responseData) => {
          this.case = responseData;
          this.case.name = this.case.name;
          this.documents = this.case.documents;
          this.currCaseName = this.case.name;
          this.customFields = this.case.custom_fields;
          this.generateStatusDropDownData();
          this.case.notes.map((note) => {
            note.created_by.first_initial = this.utils.generateFirstInitalFromUserName(
              note.created_by.username
            );
            note.created_by.avatarBgColor = note.created_by.color; //this.utils.generateRandomBackgroundColorClass();
          });
          this.case.notes = this.sortCaseNotes(this.case.notes);
          this.case.activities = this.sortActivities(this.case.activities);
          if (this.case.assigned_to) {
            this.assignedTo = {
              name: this.case.assigned_to.name,
              username: this.case.assigned_to.username,
              color: this.case.assigned_to.color,
            };
          } else {
            this.assignedTo = {
              name: "Unassigned",
              username: "unassigned",
              color: "grey",
            };
          }

          this.isCaseLoading = false;
          this.utils.generateSuccessToastrMsg(
            "Case Name Successfully updated!",
            ""
          );
          this.isSavingName = false;
          this.nameFieldEditMode = false;
        },
        (error) => {
          console.log(error.message);
        }
      );
    }
  }

  private saveDescVal(): void {
    this.isSavingDesc = true;
    this.submitted = true;

    const data = {
      description: this.caseDescForm.value.description,
      latitude: this.latitude,
      longitude: this.longitude,
    };

    if (this.caseDescForm.invalid) {
      this.isSavingDesc = false;
    } else {
      this.caseService.updateCase(this.caseId, data).subscribe(
        (responseData) => {
          this.case = responseData;
          this.case.description = this.case.description;
          this.documents = this.case.documents;
          this.currCaseName = this.case.name;
          this.customFields = this.case.custom_fields;
          this.generateStatusDropDownData();
          this.case.notes.map((note) => {
            note.created_by.first_initial = this.utils.generateFirstInitalFromUserName(
              note.created_by.username
            );
            note.created_by.avatarBgColor = note.created_by.color; //this.utils.generateRandomBackgroundColorClass();
          });
          this.case.notes = this.sortCaseNotes(this.case.notes);
          this.case.activities = this.sortActivities(this.case.activities);
          if (this.case.assigned_to) {
            this.assignedTo = {
              name: this.case.assigned_to.name,
              username: this.case.assigned_to.username,
              color: this.case.assigned_to.color,
            };
          } else {
            this.assignedTo = {
              name: "Unassigned",
              username: "unassigned",
              color: "grey",
            };
          }

          this.isCaseLoading = false;
          this.utils.generateSuccessToastrMsg(
            "Case Description Successfully updated!",
            ""
          );
          this.isSavingDesc = false;
          this.descFieldEditMode = false;
        },
        (error) => {
          console.log(error.message);
        }
      );
    }
  }

  onCaseNoteAdded(note: string): void {
    console.log(`[EditCaseComponent] received new note = ${note}`);

    const data = {
      case_id: this.caseId,
      note: note,
    };

    this.caseService.saveCaseNote(data).subscribe(
      (responseData) => {
        this.utils.generateSuccessToastrMsg("Note successfully added", "");
        this.getCaseDetails(this.caseId);
      },
      (error) => {
        console.log(`[EditCaseComponent] error adding note : error.message`);
        this.utils.generateErrorToastrMsg(error.message, "Error saving note");
      }
    );
  }

  private saveCaseNoteVal(): void {
    this.isSavingCaseNote = true;
    this.submitted = true;

    const data = {
      case_id: this.caseId,
      note: this.caseNoteForm.value.note,
    };

    if (this.caseNoteForm.invalid) {
      this.isSavingCaseNote = false;
    } else {
      this.caseService.saveCaseNote(data).subscribe(
        (responseData) => {
          this.caseNotes = responseData;
          this.case.notes.push(this.caseNotes);
          this.case.notes.map((note) => {
            note.created_by.first_initial = this.utils.generateFirstInitalFromUserName(
              note.created_by.username
            );
            note.created_by.avatarBgColor = this.utils.generateRandomBackgroundColorClass();
          });
          this.case.notes = this.sortCaseNotes(this.case.notes);
          this.case.activities = this.sortActivities(this.case.activities);
          this.utils.generateSuccessToastrMsg(
            "Case Note Succssfully updated!",
            ""
          );
          this.isSavingCaseNote = false;
          this.caseNoteEditMode = false;
        },
        (error) => {
          console.log(error.message);
        }
      );
    }
  }

  // pull out and place into helper class
  private sortCaseNotes(_notes: Note[]) {
    return (_notes = _notes.sort(
      (_noteA, _noteB) =>
        Date.parse(_noteB["created_at"]) - Date.parse(_noteA["created_at"])
    ));
  }

  private sortActivities(activities: ActivitySummaryAPI[]) {
    return (activities = activities.sort(
      (activity1, activity2) =>
        Date.parse(activity1["created_at"]) -
        Date.parse(activity2["created_at"])
    ));
  }

  public capitalizeInput(_str: string): string {
    return this.utils.generateCapitalizeString(_str);
  }

  public formatNoteCreatedAtDate(_date: string): string {
    return this.utils.generateDateFormatFromNow(_date);
  }

  public caseHasDocuments(): boolean {
    return _.isEmpty(this.documents);
  }

  public generateDocumentRequiredTxt(_option: boolean): string {
    return _option === true ? " -(Required)" : "";
  }

  public openFileUploadModal(_docId: number, _type: string): void {
    const modalOptions = {
      dialogHeaderTxt: "Upload a file",
      caseId: this.caseId,
      docId: _type === "document" ? _docId : "",
      uploadType: _type,
    };

    const modalRef = this.modalService.open(
      UploadDocumentsModalComponent,
      this.primaryModalOptions
    );
    modalRef.componentInstance.modalOptions = modalOptions;
    modalRef.result.then(
      (result) => {
        result ? this.getCaseDetails(this.caseId) : console.log("No new obj");
      },
      (reason) => {
        this.closeResult = `Dismissed ${this.getDismissReason(reason)}`;
      }
    );
  }

  public openDeleteDialogPrompt(): void {
    const dialogOptions: DialogOptions = {
      headerText: "Delete Case",
      bodyText: "Are you sure you want to delete this Case?",
      primaryActionText: "Yes, Delete",
      cancelBtnText: "Cancel",
      btnClass: "default",
      saveChanges: false,
    };

    const dialog = this.modalService.open(
      DialogComponent,
      this.primaryModalOptions
    );
    dialog.componentInstance.dialogOptions = dialogOptions;
    dialog.componentInstance.passEntry.subscribe((choice: boolean) => {
      if (choice) {
        this.deleteCase(this.caseId);
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
