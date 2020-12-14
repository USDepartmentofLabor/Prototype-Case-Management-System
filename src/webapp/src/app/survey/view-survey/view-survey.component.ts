import { Component, OnInit } from "@angular/core";
import { ActivatedRoute, Router } from "@angular/router";
import { CaseService, SurveyService } from "../../_services";
import { ActivityAPI, Survey } from "../../_models";
import { Location } from "@angular/common";
import { ActivityService } from "app/_services/activity.service";

@Component({
  selector: "app-view-survey",
  templateUrl: "./view-survey.component.html",
  styleUrls: ["./view-survey.component.css"],
  providers: [SurveyService],
})
export class ViewSurveyComponent implements OnInit {
  surveyId: number;
  title: string;
  json: object = {};
  isSurveyLoaded = false;
  sub: any;
  latitude: number;
  longitude: number;
  sourceId: number;
  sourceType = "Standalone";
  case: any;
  activity: ActivityAPI;
  showBreadcrumb = false;

  constructor(
    private route: ActivatedRoute,
    private surveyService: SurveyService,
    private caseService: CaseService,
    private activityService: ActivityService,
    private _location: Location,
    private router: Router
  ) {}

  ngOnInit() {
    this.sub = this.route.params.subscribe((params) => {
      console.log(
        `[ViewSurveyComponent.ngOnInit()] params = ${JSON.stringify(params)}`
      );
      this.surveyId = params.id;
      this.getSurveyData();
    });

    this.sourceId = +this.route.parent.snapshot.paramMap.get("id");
    console.log(`[ViewSurveyComponent.ngOnInit()] parentID = ${this.sourceId}`);

    const responseUrlParts = this.router.url.split("/");
    const whichResponseUrl = responseUrlParts[1];
    if (whichResponseUrl === "cases") {
      this.sourceType = "Case";
      this.getCase(+responseUrlParts[2]);
    } else if (whichResponseUrl === "activities") {
      this.sourceType = "Activity";
      this.getActivity(+responseUrlParts[2]);
    } else {
      this.sourceType = "Standalone";
      this.showBreadcrumb = true;
    }

    this.getLocation();
  }

  public setSourceType(): string {
    return this.router.url.indexOf("cases") !== -1 ? "Case" : "Standalone";
  }

  public getSurveyData() {
    this.surveyService.getSurvey(this.surveyId).subscribe((data) => {
      this.title = data.name;
      this.json = data["structure"];
      this.isSurveyLoaded = true;
    });
  }

  public back(): void {
    this._location.back();
  }

  public sendData(_survey: Survey) {
    const surveyData = {
      survey_id: this.surveyId,
      structure: _survey,
      case_id: this.sourceType === "Case" ? this.sourceId : null,
      activity_id: this.sourceType === "Activity" ? this.sourceId : null,
      source_type: this.sourceType,
      latitude: this.latitude,
      longitude: this.longitude,
    };

    this.surveyService.saveSurveyResponse(surveyData).subscribe((data) => {
      localStorage.removeItem("surveyResponseData");
      setTimeout(() => {
        // this._location.back();
        if (this.sourceType === "Case") {
          this.router.navigate(['/cases', this.case.id]);
        } else if (this.sourceType === 'Activity') {
          this.router.navigate(['/activities', this.activity.id]);
        } else {
          this.router.navigate(['/forms']);
        }
      }, 2500);
    });
  }

  private getActivity(activityID: number): void {
    this.activityService.getActivity(activityID).subscribe(
      (data) => {
        this.activity = data;
        this.showBreadcrumb = true;
      },
      (error) => {
        console.log(
          `[ViewSurveyComponent] error getting activity: ${error.message}`
        );
      }
    );
  }

  private getCase(caseID: number): void {
    console.log(
      `[ViewSurveyComponent] getting case: case id = ${caseID}`
    );

    this.caseService.getCase(caseID).subscribe((data) => {
      this.case = data;
      this.showBreadcrumb = true;
    }, (error) => {
      console.log(
        `[ViewSurveyComponent] error getting case: ${error.message}`
      );
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

  ngOnDestroy() {
    this.sub.unsubscribe();
  }
}
