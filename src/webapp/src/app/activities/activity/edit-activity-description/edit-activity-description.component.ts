import { Component, EventEmitter, Input, OnInit, Output } from "@angular/core";
import {
  FormBuilder,
  FormControl,
  FormGroup,
  Validators,
} from "@angular/forms";

@Component({
  selector: "app-edit-activity-description",
  templateUrl: "./edit-activity-description.component.html",
  styleUrls: ["./edit-activity-description.component.css"],
})
export class EditActivityDescriptionComponent implements OnInit {
  @Input() activityID: number;
  @Input() activityDescription: string;
  @Output() descriptionChanged = new EventEmitter<string>();
  descriptionForm: FormGroup;
  amEditing = false;
  isSavingDescription = false;

  constructor(private formBuilder: FormBuilder) {
    this.descriptionForm = this.formBuilder.group({
      description: new FormControl(null, [Validators.minLength(6)]),
    });
  }

  ngOnInit() {
    this.descriptionForm.patchValue({ description: this.activityDescription });
  }

  public changeEditing(editing: boolean): void {
    this.amEditing = editing;
  }

  public onSaveDescription(): void {
    this.isSavingDescription = true;
    console.log(`[EditActivityDescriptionComponent] save description: ${this.descriptionForm.value.description}`);

    if (this.descriptionForm.invalid) {
      this.isSavingDescription = false;
    } else {
      console.log("[EditActivityDescriptionComponent] emitting description changed event");
      
      this.activityDescription = this.descriptionForm.value.description;

      this.descriptionChanged.emit(this.activityDescription);

      this.isSavingDescription = false;
      this.amEditing = false;
    }
  }
}
