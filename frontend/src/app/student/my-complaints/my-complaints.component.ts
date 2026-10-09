import { Component, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { ComplaintService } from '../../core/services/complaint.service';
import { Complaint } from '../../core/models/complaint.model';

import { StatusBadgeComponent } from '../../shared/components/status-badge/status-badge.component';

@Component({
  selector: 'app-my-complaints',
  standalone: true,
  imports: [CommonModule, MatProgressSpinnerModule, StatusBadgeComponent],
  template: `
    <div class="page-header">
      <h1>My Requests History</h1>
      <p>Log of all maintenance, infrastructure, and facility complaints submitted by your account.</p>
    </div>

    <div *ngIf="loading()" class="loading-center">
      <mat-spinner diameter="32"></mat-spinner>
    </div>

    <div class="card" *ngIf="!loading()">
      <div *ngIf="complaints().length === 0" class="empty-state">
        <div class="empty-icon-wrap">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" width="24" height="24">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
            <polyline points="14 2 14 8 20 8"/>
          </svg>
        </div>
        <p class="empty-title">No complaints registered</p>
        <p class="empty-desc">You have not logged any requests yet.</p>
      </div>

      <div class="table-wrap" *ngIf="complaints().length > 0">
        <table class="hs-table">
          <thead>
            <tr>
              <th>Ticket ID</th>
              <th>Description</th>
              <th>Category</th>
              <th>Location</th>
              <th>Scope</th>

              <th>Status</th>
              <th>Upvotes</th>
              <th>Date Created</th>
            </tr>
          </thead>
          <tbody>
            <tr *ngFor="let c of complaints()">
              <td class="id-cell">#{{ c.id }}</td>
              <td class="text-cell">{{ c.complaint_text | slice:0:80 }}{{ c.complaint_text.length > 80 ? '…' : '' }}</td>
              <td><span class="category-tag">{{ c.category }}</span></td>
              <td>Block {{ c.block }} {{ c.room_no ? '- R' + c.room_no : '' }}</td>
              <td>
                <span class="scope-chip" [class.public]="c.complaint_type === 'Public'">
                  <svg *ngIf="c.complaint_type === 'Public'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="12" height="12">
                    <circle cx="12" cy="12" r="10"/>
                    <line x1="2" y1="12" x2="22" y2="12"/>
                  </svg>
                  <svg *ngIf="c.complaint_type === 'Private'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="12" height="12">
                    <rect x="3" y="11" width="18" height="11" rx="2" ry="2"/>
                    <path d="M7 11V7a5 5 0 0 1 10 0v4"/>
                  </svg>
                  {{ c.complaint_type }}
                </span>
              </td>

              <td><app-status-badge [status]="c.status" /></td>
              <td class="upvote-cell">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="13" height="13">
                  <path d="M14 9V5a3 3 0 0 0-3-3l-4 9v11h11.28a2 2 0 0 0 2-1.7l1.38-9a2 2 0 0 0-2-2.3zM7 22H4a2 2 0 0 1-2-2v-7a2 2 0 0 1 2-2h3"/>
                </svg>
                <span>{{ c.support_count }}</span>
              </td>
              <td class="date-cell">{{ c.created_at | date:'dd MMM yyyy' }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  `,
  styles: [`
    .loading-center {
      display: flex;
      justify-content: center;
      padding: 60px;
    }

    .empty-state {
      text-align: center;
      padding: 48px;
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
    }
    .empty-title {
      font-size: 14px;
      font-weight: 600;
      color: var(--text-primary);
    }
    .empty-desc {
      font-size: 13px;
      color: var(--text-muted);
      margin-top: 4px;
    }

    .table-wrap {
      overflow-x: auto;
    }
    .id-cell {
      font-weight: 600;
      color: var(--text-secondary);
      font-size: 12.5px;
    }
    .text-cell {
      max-width: 280px;
      font-weight: 450;
    }
    .category-tag {
      font-size: 12px;
      background: var(--sidebar-bg);
      color: var(--text-secondary);
      padding: 2px 8px;
      border-radius: var(--radius-sm);
      font-weight: 500;
    }
    .scope-chip {
      font-size: 11.5px;
      padding: 2px 8px;
      border-radius: var(--radius-sm);
      font-weight: 500;
      background: var(--sidebar-bg);
      color: var(--text-muted);
      display: inline-flex;
      align-items: center;
      gap: 4px;

      &.public {
        background: var(--primary-light);
        color: var(--primary);
      }
    }
    .upvote-cell {
      display: inline-flex;
      align-items: center;
      gap: 4px;
      color: var(--text-secondary);
      font-size: 13px;
      font-weight: 500;
    }
    .date-cell {
      color: var(--text-muted);
      font-size: 12.5px;
    }
  `]
})
export class MyComplaintsComponent implements OnInit {
  complaints = signal<Complaint[]>([]);
  loading    = signal(true);

  constructor(private svc: ComplaintService) {}

  ngOnInit(): void {
    this.svc.getMine().subscribe({
      next: data => { this.complaints.set(data); this.loading.set(false); },
      error: () => this.loading.set(false)
    });
  }
}
