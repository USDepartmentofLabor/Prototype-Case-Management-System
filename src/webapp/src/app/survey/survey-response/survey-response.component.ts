import { Component, OnInit } from "@angular/core";
import { Utils } from "../../_helpers";
import { SurveyService, CaseService } from "../../_services";
import { ActivatedRoute, Router } from "@angular/router";
import { NgbModal } from "@ng-bootstrap/ng-bootstrap";
import { DialogComponent } from "../../_components";
import { Observable, Subject } from "rxjs";
import { DomSanitizer } from "@angular/platform-browser";
import { Location } from "@angular/common";
import { ActivityAPI, DialogOptions } from "../../_models";
import * as _ from "lodash";
import { ActivityService } from "app/_services/activity.service";

interface CaseSurveyResponse {
  survey_id: number;
  case_id: string | number;
}

enum ResponseSourceType {
  Unknown,
  Case,
  Activity,
}

@Component({
  selector: "app-survey-response",
  templateUrl: "./survey-response.component.html",
  styleUrls: ["./survey-response.component.css"],
})
export class SurveyResponseComponent implements OnInit {
  surveyId: number;
  caseID: string;
  activityID: number;
  ResponseSourceType = ResponseSourceType;
  responseSourceType: ResponseSourceType = ResponseSourceType.Unknown;
  surveyResponse: object[];
  showSurvey = false;
  response: object[];
  responseId: number;
  closeResult: string;
  updatedResponseData: string;
  json: object[];
  fileUrl: object;
  fileName: string;
  navigateAway: Subject<boolean> = new Subject<boolean>();
  currSelectedResponse: number = null;
  latitude: number;
  longitude: number;
  survey: any;
  case: any;
  activity: ActivityAPI;
  gotSurvey = false;
  gotCase = false;
  gotActivity = false;
  displayBreadcrumb = false;

  constructor(
    private route: ActivatedRoute,
    private modalService: NgbModal,
    private surveyService: SurveyService,
    private caseService: CaseService,
    private activityService: ActivityService,
    private utils: Utils,
    private sanitizer: DomSanitizer,
    private _location: Location,
    private router: Router
  ) {}

  ngOnInit() {
    this.route.params.subscribe((params) => {
      this.surveyId = params.id;
      this.getSurvey();
    });

    this.parseUrl(window.location.pathname);
    if (this.responseSourceType === ResponseSourceType.Case) {
      this.getCaseSurveyResponses({
        survey_id: this.surveyId,
        case_id: this.caseID,
      });
      this.getCase(+this.caseID);
      this.gotActivity = true; // set this true here because we don't actually need the activity
    } else if (this.responseSourceType === ResponseSourceType.Activity) {
      this.getActivitySurveyResponses();
      this.getActivity(this.activityID);
      this.gotCase = true; // set this true here because we don't actually need the case
    } else {
      // in this case we don't need a case or activity for the breadcrumb, so
      // set this two to true
      this.gotActivity = true;
      this.gotCase = true;
      this.getSurveyResponses(this.surveyId);
      this.setDisplayBreadcrumb();
    }
    this.getLocation();
  }

  public back(): void {
    this._location.back();
  }

  public getCaseDefinitionId(): number {
    if (this.responseSourceType === ResponseSourceType.Activity) {
      return this.activity.case.definition.id;
    } else if (this.responseSourceType === ResponseSourceType.Case) {
      return this.case.case_definition.id;
    } else {
      return 0;
    }
  }

  private getCaseSurveyResponses(
    _caseSurveyResponse: CaseSurveyResponse
  ): void {
    this.caseService.getCaseSurveyResponses(_caseSurveyResponse).subscribe(
      (data) => {
        this.surveyResponse = data;
        this.generateResponseDownloadFile();
      },
      (error) => {
        console.log(error.message);
      }
    );
  }

  private getActivitySurveyResponses(): void {
    this.activityService
      .getActivitySurveyResponses(this.activityID, this.surveyId)
      .subscribe(
        (data) => {
          this.surveyResponse = data;
          this.generateResponseDownloadFile();
        },
        (error) => {
          console.log(error.message);
        }
      );
  }

  private getSurveyResponses(_surveyId: number): void {
    this.surveyService.getSurveyResponses(_surveyId).subscribe(
      (data) => {
        this.surveyResponse = data;
        this.generateResponseDownloadFile();
      },
      (error) => {
        console.log(error.message);
      }
    );
  }

  private getSurvey(): void {
    this.surveyService.getSurvey(this.surveyId).subscribe(data => {
      this.survey = data;
      this.gotSurvey = true;
      this.setDisplayBreadcrumb();
    }, error => {
      console.log(`[SurveyResponseComponent] error getting survey: ${error.message}`);
    })
  }

  private getActivity(activityID: number): void {
    this.activityService.getActivity(activityID).subscribe(
      (data) => {
        this.activity = data;
        this.gotActivity = true;
        this.setDisplayBreadcrumb();
      },
      (error) => {
        console.log(
          `[SurveyResponseComponent] error getting activity: ${error.message}`
        );
      }
    );
  }

  private getCase(caseID: number): void {
    console.log(
      `[SurveyResponseComponent] getting case: case id = ${caseID}`
    );

    this.caseService.getCase(caseID).subscribe((data) => {
      this.case = data;
      this.gotCase = true;
      this.setDisplayBreadcrumb();
    }, (error) => {
      console.log(
        `[SurveyResponseComponent] error getting case: ${error.message}`
      );
    });
  }

  public formatDateFromNow(_createdAtDate: string): string {
    return _createdAtDate
      ? this.utils.generateQueueDateFormat(_createdAtDate)
      : "";
  }

  public formatDate(_updatedAtDate: string): string {
    return _updatedAtDate
      ? this.utils.generateDateFormatFromNow(_updatedAtDate)
      : "";
  }

  private parseUrl(currentUrl: string): void {
    const whichResponseUrl = currentUrl.split("/")[1];
    if (whichResponseUrl === "cases") {
      this.caseID = currentUrl.split("/")[2];
      this.activityID = null;
      this.responseSourceType = ResponseSourceType.Case;
    } else if (whichResponseUrl === "activities") {
      this.caseID = null;
      this.activityID = +currentUrl.split("/")[2];
      this.responseSourceType = ResponseSourceType.Activity;
    } else {
      this.caseID = null;
      this.activityID = null;
      this.responseSourceType = ResponseSourceType.Unknown;
    }
  }

  public showResponse(_selection: number, _id: number): void {
    this.currSelectedResponse = _selection;
    this.showSurvey = false;
    this.responseId = _id;
    this.surveyService
      .getSurveyResponse(this.surveyId, this.responseId)
      .subscribe(
        (data) => {
          this.json = data.survey_structure;
          this.response = data.structure;
          this.showSurvey = true;
        },
        (error) => {
          console.log(error.message);
        }
      );
  }

  public setDisplayBreadcrumb(): boolean {
    return this.displayBreadcrumb = this.gotSurvey && this.gotCase && this.gotCase;
  }

  public closeResponse(): void {
    this.currSelectedResponse = null;
    this.showSurvey = false;
  }

  private setSourceType(): string {
    return this.router.url.indexOf("case") !== -1 ? "Case" : "Standalone";
  }

  public updateSurveyResponse(_surveyStructure: object[]): void {
    const responseData = {
      surveyId: this.surveyId,
      responseId: this.responseId,
      structure: _surveyStructure,
      latitude: this.latitude,
      longitude: this.longitude,
    };

    console.log(
      `SurveyResponseComponent.updateSurveyResponse() : responseDate = ${JSON.stringify(
        responseData
      )}`
    );

    this.surveyService.updateSurveyResponse(responseData).subscribe(
      () => {
        if (localStorage.hasOwnProperty("surveyResponseData")) {
          localStorage.removeItem("surveyResponseData");
        }
        this.utils.generateSuccessToastrMsg(
          "Survey response was successfully updated!"
        );
        this.getSurveyResponses(this.surveyId);
        this.showSurvey = false;
        this.navigateAway.next(true);
      },
      (error) => {
        this.utils.generateErrorToastrMsg(error.message);
        this.navigateAway.next(false);
      }
    );
  }

  canDeactivate(): boolean | Observable<boolean> | Promise<boolean> {
    this.updatedResponseData = localStorage.getItem("surveyResponseData");

    if (!_.isEmpty(this.updatedResponseData)) {
      this.openSaveDialog();
      return this.navigateAway;
    } else {
      return true;
    }
  }

  private generateResponseDownloadFile(): void {
    const data = JSON.stringify(this.surveyResponse) || "No survey data";
    const blob = new Blob([data], { type: "text/json;charset=UTF-8" });

    this.fileName = `Survey-Response-${this.utils.generateCurrentDate()}.json`;
    this.fileUrl = this.sanitizer.bypassSecurityTrustResourceUrl(
      window.URL.createObjectURL(blob)
    );
  }

  private openSaveDialog(): void {
    const dialogOptions: DialogOptions = {
      headerText: "Confirm Navigation",
      bodyText: `You have unsaved changes that will be lost if you decide to continue. 
      Are you sure you want to leave this page?`,
      primaryActionText: "Save, And Continue",
      cancelBtnText: "Yes, Exit",
      btnClass: "success",
      saveChanges: false,
    };

    const dialog = this.modalService.open(DialogComponent);
    dialog.componentInstance.dialogOptions = dialogOptions;
    dialog.componentInstance.passEntry.subscribe((choice: boolean) => {
      if (choice) {
        this.updateSurveyResponse(JSON.parse(this.updatedResponseData));
      } else {
        this.navigateAway.next(true);
      }
      localStorage.removeItem("surveyResponseData");
    });
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
