import { HttpClient, HttpParams } from '@angular/common/http';
import { catchError } from 'rxjs/operators';
import { Observable, throwError } from 'rxjs';
import { HttpErrorResponse } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { environment } from '../../environments/environment';
import { Role } from '../_models/index';

@Injectable({
  providedIn: 'root'
})
export class RolesService {
  remoteAPI = environment.remoteAPI;

  constructor(private http: HttpClient) {}

  public getRoles(): Observable<Role[]> {
    return this.http
      .get<Role[]>(`${this.remoteAPI}/roles`)
      .pipe(catchError(error => this.handleError(error)));
  }

  public updateRole(role_id: number, data: Role): Observable<Role> {
    return this.http
      .put<Role>(`${this.remoteAPI}/roles/${role_id}`, data)
      .pipe(catchError(error => this.handleError(error)));
  }

  public createNewRole(data: Role): Observable<Role> {
    return this.http
      .post<Role>(`${this.remoteAPI}/roles`, data)
      .pipe(catchError(error => this.handleError(error)));
  }

  public deleteRole(role_id: number):Observable<Role> | any {
    return this.http
      .delete(`${this.remoteAPI}/roles/${role_id}`)
      .pipe(catchError(error => this.handleError(error)));
  }

  private handleError(error: HttpErrorResponse) {
    if (error.error instanceof ErrorEvent) {
      // A client-side or network error occurred. Handle it accordingly.
      this.log(`An error occurred: ${error.error}`);
    } else {
      // The backend returned an unsuccessful response code.
      // The response body may contain clues as to what went wrong,
      this.log(`Backend returned code ${error.message}, ` + `body was: ${error.status}`);
    }
    // return an observable with a user-facing error message
    return throwError(error.error);
  }

  private log(message: string) {
    console.log(message);
  }
}
