import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-status-badge',
  standalone: true,
  imports: [CommonModule],
  template: `<span class="badge" [ngClass]="badgeClass">{{ status }}</span>`,
  styles: [`
    .badge {
      display: inline-flex;
      align-items: center;
      padding: 3px 8px;
      border-radius: 4px;
      font-size: 11.5px;
      font-weight: 500;
      line-height: 1;
      white-space: nowrap;
      border: 1px solid transparent;
    }
    .badge-pending {
      background-color: #FFF7ED;
      color: #D97706;
      border-color: #FED7AA;
    }
    .badge-progress {
      background-color: #D9E8EF;
      color: #4E829D;
      border-color: #C3D3DC;
    }
    .badge-resolved {
      background-color: #E8F5E9;
      color: #2E7D32;
      border-color: #C8E6C9;
    }
    .badge-rejected {
      background-color: #FFEBEE;
      color: #C62828;
      border-color: #FFCDD2;
    }
  `]
})
export class StatusBadgeComponent {
  @Input({ required: true }) status!: string;

  get badgeClass(): string {
    const map: Record<string, string> = {
      'Pending':     'badge-pending',
      'In Progress': 'badge-progress',
      'Resolved':    'badge-resolved',
      'Rejected':    'badge-rejected',
    };
    return map[this.status] || 'badge-pending';
  }
}
