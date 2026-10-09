import { Injectable, signal } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';
import { tap } from 'rxjs/operators';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';
import { User, StudentProfile, AuthTokens } from '../models/user.model';

@Injectable({ providedIn: 'root' })
export class AuthService {
  private readonly ACCESS_KEY  = 'hs_access';
  private readonly REFRESH_KEY = 'hs_refresh';
  private readonly USER_KEY    = 'hs_user';

  currentUser = signal<User | null>(this._loadUser());

  constructor(private http: HttpClient, private router: Router) {}

  // ── Registration & Login ─────────────────────────────────────────────

  register(data: {
    first_name: string; username: string;
    email: string; password: string; roll_no: string;
  }): Observable<User> {
    return this.http.post<User>(`${environment.apiUrl}/auth/register/`, data);
  }

  login(username: string, password: string): Observable<AuthTokens & { user?: User }> {
    return this.http.post<AuthTokens>(`${environment.apiUrl}/auth/login/`, { username, password })
      .pipe(tap(tokens => {
        localStorage.setItem(this.ACCESS_KEY, tokens.access);
        localStorage.setItem(this.REFRESH_KEY, tokens.refresh);
        // Fetch user info immediately after login
        this.fetchCurrentUser().subscribe();
      }));
  }

  fetchCurrentUser(): Observable<User> {
    return this.http.get<User>(`${environment.apiUrl}/auth/me/`)
      .pipe(tap(user => {
        this.currentUser.set(user);
        localStorage.setItem(this.USER_KEY, JSON.stringify(user));
      }));
  }

  logout(): void {
    localStorage.removeItem(this.ACCESS_KEY);
    localStorage.removeItem(this.REFRESH_KEY);
    localStorage.removeItem(this.USER_KEY);
    this.currentUser.set(null);
    this.router.navigate(['/login']);
  }

  // ── Profile ──────────────────────────────────────────────────────────

  getProfile(): Observable<StudentProfile> {
    return this.http.get<StudentProfile>(`${environment.apiUrl}/auth/profile/`);
  }

  updateProfile(data: Partial<StudentProfile>): Observable<StudentProfile> {
    return this.http.patch<StudentProfile>(`${environment.apiUrl}/auth/profile/`, data)
      .pipe(tap(() => this.fetchCurrentUser().subscribe()));
  }

  // ── Helpers ──────────────────────────────────────────────────────────

  getToken(): string | null {
    return localStorage.getItem(this.ACCESS_KEY);
  }

  getRefreshToken(): string | null {
    return localStorage.getItem(this.REFRESH_KEY);
  }

  setTokens(access: string, refresh: string): void {
    localStorage.setItem(this.ACCESS_KEY, access);
    localStorage.setItem(this.REFRESH_KEY, refresh);
  }

  isLoggedIn(): boolean {
    return !!this.getToken();
  }

  isAdmin(): boolean {
    return this.currentUser()?.is_staff === true;
  }

  private _loadUser(): User | null {
    try {
      const raw = localStorage.getItem(this.USER_KEY);
      return raw ? JSON.parse(raw) : null;
    } catch { return null; }
  }
}
