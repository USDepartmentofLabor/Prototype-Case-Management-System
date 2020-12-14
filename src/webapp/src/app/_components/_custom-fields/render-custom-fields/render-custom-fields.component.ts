import { Component, OnInit, Input, Output, EventEmitter } from "@angular/core";
import { Utils } from "app/_helpers";
import { CaseService } from "app/_services";
import { ActivityService } from "app/_services/activity.service";
import { Coordinate, CustomField, CustomFieldValue } from "../../../_models";

export enum CustomFieldContainerType {
  Case,
  Activity,
  JustSave,
}

@Component({
  selector: "render-custom-fields",
  templateUrl: "./render-custom-fields.component.html",
  styleUrls: ["./render-custom-fields.component.css"],
})
export class RenderCustomFieldsComponent implements OnInit {
  @Input() public containerId: number;
  @Input() containerType: CustomFieldContainerType =
    CustomFieldContainerType.Case;
  @Input() public customFieldsData: CustomField[];
  @Output() fieldsChanged = new EventEmitter<CustomField[]>();
  customFields: CustomField[] = [];
  latitude: number;
  longitude: number;

  constructor(
    private caseService: CaseService,
    private activityService: ActivityService,
    private utils: Utils
  ) {}

  ngOnInit() {
    this.customFields = this.customFieldsData;
    this.getLocation();
  }

  public onFieldChanged(field: CustomField): void {
    if (this.containerType === CustomFieldContainerType.Case) {
      this.caseService
        .updateCustomFieldValue(
          this.containerId,
          field.id.toString(),
          field.value,
          new Coordinate(this.latitude, this.longitude)
        )
        .subscribe((_) => {
          this.utils.generateSuccessToastrMsg("Successfully saved!", "");
        });
    } else if (this.containerType === CustomFieldContainerType.Activity) {
      this.activityService
        .updateCustomFieldValue(
          this.containerId,
          field.id.toString(),
          field.value,
          new Coordinate(this.latitude, this.longitude)
        )
        .subscribe((_) => {
          this.utils.generateSuccessToastrMsg("Successfully saved!", "");
        });
    } else if (this.containerType === CustomFieldContainerType.JustSave) {
      this.customFields = this.customFields.map((cf) =>
        cf.id === field.id ? field : cf
      );
      this.fieldsChanged.emit(this.customFields);
    } else {
      console.log("[RenderCustomFieldsComponent] unknown container type");
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
