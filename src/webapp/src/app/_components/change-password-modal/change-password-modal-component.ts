import { Component, Output, EventEmitter } from "@angular/core";
import { NgbActiveModal } from "@ng-bootstrap/ng-bootstrap";
import { FormBuilder, FormGroup, Validators } from "@angular/forms";
import { pwdMatchValidator } from "../../_helpers";

@Component({
  selector: "app-change-password-modal-component",
  templateUrl: "./change-password-modal-component.html",
  styleUrls: ["./change-password-modal-component.css"],
})
export class ChangePasswordModalComponent {
  @Output() passedData: EventEmitter<EventListener> = new EventEmitter();
  userChangePasswordForm: FormGroup;
  changePasswordBtnTxt: string;
  isSavingPasswordData: boolean;
  fieldTextType: boolean;
  repeatFieldTextType: boolean;
  submitted: boolean = false;

  constructor(
    public activeModal: NgbActiveModal,
    private formBuilder: FormBuilder
  ) {
    this.userChangePasswordForm = this.formBuilder.group(
      {
        newPassword: [
          "",
          [
            Validators.required,
            Validators.minLength(10),
            Validators.maxLength(64),
          ],
        ],
        confirmPassword: ["", [Validators.required]],
      },
      {
        validator: pwdMatchValidator("newPassword", "confirmPassword"),
      }
    );
  }

  // convenience getter for easy access to form fields
  get form() {
    return this.userChangePasswordForm.controls;
  }

  public generateChangePasswordBtnTxt(): string {
    return this.isSavingPasswordData ? "Saving password..." : "Change Password";
  }

  public toggleFieldTextType(): void {
    this.fieldTextType = !this.fieldTextType;
  }

  public toggleRepeatFieldTextType(): void {
    this.repeatFieldTextType = !this.repeatFieldTextType;
  }

  public submit(): void {
    this.isSavingPasswordData = true;
    this.submitted = true;

    if (this.userChangePasswordForm.invalid) {
      this.isSavingPasswordData = false;
    } else {
      this.passedData.emit(this.userChangePasswordForm.value);
      setTimeout(() => {
        this.activeModal.close(this.userChangePasswordForm.value);
      }, 1000);
    }
  }
}
