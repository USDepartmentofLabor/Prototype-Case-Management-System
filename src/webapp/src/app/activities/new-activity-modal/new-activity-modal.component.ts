import { Component, Input, OnInit } from "@angular/core";
import { NgbActiveModal } from "@ng-bootstrap/ng-bootstrap";
import { ActivityService } from "app/_services/activity.service";
import {
  FormBuilder,
  FormControl,
  FormGroup,
  Validators,
} from "@angular/forms";
import { PostActivity } from "app/_models/activity";
import { Utils } from 'app/_helpers';

@Component({
  selector: "app-new-activity-modal",
  templateUrl: "./new-activity-modal.component.html",
  styleUrls: ["./new-activity-modal.component.css"],
})
export class NewActivityModalComponent implements OnInit {
  @Input() caseId: number;
  @Input() caseDefinitionId: number;
  activityDefinitions: { id: number; name: string }[] = [];
  newActivityForm: FormGroup;
  errorMsg: string;
  isActivityDefinitionsLoading = false;
  submitted = false;
  latitude: number;
  longitude: number;

  constructor(
    public activeModal: NgbActiveModal,
    public activityService: ActivityService,
    private formBuilder: FormBuilder,
    private utils: Utils
  ) {
    this.newActivityForm = this.formBuilder.group({
      name: new FormControl(null, [
        Validators.required,
        Validators.minLength(6),
      ]),
      description: new FormControl(null, []),
      note: new FormControl(null, []),
      activityDefinitionRadioGroup: new FormControl(null, [
        Validators.required,
      ]),
    });
  }

  ngOnInit() {
    this.getActivityDefinitions();
    this.getLocation();
  }

  get form() {
    return this.newActivityForm.controls;
  }

  public onCreateNewActivity() {
    console.log("clicked onSaveActivity()");
    this.submitted = true;

    if (this.newActivityForm.invalid) {
      console.log("form invalid");
    } else {
      const data = new PostActivity(
        this.newActivityForm.value.activityDefinitionRadioGroup,
        this.caseId,
        this.newActivityForm.value.name,
        this.newActivityForm.value.description,
        [this.newActivityForm.value.note],
        this.latitude,
        this.longitude
      );

      console.log(`post data = ${JSON.stringify(data)}`);
      this.activityService.createActivity(data).subscribe(
        () => {
          this.utils.generateSuccessToastrMsg(
            "Activity successfully created.",
            ""
          );
          this.activeModal.close("create-activity");
        },
        (error) => {
          this.errorMsg = error.message;
          console.log(error.message);
        }
      );
    }
  }

  private getActivityDefinitions(): void {
    this.isActivityDefinitionsLoading = true;
    this.activityService.getAllActivityDefinitions().subscribe(
      (activityDefinitions) => {
        this.activityDefinitions = []
        activityDefinitions.forEach((ad) => {
          if (ad.case_definition.id === this.caseDefinitionId) {
            this.activityDefinitions.push({ id: ad.id, name: ad.name });
          }
        });
        this.isActivityDefinitionsLoading = false;
      },
      (error) => {
        console.log(error.message);
      }
    );
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
