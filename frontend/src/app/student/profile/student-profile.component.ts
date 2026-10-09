import { Component, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { AuthService } from '../../core/services/auth.service';
import { StudentProfile, User } from '../../core/models/user.model';

@Component({
  selector: 'app-student-profile',
  standalone: true,
  imports: [CommonModule, FormsModule, MatSnackBarModule, MatProgressSpinnerModule],
  template: `
    <div class="page-header">
      <h1>Resident Profile</h1>
      <p>Manage your account identity, contact information, and assigned hostel accommodation details.</p>
    </div>

    <div *ngIf="loading()" class="loading-center">
      <mat-spinner diameter="32"></mat-spinner>
    </div>

    <div class="profile-grid" *ngIf="!loading()">
      <!-- User Account Card -->
      <div class="card user-card">
        <div class="avatar-circle">{{ initial() }}</div>
        <h2 class="user-fullname">{{ user()?.first_name || user()?.username }}</h2>
        <span class="role-tag">Resident Student</span>

        <div class="info-list">
          <div class="info-row">
            <span class="info-label">Roll Number</span>
            <span class="info-val">{{ profile()?.roll_no || 'N/A' }}</span>
          </div>
          <div class="info-row">
            <span class="info-label">Username</span>
            <span class="info-val">{{ user()?.username }}</span>
          </div>
          <div class="info-row">
            <span class="info-label">Email Address</span>
            <span class="info-val">{{ user()?.email }}</span>
          </div>
        </div>
      </div>

      <!-- Update Hostel Form Card -->
      <div class="card form-card">
        <h2 class="section-title">Hostel Allocation & Contact Information</h2>
        <form (ngSubmit)="onSave()" novalidate>
          <div class="grid-2-form">
            <div class="field-group">
              <label class="field-label">Assigned Block</label>
              <select [(ngModel)]="form.block" name="block" required>
                <option value="">Select Block</option>
                <option *ngFor="let b of blocks" [value]="b">Block {{ b }}</option>
              </select>
            </div>

            <div class="field-group">
              <label class="field-label">Floor</label>
              <select [(ngModel)]="form.floor" name="floor" required>
                <option value="">Select Floor</option>
                <option *ngFor="let f of floors" [value]="f">{{ f }} Floor</option>
              </select>
            </div>
          </div>

          <div class="field-group">
            <label class="field-label">Room Number</label>
            <input type="text" [(ngModel)]="form.room_no" name="room_no" placeholder="e.g. 210" required />
          </div>

          <div class="field-group">
            <label class="field-label">Contact Phone Number</label>
            <input type="tel" [(ngModel)]="form.phone" name="phone" placeholder="e.g. 9876543210" />
          </div>

          <div class="form-actions">
            <button type="submit" class="btn-primary" [disabled]="saving()">
              <mat-spinner *ngIf="saving()" diameter="18"></mat-spinner>
              <span>{{ saving() ? 'Saving Changes...' : 'Update Details' }}</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  `,
  styles: [`
    .loading-center {
      display: flex;
      justify-content: center;
      padding: 60px;
    }

    .profile-grid {
      display: grid;
      grid-template-columns: 300px 1fr;
      gap: 24px;
      align-items: start;
      @media(max-width: 840px) {
        grid-template-columns: 1fr;
      }
    }

    .user-card {
      display: flex;
      flex-direction: column;
      align-items: center;
      text-align: center;
      padding: 28px 24px;
    }

    .avatar-circle {
      width: 72px;
      height: 72px;
      border-radius: 50%;
      background: var(--primary-light);
      border: 2px solid var(--primary-border);
      color: var(--primary);
      font-size: 28px;
      font-weight: 700;
      display: flex;
      align-items: center;
      justify-content: center;
      margin-bottom: 12px;
    }

    .user-fullname {
      font-size: 17px;
      font-weight: 700;
      color: var(--text-primary);
    }
    .role-tag {
      font-size: 11.5px;
      font-weight: 600;
      background: var(--sidebar-bg);
      color: var(--text-secondary);
      padding: 2px 10px;
      border-radius: var(--radius-sm);
      margin: 6px 0 20px;
    }

    .info-list {
      width: 100%;
      border-top: 1px solid var(--border-subtle);
      padding-top: 16px;
      display: flex;
      flex-direction: column;
      gap: 12px;
    }
    .info-row {
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-size: 13px;
    }
    .info-label {
      color: var(--text-muted);
    }
    .info-val {
      font-weight: 600;
      color: var(--text-primary);
    }

    .grid-2-form {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 12px;
    }
    .field-group {
      margin-bottom: 16px;
    }
    .field-label {
      display: block;
      font-size: 13px;
      font-weight: 500;
      color: var(--text-primary);
      margin-bottom: 6px;
    }

    .form-actions {
      margin-top: 20px;
      padding-top: 16px;
      border-top: 1px solid var(--border-subtle);
    }
  `]
})
export class StudentProfileComponent implements OnInit {
  user    = signal<User | null>(null);
  profile = signal<StudentProfile | null>(null);
  loading = signal(true);
  saving  = signal(false);

  blocks = ['A', 'B', 'C', 'D'];
  floors = ['Ground', 'First', 'Second', 'Third'];

  form = { block: '', floor: '', room_no: '', phone: '' };

  constructor(private auth: AuthService, private snack: MatSnackBar) {}

  ngOnInit(): void {
    this.user.set(this.auth.currentUser());
    this.auth.getProfile().subscribe({
      next: p => {
        this.profile.set(p);
        this.form = {
          block: p.block || '',
          floor: p.floor || '',
          room_no: p.room_no || '',
          phone: p.phone || ''
        };
        this.loading.set(false);
      },
      error: () => this.loading.set(false)
    });
  }

  initial(): string {
    return (this.user()?.first_name?.[0] || 'S').toUpperCase();
  }

  onSave(): void {
    this.saving.set(true);
    this.auth.updateProfile(this.form).subscribe({
      next: updated => {
        this.profile.set(updated);
        this.saving.set(false);
        this.snack.open('Hostel details updated successfully!', 'OK', { duration: 2500 });
      },
      error: () => {
        this.saving.set(false);
        this.snack.open('Failed to update details.', 'Close', { duration: 3000 });
      }
    });
  }
}
