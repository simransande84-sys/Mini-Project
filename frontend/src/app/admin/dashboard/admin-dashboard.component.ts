import { Component, OnInit, signal, ElementRef, ViewChild, AfterViewInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { Chart, registerables } from 'chart.js';
import { DashboardService } from '../../core/services/dashboard.service';
import { ComplaintService } from '../../core/services/complaint.service';
import { DashboardStats } from '../../core/models/dashboard.model';
import { Complaint } from '../../core/models/complaint.model';
import { PriorityBadgeComponent } from '../../shared/components/priority-badge/priority-badge.component';
import { StatusBadgeComponent } from '../../shared/components/status-badge/status-badge.component';

Chart.register(...registerables);

@Component({
  selector: 'app-admin-dashboard',
  standalone: true,
  imports: [CommonModule, RouterModule, MatProgressSpinnerModule, PriorityBadgeComponent, StatusBadgeComponent],
  template: `
    <div class="page-header">
      <h1>Administration Overview</h1>
      <p>Real-time campus complaint metrics, priority distribution, and resolution tracking.</p>
    </div>

    <!-- Loading -->
    <div *ngIf="loading()" class="loading-center">
      <mat-spinner diameter="36"></mat-spinner>
    </div>

    <ng-container *ngIf="!loading() && stats()">
      <!-- KPI Summary Cards -->
      <div class="grid-5 mb-24">
        <div class="kpi-card">
          <div class="kpi-icon-wrap icon-blue">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
              <polyline points="14 2 14 8 20 8"/>
            </svg>
          </div>
          <div class="kpi-info">
            <div class="kpi-label">Total Logging</div>
            <div class="kpi-value">{{ stats()!.total_complaints }}</div>
          </div>
        </div>

        <div class="kpi-card">
          <div class="kpi-icon-wrap icon-red">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polygon points="12 2 2 22 22 22 12 2"/>
              <line x1="12" y1="9" x2="12" y2="13"/>
              <line x1="12" y1="17" x2="12.01" y2="17"/>
            </svg>
          </div>
          <div class="kpi-info">
            <div class="kpi-label">Critical Urgency</div>
            <div class="kpi-value">{{ stats()!.by_priority['Critical'] || 0 }}</div>
          </div>
        </div>

        <div class="kpi-card">
          <div class="kpi-icon-wrap icon-amber">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="10"/>
              <line x1="12" y1="8" x2="12" y2="12"/>
              <line x1="12" y1="16" x2="12.01" y2="16"/>
            </svg>
          </div>
          <div class="kpi-info">
            <div class="kpi-label">High Priority</div>
            <div class="kpi-value">{{ stats()!.by_priority['High'] || 0 }}</div>
          </div>
        </div>

        <div class="kpi-card">
          <div class="kpi-icon-wrap icon-yellow">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="10"/>
              <polyline points="12 6 12 12 16 14"/>
            </svg>
          </div>
          <div class="kpi-info">
            <div class="kpi-label">Medium Priority</div>
            <div class="kpi-value">{{ stats()!.by_priority['Medium'] || 0 }}</div>
          </div>
        </div>

        <div class="kpi-card">
          <div class="kpi-icon-wrap icon-green">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
              <polyline points="22 4 12 14.01 9 11.01"/>
            </svg>
          </div>
          <div class="kpi-info">
            <div class="kpi-label">Low Priority</div>
            <div class="kpi-value">{{ stats()!.by_priority['Low'] || 0 }}</div>
          </div>
        </div>
      </div>

      <!-- Analytics Charts Grid Row 1 -->
      <div class="grid-2 mb-24">
        <div class="card">
          <h2 class="section-title">Priority Breakdown</h2>
          <div class="chart-wrap"><canvas #priorityChart></canvas></div>
        </div>
        <div class="card">
          <h2 class="section-title">Complaints by Category</h2>
          <div class="chart-wrap"><canvas #categoryChart></canvas></div>
        </div>
      </div>

      <!-- Analytics Charts Grid Row 2 -->
      <div class="grid-2 mb-24">
        <div class="card">
          <h2 class="section-title">Monthly Complaint Volume</h2>
          <div class="chart-wrap"><canvas #trendChart></canvas></div>
        </div>
        <div class="card">
          <h2 class="section-title">Distribution by Hostel Block</h2>
          <div class="chart-wrap"><canvas #blockChart></canvas></div>
        </div>
      </div>

      <!-- Recent Complaints Table -->
      <div class="card">
        <div class="table-header">
          <div>
            <h2 class="section-title mb-0">Recent Inflow Requests</h2>
            <p class="section-sub">Latest registered resident complaints across campus</p>
          </div>
          <a routerLink="/admin/complaints" class="view-all-link">
            View All Complaints
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14">
              <polyline points="9 18 15 12 9 6"/>
            </svg>
          </a>
        </div>
        <div class="table-wrap">
          <table class="hs-table">
            <thead>
              <tr>
                <th>Ticket ID</th>
                <th>Description</th>
                <th>Hostel Block</th>
                <th>Category</th>
                <th>Priority Score</th>
                <th>Status</th>
                <th>Upvotes</th>
                <th>Date</th>
              </tr>
            </thead>
            <tbody>
              <tr *ngFor="let c of recent()">
                <td class="id-cell">#{{ c.id }}</td>
                <td class="text-cell">{{ c.complaint_text | slice:0:70 }}{{ c.complaint_text.length > 70 ? '…' : '' }}</td>
                <td>Block {{ c.block }}</td>
                <td><span class="category-chip">{{ c.category }}</span></td>
                <td><app-priority-badge [priority]="c.predicted_priority" /></td>
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
    </ng-container>
  `,
  styles: [`
    .mb-24 { margin-bottom: 24px; }
    .mb-0  { margin-bottom: 0; }
    .loading-center { display: flex; justify-content: center; padding: 60px; }

    .grid-5 {
      display: grid;
      grid-template-columns: repeat(5, 1fr);
      gap: 16px;
      @media(max-width: 1100px) { grid-template-columns: repeat(3, 1fr); }
      @media(max-width: 640px)  { grid-template-columns: 1fr; }
    }

    .icon-blue   { background: var(--primary-light); color: var(--primary); }
    .icon-red    { background: #FEF2F2; color: #DC2626; }
    .icon-amber  { background: #FFF7ED; color: #D97706; }
    .icon-yellow { background: #FFFBEB; color: #B45309; }
    .icon-green  { background: #F0FDF4; color: #16A34A; }

    .chart-wrap {
      position: relative;
      height: 220px;
      margin-top: 12px;
    }

    .table-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 16px;
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

      &:hover {
        text-decoration: underline;
      }
    }

    .table-wrap { overflow-x: auto; }
    .id-cell {
      font-weight: 600;
      color: var(--text-secondary);
      font-size: 12.5px;
    }
    .text-cell { max-width: 280px; font-weight: 450; }
    .category-chip {
      font-size: 12px;
      background: var(--sidebar-bg);
      color: var(--text-secondary);
      padding: 2px 8px;
      border-radius: var(--radius-sm);
      font-weight: 500;
    }
    .upvote-cell {
      display: inline-flex;
      align-items: center;
      gap: 4px;
      color: var(--text-secondary);
      font-size: 13px;
    }
    .date-cell {
      color: var(--text-muted);
      font-size: 12.5px;
    }
  `]
})
export class AdminDashboardComponent implements OnInit, AfterViewInit {
  @ViewChild('priorityChart') priorityRef!: ElementRef<HTMLCanvasElement>;
  @ViewChild('categoryChart') categoryRef!: ElementRef<HTMLCanvasElement>;
  @ViewChild('trendChart')    trendRef!:    ElementRef<HTMLCanvasElement>;
  @ViewChild('blockChart')    blockRef!:    ElementRef<HTMLCanvasElement>;

  stats   = signal<DashboardStats | null>(null);
  recent  = signal<Complaint[]>([]);
  loading = signal(true);

  constructor(private dashSvc: DashboardService, private compSvc: ComplaintService) {}

  ngOnInit(): void {
    this.dashSvc.getStats().subscribe({
      next: s => {
        this.stats.set(s);
        this.loading.set(false);
        this.compSvc.getAll({ page_size: '10' } as any).subscribe(r => {
          this.recent.set(r.results ?? (r as any));
        });
      },
      error: () => this.loading.set(false)
    });
  }

  ngAfterViewInit(): void {
    const interval = setInterval(() => {
      if (this.stats()) {
        this.drawCharts();
        clearInterval(interval);
      }
    }, 200);
  }

  private drawCharts(): void {
    const s = this.stats()!;

    // Priority Doughnut Chart
    new Chart(this.priorityRef.nativeElement, {
      type: 'doughnut',
      data: {
        labels: Object.keys(s.by_priority),
        datasets: [{
          data: Object.values(s.by_priority),
          backgroundColor: ['#DC2626', '#D97706', '#B45309', '#16A34A'],
          borderWidth: 0,
          hoverOffset: 4
        }]
      },
      options: {
        plugins: { legend: { position: 'bottom', labels: { padding: 14, font: { size: 12 } } } },
        cutout: '65%'
      }
    });

    // Category Bar Chart
    new Chart(this.categoryRef.nativeElement, {
      type: 'bar',
      data: {
        labels: Object.keys(s.by_category),
        datasets: [{
          label: 'Complaints',
          data: Object.values(s.by_category),
          backgroundColor: '#4E829D',
          borderRadius: 4,
          borderSkipped: false
        }]
      },
      options: {
        plugins: { legend: { display: false } },
        scales: {
          x: { grid: { display: false }, ticks: { font: { size: 11 } } },
          y: { grid: { color: '#D9E8EF' }, ticks: { font: { size: 11 } } }
        }
      }
    });

    // Monthly Trend Chart
    new Chart(this.trendRef.nativeElement, {
      type: 'line',
      data: {
        labels: s.monthly_trend.map(m => m.month),
        datasets: [{
          label: 'Volume',
          data: s.monthly_trend.map(m => m.count),
          borderColor: '#4E829D',
          backgroundColor: 'rgba(78, 130, 157, 0.08)',
          fill: true,
          tension: 0.3,
          pointBackgroundColor: '#4E829D',
          pointRadius: 3
        }]
      },
      options: {
        plugins: { legend: { display: false } },
        scales: {
          x: { grid: { display: false } },
          y: { grid: { color: '#D9E8EF' } }
        }
      }
    });

    // Block Bar Chart
    new Chart(this.blockRef.nativeElement, {
      type: 'bar',
      data: {
        labels: Object.keys(s.by_block).map(b => `Block ${b}`),
        datasets: [{
          label: 'Complaints',
          data: Object.values(s.by_block),
          backgroundColor: ['#4E829D', '#6B819B', '#253247', '#C3D3DC'],
          borderRadius: 4,
          borderSkipped: false
        }]
      },
      options: {
        indexAxis: 'y',
        plugins: { legend: { display: false } },
        scales: {
          x: { grid: { color: '#D9E8EF' } },
          y: { grid: { display: false } }
        }
      }
    });
  }
}
