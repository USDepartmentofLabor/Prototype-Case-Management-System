import { Injectable } from '@angular/core';
import { Observable, of, throwError } from 'rxjs';
import { catchError, tap } from 'rxjs/operators';
import { HttpClient, HttpHeaders } from '@angular/common/http';

import { environment } from '../../environments/environment';
import { HttpErrorResponse } from '@angular/common/http';

const httpOptions = {
    headers: new HttpHeaders({
        'Content-Type': 'application/json'
    })
};

@Injectable({
    providedIn: 'root'
})
export class SurveyService {
    remoteAPI = environment.remoteAPI;

    constructor(private http: HttpClient) {
    }

    public getAllSurveys(queryString: string = 'none'): Observable<any> {
        return this.http.get<[]>(`${this.remoteAPI}/surveys/?archived=${queryString}`).pipe(
            tap(_ => this.log('fetched all surveys')),
            catchError(error => this.handleError(error))
        );
    }

    public getSurvey(surveyId: number): Observable<any> {
        return this.http.get(`${this.remoteAPI}/surveys/${surveyId}`).pipe(
            tap(_ => this.log('fetched surveys by surveyId')),
            catchError(error => this.handleError(error))
        );
    }

    public saveSurvey(data: any): Observable<any> {
        return this.http
            .post(`${this.remoteAPI}/surveys/`, data)
            .pipe(catchError(error => this.handleError(error)));
    }

    public updateSurvey(data: any): Observable<any> {
        return this.http
            .put(`${this.remoteAPI}/surveys/${data.id}`, data)
            .pipe(catchError(error => this.handleError(error)));
    }

    public saveSurveyResponse(data: any): Observable<any> {
        return this.http
            .post(`${this.remoteAPI}/surveys/${data.survey_id}/responses`, data)
            .pipe(catchError(error => this.handleError(error)));
    }

    public getSurveyResponses(id: number): Observable<any> {
        return this.http
            .get(`${this.remoteAPI}/surveys/${id}/responses`)
            .pipe(catchError(error => this.handleError(error)));
    }

    public getSurveyResponse(surveyId: number, responseId: number): Observable<any> {
        return this.http
            .get(`${this.remoteAPI}/surveys/${surveyId}/responses/${responseId}`)
            .pipe(catchError(error => this.handleError(error)));
    }

    public updateSurveyResponse(data: any): Observable<any> {
        return this.http
            .put(
                `${this.remoteAPI}/surveys/${data.surveyId}/responses/${data.responseId}`, data)
            .pipe(catchError(error => this.handleError(error)));
    }

    public deleteSurvey(surveyId: number): Observable<any> {
        return this.http
            .delete(`${this.remoteAPI}/surveys/${surveyId}`)
            .pipe(catchError(error => this.handleError(error)));
    }

    /**
     * Handle HTTP operation that failed
     */

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
        console.log(`Dataservice: ${message}`);
    }
}
