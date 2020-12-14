import { Component, EventEmitter, Input, OnInit, Output } from "@angular/core";
import {
  FormBuilder,
  FormControl,
  FormGroup,
  Validators,
} from "@angular/forms";
import { Utils } from "app/_helpers";

@Component({
  selector: "app-edit-activity-name",
  templateUrl: "./edit-activity-name.component.html",
  styleUrls: ["./edit-activity-name.component.css"],
})
export class EditActivityNameComponent implements OnInit {
  @Input() activityID: number;
  @Input() activityName: string;
  @Output() nameChanged = new EventEmitter<string>();
  nameForm: FormGroup;
  amEditing: boolean = false;
  isSavingName: boolean = false;
  submitted: boolean = false;

  constructor(private formBuilder: FormBuilder, private utils: Utils) {
    this.nameForm = this.formBuilder.group({
      name: new FormControl(null, [
        Validators.required,
        Validators.minLength(6),
      ]),
    });
  }

  ngOnInit() {
    this.nameForm.patchValue({
      name: this.activityName,
    });
  }

  get form() {
    return this.nameForm.controls;
  }

  public changeEditing(editing: boolean): void {
    this.amEditing = editing;
  }

  public capitalizeInput(_str: string): string {
    return this.utils.generateCapitalizeString(_str);
  }

  public onSaveName(): void {
    this.isSavingName = true;
    this.submitted = true;
    console.log(`[EditActivityNameComponent] save name: ${this.nameForm.value.name}`);

    if (this.nameForm.invalid) {
      this.isSavingName = false;
    } else {
      console.log("[EditActivityNameComponent] emitting name changed event");
      
      this.activityName = this.nameForm.value.name;

      this.nameChanged.emit(this.activityName);

      this.isSavingName = false;
      this.amEditing = false;
    }
  }
}
