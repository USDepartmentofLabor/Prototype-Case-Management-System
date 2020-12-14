import { HttpClient } from '@angular/common/http';
import { catchError } from 'rxjs/operators';
import { Observable, throwError } from 'rxjs';
import { HttpErrorResponse } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { environment } from '../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class AdminService {
  remoteAPI = environment.remoteAPI;

  constructor(private http: HttpClient) {}

  public resetReporting(): Observable<any> {
    return this.http
      .post(`${this.remoteAPI}/reset-reporting`,{})
      .pipe(catchError(error => this.handleError(error)));
  }

  public getProject(): Observable<any> {
    return this.http
      .get(`${this.remoteAPI}/project`)
      .pipe(catchError(error => this.handleError(error)));
  }

  public updateRole(data): Observable<any> {
    return this.http
      .put(`${this.remoteAPI}/project`, data)
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
