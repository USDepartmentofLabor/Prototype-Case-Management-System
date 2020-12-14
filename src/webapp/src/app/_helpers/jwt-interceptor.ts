import { Injectable } from '@angular/core';
import { HttpInterceptor, HttpEvent, HttpHandler, HttpRequest } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({providedIn: 'root'})
export class JwtInterceptor implements HttpInterceptor {
    constructor() {
    }

    intercept(req: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {

        const token = JSON.parse(localStorage.getItem('token'));

        if (token) {
            req = req.clone({
                setHeaders: {
                    // 'Content-Type': 'multipart/form-data',
                    Authorization: `Bearer ${token}`
                }
            });
        }
        return next.handle(req);
    }
}
