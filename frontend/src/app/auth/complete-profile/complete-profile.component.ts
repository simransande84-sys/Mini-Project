import { Component, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatSelectModule } from '@angular/material/select';
import { AuthService } from '../../core/services/auth.service';

@Component({
  selector: 'app-complete-profile',
  standalone: true,
  imports: [CommonModule, FormsModule, MatSnackBarModule, MatProgressSpinnerModule, MatSelectModule],
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
            <h2 class="welcome-title">Complete Hostel Profile</h2>
            <p class="welcome-sub">Provide your allocated room details so ticket requests automatically route to your resident block.</p>
          </div>

          <!-- Form -->
          <form (ngSubmit)="onSave()" novalidate class="login-form">
            <div class="grid-2-form">
              <div class="field-group">
                <select [(ngModel)]="form.block" name="block" required class="elegant-input elegant-select">
                  <option value="" disabled selected>Select Block</option>
                  <option *ngFor="let b of blocks" [value]="b">Block {{ b }}</option>
                </select>
              </div>
              <div class="field-group">
                <select [(ngModel)]="form.floor" name="floor" required class="elegant-input elegant-select">
                  <option value="" disabled selected>Select Floor</option>
                  <option *ngFor="let f of floors" [value]="f">{{ f }} Floor</option>
                </select>
              </div>
            </div>

            <div class="field-group">
              <input type="text" [(ngModel)]="form.room_no" name="room_no"
                     placeholder="Room Number (e.g. 210)" required class="elegant-input" />
            </div>

            <div class="field-group">
              <input type="tel" [(ngModel)]="form.phone" name="phone"
                     placeholder="Phone Number (Optional)" class="elegant-input" />
            </div>

            <button type="submit" class="btn-primary full-width elegant-btn" [disabled]="loading()">
              <mat-spinner *ngIf="loading()" diameter="18"></mat-spinner>
              <span>{{ loading() ? 'Saving Profile...' : 'Save & Continue' }}</span>
            </button>

            <button type="button" class="btn-skip" (click)="skip()">Skip for now</button>
          </form>
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
      font-size: 32px;
      font-weight: 800;
      color: #253247;
      letter-spacing: -0.03em;
      margin-bottom: 12px;
    }

    .welcome-sub {
      font-size: 14.5px;
      color: var(--text-muted);
      line-height: 1.5;
      max-width: 90%;
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

    select.elegant-select {
      appearance: none;
      -webkit-appearance: none;
      -moz-appearance: none;
      background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='%23253247' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpolyline points='6 9 12 15 18 9'%3E%3C/polyline%3E%3C/svg%3E");
      background-repeat: no-repeat;
      background-position: right 16px center;
      background-size: 16px;
      padding-right: 40px;
      cursor: pointer;
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
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
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

    .btn-skip {
      width: 100%;
      background: transparent;
      color: #6B819B;
      border: none;
      font-size: 14px;
      font-weight: 500;
      cursor: pointer;
      margin-top: 12px;
      transition: color 180ms ease;

      &:hover {
        color: #253247;
        text-decoration: underline;
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

    @media (max-width: 1024px) {
      .welcome-title { font-size: 28px; }
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
      }
      .illustration {
        max-height: 35vh;
      }
    }
  `]
})
export class CompleteProfileComponent {
  blocks = ['A', 'B', 'C', 'D'];
  floors = ['Ground', 'First', 'Second', 'Third', 'Fourth'];
  form   = { block: '', floor: '', room_no: '', phone: '' };
  loading = signal(false);

  constructor(private auth: AuthService, private router: Router, private snack: MatSnackBar) {}

  onSave(): void {
    if (!this.form.block || !this.form.floor || !this.form.room_no) {
      this.snack.open('Please select block, floor and enter room number.', 'Close', { duration: 3000 });
      return;
    }
    this.loading.set(true);
    this.auth.updateProfile(this.form).subscribe({
      next: () => {
        this.loading.set(false);
        this.snack.open('Profile saved!', 'OK', { duration: 2000 });
        this.router.navigate(['/student/home']);
      },
      error: () => {
        this.loading.set(false);
        this.snack.open('Failed to save profile. Try again.', 'Close', { duration: 3000 });
      }
    });
  }

  skip(): void { this.router.navigate(['/student/home']); }
}

