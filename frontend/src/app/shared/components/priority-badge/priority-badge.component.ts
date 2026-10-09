import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Priority } from '../../../core/models/complaint.model';

@Component({
  selector: 'app-priority-badge',
  standalone: true,
  imports: [CommonModule],
  template: `
    <span class="badge" [ngClass]="badgeClass">
      <span class="dot"></span>
      {{ priority }}
    </span>
  `,
  styles: [`
    .badge {
      display: inline-flex;
      align-items: center;
      gap: 5px;
      padding: 3px 8px;
      border-radius: 4px;
      font-size: 11.5px;
      font-weight: 500;
      line-height: 1;
      white-space: nowrap;
      border: 1px solid transparent;
    }
    .dot {
      width: 5px;
      height: 5px;
      border-radius: 50%;
      background-color: currentColor;
      flex-shrink: 0;
    }
    .badge-critical {
      background-color: #FEF2F2;
      color: #DC2626;
      border-color: #FECACA;
    }
    .badge-high {
      background-color: #FFF7ED;
      color: #D97706;
      border-color: #FED7AA;
    }
    .badge-medium {
      background-color: #FFFBEB;
      color: #B45309;
      border-color: #FDE68A;
    }
    .badge-low {
      background-color: #F0FDF4;
      color: #15803D;
      border-color: #BBF7D0;
    }
  `]
})
export class PriorityBadgeComponent {
  @Input({ required: true }) priority!: Priority | string;

  get badgeClass(): string {
    return `badge-${(this.priority || '').toLowerCase()}`;
  }
}
