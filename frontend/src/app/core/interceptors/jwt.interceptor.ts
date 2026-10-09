import { HttpInterceptorFn, HttpRequest, HttpHandlerFn, HttpErrorResponse } from '@angular/common/http';
import { inject } from '@angular/core';
import { catchError, switchMap, throwError } from 'rxjs';
import { AuthService } from '../services/auth.service';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../../environments/environment';

/**
 * JWT Interceptor
 * ---------------
 * 1. Attaches "Authorization: Bearer <token>" to every outgoing API request.
 * 2. On 401 response → attempts token refresh → retries the original request.
 * 3. If refresh also fails → logs the user out.
 */
export const jwtInterceptor: HttpInterceptorFn = (req: HttpRequest<unknown>, next: HttpHandlerFn) => {
  const auth = inject(AuthService);
  const http = inject(HttpClient);

  // Skip interceptor for auth endpoints to avoid loops
  const isAuthUrl = req.url.includes('/auth/login/') || req.url.includes('/auth/refresh/');

  const token = auth.getToken();
  const authReq = (token && !isAuthUrl)
    ? req.clone({ setHeaders: { Authorization: `Bearer ${token}` } })
    : req;

  return next(authReq).pipe(
    catchError((error: HttpErrorResponse) => {
      // If 401 and we have a refresh token, try to refresh
      if (error.status === 401 && auth.getRefreshToken() && !isAuthUrl) {
        return http.post<{ access: string }>(
          `${environment.apiUrl}/auth/refresh/`,
          { refresh: auth.getRefreshToken() }
        ).pipe(
          switchMap(res => {
            auth.setTokens(res.access, auth.getRefreshToken()!);
            const retryReq = req.clone({
              setHeaders: { Authorization: `Bearer ${res.access}` }
            });
            return next(retryReq);
          }),
          catchError(refreshErr => {
            // Refresh failed — log out completely
            auth.logout();
            return throwError(() => refreshErr);
          })
        );
      }
      return throwError(() => error);
    })
  );
};
