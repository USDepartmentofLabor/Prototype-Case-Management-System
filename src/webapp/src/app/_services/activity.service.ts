import { HttpClient, HttpErrorResponse } from "@angular/common/http";
import { Injectable } from "@angular/core";
import { environment } from "environments/environment";
import { Observable, throwError } from "rxjs";
import { catchError, tap } from "rxjs/operators";
import {
  ActivityAPI,
  ActivityDefinitionResponse,
  AddNoteResponse,
  Coordinate,
  CustomField,
  PostActivity,
  PostActivityDefinition,
  PostCustomField,
  PutCustomField,
} from "../_models";

@Injectable({
  providedIn: "root",
})
export class ActivityService {
  remoteAPI = environment.remoteAPI;

  constructor(private http: HttpClient) {}

  public getActivity(activityId: number): Observable<ActivityAPI> {
    return this.http
      .get<ActivityAPI>(`${this.remoteAPI}/activities/${activityId}`)
      .pipe(catchError((error) => this.handleError(error)));
  }

  public updateActivity(id: number, data: any): Observable<any> {
    console.log(
      `[ActivityService.updateActivity(): data to post ${JSON.stringify(data)}`
    );
    return this.http
      .put(`${this.remoteAPI}/activities/${id}`, data)
      .pipe(catchError((error) => this.handleError(error)));
  }

  public createActivity(newActivity: PostActivity): Observable<ActivityAPI> {
    return this.http
      .post<ActivityAPI>(`${this.remoteAPI}/activities`, newActivity)
      .pipe(catchError((error) => this.handleError(error)));
  }

  public deleteActivity(activityId: number): Observable<any> {
    return this.http
      .delete(`${this.remoteAPI}/activities/${activityId}`)
      .pipe(catchError((error) => this.handleError(error)));
  }

  public getAllActivityDefinitions(): Observable<ActivityDefinitionResponse[]> {
    return this.http
      .get<ActivityDefinitionResponse[]>(
        `${this.remoteAPI}/activity_definitions`
      )
      .pipe(catchError((error) => this.handleError(error)));
  }

  public createActivityDefinition(
    data: PostActivityDefinition
  ): Observable<ActivityDefinitionResponse> {
    console.log(
      `[ActivityService.createActivityDefinition(): data ${JSON.stringify(
        data
      )}`
    );
    return this.http
      .post<ActivityDefinitionResponse>(
        `${this.remoteAPI}/activity_definitions`,
        data
      )
      .pipe(catchError((error) => this.handleError(error)));
  }

  public updateActivityDefinition(
    id: number,
    data: any
  ): Observable<ActivityDefinitionResponse> {
    console.log(
      `[ActivityService.updateSctivityDefinition(): update activity definitions ${id} with ${JSON.stringify(
        data
      )}`
    );
    return this.http
      .put<ActivityDefinitionResponse>(
        `${this.remoteAPI}/activity_definitions/${id}`,
        data
      )
      .pipe(catchError((error) => this.handleError(error)));
  }

  public updateCustomField(
    activityDefinitionId: number,
    customFieldId: string,
    data: PutCustomField
  ): Observable<any> {
    console.log(
      `[ActivityService.updateCustomField(): update custom field ${customFieldId} for activity definitions ${activityDefinitionId} with ${JSON.stringify(
        data
      )}`
    );
    return this.http
      .put<ActivityDefinitionResponse>(
        `${this.remoteAPI}/activity_definitions/${activityDefinitionId}/custom_fields/${customFieldId}`,
        data
      )
      .pipe(catchError((error) => this.handleError(error)));
  }

  public createCustomField(
    activityDefinitionId: number,
    data: PostCustomField
  ): Observable<CustomField> {
    return this.http
      .post<CustomField>(
        `${this.remoteAPI}/activity_definitions/${activityDefinitionId}/custom_fields`,
        data
      )
      .pipe(catchError((error) => this.handleError(error)));
  }

  public updateCustomFieldValue(
    activityId: number,
    customFieldId: string,
    customFieldValue: string | number[] | { id: number; rank: number },
    coordinate: Coordinate
  ) {
    const data = {
      value: customFieldValue,
      latitude: coordinate.latitude,
      longitude: coordinate.longitude,
    };
    return this.http
      .put(
        `${this.remoteAPI}/activities/${activityId}/custom_fields/${customFieldId}`,
        data
      )
      .pipe(
        tap(
          (_) =>
            this.log(
              `update custom field id = ${customFieldId} value = '${customFieldValue}' for activity id = ${activityId}`
            ),
          catchError((error) => this.handleError(error))
        )
      );
  }

  public saveNote(id: number, note: string): Observable<any> {
    const data = {
      note: note,
    };
    return this.http
      .post<AddNoteResponse>(`${this.remoteAPI}/activities/${id}/notes`, data)
      .pipe(catchError((error) => this.handleError(error)));
  }

  public uploadFile(fileObj: any): Observable<any> {
    const formData: FormData = new FormData();
    formData.set("document_id", fileObj.docId);
    formData.set("file", fileObj.file);
    formData.set("uploaded_location_latitude", fileObj.latitude);
    formData.set("uploaded_location_longitude", fileObj.longitude);
    return this.http
      .post(
        `${this.remoteAPI}/activities/${fileObj.activityId}/add_file`,
        formData
      )
      .pipe(catchError((error) => this.handleError(error)));
  }

  public deleteFile(id: number) {
    return this.http
      .delete(`${this.remoteAPI}/activities/files/${id}`)
      .pipe(catchError((error) => this.handleError(error)));
  }

  public downloadFile(id: number) {
    return this.http
      .get(`${this.remoteAPI}/activities/files/${id}/download`)
      .pipe(catchError((error) => this.handleError(error)));
  }

  public getActivitySurveyResponses(activityId: number, surveyId: number): Observable<any> {
    return this.http
      .get(
        `${this.remoteAPI}/activities/${activityId}/surveys/${surveyId}/responses`
      )
      .pipe(catchError((error) => this.handleError(error)));
  }

  private handleError(error: HttpErrorResponse) {
    if (error.error instanceof ErrorEvent) {
      // A client-side or network error occurred. Handle it accordingly.
      this.log(`[ActivityService] An error occurred: ${error.error}`);
    } else {
      // The backend returned an unsuccessful response code.
      // The response body may contain clues as to what went wrong,
      this.log(
        `[ActivityService] Backend returned code ${error.message}, ` +
          `body was: ${error.status}`
      );
    }
    // return an observable with a user-facing error message
    return throwError(error.error);
  }

  private log(message: string) {
    console.log(message);
  }
}
