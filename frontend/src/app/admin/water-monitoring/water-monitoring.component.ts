import { Component, OnInit, signal, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpErrorResponse } from '@angular/common/http';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { Subject, timer, of } from 'rxjs';
import { takeUntil, exhaustMap, catchError } from 'rxjs';
import { WaterLevelService } from '../../core/services/water-level.service';
import { WaterLevelData } from '../../core/models/water-level.model';

@Component({
  selector: 'app-water-monitoring',
  standalone: true,
  imports: [CommonModule, MatProgressSpinnerModule],
  template: `
    <div class="page-header">
      <div class="header-content">
        <div>
          <h1>Water Monitoring</h1>
          <p>Live water tank status and level.</p>
        </div>
        <div class="header-actions">
          <button class="btn-refresh" (click)="refreshNow()" [disabled]="refreshing()">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="15" height="15" [class.spin]="refreshing()">
              <path d="M23 4v6h-6M1 20v-6h6"/>
              <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"/>
            </svg>
            <span>Sync Telemetry</span>
          </button>
        </div>
      </div>
    </div>

    <!-- Critical Water Warning: only shown when valid, fresh telemetry reports level < 15% -->
    <div *ngIf="isCriticalAlert()" class="alert-banner critical-alert">
      <div class="alert-icon">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18">
          <circle cx="12" cy="12" r="10"/>
          <line x1="12" y1="8" x2="12" y2="12"/>
          <line x1="12" y1="16" x2="12.01" y2="16"/>
        </svg>
      </div>
      <div class="alert-body">
        <strong>Critical water level &mdash; below 15%.</strong> Please arrange for water replenishment.
      </div>
    </div>

    <!-- Telemetry Unavailable Warning: only shown when connection failed or unconfigured -->
    <div *ngIf="isUnknownOrUnavailable() && waterError()" class="alert-banner warning-alert">
      <div class="alert-icon">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18">
          <circle cx="12" cy="12" r="10"/>
          <line x1="12" y1="8" x2="12" y2="12"/>
          <line x1="12" y1="16" x2="12.01" y2="16"/>
        </svg>
      </div>
      <div class="alert-body">
        <strong>Telemetry Unavailable:</strong> {{ waterError() }}
      </div>
    </div>

    <!-- Main Water-Level Card -->
    <div class="card water-card">
      <!-- Loading indicator during initial connection check -->
      <div *ngIf="waterLoading()" class="loading-state">
        <mat-spinner diameter="30"></mat-spinner>
        <span>Checking water telemetry...</span>
      </div>

      <div *ngIf="!waterLoading()" class="water-card-layout">
        <!-- Water Tank Gauge -->
        <div class="tank-container">
          <div class="tank-scale">
            <span class="scale-mark">100%</span>
            <span class="scale-mark">75%</span>
            <span class="scale-mark">50%</span>
            <span class="scale-mark">25%</span>
            <span class="scale-mark">0%</span>
          </div>

          <div class="tank-cylinder">
            <!-- 15% Threshold Reference Line -->
            <div class="tank-threshold-line" title="15% Critical Threshold"></div>

            <!-- Proportional Water Level Fill -->
            <div class="tank-fill"
                 [style.height.%]="waterLevelPercent()"
                 [ngClass]="getFillClass()">
            </div>
          </div>
        </div>

        <!-- Readout & Status Details -->
        <div class="details-panel">
          <!-- Connection / Status Badge -->
          <div class="badge-wrapper">
            <span class="status-badge" [ngClass]="getBadgeClass()">
              <span class="status-dot"></span>
              {{ getStatusLabel() }}
            </span>
          </div>

          <!-- Main Water-Level Percentage -->
          <div class="level-display">
            <span class="level-value" *ngIf="hasValidReading()">
              {{ waterData()!.percentage | number:'1.0-1' }}<span class="level-unit">%</span>
            </span>
            <span class="level-value muted" *ngIf="!hasValidReading()">--</span>
          </div>

          <!-- Last Updated Timestamp (only when valid reading exists) -->
          <div class="timestamp-display" *ngIf="hasValidReading() && waterLastUpdated()">
            Last updated: {{ waterLastUpdated() | date:'hh:mm:ss a' }}
          </div>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .header-content {
      display: flex;
      align-items: center;
      justify-content: space-between;
      flex-wrap: wrap;
      gap: 16px;
    }

    .header-actions {
      display: flex;
      gap: 10px;
    }

    .btn-refresh {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 8px 16px;
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: var(--radius-md);
      font-size: 13px;
      font-weight: 600;
      color: var(--text-primary);
      cursor: pointer;
      transition: all var(--transition-fast);

      &:hover:not(:disabled) {
        background: var(--primary-light);
        border-color: var(--primary);
        color: var(--primary);
      }

      &:disabled {
        opacity: 0.6;
        cursor: not-allowed;
      }
    }

    .spin {
      animation: spin 1s linear infinite;
    }

    @keyframes spin {
      from { transform: rotate(0deg); }
      to   { transform: rotate(360deg); }
    }

    /* ── Compact Banners ──────────────────────────────────────────────── */
    .alert-banner {
      display: flex;
      align-items: center;
      gap: 12px;
      padding: 12px 18px;
      border-radius: var(--radius-md);
      font-size: 13.5px;
      margin-bottom: 20px;
    }

    .critical-alert {
      background: #FEF2F2;
      border: 1px solid #FECACA;
      color: #991B1B;

      .alert-icon {
        color: #DC2626;
      }
    }

    .warning-alert {
      background: #FFFBEB;
      border: 1px solid #FDE68A;
      color: #92400E;

      .alert-icon {
        color: #D97706;
      }
    }

    .alert-body {
      flex: 1;
      line-height: 1.4;
    }

    /* ── Main Water Card ──────────────────────────────────────────────── */
    .water-card {
      max-width: 640px;
      padding: 32px;
      margin-bottom: 24px;
    }

    .loading-state {
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 12px;
      padding: 48px 16px;
      color: var(--text-secondary);
      font-size: 14px;
    }

    .water-card-layout {
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 48px;
    }

    /* ── Minimal Water Tank Gauge ─────────────────────────────────────── */
    .tank-container {
      display: flex;
      align-items: stretch;
      gap: 12px;
      height: 240px;
    }

    .tank-scale {
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      font-size: 11px;
      font-weight: 500;
      color: var(--text-secondary);
      text-align: right;
      user-select: none;
      padding: 2px 0;
    }

    .tank-cylinder {
      width: 84px;
      height: 240px;
      border: 2px solid var(--border);
      border-radius: var(--radius-md);
      background: #F8FAFC;
      position: relative;
      overflow: hidden;
      display: flex;
      flex-direction: column;
      justify-content: flex-end;
    }

    .tank-threshold-line {
      position: absolute;
      bottom: 15%;
      left: 0;
      right: 0;
      height: 1px;
      border-top: 1px dashed #DC2626;
      z-index: 2;
      opacity: 0.6;
      pointer-events: none;
    }

    .tank-fill {
      width: 100%;
      background: #4E829D;
      transition: height 0.3s ease;

      &.fill-critical {
        background: #DC2626;
      }

      &.fill-low {
        background: #D97706;
      }

      &.fill-normal, &.fill-high {
        background: #4E829D;
      }

      &.fill-empty {
        background: transparent;
      }
    }

    /* ── Details Panel ───────────────────────────────────────────────── */
    .details-panel {
      display: flex;
      flex-direction: column;
      gap: 12px;
      min-width: 200px;
    }

    .badge-wrapper {
      margin-bottom: 4px;
    }

    .status-badge {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 4px 12px;
      border-radius: 9999px;
      font-size: 12.5px;
      font-weight: 600;
      line-height: 1.2;

      &.badge-online-normal, &.badge-online-high {
        background: #E8F5E9;
        color: #166534;
        border: 1px solid #BBF7D0;
      }

      &.badge-online-low {
        background: #FEF3C7;
        color: #92400E;
        border: 1px solid #FDE68A;
      }

      &.badge-online-critical {
        background: #FEE2E2;
        color: #991B1B;
        border: 1px solid #FECACA;
      }

      &.badge-offline {
        background: #F1F5F9;
        color: #475569;
        border: 1px solid #CBD5E1;
      }

      &.badge-unknown {
        background: #FFFBEB;
        color: #92400E;
        border: 1px solid #FDE68A;
      }
    }

    .status-dot {
      width: 6px;
      height: 6px;
      border-radius: 50%;
      background: currentColor;
    }

    .level-display {
      line-height: 1;

      .level-value {
        font-size: 46px;
        font-weight: 700;
        color: var(--text-primary);
        letter-spacing: -0.02em;

        &.muted {
          color: #94A3B8;
        }
      }

      .level-unit {
        font-size: 24px;
        font-weight: 600;
        color: var(--text-secondary);
        margin-left: 2px;
      }
    }

    .timestamp-display {
      font-size: 12px;
      color: var(--text-secondary);
      margin-top: 4px;
    }

    /* ── Responsive ─────────────────────────────────────────────────── */
    @media (max-width: 600px) {
      .water-card {
        padding: 24px 16px;
      }

      .water-card-layout {
        flex-direction: column;
        gap: 24px;
        text-align: center;
      }

      .details-panel {
        align-items: center;
      }
    }
  `]
})
export class WaterMonitoringComponent implements OnInit, OnDestroy {
  waterData        = signal<WaterLevelData | null>(null);
  waterLoading     = signal<boolean>(true);
  waterError       = signal<string | null>(null);
  waterLastUpdated = signal<Date | null>(null);
  refreshing       = signal<boolean>(false);

  private destroy$ = new Subject<void>();

  constructor(private waterSvc: WaterLevelService) {}

  ngOnInit(): void {
    this.startPolling();
  }

  private startPolling(): void {
    timer(0, 3000)
      .pipe(
        takeUntil(this.destroy$),
        exhaustMap(() =>
          this.waterSvc.getWaterLevel().pipe(
            catchError((err: HttpErrorResponse) => {
              this.handleErrorResponse(err);
              return of(null);
            })
          )
        )
      )
      .subscribe(data => {
        if (data) {
          this.handleSuccessResponse(data);
        }
      });
  }

  refreshNow(): void {
    this.refreshing.set(true);
    this.waterSvc.getWaterLevel().pipe(
      catchError((err: HttpErrorResponse) => {
        this.handleErrorResponse(err);
        return of(null);
      })
    ).subscribe(data => {
      if (data) {
        this.handleSuccessResponse(data);
      }
    });
  }

  private handleSuccessResponse(data: WaterLevelData): void {
    this.waterData.set(data);
    this.waterError.set(null);
    if (this.hasValidReading(data)) {
      this.waterLastUpdated.set(new Date(data.timestamp || Date.now()));
    } else {
      this.waterLastUpdated.set(null);
    }
    this.waterLoading.set(false);
    this.refreshing.set(false);
  }

  private handleErrorResponse(err: HttpErrorResponse): void {
    if (err.error && typeof err.error === 'object') {
      this.waterData.set(err.error);
      this.waterError.set(err.error.detail || err.error.error || null);
    } else {
      this.waterData.set({
        percentage: null,
        water_level_cm: null,
        status: 'Unavailable',
        device_status: 'Unknown',
        source: 'Blynk',
        timestamp: null,
        detail: 'Blynk IoT telemetry is currently unavailable.'
      });
      this.waterError.set('Blynk IoT telemetry is currently unavailable.');
    }
    this.waterLastUpdated.set(null);
    this.waterLoading.set(false);
    this.refreshing.set(false);
  }

  isOffline(): boolean {
    const data = this.waterData();
    if (!data) return false;
    return data.device_status === 'Offline' || data.status === 'Offline';
  }

  isUnknownOrUnavailable(): boolean {
    if (this.isOffline()) return false;
    const data = this.waterData();
    if (!data) return !this.waterLoading();
    return data.device_status === 'Unknown' || data.status === 'Unavailable' || data.percentage === null;
  }

  hasValidReading(dataOverride?: WaterLevelData | null): boolean {
    const data = dataOverride !== undefined ? dataOverride : this.waterData();
    if (!data) return false;
    const isOff = data.device_status === 'Offline' || data.status === 'Offline';
    const isUnk = data.device_status === 'Unknown' || data.status === 'Unavailable';
    return !isOff && !isUnk && data.percentage !== null && data.percentage !== undefined;
  }

  isCriticalAlert(): boolean {
    const data = this.waterData();
    return this.hasValidReading() && data !== null && data.percentage !== null && data.percentage < 15;
  }

  waterLevelPercent(): number {
    if (!this.hasValidReading()) {
      return 0;
    }
    const p = this.waterData()?.percentage ?? 0;
    return Math.min(100, Math.max(0, p));
  }

  getFillClass(): string {
    if (!this.hasValidReading()) {
      return 'fill-empty';
    }
    const status = this.waterData()?.status;
    switch (status) {
      case 'Critical': return 'fill-critical';
      case 'Low':      return 'fill-low';
      case 'High':     return 'fill-high';
      default:         return 'fill-normal';
    }
  }

  getStatusLabel(): string {
    if (this.isOffline()) {
      return 'Device Offline';
    }
    if (this.isUnknownOrUnavailable()) {
      return 'Connection Status Unknown';
    }
    const status = this.waterData()?.status || 'Online';
    return `Device Online \u2022 ${status}`;
  }

  getBadgeClass(): string {
    if (this.isOffline()) {
      return 'badge-offline';
    }
    if (this.isUnknownOrUnavailable()) {
      return 'badge-unknown';
    }
    const status = this.waterData()?.status;
    switch (status) {
      case 'Critical': return 'badge-online-critical';
      case 'Low':      return 'badge-online-low';
      case 'High':     return 'badge-online-high';
      default:         return 'badge-online-normal';
    }
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }
}
