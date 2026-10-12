import { Component, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatSelectModule } from '@angular/material/select';
import { ComplaintService } from '../../core/services/complaint.service';
import { VoteService } from '../../core/services/vote.service';
import { AuthService } from '../../core/services/auth.service';
import { Complaint } from '../../core/models/complaint.model';

import { StatusBadgeComponent } from '../../shared/components/status-badge/status-badge.component';

@Component({
  selector: 'app-public-feed',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    MatSnackBarModule,
    MatProgressSpinnerModule,
    MatSelectModule,
    StatusBadgeComponent
  ],
  template: `
    <div class="page-header">
      <h1>Public Noticeboard Feed</h1>
      <p>Browse complaints submitted by residents. Support issues affecting your block to help the community.</p>
    </div>

    <!-- Toolbar & Filters -->
    <div class="card mb-20">
      <div class="filters-wrap">
        <div class="search-box">
          <svg class="search-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="11" cy="11" r="8"/>
            <line x1="21" y1="21" x2="16.65" y2="16.65"/>
          </svg>
          <input type="text" [(ngModel)]="search" (ngModelChange)="applyFilter()"
                 placeholder="Search complaints description..." class="search-input" />
        </div>

        <div class="filter-controls">
          <mat-select [(ngModel)]="filterCategory" (selectionChange)="applyFilter()" placeholder="All Categories" class="filter-select">
            <mat-option value="">All Categories</mat-option>
            <mat-option *ngFor="let cat of categories" [value]="cat">{{ cat }}</mat-option>
          </mat-select>

          <mat-select [(ngModel)]="filterBlock" (selectionChange)="applyFilter()" placeholder="All Blocks" class="filter-select">
            <mat-option value="">All Blocks</mat-option>
            <mat-option *ngFor="let b of blocks" [value]="b">Block {{ b }}</mat-option>
          </mat-select>

          <mat-select [(ngModel)]="sortBy" (selectionChange)="applyFilter()" placeholder="Sort By" class="filter-select">
            <mat-option value="support">Sort: Upvote Count</mat-option>
            <mat-option value="recent">Sort: Most Recent</mat-option>
          </mat-select>
        </div>
      </div>
    </div>

    <div *ngIf="loading()" class="loading-center">
      <mat-spinner diameter="36"></mat-spinner>
    </div>

    <div *ngIf="!loading() && filtered().length === 0" class="card empty-state">
      <div class="empty-icon-wrap">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" width="24" height="24">
          <circle cx="12" cy="12" r="10"/>
          <line x1="2" y1="12" x2="22" y2="12"/>
        </svg>
      </div>
      <p class="empty-title">No public requests found</p>
      <p class="empty-desc">No complaints match your current filter parameters.</p>
    </div>

    <!-- Feed Grid -->
    <div class="feed-grid" *ngIf="!loading() && filtered().length > 0">
      <div class="card complaint-card" *ngFor="let c of filtered()">
        <div class="card-top">
          <div class="meta-tags">
            <span class="tag-category">{{ c.category }}</span>
            <span class="tag-location">Block {{ c.block }}</span>
            <span *ngIf="c.room_no" class="tag-location">Room {{ c.room_no }}</span>
          </div>
        </div>

        <div class="complaint-body">
          <p>{{ c.complaint_text }}</p>
        </div>

        <div class="card-footer">
          <div class="footer-left">
            <app-status-badge [status]="c.status" />
            <span class="complaint-date">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="13" height="13">
                <rect x="3" y="4" width="18" height="18" rx="2" ry="2"/>
                <line x1="16" y1="2" x2="16" y2="6"/>
                <line x1="8" y1="2" x2="8" y2="6"/>
                <line x1="3" y1="10" x2="21" y2="10"/>
              </svg>
              {{ c.created_at | date:'dd MMM yyyy' }}
            </span>
          </div>

          <div class="support-action">
            <button class="btn-support"
                    [class.supported]="c.user_has_voted"
                    [disabled]="c.user_has_voted || votingId() === c.id"
                    (click)="onSupport(c)">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14">
                <path d="M14 9V5a3 3 0 0 0-3-3l-4 9v11h11.28a2 2 0 0 0 2-1.7l1.38-9a2 2 0 0 0-2-2.3zM7 22H4a2 2 0 0 1-2-2v-7a2 2 0 0 1 2-2h3"/>
              </svg>
              <span *ngIf="votingId() !== c.id">
                {{ c.user_has_voted ? 'Upvoted' : 'Support Issue' }} ({{ c.support_count }})
              </span>
              <span *ngIf="votingId() === c.id">Updating...</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .mb-20 { margin-bottom: 20px; }

    .filters-wrap {
      display: flex;
      gap: 12px;
      align-items: center;
      flex-wrap: wrap;
    }

    .search-box {
      position: relative;
      flex: 1;
      min-width: 240px;
    }
    .search-icon {
      position: absolute;
      left: 10px;
      top: 10px;
      width: 16px;
      height: 16px;
      color: var(--text-muted);
    }
    .search-input {
      padding-left: 34px !important;
    }

    .filter-controls {
      display: flex;
      gap: 10px;
      flex-wrap: wrap;
    }

    .filter-select {
      min-width: 160px;
    }

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

    .feed-grid {
      display: flex;
      flex-direction: column;
      gap: 14px;
    }

    .complaint-card {
      display: flex;
      flex-direction: column;
      gap: 12px;
      padding: 20px;
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: var(--radius-lg);

      &:hover {
        border-color: var(--border);
      }
    }

    .card-top {
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 12px;
      flex-wrap: wrap;
    }

    .meta-tags {
      display: flex;
      gap: 6px;
      align-items: center;
    }
    .tag-category {
      background: var(--primary-light);
      color: var(--primary);
      font-weight: 600;
      font-size: 12px;
      padding: 2px 8px;
      border-radius: var(--radius-sm);
    }
    .tag-location {
      background: var(--sidebar-bg);
      color: var(--text-secondary);
      font-weight: 500;
      font-size: 12px;
      padding: 2px 8px;
      border-radius: var(--radius-sm);
    }

    .complaint-body p {
      font-size: 14px;
      line-height: 1.55;
      color: var(--text-primary);
    }

    .card-footer {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding-top: 12px;
      border-top: 1px solid var(--border-subtle);
      flex-wrap: wrap;
      gap: 12px;
    }
    .footer-left {
      display: flex;
      align-items: center;
      gap: 12px;
    }
    .complaint-date {
      display: inline-flex;
      align-items: center;
      gap: 4px;
      font-size: 12px;
      color: var(--text-muted);
    }

    .btn-support {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      height: 32px;
      padding: 0 12px;
      border-radius: var(--radius-md);
      border: 1px solid var(--primary);
      background: transparent;
      color: var(--primary);
      font-size: 12.5px;
      font-weight: 500;
      cursor: pointer;
      transition: all 0.15s ease;

      &:hover:not(:disabled) {
        background: var(--primary-light);
      }

      &.supported {
        border-color: var(--success);
        color: var(--success);
        background: var(--success-bg);
        cursor: default;
      }

      &:disabled {
        opacity: 0.65;
        cursor: not-allowed;
      }
    }
  `]
})
export class PublicFeedComponent implements OnInit {
  complaints     = signal<Complaint[]>([]);
  filtered       = signal<Complaint[]>([]);
  loading        = signal(true);
  votingId       = signal<number | null>(null);

  search         = '';
  filterCategory = '';
  filterBlock    = '';
  sortBy         = 'support';

  categories = [
    'AC', 'Cleanliness', 'Door', 'Drainage', 'Electricity', 'Fan', 'Fire Safety',
    'Furniture', 'Internet', 'Laundry', 'Leakage', 'Lift', 'Light', 'Mattress',
    'Medical', 'Mess', 'Noise', 'Parking', 'Pest Control', 'Ragging/Harassment',
    'Room Allocation', 'Security', 'Structural', 'Study Room', 'Washroom',
    'Water Cooler', 'Water Supply', 'WiFi', 'Window', 'Other'
  ];
  blocks     = ['A', 'B', 'C', 'D'];

  constructor(
    private compSvc: ComplaintService,
    private voteSvc: VoteService,
    public auth: AuthService,
    private snack: MatSnackBar
  ) {}

  ngOnInit(): void {
    this.load();
  }

  load(): void {
    this.loading.set(true);
    this.compSvc.getPublic().subscribe({
      next: data => {
        this.complaints.set(data);
        this.applyFilter();
        this.loading.set(false);
      },
      error: () => this.loading.set(false)
    });
  }

  applyFilter(): void {
    let data = [...this.complaints()];
    if (this.search) {
      const q = this.search.toLowerCase();
      data = data.filter(c => c.complaint_text.toLowerCase().includes(q));
    }
    if (this.filterCategory) {
      data = data.filter(c => c.category === this.filterCategory);
    }
    if (this.filterBlock) {
      data = data.filter(c => c.block === this.filterBlock);
    }

    if (this.sortBy === 'support') {
      data.sort((a, b) => b.support_count - a.support_count);
    } else {
      data.sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime());
    }

    this.filtered.set(data);
  }

  onSupport(c: Complaint): void {
    if (!this.auth.isLoggedIn()) {
      this.snack.open('Please login to support complaints.', 'Close', { duration: 3000 });
      return;
    }
    if (c.user_has_voted) return;

    this.votingId.set(c.id);
    this.voteSvc.castVote(c.id).subscribe({
      next: res => {
        this.votingId.set(null);
        const updated = this.complaints().map(item => {
          if (item.id === c.id) {
            return {
              ...item,
              support_count: res.support_count,
              predicted_priority: res.predicted_priority,
              user_has_voted: true
            };
          }
          return item;
        });
        this.complaints.set(updated);
        this.applyFilter();
        this.snack.open('Support added! Thank you for your upvote.', 'OK', { duration: 2500 });
      },
      error: err => {
        this.votingId.set(null);
        const msg = err?.error?.error || 'Failed to add support.';
        this.snack.open(msg, 'Close', { duration: 3000 });
      }
    });
  }
}
