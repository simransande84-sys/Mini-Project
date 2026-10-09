import { Component, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatSelectModule } from '@angular/material/select';
import { ComplaintService } from '../../core/services/complaint.service';
import { Complaint, ComplaintStatus } from '../../core/models/complaint.model';
import { PriorityBadgeComponent } from '../../shared/components/priority-badge/priority-badge.component';

@Component({
  selector: 'app-admin-complaints',
  standalone: true,
  imports: [CommonModule, FormsModule, MatSnackBarModule, MatProgressSpinnerModule, MatSelectModule, PriorityBadgeComponent],
  template: `
    <div class="page-header">
      <h1>All Complaints Queue</h1>
      <p>Search, filter, update statuses, or purge complaint entries across all hostel blocks.</p>
    </div>

    <!-- Filter Bar -->
    <div class="card filters-card mb-20">
      <div class="filters">
        <div class="search-box">
          <svg class="search-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="11" cy="11" r="8"/>
            <line x1="21" y1="21" x2="16.65" y2="16.65"/>
          </svg>
          <input type="text" [(ngModel)]="search" (ngModelChange)="applyFilter()"
                 placeholder="Search complaints..." class="search-input" />
        </div>

        <mat-select [(ngModel)]="filterPriority" (selectionChange)="applyFilter()" placeholder="All Priorities" class="filter-select">
          <mat-option value="">All Priorities</mat-option>
          <mat-option *ngFor="let p of priorities" [value]="p">{{ p }}</mat-option>
        </mat-select>

        <mat-select [(ngModel)]="filterStatus" (selectionChange)="applyFilter()" placeholder="All Statuses" class="filter-select">
          <mat-option value="">All Statuses</mat-option>
          <mat-option *ngFor="let s of statuses" [value]="s">{{ s }}</mat-option>
        </mat-select>

        <mat-select [(ngModel)]="filterBlock" (selectionChange)="applyFilter()" placeholder="All Blocks" class="filter-select">
          <mat-option value="">All Blocks</mat-option>
          <mat-option *ngFor="let b of blocks" [value]="b">Block {{ b }}</mat-option>
        </mat-select>

        <button class="btn-secondary btn-clear" (click)="clearFilters()">Clear</button>
      </div>
      <div class="results-count">Displaying {{ filtered().length }} of {{ complaints().length }} entries</div>
    </div>

    <!-- Table -->
    <div class="card">
      <div *ngIf="loading()" class="loading-center">
        <mat-spinner diameter="36"></mat-spinner>
      </div>

      <div class="table-wrap" *ngIf="!loading()">
        <table class="hs-table">
          <thead>
            <tr>
              <th>Ticket ID</th>
              <th>Description</th>
              <th>Scope</th>
              <th>Location</th>
              <th>Category</th>
              <th>Priority Score</th>
              <th>Status Action</th>
              <th>Upvotes</th>
              <th>Date</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr *ngFor="let c of paginated()">
              <td class="id-cell">#{{ c.id }}</td>
              <td class="text-cell">{{ c.complaint_text | slice:0:70 }}{{ c.complaint_text.length > 70 ? '…' : '' }}</td>
              <td>
                <span class="type-chip" [class.public]="c.complaint_type === 'Public'">
                  {{ c.complaint_type }}
                </span>
              </td>
              <td>Block {{ c.block }}</td>
              <td><span class="category-chip">{{ c.category }}</span></td>
              <td><app-priority-badge [priority]="c.predicted_priority" /></td>
              <td>
                <mat-select class="status-select" [value]="c.status"
                            (selectionChange)="updateStatus(c, $event.value)">
                  <mat-option *ngFor="let s of statuses" [value]="s">{{ s }}</mat-option>
                </mat-select>
              </td>
              <td class="upvote-cell">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="12" height="12">
                  <path d="M14 9V5a3 3 0 0 0-3-3l-4 9v11h11.28a2 2 0 0 0 2-1.7l1.38-9a2 2 0 0 0-2-2.3zM7 22H4a2 2 0 0 1-2-2v-7a2 2 0 0 1 2-2h3"/>
                </svg>
                <span>{{ c.support_count }}</span>
              </td>
              <td class="date-cell">{{ c.created_at | date:'dd MMM yyyy' }}</td>
              <td>
                <button class="btn-icon-danger" (click)="deleteComplaint(c)" title="Delete Complaint">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="15" height="15">
                    <polyline points="3 6 5 6 21 6"/>
                    <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
                  </svg>
                </button>
              </td>
            </tr>
            <tr *ngIf="paginated().length === 0">
              <td colspan="10" class="empty-cell">No complaints found matching filter criteria.</td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Pagination Controls -->
      <div class="pagination" *ngIf="!loading() && totalPages() > 1">
        <button class="btn-secondary btn-pag" (click)="page.set(page()-1)" [disabled]="page() === 1">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14">
            <polyline points="15 18 9 12 15 6"/>
          </svg>
          Previous
        </button>
        <span class="pag-info">Page {{ page() }} of {{ totalPages() }}</span>
        <button class="btn-secondary btn-pag" (click)="page.set(page()+1)" [disabled]="page() === totalPages()">
          Next
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14">
            <polyline points="9 18 15 12 9 6"/>
          </svg>
        </button>
      </div>
    </div>
  `,
  styles: [`
    .mb-20 { margin-bottom: 20px; }

    .filters-card {
      padding: 16px 20px;
    }
    .filters {
      display: flex;
      gap: 10px;
      flex-wrap: wrap;
      align-items: center;
    }

    .filter-select {
      min-width: 140px;
    }

    .search-box {
      position: relative;
      flex: 1;
      min-width: 220px;
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

    .btn-clear {
      height: 38px;
      padding: 0 14px;
    }

    .results-count {
      font-size: 12px;
      color: var(--text-muted);
      margin-top: 10px;
    }

    .loading-center {
      display: flex;
      justify-content: center;
      padding: 40px;
    }
    .table-wrap { overflow-x: auto; }

    .id-cell {
      font-weight: 600;
      color: var(--text-secondary);
      font-size: 12.5px;
    }
    .text-cell { max-width: 260px; font-weight: 450; }
    .category-chip {
      font-size: 12px;
      background: var(--sidebar-bg);
      color: var(--text-secondary);
      padding: 2px 8px;
      border-radius: var(--radius-sm);
      font-weight: 500;
    }
    .type-chip {
      font-size: 11.5px;
      padding: 2px 8px;
      border-radius: var(--radius-sm);
      font-weight: 500;
      background: var(--sidebar-bg);
      color: var(--text-muted);

      &.public {
        background: var(--primary-light);
        color: var(--primary);
      }
    }

    .status-select {
      min-width: 120px;
    }

    .upvote-cell {
      display: inline-flex;
      align-items: center;
      gap: 4px;
      color: var(--text-secondary);
      font-size: 12.5px;
    }
    .date-cell {
      color: var(--text-muted);
      font-size: 12.5px;
    }

    .btn-icon-danger {
      background: none;
      border: 1px solid transparent;
      color: var(--text-muted);
      cursor: pointer;
      padding: 5px;
      border-radius: var(--radius-sm);
      display: flex;
      align-items: center;
      justify-content: center;

      &:hover {
        background-color: var(--danger-bg);
        color: var(--danger);
        border-color: var(--danger-border);
      }
    }

    .empty-cell {
      text-align: center;
      color: var(--text-muted);
      padding: 32px;
    }

    .pagination {
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 16px;
      padding-top: 16px;
      border-top: 1px solid var(--border-subtle);
      margin-top: 12px;
    }
    .btn-pag {
      height: 32px;
      padding: 0 12px;
      font-size: 12.5px;
    }
    .pag-info {
      font-size: 12.5px;
      color: var(--text-muted);
    }
  `]
})
export class AdminComplaintsComponent implements OnInit {
  complaints    = signal<Complaint[]>([]);
  filtered      = signal<Complaint[]>([]);
  loading       = signal(true);
  page          = signal(1);
  readonly PER  = 15;

  search         = '';
  filterPriority = '';
  filterStatus   = '';
  filterBlock    = '';

  priorities = ['Critical', 'High', 'Medium', 'Low'];
  statuses   = ['Pending', 'In Progress', 'Resolved', 'Rejected'];
  blocks     = ['A', 'B', 'C', 'D'];

  constructor(private svc: ComplaintService, private snack: MatSnackBar) {}

  ngOnInit(): void {
    this.load();
  }

  load(): void {
    this.loading.set(true);
    this.svc.getAll().subscribe({
      next: res => {
        const data = (res as any).results ?? res;
        this.complaints.set(data);
        this.applyFilter();
        this.loading.set(false);
      },
      error: () => this.loading.set(false)
    });
  }

  applyFilter(): void {
    this.page.set(1);
    let data = this.complaints();
    if (this.search)
      data = data.filter(c => c.complaint_text.toLowerCase().includes(this.search.toLowerCase()));
    if (this.filterPriority)
      data = data.filter(c => c.predicted_priority === this.filterPriority);
    if (this.filterStatus)
      data = data.filter(c => c.status === this.filterStatus);
    if (this.filterBlock)
      data = data.filter(c => c.block === this.filterBlock);
    this.filtered.set(data);
  }

  clearFilters(): void {
    this.search = ''; this.filterPriority = ''; this.filterStatus = ''; this.filterBlock = '';
    this.applyFilter();
  }

  paginated(): Complaint[] {
    const start = (this.page() - 1) * this.PER;
    return this.filtered().slice(start, start + this.PER);
  }

  totalPages(): number { return Math.ceil(this.filtered().length / this.PER); }

  updateStatus(c: Complaint, status: string): void {
    this.svc.updateStatus(c.id, status).subscribe({
      next: updated => {
        const list = this.complaints().map(x => x.id === c.id ? { ...x, status: updated.status } : x);
        this.complaints.set(list);
        this.applyFilter();
        this.snack.open(`Status updated to "${status}"`, 'OK', { duration: 2000 });
      },
      error: () => this.snack.open('Failed to update status.', 'Close', { duration: 3000 })
    });
  }

  deleteComplaint(c: Complaint): void {
    if (!confirm(`Delete complaint #${c.id}? This cannot be undone.`)) return;
    this.svc.delete(c.id).subscribe({
      next: () => {
        this.complaints.set(this.complaints().filter(x => x.id !== c.id));
        this.applyFilter();
        this.snack.open('Complaint deleted.', 'OK', { duration: 2000 });
      },
      error: () => this.snack.open('Failed to delete.', 'Close', { duration: 3000 })
    });
  }
}
