import { Component, OnInit } from "@angular/core";
import { Router, ActivatedRoute } from "@angular/router";
import {
  FormBuilder,
  FormGroup,
  Validators,
  FormControl,
} from "@angular/forms";
import { AuthenticationService, GeneralService } from "../_services";
import { first } from "rxjs/operators";
import { Utils } from "../_helpers";

@Component({
  selector: "app-login",
  templateUrl: "./login.component.html",
  styleUrls: ["./login.component.css"],
})
export class LoginComponent implements OnInit {
  errorMsg: string;
  returnUrl: string;
  loginForm: FormGroup;
  resetPasswordForm: FormGroup;
  isLoggingIn: boolean;
  loginBtnTxt = "";
  submitted = false;
  forgotPassword = false;
  latitude: number;
  longitude: number;
  // TODO: move version to config/environment
  currentVersion = "Build: 0.28.0";

  constructor(
    private router: Router,
    private route: ActivatedRoute,
    private utils: Utils,
    private formBuilder: FormBuilder,
    private authService: AuthenticationService,
    private generalService: GeneralService
  ) {
    this.loginForm = this.formBuilder.group({
      email: new FormControl(null, [Validators.required, Validators.email]),
      password: new FormControl(null, [
        Validators.required,
        Validators.minLength(2),
      ]),
    });
    this.resetPasswordForm = this.formBuilder.group({
      email: new FormControl(["", [Validators.required, Validators.email]]),
    });
  }

  ngOnInit() {
    this.authService.logout();
    this.returnUrl = this.route.snapshot.queryParams.returnUrl;
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

  // convenience getter for easy access to form fields
  get form() {
    return this.loginForm.controls;
  }
  get passForm() {
    return this.resetPasswordForm.controls;
  }

  public login(): void {
    this.isLoggingIn = true;
    this.submitted = true;

    if (this.errorMsg) {
      this.errorMsg = "";
    }

    if (this.loginForm.invalid) {
      this.isLoggingIn = false;
    } else {
      console.log("calling login server");
      this.authService
        .login(
          this.form.email.value,
          this.form.password.value,
          this.latitude,
          this.longitude
        )
        .pipe(first())
        .subscribe(
          () => {
            console.log("login successful");
            this.getAppLookupData();
            // this.returnUrl = `/cases`;
            this.returnUrl = `/landing-page`;
            // this.returnUrl = `/forms`;
            this.router.navigate([this.returnUrl]);
          },
          (error) => {
            this.errorMsg = error.message;
            this.submitted = false;
            this.form.password.reset();
            this.isLoggingIn = false;
          }
        );
    }
  }

  public sendResetPassword(): void {
    console.log("sending reset password: " + this.form.email.value);

    if (this.errorMsg) {
      this.errorMsg = "";
    }

    console.log("sending reset password: " + this.form.email.value);
    this.authService
      .requestPasswordReset(this.form.email.value)
      .pipe(first())
      .subscribe(
        () => {
          console.log("password reset request successful");
          this.forgotPassword = false;
          this.submitted = false;
          this.isLoggingIn = false;
        },
        (error) => {
          this.errorMsg = error.message;
          this.submitted = false;
          this.form.password.reset();
          this.forgotPassword = true;
          this.isLoggingIn = false;
        }
      );
  }

  private getAppLookupData(): void {
    this.generalService.getLookupsData().subscribe((data) => {
      localStorage.setItem("lookupData", JSON.stringify(data));
    });
  }

  public displayForgotPasswordForm(): void {
    this.submitted = false;
    this.forgotPassword = !this.forgotPassword;
  }

  public generateSignBtnTxt(): string {
    return this.isLoggingIn ? "Logging In..." : "Log In";
  }

  public getCurrentYear(): number {
    return this.utils.generateCurrentYear();
  }
}
