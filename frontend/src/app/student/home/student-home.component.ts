import { Component, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { ComplaintService } from '../../core/services/complaint.service';
import { AuthService } from '../../core/services/auth.service';
import { Complaint } from '../../core/models/complaint.model';

import { StatusBadgeComponent } from '../../shared/components/status-badge/status-badge.component';

@Component({
  selector: 'app-student-home',
  standalone: true,
  imports: [CommonModule, RouterModule, StatusBadgeComponent],
  template: `
    <div class="page-header">
      <h1>Welcome back, {{ auth.currentUser()?.first_name || 'Student' }}</h1>
      <p>Here’s an overview of your hostel requests and community issues.</p>
    </div>

    <!-- Summary KPI Cards -->
    <div class="grid-4 mb-24">
      <div class="kpi-card">
        <div class="kpi-icon-wrap icon-neutral">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
            <path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z"/>
            <path d="M14 2v4a2 2 0 0 0 2 2h4"/>
            <path d="M10 9H8"/>
            <path d="M16 13H8"/>
            <path d="M16 17H8"/>
          </svg>
        </div>
        <div class="kpi-info">
          <div class="kpi-label">My Submissions</div>
          <div class="kpi-value">{{ myComplaints().length }}</div>
        </div>
      </div>

      <div class="kpi-card">
        <div class="kpi-icon-wrap icon-amber">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="12" r="10"/>
            <polyline points="12 6 12 12 16 14"/>
          </svg>
        </div>
        <div class="kpi-info">
          <div class="kpi-label">Pending Action</div>
          <div class="kpi-value">{{ pendingCount() }}</div>
        </div>
      </div>

      <div class="kpi-card">
        <div class="kpi-icon-wrap icon-green">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="12" r="10"/>
            <path d="m9 12 2 2 4-4"/>
          </svg>
        </div>
        <div class="kpi-info">
          <div class="kpi-label">Resolved</div>
          <div class="kpi-value">{{ resolvedCount() }}</div>
        </div>
      </div>

      <div class="kpi-card">
        <div class="kpi-icon-wrap icon-blue">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
            <path d="M7 10v12"/>
            <path d="M15 5.88 14 10h5.83a2 2 0 0 1 1.92 2.56l-2.33 8A2 2 0 0 1 17.5 22H4a2 2 0 0 1-2-2v-8a2 2 0 0 1 2-2h2.76a2 2 0 0 0 1.79-1.11L12 2a3.13 3.13 0 0 1 3 3.88Z"/>
          </svg>
        </div>
        <div class="kpi-info">
          <div class="kpi-label">Supported Issues</div>
          <div class="kpi-value">{{ supportedCount() }}</div>
        </div>
      </div>
    </div>

    <!-- Action Gateway Grid -->
    <div class="grid-2 mb-24">
      <a routerLink="/student/submit" class="action-card">
        <div class="action-icon-box">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
            <path d="M5 12h14"/>
            <path d="M12 5v14"/>
          </svg>
        </div>
        <div class="action-content">
          <div class="action-title">Submit New Complaint</div>
          <div class="action-desc">Report a hostel issue and track its resolution.</div>
        </div>
        <svg class="action-arrow" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
          <path d="m9 18 6-6-6-6"/>
        </svg>
      </a>

      <a routerLink="/student/public" class="action-card">
        <div class="action-icon-box">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="12" r="10"/>
            <path d="M12 2a14.5 14.5 0 0 0 0 20 14.5 14.5 0 0 0 0-20"/>
            <path d="M2 12h20"/>
          </svg>
        </div>
        <div class="action-content">
          <div class="action-title">Public Noticeboard</div>
          <div class="action-desc">See issues reported by other residents.</div>
        </div>
        <svg class="action-arrow" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
          <path d="m9 18 6-6-6-6"/>
        </svg>
      </a>
    </div>

    <!-- Recent Complaints Table -->
    <div class="table-section">
      <div class="table-header">
        <div>
          <h2 class="section-title mb-0">Recent Submissions</h2>
          <p class="section-sub">List of your recent issues logged into the system</p>
        </div>
        <a routerLink="/student/mine" class="view-all-link">
          View All
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" width="14" height="14">
            <path d="m9 18 6-6-6-6"/>
          </svg>
        </a>
      </div>

      <div *ngIf="myComplaints().length === 0" class="empty-state">
        <div class="empty-icon-wrap">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
            <polyline points="14 2 14 8 20 8"/>
          </svg>
        </div>
        <p class="empty-title">No complaints submitted</p>
        <p class="empty-desc">You haven't submitted any hostel requests yet.</p>
        <a routerLink="/student/submit" class="btn-primary">Submit First Complaint</a>
      </div>

      <div class="table-wrap" *ngIf="myComplaints().length > 0">
        <table class="hs-table">
          <thead>
            <tr>
              <th>Description</th>
              <th>Category</th>

              <th>Status</th>
              <th>Date</th>
            </tr>
          </thead>
          <tbody>
            <tr *ngFor="let c of myComplaints().slice(0,5)">
              <td class="text-cell">{{ c.complaint_text | slice:0:70 }}{{ c.complaint_text.length > 70 ? '…' : '' }}</td>
              <td><span class="category-chip">{{ c.category }}</span></td>

              <td><app-status-badge [status]="c.status" /></td>
              <td class="date-cell">{{ c.created_at | date:'dd MMM yyyy' }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  `,
  styles: [`
    .mb-24 { margin-bottom: 24px; }
    .mb-0 { margin-bottom: 0; }

    .icon-neutral { color: var(--text-muted); }
    .icon-amber   { color: #D97706; }
    .icon-green   { color: #2E7D32; }
    .icon-blue    { color: var(--primary); }

    .action-card {
      background: var(--surface-white);
      border: 1px solid var(--border);
      border-radius: var(--radius-sm);
      padding: 16px 20px;
      display: flex;
      align-items: center;
      gap: 16px;
      text-decoration: none;
      color: var(--text-primary);
      box-shadow: none; /* Removed heavy shadow */
      transition: border-color 200ms ease-in-out, background-color 200ms ease-in-out;

      &:hover {
        background-color: var(--nav-hover-bg);
        border-color: var(--border);

        .action-arrow {
          transform: translateX(3px);
          color: var(--primary);
        }
      }
    }

    .action-icon-box {
      color: var(--primary);
      display: flex;
      align-items: center;
      justify-content: center;
      flex-shrink: 0;

      svg {
        width: 20px;
        height: 20px;
      }
    }

    .action-content {
      flex: 1;
    }
    .action-title {
      font-size: 14.5px;
      font-weight: 600;
      color: var(--text-primary);
    }
    .action-desc {
      font-size: 13px;
      color: var(--text-muted);
      margin-top: 2px;
      line-height: 1.4;
    }

    .action-arrow {
      width: 18px;
      height: 18px;
      color: var(--text-muted);
      transition: transform 200ms ease-in-out, color 200ms ease-in-out;
      flex-shrink: 0;
    }

    .table-section {
      background: var(--surface-white);
      border: 1px solid var(--border);
      border-radius: 6px;
      padding: 16px;
    }

    .table-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 12px;
    }
    .section-sub {
      font-size: 12.5px;
      color: var(--text-muted);
      margin-top: 2px;
    }

    .view-all-link {
      color: var(--primary);
      text-decoration: none;
      font-size: 13px;
      font-weight: 500;
      display: inline-flex;
      align-items: center;
      gap: 4px;
      transition: color 180ms ease-in-out;

      &:hover {
        color: var(--primary-hover);
        text-decoration: underline;
      }
    }

    .table-wrap {
      overflow-x: auto;
    }
    .text-cell {
      max-width: 320px;
      font-weight: 450;
    }
    .category-chip {
      font-size: 12px;
      background: var(--bg);
      color: var(--text-secondary);
      padding: 2px 8px;
      border-radius: var(--radius-sm);
      font-weight: 500;
    }
    .date-cell {
      color: var(--text-muted);
      font-size: 12.5px;
    }

    .empty-state {
      text-align: center;
      padding: 40px 20px;
      display: flex;
      flex-direction: column;
      align-items: center;
    }
    .empty-icon-wrap {
      width: 48px;
      height: 48px;
      border-radius: 50%;
      background: var(--sidebar-bg);
      color: var(--text-muted);
      display: flex;
      align-items: center;
      justify-content: center;
      margin-bottom: 12px;

      svg { width: 22px; height: 22px; }
    }
    .empty-title {
      font-size: 14px;
      font-weight: 600;
      color: var(--text-primary);
    }
    .empty-desc {
      font-size: 13px;
      color: var(--text-muted);
      margin: 4px 0 16px;
    }
  `]
})
export class StudentHomeComponent implements OnInit {
  myComplaints  = signal<Complaint[]>([]);

  pendingCount  = signal(0);
  resolvedCount = signal(0);
  supportedCount= signal(0);

  constructor(public auth: AuthService, private svc: ComplaintService) {}

  ngOnInit(): void {
    this.svc.getMine().subscribe(data => {
      this.myComplaints.set(data);
      this.pendingCount.set(data.filter(c => c.status === 'Pending').length);
      this.resolvedCount.set(data.filter(c => c.status === 'Resolved').length);
      this.supportedCount.set(data.filter(c => c.user_has_voted).length);
    });
  }
}
