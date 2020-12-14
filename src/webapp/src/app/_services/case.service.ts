import { HttpClient, HttpHeaders, HttpParams } from "@angular/common/http";
import { catchError, switchMap, tap } from "rxjs/operators";
import { Observable, throwError } from "rxjs";
import { HttpErrorResponse } from "@angular/common/http";
import { Injectable } from "@angular/core";
import { environment } from "../../environments/environment";
import {
  ActivityDefinitionResponse,
  Case,
  CaseDefinition,
  PostCaseDefinition,
  CustomField,
} from "../_models";
import { Coordinate } from "../_models/geo";

const httpOptions = {
  headers: new HttpHeaders({
    "Content-Type": "multipart/form-data",
  }),
};

@Injectable({
  providedIn: "root",
})
export class CaseService {
  remoteAPI = environment.remoteAPI;

  constructor(private http: HttpClient) {}

  public createNewCaseDefinition(
    newCaseDefinition: CaseDefinition
  ): Observable<CaseDefinition> {
    console.log("new case definiton argumment");
    console.log(`${JSON.stringify(newCaseDefinition)}`);
    const data: PostCaseDefinition = {
      name: newCaseDefinition.name,
      key: newCaseDefinition.key,
      description: newCaseDefinition.description
        ? newCaseDefinition.description
        : null,
      surveys: newCaseDefinition.surveys
        ? ((newCaseDefinition.surveys as any) as number[])
        : [],
      documents: newCaseDefinition.documents
        ? newCaseDefinition.documents.map((d) => {
            return {
              name: d.name,
              description: d.description,
              is_required: d.is_required,
            };
          })
        : [],
      custom_fields: newCaseDefinition.custom_fields
        ? newCaseDefinition.custom_fields.map((cf) => {
            return {
              name: cf.name,
              field_type: cf.field_type,
              selections: cf.selections,
              validation_rules: [],
              custom_section_id: null,
              help_text: cf.help_text,
              sort_order: cf.sort_order,
            };
          })
        : [],
      activity_definitions: newCaseDefinition.activity_definitions
        ? newCaseDefinition.activity_definitions.map((ad) => {
            return {
              name: ad.name,
              description: ad.description,
              case_definition_id: 0,
              surveys: ad.surveys
                ? ad.surveys.map((s) => {
                    return s.id;
                  })
                : [],
              documents: ad.documents
                ? ad.documents.map((doc) => {
                    return {
                      name: doc.name,
                      description: doc.description,
                      is_required: doc.is_required,
                    };
                  })
                : [],
              custom_fields: ad.custom_fields
                ? ad.custom_fields.map((cf) => {
                    return {
                      name: cf.name,
                      field_type: cf.fieldType,
                      selections: cf.selections,
                      validation_rules: [],
                      custom_section_id: null,
                      help_text: cf.help_text,
                      sort_order: cf.sort_order,
                    };
                  })
                : [],
            };
          })
        : [],
    };
    console.log("mapped case definitions");
    console.log(`${JSON.stringify(data)}`);
    return this.http
      .post<CaseDefinition>(`${this.remoteAPI}/case_definitions/`, data)
      .pipe(catchError((error) => this.handleError(error)));
  }

  public updateCaseDefinition(
    data: CaseDefinition,
    caseDefinitionId
  ): Observable<any> {
    return this.http
      .put(`${this.remoteAPI}/case_definitions/${caseDefinitionId}`, data)
      .pipe(catchError((error) => this.handleError(error)));
  }

  public getAllCaseDefinitions(): Observable<any> {
    return this.http
      .get(`${this.remoteAPI}/case_definitions/`)
      .pipe(catchError((error) => this.handleError(error)));
  }

  public getCaseDefinition(caseDefinitionId: number): Observable<any> {
    return this.http
      .get(`${this.remoteAPI}/case_definitions/${caseDefinitionId}`)
      .pipe(catchError((error) => this.handleError(error)));
  }

  public deleteCaseDefinition(caseDefinitionId: number): Observable<any> {
    return this.http
      .delete(`${this.remoteAPI}/case_definitions/${caseDefinitionId}`)
      .pipe(catchError((error) => this.handleError(error)));
  }

  public getCaseDefinitionsCustomFields(
    caseDefinitionId: number
  ): Observable<CustomField[]> {
    return this.http
      .get<CustomField[]>(
        `${this.remoteAPI}/case_definitions/${caseDefinitionId}/custom_fields`
      )
      .pipe(catchError((error) => this.handleError(error)));
  }

  public createNewCase(caseDefinitionId: number, data: any): Observable<any> {
    console.log(
      `CaseService.createNewCase(): data to post ${JSON.stringify(data)}`
    );
    return this.http
      .post(
        `${this.remoteAPI}/case_definitions/${caseDefinitionId}/cases`,
        data
      )
      .pipe(catchError((error) => this.handleError(error)));
  }

  public deleteCase(caseId: number): Observable<any> {
    return this.http
      .delete(`${this.remoteAPI}/cases/${caseId}`)
      .pipe(catchError((error) => this.handleError(error)));
  }

  public getAllCases(): Observable<any> {
    return this.http
      .get(`${this.remoteAPI}/cases`)
      .pipe(catchError((error) => this.handleError(error)));
  }

  public getCase(caseId: number): Observable<any> {
    return this.http
      .get(`${this.remoteAPI}/cases/${caseId}`)
      .pipe(catchError((error) => this.handleError(error)));
  }

  public getCasesBySearchParam(
    query: string,
    caseDefnId?: number
  ): Observable<any> {
    let params = new HttpParams();
    params = params.append("search_term", `${query}`);
    if (caseDefnId) {
      params = params.append("case_definition_id", `${caseDefnId}`);
    }
    return this.http
      .get(`${this.remoteAPI}/cases`, { params })
      .pipe(catchError((error) => this.handleError(error)));
  }

  public getCaseSurveyResponses(obj: any): Observable<any> {
    return this.http
      .get(
        `${this.remoteAPI}/cases/${obj.case_id}/surveys/${obj.survey_id}/responses`
      )
      .pipe(catchError((error) => this.handleError(error)));
  }

  public updateCase(caseId: number, caseData: any): Observable<any> {
    console.log(
      `CaseService.updateCase(): caseData to post ${JSON.stringify(caseData)}`
    );
    return this.http
      .put(`${this.remoteAPI}/cases/${caseId}`, caseData)
      .pipe(catchError((error) => this.handleError(error)));
  }

  public updateCustomFieldValue(
    caseId: number,
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
        `${this.remoteAPI}/cases/${caseId}/custom_fields/${customFieldId}`,
        data
      )
      .pipe(
        tap(
          (_) =>
            this.log(
              `update custom field id = ${customFieldId} value = '${customFieldValue}' for case id = ${caseId}`
            ),
          catchError((error) => this.handleError(error))
        )
      );
  }

  public saveCaseNote(caseNote: {
    case_id: number;
    note: string;
  }): Observable<any> {
    return this.http
      .post(`${this.remoteAPI}/cases/${caseNote.case_id}/notes`, caseNote)
      .pipe(catchError((error) => this.handleError(error)));
  }

  public uploadFile(fileObj: any): Observable<any> {
    const formData: FormData = new FormData();
    formData.set("document_id", fileObj.docId);
    formData.set("file", fileObj.file);
    formData.set("uploaded_location_latitude", fileObj.latitude);
    formData.set("uploaded_location_longitude", fileObj.longitude);
    return this.http
      .post(`${this.remoteAPI}/cases/${fileObj.caseId}/add_file`, formData)
      .pipe(catchError((error) => this.handleError(error)));
  }

  public deleteFile(caseFileId: number) {
    return this.http
      .delete(`${this.remoteAPI}/cases/files/${caseFileId}`)
      .pipe(catchError((error) => this.handleError(error)));
  }

  public downloadFile(caseFileId: number) {
    return this.http
      .get(`${this.remoteAPI}/cases/files/${caseFileId}/download`)
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
    console.log(message);
  }
}
