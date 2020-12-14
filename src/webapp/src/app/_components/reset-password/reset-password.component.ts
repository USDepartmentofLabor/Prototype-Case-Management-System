import { Component, OnInit } from "@angular/core";
import { FormBuilder, FormGroup, Validators } from "@angular/forms";
import { ActivatedRoute } from "@angular/router";
import { AuthenticationService } from "app/_services";
import { pwdMatchValidator } from "../../_helpers";

@Component({
  selector: "app-reset-password",
  templateUrl: "./reset-password.component.html",
  styleUrls: ["./reset-password.component.css"],
})
export class ResetPasswordComponent implements OnInit {
  token: string;
  resetPasswordForm: FormGroup;
  fieldTextType: boolean;
  repeatFieldTextType: boolean;
  submitted: boolean = false;
  errorMessage: string = "";
  buttonText: string = "Reset Password";
  showSuccess: boolean = false;
  showFailed: boolean = false;

  constructor(
    private formBuilder: FormBuilder,
    public route: ActivatedRoute,
    private authService: AuthenticationService
  ) {
    this.resetPasswordForm = this.formBuilder.group(
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

  ngOnInit() {
    this.route.params.subscribe((params) => {
      this.token = params.token;
    });
  }

  get form() {
    return this.resetPasswordForm.controls;
  }

  public toggleFieldTextType(): void {
    this.fieldTextType = !this.fieldTextType;
  }

  public toggleRepeatFieldTextType(): void {
    this.repeatFieldTextType = !this.repeatFieldTextType;
  }

  public submit(): void {
    const newPassword: string = this.form.newPassword.value as string;
    const confirmPassword: string = this.form.confirmPassword.value as string;
    this.submitted = true;
    this.errorMessage = "";
    this.buttonText = "Saving ...";
    this.showFailed = false;
    this.showSuccess = false;

    console.log("resetting password for");
    console.log(`token = ${this.token}`);
    console.log(`new password = ${JSON.stringify(newPassword)}`);
    console.log(`confirm password = ${JSON.stringify(confirmPassword)}`);
    console.log(`form valid: ${this.resetPasswordForm.valid}`);
    console.log(`form invalid: ${this.resetPasswordForm.invalid}`);

    if (this.resetPasswordForm.valid) {
      console.log("sending reset request");
      this.authService
        .resetPassword(newPassword, confirmPassword, this.token)
        .subscribe(
          () => {
            console.log("password reset request successful");
            this.submitted = false;
            this.showSuccess = true;
            this.resetForm();
          },
          (error) => {
            console.log(`password reset request failed: ${error.message}`);
            this.errorMessage = error.message;
            this.submitted = false;
            this.showFailed = true;
            this.resetForm()
          }
        );
    }
  }

  resetForm() {
    this.buttonText = "Reset Password";
    this.form.newPassword.reset();
    this.form.confirmPassword.reset();
  };
}
