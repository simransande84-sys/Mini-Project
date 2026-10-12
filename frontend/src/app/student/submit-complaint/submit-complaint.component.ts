import { Component, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatSelectModule } from '@angular/material/select';
import { ComplaintService } from '../../core/services/complaint.service';
import { Complaint } from '../../core/models/complaint.model';


@Component({
  selector: 'app-submit-complaint',
  standalone: true,
  imports: [CommonModule, FormsModule, MatSnackBarModule, MatProgressSpinnerModule, MatSelectModule],
  template: `
    <div class="page-header">
      <h1>Submit Hostel Request</h1>
      <p>Log a facility or maintenance issue and track its resolution status.</p>
    </div>

    <div class="submit-grid">
      <!-- Main Form -->
      <div class="card">
        <form (ngSubmit)="onSubmit()" novalidate>
          
          <!-- Section 1: Visibility Scope -->
          <div class="form-section">
            <label class="section-label">Complaint Visibility Scope <span class="req">*</span></label>
            <div class="radio-grid">
              <label class="radio-card" [class.selected]="form.complaint_type === 'Public'">
                <input type="radio" [(ngModel)]="form.complaint_type" name="type" value="Public" />
                <div class="radio-content">
                  <div class="radio-header">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="15" height="15">
                      <circle cx="12" cy="12" r="10"/>
                      <line x1="2" y1="12" x2="22" y2="12"/>
                    </svg>
                    <span>Public Complaint</span>
                  </div>
                  <span class="radio-desc">Visible on resident noticeboard for community upvotes & support</span>
                </div>
              </label>

              <label class="radio-card" [class.selected]="form.complaint_type === 'Private'">
                <input type="radio" [(ngModel)]="form.complaint_type" name="type" value="Private" />
                <div class="radio-content">
                  <div class="radio-header">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="15" height="15">
                      <rect x="3" y="11" width="18" height="11" rx="2" ry="2"/>
                      <path d="M7 11V7a5 5 0 0 1 10 0v4"/>
                    </svg>
                    <span>Private Complaint</span>
                  </div>
                  <span class="radio-desc">Direct report to administration staff only</span>
                </div>
              </label>
            </div>
          </div>

          <!-- Section 2: Details -->
          <div class="form-section mb-0">
            <div class="field-group">
              <label class="field-label">Complaint Description <span class="req">*</span></label>
              <textarea [(ngModel)]="form.complaint_text" name="complaint_text" rows="4"
                        placeholder="Provide exact details of the defect, location inside the room/hallway, and urgency (10–1,000 characters)..."
                        minlength="10" maxlength="1000"
                        required></textarea>
            </div>

            <div class="field-group">
              <label class="field-label">Category <span class="req">*</span></label>
              <mat-select [(ngModel)]="form.category" name="category" placeholder="Select Category" required>
                <mat-option value="">Select Category</mat-option>
                <mat-option *ngFor="let c of categories" [value]="c">{{ c }}</mat-option>
              </mat-select>
            </div>

            <div class="field-group">
              <label class="field-label">How long has this issue existed? <span class="req">*</span></label>
              <mat-select [(ngModel)]="form.duration" name="duration" placeholder="Select Duration" required>
                <mat-option value="">Select Duration</mat-option>
                <mat-option *ngFor="let d of durationOptions" [value]="d">{{ d }}</mat-option>
              </mat-select>
            </div>
          </div>

          <div class="form-actions">
            <button type="submit" class="btn-primary full-width" [disabled]="submitting()">
              <mat-spinner *ngIf="submitting()" diameter="18"></mat-spinner>
              <span>{{ submitting() ? 'Submitting Request...' : 'Submit Complaint' }}</span>
            </button>
          </div>
        </form>
      </div>

      <!-- Right Column Cards -->
      <div class="right-panel">

        <!-- Success Confirmation Card -->
        <div class="card success-card" *ngIf="submitted()">
          <div class="success-icon-wrap">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="20" height="20">
              <polyline points="20 6 9 17 4 12"/>
            </svg>
          </div>
          <h3>Request Registered Successfully</h3>
          <p>Your complaint has been assigned ticket ID <strong>#{{ submitted()!.id }}</strong>.</p>
          <div class="submitted-meta">
            <div>
              <span class="meta-title">Status:</span>
              <strong>{{ submitted()!.status }}</strong>
            </div>
          </div>
          <button class="btn-secondary full-width mt-16" (click)="resetForm()">Submit Another Issue</button>
        </div>

      </div>
    </div>
  `,
  styles: [`
    .submit-grid {
      display: grid;
      grid-template-columns: 1fr 330px;
      gap: 24px;
      align-items: start;
      @media(max-width: 960px) {
        grid-template-columns: 1fr;
      }
    }

    .form-section {
      margin-bottom: 20px;
      padding-bottom: 20px;
      border-bottom: 1px solid var(--border-subtle);
      &.mb-0 {
        margin-bottom: 0;
        padding-bottom: 0;
        border-bottom: none;
      }
    }

    .section-label {
      display: block;
      font-size: 13px;
      font-weight: 600;
      color: var(--text-primary);
      margin-bottom: 10px;
    }
    .field-label {
      display: block;
      font-size: 13px;
      font-weight: 500;
      color: var(--text-primary);
      margin-bottom: 6px;
    }
    .req { color: var(--danger); }

    .radio-grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 12px;
    }
    .radio-card {
      border: 1px solid var(--border);
      border-radius: var(--radius-md);
      padding: 12px;
      cursor: pointer;
      display: flex;
      gap: 10px;
      background-color: var(--surface);
      transition: all 0.15s ease;

      input[type="radio"] {
        width: 15px;
        height: 15px;
        margin-top: 2px;
        accent-color: var(--primary);
      }

      &:hover {
        border-color: var(--border);
        background-color: var(--bg);
      }

      &.selected {
        border-color: var(--primary);
        background-color: var(--nav-active-bg);
        color: var(--nav-active-text);
      }
    }

    .radio-content {
      display: flex;
      flex-direction: column;
    }
    .radio-header {
      display: flex;
      align-items: center;
      gap: 6px;
      font-size: 13px;
      font-weight: 600;
    }
    .radio-desc {
      font-size: 11.5px;
      color: var(--text-muted);
      margin-top: 4px;
      line-height: 1.3;
    }

    .field-group {
      margin-bottom: 14px;
    }
    .grid-2-form {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 12px;
    }
    .grid-3-form {
      display: grid;
      grid-template-columns: 1fr 1fr 1fr;
      gap: 12px;
    }

    .form-actions {
      margin-top: 20px;
      padding-top: 16px;
      border-top: 1px solid var(--border);
    }
    .full-width {
      width: 100%;
    }

    .right-panel {
      display: flex;
      flex-direction: column;
      gap: 16px;
    }

    .preview-card {
      border-color: var(--primary-border);
      background-color: var(--primary-light);
    }
    .preview-header {
      display: flex;
      align-items: center;
      gap: 6px;
      font-size: 13px;
      font-weight: 600;
      color: var(--nav-active-text);
      margin-bottom: 12px;
    }
    .preview-body {
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 8px;
    }
    .preview-label {
      font-size: 12.5px;
      color: var(--text-secondary);
    }
    .preview-note {
      font-size: 12px;
      color: var(--text-muted);
      line-height: 1.4;
    }

    .success-card {
      border-color: var(--success-border);
      background-color: var(--success-bg);
      text-align: center;
      display: flex;
      flex-direction: column;
      align-items: center;

      h3 {
        font-size: 15px;
        font-weight: 700;
        color: var(--text-primary);
        margin: 10px 0 4px;
      }
      p {
        font-size: 13px;
        color: var(--text-secondary);
      }
    }

    .success-icon-wrap {
      width: 40px;
      height: 40px;
      border-radius: 50%;
      background-color: var(--success);
      color: #FFFFFF;
      display: flex;
      align-items: center;
      justify-content: center;
    }

    .submitted-meta {
      width: 100%;
      margin-top: 12px;
      padding-top: 12px;
      border-top: 1px solid var(--success-border);
      display: flex;
      justify-content: space-between;
      font-size: 12.5px;

      .meta-title {
        color: var(--text-muted);
        margin-right: 4px;
      }
    }
    .mt-16 { margin-top: 16px; }

    .info-card {
      background-color: var(--surface);
    }
    .info-title {
      display: flex;
      align-items: center;
      gap: 6px;
      font-size: 13.5px;
      font-weight: 600;
      color: var(--text-primary);
      margin-bottom: 12px;
    }

    .steps-list {
      list-style: none;
      display: flex;
      flex-direction: column;
      gap: 10px;

      li {
        display: flex;
        align-items: flex-start;
        gap: 10px;
        font-size: 12.5px;
        color: var(--text-secondary);
        line-height: 1.4;

        span {
          width: 18px;
          height: 18px;
          border-radius: 50%;
          background: var(--sidebar-bg);
          color: var(--text-primary);
          font-size: 11px;
          font-weight: 600;
          display: flex;
          align-items: center;
          justify-content: center;
          flex-shrink: 0;
          margin-top: 1px;
        }
      }
    }
  `]
})
export class SubmitComplaintComponent {
  types      = ['Public', 'Private'];
  categories = [
    'AC', 'Cleanliness', 'Door', 'Drainage', 'Electricity', 'Fan', 'Fire Safety',
    'Furniture', 'Internet', 'Laundry', 'Leakage', 'Lift', 'Light', 'Mattress',
    'Medical', 'Mess', 'Noise', 'Parking', 'Pest Control', 'Ragging/Harassment',
    'Room Allocation', 'Security', 'Structural', 'Study Room', 'Washroom',
    'Water Cooler', 'Water Supply', 'WiFi', 'Window', 'Other'
  ];

  // Exact Duration_Standardized values from training dataset (Dataset_duration.csv)
  durationOptions = [
    '1 hour', '2 hours', '3 hours', '4 hours', '5 hours', '6 hours', '8 hours',
    '1 day', '2 days', '3 days', '4 days', '6 days', '8 days', '12 days',
    '1 week', '2 weeks', '4 weeks'
  ];

  form = {
    complaint_type: 'Public', complaint_text: '', category: '',
    duration: ''
  };

  submitted = signal<Complaint | null>(null);
  submitting = signal(false);

  constructor(private svc: ComplaintService, private snack: MatSnackBar) {}

  onSubmit(): void {
    // Prevent duplicate submissions while a request is already in-flight
    if (this.submitting()) return;

    const { complaint_text, category, complaint_type, duration } = this.form;
    if (!complaint_text.trim() || !category || !duration) {
      this.snack.open('Please fill all required fields.', 'Close', { duration: 3000 }); return;
    }
    if (complaint_text.trim().length < 10) {
      this.snack.open('Complaint description must be at least 10 characters.', 'Close', { duration: 3000 }); return;
    }
    if (complaint_text.trim().length > 1000) {
      this.snack.open('Complaint description cannot exceed 1,000 characters.', 'Close', { duration: 3000 }); return;
    }

    this.submitting.set(true);
    this.svc.create({ complaint_text, complaint_type: complaint_type as any, category, duration }).subscribe({
      next: c => {
        // Reset form FIRST so stale data never persists on the page
        this.form = { complaint_type: 'Public', complaint_text: '', category: '', duration: '' };
        this.submitted.set(c);
        this.submitting.set(false);
      },
      error: err => {
        // Keep form data intact so the student can retry without re-entering
        this.submitting.set(false);
        let errMsg = 'Submission failed. Try again.';
        if (err.error) {
          if (typeof err.error === 'string') {
            errMsg = err.error;
          } else if (Array.isArray(err.error) && err.error.length > 0) {
            errMsg = err.error[0];
          } else if (typeof err.error === 'object') {
            const values = Object.values(err.error);
            if (values.length > 0) {
              const firstVal: any = values[0];
              if (Array.isArray(firstVal) && firstVal.length > 0) {
                errMsg = firstVal[0];
              } else if (typeof firstVal === 'string') {
                errMsg = firstVal;
              }
            }
          }
        }
        this.snack.open(errMsg, 'Close', { duration: 5000 });
      }
    });
  }

  resetForm(): void {
    this.form = { complaint_type: 'Public', complaint_text: '', category: '', duration: '' };
    this.submitted.set(null);
  }
}
