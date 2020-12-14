import { HttpClient } from '@angular/common/http';
import { catchError, tap, map } from 'rxjs/operators';
import { Observable, throwError } from 'rxjs';
import { HttpErrorResponse } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { environment } from '../../environments/environment';
import { Dashboard, DashboardAPI, DefaultDashboard, DefaultDashboardAPI } from '../_models';

@Injectable({
    providedIn: 'root'
})
export class GeneralService {
    remoteAPI = environment.remoteAPI;

    constructor(private http: HttpClient) {
    }

    public getLookupsData(): Observable<any> {
        return this.http
            .get(`${this.remoteAPI}/lookups`)
            .pipe(catchError(error => this.handleError(error)));
    }

    public getConfigs(): Observable<any> {
        return this.http
            .get(`${this.remoteAPI}/configuration`)
            .pipe(catchError(error => this.handleError(error)));
    }

    public getDashboards(): Observable<Dashboard[]> {
        return this.http.get<DashboardAPI[]>(`${this.remoteAPI}/dashboards`)
            .pipe(
                map(dashboards => {
                    return dashboards.map(dashboard_result => {
                        return new Dashboard(dashboard_result.id, dashboard_result.name, dashboard_result.description,
                            dashboard_result.is_default_dashboard);
                    });
                }),
                tap((_) => this.log('got dashboards from api')),
                catchError((error) => this.handleError(error)));
    }

    public setDefaultDashboard(dashboardID: number): Observable<Dashboard[]> {
        const apiUrl = `${this.remoteAPI}/dashboards/set-default`;
        const data = {
            dashboard_id: dashboardID,
        };
        return this.http.put<DashboardAPI[]>(apiUrl, data)
            .pipe(map(dashboards => {
                    return dashboards.map(dashboard_result => {
                        return new Dashboard(dashboard_result.id, dashboard_result.name, dashboard_result.description,
                            dashboard_result.is_default_dashboard);
                    });
                }),
                tap((_) => this.log('updated default dashboard to API')),
                catchError((error) => this.handleError(error)));
    }

    public getDefaultDashboard(): Observable<DefaultDashboard> {
        const apiUrl = `${this.remoteAPI}/dashboards/get-default`;
        return this.http.get<DefaultDashboardAPI>(apiUrl)
            .pipe(
                map(dashboard => {
                    return new DefaultDashboard(dashboard.default_dashboard_id, dashboard.default_dashboard_url);
                }),
                tap(() => this.log("got default dashboard from api")),
                catchError((error) => this.handleError(error))
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
