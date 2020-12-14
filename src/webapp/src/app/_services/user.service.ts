import { HttpClient, HttpParams } from "@angular/common/http";
import { catchError, map } from "rxjs/operators";
import { Observable, throwError } from "rxjs";
import { HttpErrorResponse } from "@angular/common/http";
import { Injectable } from "@angular/core";
import { environment } from "../../environments/environment";
import { User } from "../_models/index";

const params = new HttpParams().set("status", "any");

@Injectable({
  providedIn: "root",
})
export class UserService {
  remoteAPI = environment.remoteAPI;

  constructor(private http: HttpClient) {}

  public getAllUsers(): Observable<User[]> {
    return this.http
      .get<User[]>(`${this.remoteAPI}/users/`, { params })
      .pipe(catchError((error) => this.handleError(error)));
  }

  public getUserByID(userId: number): Observable<any> {
    return this.http
      .get<User>(`${this.remoteAPI}/users/${userId}`)
      .pipe(catchError((error) => this.handleError(error)));
  }

  public updateUser(userId: number, user: any): Observable<any> {
    return this.http
      .put<User>(`${this.remoteAPI}/users/${userId}`, user)
      .pipe(catchError((error) => this.handleError(error)));
  }

  public createNewUser(data: any): Observable<any> {
    return this.http
      .post<User>(`${this.remoteAPI}/users/`, data)
      .pipe(catchError((error) => this.handleError(error)));
  }

  public resendWelcome(userId: number): Observable<any> {
    return this.http
      .post<any>(`${this.remoteAPI}/users/${userId}/resend-welcome`, {})
      .pipe(catchError((error) => this.handleError(error)));
  }

  public getAssignableUsers(): Observable<User[]> {
    return this.http
      .get<User[]>(`${this.remoteAPI}/users?assignable=true`)
      .pipe(catchError((error) => this.handleError(error)));
  }

  public isUserAssignable(user: User): boolean {
    const lookupData = JSON.parse(localStorage.getItem("lookupData")) || "";
    const lookupDataPerm = lookupData.permissions;
    const adminPerm = lookupDataPerm.find((perm) => perm.code === "ADMIN")
      .value;
    const assignablePerm = lookupDataPerm.find(
      (perm) => perm.code === "ASSIGNABLE_TO_CASE"
    ).value;
    return (
      (assignablePerm & user.role.permissions) === assignablePerm ||
      (adminPerm & user.role.permissions) === adminPerm
    );
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
    console.log(message);
  }
}
