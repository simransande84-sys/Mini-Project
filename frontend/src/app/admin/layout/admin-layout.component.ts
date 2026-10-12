import { Component, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, Router, RouterOutlet } from '@angular/router';
import { AuthService } from '../../core/services/auth.service';

interface NavItem {
  svgPath: string;
  label: string;
  route: string;
  soon?: boolean;
}

@Component({
  selector: 'app-admin-layout',
  standalone: true,
  imports: [CommonModule, RouterModule, RouterOutlet],
  template: `
    <div class="shell" [class.collapsed]="collapsed()">
      <!-- Sidebar -->
      <aside class="sidebar">
        <div class="sidebar-brand">
          <div class="brand-logo-wrap">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18">
              <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/>
            </svg>
          </div>
          <div class="brand-text">
            <span class="brand-title">HostelSense</span>
            <span class="brand-badge">ADMIN</span>
          </div>
        </div>

        <nav class="sidebar-nav">
          <a *ngFor="let item of navItems" class="nav-item"
             [routerLink]="item.soon ? null : item.route"
             routerLinkActive="active"
             [class.soon]="item.soon"
             [title]="item.soon ? 'Coming Soon' : item.label">
            <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path [attr.d]="item.svgPath"/>
            </svg>
            <span class="nav-label">{{ item.label }}</span>
            <span *ngIf="item.soon" class="soon-badge">SOON</span>
          </a>
        </nav>

        <div class="sidebar-footer">
          <button class="nav-item logout-btn" (click)="logout()">
            <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/>
              <polyline points="16 17 21 12 16 7"/>
              <line x1="21" y1="12" x2="9" y2="12"/>
            </svg>
            <span class="nav-label">Sign Out</span>
          </button>
        </div>
      </aside>

      <!-- Main Content -->
      <div class="main">
        <header class="topbar">
          <button class="toggle-btn" (click)="collapsed.set(!collapsed())" title="Toggle Sidebar">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18">
              <line x1="3" y1="12" x2="21" y2="12"/>
              <line x1="3" y1="6" x2="21" y2="6"/>
              <line x1="3" y1="18" x2="21" y2="18"/>
            </svg>
          </button>

          <div class="system-tag">
            <span class="dot-online"></span>
            <span>Administration Console</span>
          </div>

          <div class="topbar-right">
            <div class="admin-chip">
              <span class="avatar">A</span>
              <div class="user-meta">
                <span class="user-name">{{ auth.currentUser()?.first_name || 'Administrator' }}</span>
                <span class="user-role">Super Admin</span>
              </div>
            </div>
          </div>
        </header>

        <main class="content">
          <router-outlet />
        </main>
      </div>
    </div>
  `,
  styles: [`
    .shell {
      display: flex;
      height: 100vh;
      overflow: hidden;
      background-color: var(--bg);
    }

    .sidebar {
      width: var(--sidebar-w);
      background: var(--sidebar-bg);
      border-right: 1px solid var(--border);
      display: flex;
      flex-direction: column;
      flex-shrink: 0;
      transition: width 200ms ease-in-out;
      overflow: hidden;
    }
    .shell.collapsed .sidebar {
      width: var(--sidebar-w-collapsed);
    }
    .shell.collapsed .brand-text,
    .shell.collapsed .nav-label,
    .shell.collapsed .soon-badge {
      display: none;
    }

    .sidebar-brand {
      display: flex;
      align-items: center;
      gap: 10px;
      padding: 16px;
      border-bottom: 1px solid var(--border);
      height: 60px;
    }
    .brand-logo-wrap {
      width: 32px;
      height: 32px;
      border-radius: var(--radius-md);
      background-color: var(--surface-white);
      border: 1px solid var(--border);
      color: var(--text-primary);
      display: flex;
      align-items: center;
      justify-content: center;
      flex-shrink: 0;
      box-shadow: var(--shadow-sm);
    }
    .brand-text {
      display: flex;
      align-items: center;
      gap: 6px;
    }
    .brand-title {
      font-size: 14.5px;
      font-weight: 700;
      color: var(--text-primary);
      letter-spacing: -0.01em;
    }
    .brand-badge {
      font-size: 9px;
      font-weight: 700;
      background: var(--text-primary);
      color: #FFFFFF;
      padding: 1px 5px;
      border-radius: 3px;
      letter-spacing: 0.05em;
    }

    .sidebar-nav {
      flex: 1;
      padding: 12px 8px;
      display: flex;
      flex-direction: column;
      gap: 3px;
      overflow-y: auto;
    }

    .nav-item {
      display: flex;
      align-items: center;
      gap: 10px;
      padding: 8.5px 12px;
      border-radius: var(--radius-md);
      text-decoration: none;
      color: var(--text-secondary);
      font-size: 13.5px;
      font-weight: 500;
      transition: background-color 200ms ease-in-out, color 200ms ease-in-out;
      cursor: pointer;
      border: none;
      background: none;
      width: 100%;
      white-space: nowrap;
      position: relative;

      &:hover:not(.soon) {
        background-color: var(--nav-hover-bg); /* Muted neutral tint */
        color: var(--text-primary);
      }

      &.active {
        background-color: var(--nav-active-bg);
        color: var(--nav-active-text);
        font-weight: 600;

        &::before {
          content: '';
          position: absolute;
          left: -8px;
          top: 6px;
          bottom: 6px;
          width: 3px;
          background-color: var(--primary);
          border-radius: 0 3px 3px 0;
        }
      }

      &.soon {
        cursor: default;
        opacity: 0.55;
      }
    }

    .nav-icon {
      width: 18px;
      height: 18px;
      flex-shrink: 0;
      transition: color 200ms ease-in-out;
    }

    .soon-badge {
      margin-left: auto;
      font-size: 9px;
      font-weight: 700;
      background: var(--primary-light);
      color: var(--text-muted);
      padding: 1px 5px;
      border-radius: 3px;
    }

    .sidebar-footer {
      padding: 12px 8px;
      border-top: 1px solid var(--border);
    }
    .logout-btn {
      color: var(--text-muted);
      &:hover {
        background-color: var(--danger-bg);
        color: var(--danger);
      }
    }

    .main {
      flex: 1;
      display: flex;
      flex-direction: column;
      overflow: hidden;
    }

    .topbar {
      height: 60px;
      background: var(--surface-white);
      border-bottom: 1px solid var(--border);
      display: flex;
      align-items: center;
      padding: 0 24px;
      gap: 16px;
      flex-shrink: 0;
    }

    .toggle-btn {
      background: var(--surface-white);
      border: 1px solid var(--border);
      color: var(--text-secondary);
      width: 32px;
      height: 32px;
      border-radius: var(--radius-md);
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      transition: background-color 200ms ease-in-out, border-color 200ms ease-in-out;

      &:hover {
        background-color: var(--bg);
        color: var(--text-primary);
        border-color: var(--border);
      }
    }

    .system-tag {
      display: flex;
      align-items: center;
      gap: 6px;
      font-size: 12.5px;
      font-weight: 500;
      color: var(--text-muted);
      border-left: 1px solid var(--border);
      padding-left: 16px;
    }
    .dot-online {
      width: 6px;
      height: 6px;
      border-radius: 50%;
      background-color: var(--success);
    }

    .topbar-right {
      margin-left: auto;
    }

    .admin-chip {
      display: flex;
      align-items: center;
      gap: 10px;
    }
    .avatar {
      width: 32px;
      height: 32px;
      border-radius: 50%;
      background: var(--bg);
      border: 1px solid var(--border);
      color: var(--text-primary);
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 13px;
      font-weight: 600;
    }
    .user-meta {
      display: flex;
      flex-direction: column;
      line-height: 1.2;
    }
    .user-name {
      font-size: 13px;
      font-weight: 600;
      color: var(--text-primary);
    }
    .user-role {
      font-size: 11px;
      color: var(--text-muted);
    }

    .content {
      flex: 1;
      overflow-y: auto;
      padding: 24px 32px;
      background-color: var(--bg);
    }
  `]
})
export class AdminLayoutComponent {
  collapsed = signal(false);

  navItems: NavItem[] = [
    { svgPath: 'M3 3h7v7H3zM14 3h7v7h-7zM14 14h7v7h-7zM3 14h7v7H3z', label: 'Dashboard', route: '/admin/dashboard' },
    { svgPath: 'M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8zM14 2v6h6', label: 'All Complaints', route: '/admin/complaints' },
    { svgPath: 'M12 2.69l5.66 5.66a8 8 0 1 1-11.31 0z', label: 'Water Monitoring', route: '/admin/water-monitoring' },
    { svgPath: 'M12 15a3 3 0 1 0 0-6 3 3 0 0 0 0 6z', label: 'Settings', route: '', soon: true },
  ];

  constructor(public auth: AuthService, private router: Router) {}

  logout(): void { this.auth.logout(); }
}
