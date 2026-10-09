import { Component, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterModule, Router } from '@angular/router';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { AuthService } from '../../core/services/auth.service';

@Component({
  selector: 'app-register',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterModule, MatSnackBarModule, MatProgressSpinnerModule],
  template: `
    <div class="split-layout">
      <!-- Left Column: Form -->
      <div class="form-section">
        <div class="form-content">
          <!-- Branding -->
          <div class="brand-header">
            <h1 class="brand-name">HostelSense AI</h1>
          </div>

          <!-- Headings -->
          <div class="welcome-section">
            <h2 class="welcome-title">Create Account</h2>
            <p class="welcome-sub">Register with your official student roll number and university email.</p>
          </div>

          <!-- Form -->
          <form (ngSubmit)="onRegister()" novalidate class="login-form">
            <div class="grid-2-form">
              <div class="field-group">
                <input type="text" [(ngModel)]="form.first_name" name="first_name"
                       placeholder="Full Name (e.g. Alex Smith)" required class="elegant-input" />
              </div>
              <div class="field-group">
                <input type="text" [(ngModel)]="form.roll_no" name="roll_no"
                       placeholder="Roll No (e.g. 21CS101)" required class="elegant-input" />
              </div>
            </div>

            <div class="field-group">
              <input type="text" [(ngModel)]="form.username" name="username"
                     placeholder="Choose Username" required class="elegant-input" />
            </div>

            <div class="field-group">
              <input type="email" [(ngModel)]="form.email" name="email"
                     placeholder="University Email" required class="elegant-input" />
            </div>

            <div class="field-group">
              <div class="pwd-input-wrap">
                <input [type]="showPwd() ? 'text' : 'password'" [(ngModel)]="form.password"
                       name="password" placeholder="Password (Min. 6 chars)" required class="elegant-input" />
                <button type="button" class="pwd-toggle" (click)="showPwd.set(!showPwd())" title="Toggle Password">
                  <svg *ngIf="!showPwd()" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" width="18" height="18">
                    <path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7Z"/>
                    <circle cx="12" cy="12" r="3"/>
                  </svg>
                  <svg *ngIf="showPwd()" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" width="18" height="18">
                    <path d="M9.88 9.88a3 3 0 1 0 4.24 4.24"/>
                    <path d="M10.73 5.08A10.43 10.43 0 0 1 12 5c7 0 10 7 10 7a13.16 13.16 0 0 1-1.67 2.68"/>
                    <path d="M6.61 6.61A13.526 13.526 0 0 0 2 12s3 7 10 7a9.74 9.74 0 0 0 5.39-1.61"/>
                    <line x1="2" x2="22" y1="2" y2="22"/>
                  </svg>
                </button>
              </div>
            </div>

            <button type="submit" class="btn-primary full-width elegant-btn" [disabled]="loading()">
              <mat-spinner *ngIf="loading()" diameter="18"></mat-spinner>
              <span>{{ loading() ? 'Registering...' : 'Register' }}</span>
            </button>
          </form>

          <div class="auth-footer">
            <p>Already a member? <a routerLink="/login">Sign In here</a></p>
          </div>
        </div>
      </div>

      <!-- Right Column: Visual Container -->
      <div class="visual-section">
        <div class="visual-container">
          <img src="login_illustration.png?v=3" alt="Campus Illustration" class="illustration">
        </div>
      </div>
    </div>
  `,
  styles: [`
    .split-layout {
      display: grid;
      grid-template-columns: 1fr 1fr;
      min-height: 100vh;
      background-color: #FFFFFF;
    }

    /* Left Side */
    .form-section {
      display: flex;
      flex-direction: column;
      justify-content: center;
      align-items: center;
      padding: 40px;
      position: relative;
    }

    .form-content {
      width: 100%;
      max-width: 420px;
      display: flex;
      flex-direction: column;
    }

    .brand-header {
      display: flex;
      align-items: center;
      margin-bottom: 32px;
    }

    .brand-name {
      font-size: 16px;
      font-weight: 700;
      color: var(--text-primary);
      letter-spacing: -0.01em;
    }

    .welcome-section {
      text-align: center;
      margin-bottom: 28px;
    }

    .welcome-title {
      font-size: 40px;
      font-weight: 800;
      color: #253247;
      letter-spacing: -0.03em;
      margin-bottom: 12px;
    }

    .welcome-sub {
      font-size: 15px;
      color: var(--text-muted);
      line-height: 1.5;
      max-width: 80%;
      margin: 0 auto;
    }

    .login-form {
      display: flex;
      flex-direction: column;
      gap: 16px;
    }

    .grid-2-form {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 12px;
    }

    .elegant-input {
      width: 100%;
      padding: 14px 20px;
      border: 1px solid #C3D3DC;
      border-radius: 999px;
      font-size: 14px;
      color: #253247;
      outline: none;
      transition: border-color 200ms;

      &::placeholder {
        color: #6B819B;
        font-weight: 500;
      }
      
      &:focus {
        border-color: #4E829D;
      }
    }

    .pwd-input-wrap {
      position: relative;
      input { padding-right: 48px; }
    }

    .pwd-toggle {
      position: absolute;
      right: 16px;
      top: 50%;
      transform: translateY(-50%);
      background: none;
      border: none;
      color: #6B819B;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      transition: color 180ms;
      &:hover { color: #253247; }
    }

    .elegant-btn {
      margin-top: 8px;
      background-color: #4E829D;
      color: #FFFFFF;
      padding: 16px;
      border-radius: 999px;
      font-size: 15px;
      font-weight: 600;
      border: none;
      cursor: pointer;
      transition: background-color 200ms, transform 100ms;
      
      &:hover {
        background-color: #3E6E86;
      }
      
      &:active {
        transform: scale(0.98);
      }
    }

    .full-width {
      width: 100%;
    }

    /* Social Divider */
    .divider {
      display: flex;
      align-items: center;
      text-align: center;
      margin: 24px 0 16px 0;
      color: #6B819B;
      font-size: 13px;
      font-weight: 500;
      
      &::before, &::after {
        content: '';
        flex: 1;
        border-bottom: 1px solid #C3D3DC;
      }
      &::before { margin-right: 16px; }
      &::after { margin-left: 16px; }
    }

    .social-login {
      display: flex;
      flex-direction: column;
      gap: 10px;
      margin-bottom: 24px;
    }

    .social-btn {
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 10px;
      width: 100%;
      height: 44px;
      border: 1px solid #C3D3DC;
      border-radius: 999px;
      background: #FFFFFF;
      color: #253247;
      font-size: 14px;
      font-weight: 500;
      cursor: pointer;
      transition: all 200ms ease;
      font-family: inherit;

      &:hover:not(:disabled) {
        background-color: #EEF5F8;
        border-color: #C3D3DC;
        transform: translateY(-1px);
      }

      &:disabled {
        opacity: 0.6;
        cursor: not-allowed;
      }

      svg { flex-shrink: 0; }
    }

    .auth-footer {
      text-align: center;
      font-size: 14px;
      color: #6B819B;

      a {
        color: #4E829D;
        text-decoration: none;
        font-weight: 600;
        transition: color 180ms ease-in-out;
        &:hover { color: #3E6E86; text-decoration: underline; }
      }
    }

    /* Right Side */
    .visual-section {
      display: flex;
      align-items: stretch;
      justify-content: center;
      padding: 24px;
      background-color: #FFFFFF;
    }

    .visual-container {
      flex: 1;
      background-color: #E8F1F5;
      border-radius: 32px;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 0;
      position: relative;
      overflow: hidden;
    }

    .illustration {
      width: 100%;
      height: 100%;
      object-fit: cover;
      object-position: center;
      display: block;
      border-radius: 32px;
    }

    .visual-caption {
      text-align: center;
      font-size: 24px;
      color: #253247;
      line-height: 1.4;
      
      strong {
        font-weight: 800;
      }
    }

    @media (max-width: 1024px) {
      .welcome-title { font-size: 32px; }
      .visual-caption { font-size: 20px; }
    }

    @media (max-width: 900px) {
      .split-layout {
        grid-template-columns: 1fr;
        grid-template-rows: auto auto;
      }
      .visual-section {
        padding: 24px;
      }
      .visual-container {
        border-radius: 24px;
        padding: 32px 20px;
      }
      .illustration {
        max-height: 35vh;
      }
    }
  `]
})
export class RegisterComponent {
  form = { first_name: '', username: '', email: '', password: '', roll_no: '' };
  loading = signal(false);
  showPwd = signal(false);

  constructor(
    private auth: AuthService,
    private router: Router,
    private snack: MatSnackBar
  ) {}

  onRegister(): void {
    const { first_name, username, email, password, roll_no } = this.form;
    if (!first_name || !username || !email || !password || !roll_no) {
      this.snack.open('Please fill in all fields.', 'Close', { duration: 3000 });
      return;
    }
    this.loading.set(true);
    this.auth.register(this.form).subscribe({
      next: () => {
        this.auth.login(username, password).subscribe({
          next: () => {
            this.loading.set(false);
            this.snack.open('Account created! Please complete your hostel profile.', 'OK', { duration: 4000 });
            this.router.navigate(['/complete-profile']);
          },
          error: () => {
            this.loading.set(false);
            this.snack.open('Account created successfully! Please sign in.', 'OK', { duration: 4000 });
            this.router.navigate(['/login']);
          }
        });
      },
      error: (err) => {
        this.loading.set(false);
        const errObj = err?.error;
        let msg = 'Registration failed. Please try again.';
        if (errObj && typeof errObj === 'object') {
          const firstKey = Object.keys(errObj)[0];
          if (firstKey) {
            const val = errObj[firstKey];
            const strVal = Array.isArray(val) ? val[0] : (typeof val === 'string' ? val : '');
            if (strVal) {
              const fieldName = firstKey.replace('_', ' ');
              msg = `${fieldName.charAt(0).toUpperCase() + fieldName.slice(1)}: ${strVal}`;
            }
          }
        } else if (typeof errObj === 'string') {
          msg = errObj;
        }
        this.snack.open(msg, 'Close', { duration: 5000 });
      }
    });
  }
}
