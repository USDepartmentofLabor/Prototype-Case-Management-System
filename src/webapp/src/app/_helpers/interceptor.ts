import { catchError } from 'rxjs/operators';
import { Injectable } from '@angular/core';
import { HttpInterceptor, HttpErrorResponse, HttpEvent, HttpHandler, HttpRequest } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { AuthenticationService } from '../_services/';
import { Router } from '@angular/router';
import * as _ from 'lodash';

@Injectable({providedIn: 'root'})
export class Interceptor implements HttpInterceptor {
    constructor(
        private authService: AuthenticationService,
        private router: Router
    ) {
    }

    intercept(req: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {
        const token = JSON.parse(localStorage.getItem('token'));
        return next.handle(req).pipe(
            catchError((error: HttpErrorResponse) => {
                if (error.status === 401 || _.isEmpty(token)) {
                    this.authService.logout();
                    this.router.navigate([`/login`]);
                }
                return throwError(error);
            })
        );
    }
}
