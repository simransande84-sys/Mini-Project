import { Component, OnInit, signal, ElementRef, ViewChild, AfterViewInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { Chart, registerables } from 'chart.js';
import { DashboardService } from '../../core/services/dashboard.service';
import { ComplaintService } from '../../core/services/complaint.service';
import { DashboardStats } from '../../core/models/dashboard.model';
import { Complaint } from '../../core/models/complaint.model';
import { PriorityBadgeComponent } from '../../shared/components/priority-badge/priority-badge.component';

Chart.register(...registerables);

@Component({
  selector: 'app-admin-analytics',
  standalone: true,
  imports: [CommonModule, MatProgressSpinnerModule, PriorityBadgeComponent],
  template: `
    <div class="page-header">
      <h1>Advanced Analytics</h1>
      <p>In-depth analytical breakdown of issue categories, block-wise trends, and high-impact resident upvotes.</p>
    </div>

    <div *ngIf="loading()" class="loading-center">
      <mat-spinner diameter="36"></mat-spinner>
    </div>

    <ng-container *ngIf="!loading()">
      <!-- Summary Row -->
      <div class="grid-4 mb-24">
        <div class="stat-card" *ngFor="let item of summaryItems()">
          <div class="stat-icon" [style.background]="item.bg" [style.color]="item.color">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="20" height="20">
              <path [attr.d]="item.svgPath"/>
            </svg>
          </div>
          <div class="stat-info">
            <div class="stat-val">{{ item.val }}</div>
            <div class="stat-lbl">{{ item.label }}</div>
          </div>
        </div>
      </div>

      <!-- Charts Row 1 -->
      <div class="grid-2 mb-24">
        <div class="card">
          <h2 class="section-title">Priority Split</h2>
          <div class="chart-wrap"><canvas #pieChart></canvas></div>
        </div>
        <div class="card">
          <h2 class="section-title">Public vs Private Ratio</h2>
          <div class="chart-wrap"><canvas #typeChart></canvas></div>
        </div>
      </div>

      <!-- Charts Row 2 -->
      <div class="grid-2 mb-24">
        <div class="card">
          <h2 class="section-title">Category Breakdown</h2>
          <div class="chart-wrap-lg"><canvas #catChart></canvas></div>
        </div>
        <div class="card">
          <h2 class="section-title">Block-wise Volume Distribution</h2>
          <div class="chart-wrap-lg"><canvas #blockChart></canvas></div>
        </div>
      </div>

      <div class="card mb-24">
        <h2 class="section-title">Monthly Volume Trend (12-Month Rolling)</h2>
        <div class="chart-wrap-lg"><canvas #trendChart></canvas></div>
      </div>

      <!-- Trending Complaints Table -->
      <div class="card">
        <div class="table-header">
          <div>
            <h2 class="section-title mb-0">High-Impact Upvoted Requests</h2>
            <p class="section-sub">Public complaints receiving the highest resident support count</p>
          </div>
        </div>
        <div class="table-wrap">
          <table class="hs-table">
            <thead>
              <tr>
                <th>Rank</th>
                <th>Description</th>
                <th>Category</th>
                <th>Hostel Block</th>
                <th>Priority Score</th>
                <th>Upvote Count</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              <tr *ngFor="let c of trending(); let i = index">
                <td class="rank-cell">#{{ i+1 }}</td>
                <td class="text-cell">{{ c.complaint_text | slice:0:80 }}…</td>
                <td><span class="category-chip">{{ c.category }}</span></td>
                <td>Block {{ c.block }}</td>
                <td><app-priority-badge [priority]="c.predicted_priority" /></td>
                <td class="upvote-cell">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="13" height="13">
                    <path d="M14 9V5a3 3 0 0 0-3-3l-4 9v11h11.28a2 2 0 0 0 2-1.7l1.38-9a2 2 0 0 0-2-2.3zM7 22H4a2 2 0 0 1-2-2v-7a2 2 0 0 1 2-2h3"/>
                  </svg>
                  <strong>{{ c.support_count }}</strong>
                </td>
                <td><span class="status-tag">{{ c.status }}</span></td>
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

    .stat-card {
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: var(--radius-lg);
      padding: 18px 20px;
      display: flex;
      align-items: center;
      gap: 14px;
      box-shadow: var(--shadow-sm);
    }
    .stat-icon {
      width: 42px;
      height: 42px;
      border-radius: var(--radius-md);
      display: flex;
      align-items: center;
      justify-content: center;
      flex-shrink: 0;
    }
    .stat-val {
      font-size: 24px;
      font-weight: 700;
      color: var(--text-primary);
      line-height: 1.2;
    }
    .stat-lbl {
      font-size: 12px;
      color: var(--text-muted);
      font-weight: 500;
    }

    .chart-wrap    { position: relative; height: 220px; margin-top: 12px; }
    .chart-wrap-lg { position: relative; height: 280px; margin-top: 12px; }

    .table-header { margin-bottom: 16px; }
    .section-sub  { font-size: 12.5px; color: var(--text-muted); margin-top: 2px; }

    .table-wrap { overflow-x: auto; }
    .rank-cell { font-weight: 600; color: var(--text-secondary); font-size: 12.5px; }
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
      color: var(--primary);
    }
    .status-tag {
      font-size: 12px;
      font-weight: 500;
      color: var(--text-secondary);
    }
  `]
})
export class AdminAnalyticsComponent implements OnInit, AfterViewInit {
  @ViewChild('pieChart')   pieRef!:   ElementRef<HTMLCanvasElement>;
  @ViewChild('typeChart')  typeRef!:  ElementRef<HTMLCanvasElement>;
  @ViewChild('catChart')   catRef!:   ElementRef<HTMLCanvasElement>;
  @ViewChild('blockChart') blockRef!: ElementRef<HTMLCanvasElement>;
  @ViewChild('trendChart') trendRef!: ElementRef<HTMLCanvasElement>;

  stats    = signal<DashboardStats | null>(null);
  trending = signal<Complaint[]>([]);
  loading  = signal(true);

  summaryItems = signal<{ svgPath:string; bg:string; color:string; val:number; label:string }[]>([]);

  constructor(private dashSvc: DashboardService, private compSvc: ComplaintService) {}

  ngOnInit(): void {
    this.dashSvc.getStats().subscribe({
      next: s => {
        this.stats.set(s);
        this.summaryItems.set([
          { svgPath: 'M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8zM14 2v6h6', bg: '#D9E8EF', color: '#4E829D', val: s.total_complaints, label: 'Total Volume' },
          { svgPath: 'M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5', bg: '#FEF2F2', color: '#DC2626', val: s.by_priority['Critical'] || 0, label: 'Critical Urgency' },
          { svgPath: 'M12 8v4m0 4h.01M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0z', bg: '#FFF7ED', color: '#D97706', val: s.by_priority['High'] || 0, label: 'High Priority' },
          { svgPath: 'M22 11.08V12a10 10 0 1 1-5.93-9.14M22 4L12 14.01l-3-3', bg: '#F0FDF4', color: '#16A34A', val: s.by_priority['Low'] || 0, label: 'Low Priority' },
        ]);
        this.loading.set(false);
      },
      error: () => this.loading.set(false)
    });

    this.compSvc.getPublic().subscribe(data => {
      this.trending.set([...data].sort((a, b) => b.support_count - a.support_count).slice(0, 10));
    });
  }

  ngAfterViewInit(): void {
    const interval = setInterval(() => {
      if (this.stats()) { this.drawCharts(); clearInterval(interval); }
    }, 200);
  }

  private drawCharts(): void {
    const s = this.stats()!;

    new Chart(this.pieRef.nativeElement, {
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
      options: { plugins: { legend: { position: 'bottom' } }, cutout: '65%' }
    });

    new Chart(this.typeRef.nativeElement, {
      type: 'pie',
      data: {
        labels: Object.keys(s.by_complaint_type),
        datasets: [{
          data: Object.values(s.by_complaint_type),
          backgroundColor: ['#4E829D', '#6B819B'],
          borderWidth: 0,
          hoverOffset: 4
        }]
      },
      options: { plugins: { legend: { position: 'bottom' } } }
    });

    new Chart(this.catRef.nativeElement, {
      type: 'bar',
      data: {
        labels: Object.keys(s.by_category),
        datasets: [{
          label: 'Volume',
          data: Object.values(s.by_category),
          backgroundColor: '#4E829D',
          borderRadius: 4,
          borderSkipped: false
        }]
      },
      options: {
        plugins: { legend: { display: false } },
        scales: { x: { grid: { display: false } }, y: { grid: { color: '#D9E8EF' } } }
      }
    });

    new Chart(this.blockRef.nativeElement, {
      type: 'bar',
      data: {
        labels: Object.keys(s.by_block).map(b => `Block ${b}`),
        datasets: [{
          label: 'Volume',
          data: Object.values(s.by_block),
          backgroundColor: ['#4E829D', '#6B819B', '#253247', '#C3D3DC'],
          borderRadius: 4,
          borderSkipped: false
        }]
      },
      options: {
        indexAxis: 'y',
        plugins: { legend: { display: false } },
        scales: { x: { grid: { color: '#D9E8EF' } }, y: { grid: { display: false } } }
      }
    });

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
          pointRadius: 4
        }]
      },
      options: {
        plugins: { legend: { display: false } },
        scales: { x: { grid: { display: false } }, y: { grid: { color: '#D9E8EF' } } }
      }
    });
  }
}
