import { Injectable } from "@angular/core";
import { HttpClient } from "@angular/common/http";
import { BehaviorSubject, Observable, throwError } from "rxjs";
import { map, catchError } from "rxjs/operators";
import { HttpErrorResponse } from "@angular/common/http";
import { User } from "../_models";
import { environment } from "../../environments/environment";

@Injectable({ providedIn: "root" })
export class AuthenticationService {
  remoteAPI = environment.remoteAPI;
  private currentUserSubject: BehaviorSubject<User>;
  public currentUser: Observable<User>;
  private loggedIn = new BehaviorSubject<boolean>(this.tokenAvailable());

  constructor(private http: HttpClient) {
    this.currentUserSubject = new BehaviorSubject<User>(
      JSON.parse(localStorage.getItem("currentUser"))
    );
    this.currentUser = this.currentUserSubject.asObservable();
  }

  get isLoggedIn() {
    return this.loggedIn.asObservable();
  }

  get currentUserValue(): User {
    return this.currentUserSubject.value;
  }

  private tokenAvailable(): boolean {
    return !!localStorage.getItem("token");
  }

  public login(
    login: string,
    password: string,
    latitude: number,
    longitude: number
  ): Observable<any> {
    const loginObject = {
      login: login,
      password: password,
      latitude: latitude,
      longitude: longitude,
    };
    return this.http.post(`${this.remoteAPI}/auth/login`, loginObject).pipe(
      map((user) => {
        if (user && user["access_token"]) {
          localStorage.setItem("token", JSON.stringify(user["access_token"]));
          localStorage.setItem("currentUser", JSON.stringify(user["profile"]));
          this.currentUserSubject.next(user["profile"]);
          this.loggedIn.next(true);
        }
      }),
      catchError((error) => this.handleError(error))
    );
  }

  public changePassword(data: any, userId: number): Observable<any> {
    return this.http
      .post(`${this.remoteAPI}/users/${userId}/change-password`, data)
      .pipe(catchError((error) => this.handleError(error)));
  }

  public logout() {
    localStorage.clear();
    this.loggedIn.next(false);
    this.currentUserSubject.next(null);
  }

  public requestPasswordReset(email: string): Observable<any> {
    const data = {
      email: email,
    };
    return this.http
      .post(`${this.remoteAPI}/auth/request-password-reset`, data)
      .pipe(catchError((error) => this.handleError(error)));
  }

  public resetPassword(newPassword: string, confirmPassword: string, token: string): Observable<any> {
    const data = {
        "new_password": newPassword,
        "confirm_password": confirmPassword
      }
      return this.http
        .post(`${this.remoteAPI}/auth/reset-password/${token}`, data)
        .pipe(catchError((error) => this.handleError(error)));
  }

  private handleError(error: HttpErrorResponse) {
    if (error.error instanceof ErrorEvent) {
      // A client-side or network error occurred. Handle it accordingly.
      this.log(`An error occurred: ${error.error}`);
    } else {
      // The backend returned an unsuccessful response code.
      // The response body may contain clues as to what went wrong,
      this.log(
        `Backend returned code ${error.message}, ` + `body was: ${error.status}`
      );
    }
    // return an observable with a user-facing error message
    return throwError(error.error);
  }

  private log(message: string) {
    console.log(`AuthenticationService: ${message}`);
  }
}
