import { Component, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, RouterOutlet } from '@angular/router';
import { AuthService } from '../../core/services/auth.service';

@Component({
  selector: 'app-student-layout',
  standalone: true,
  imports: [CommonModule, RouterModule, RouterOutlet],
  template: `
    <div class="shell" [class.collapsed]="collapsed()">
      <!-- Sidebar -->
      <aside class="sidebar">
        <div class="sidebar-brand">
          <div class="brand-logo-wrap">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M15 22v-4a4.8 4.8 0 0 0-1-3.5c3 0 6-2 6-5.5.08-1.25-.27-2.48-1-3.5.28-1.15.28-2.35 0-3.5 0 0-1 0-3 1.5-2.64-.5-5.36-.5-8 0C6 2 5 2 5 2c-.3 1.15-.3 2.35 0 3.5A5.403 5.403 0 0 0 4 9c0 3.5 3 5.5 6 5.5-.39.49-.68 1.05-.85 1.65-.17.6-.22 1.23-.15 1.85v4" />
              <path d="M9 18c-4.51 2-5-2-7-2" />
            </svg>
          </div>
          <div class="brand-text">
            <span class="brand-title">HostelSense</span>
            <span class="brand-badge">PORTAL</span>
          </div>
        </div>

        <nav class="sidebar-nav">
          <a class="nav-item" routerLink="/student/home" routerLinkActive="active">
            <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
              <rect width="7" height="9" x="3" y="3" rx="1" />
              <rect width="7" height="5" x="14" y="3" rx="1" />
              <rect width="7" height="9" x="14" y="12" rx="1" />
              <rect width="7" height="5" x="3" y="16" rx="1" />
            </svg>
            <span class="nav-label">Dashboard</span>
          </a>

          <a class="nav-item" routerLink="/student/submit" routerLinkActive="active">
            <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
              <path d="M5 12h14"/>
              <path d="M12 5v14"/>
            </svg>
            <span class="nav-label">Submit Issue</span>
          </a>

          <a class="nav-item" routerLink="/student/mine" routerLinkActive="active">
            <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
              <path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z"/>
              <path d="M14 2v4a2 2 0 0 0 2 2h4"/>
              <path d="M10 9H8"/>
              <path d="M16 13H8"/>
              <path d="M16 17H8"/>
            </svg>
            <span class="nav-label">My Requests</span>
          </a>

          <a class="nav-item" routerLink="/student/public" routerLinkActive="active">
            <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
              <circle cx="12" cy="12" r="10"/>
              <path d="M12 2a14.5 14.5 0 0 0 0 20 14.5 14.5 0 0 0 0-20"/>
              <path d="M2 12h20"/>
            </svg>
            <span class="nav-label">Public Feed</span>
          </a>

          <a class="nav-item" routerLink="/student/profile" routerLinkActive="active">
            <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
              <circle cx="12" cy="8" r="5"/>
              <path d="M20 21a8 8 0 0 0-16 0"/>
            </svg>
            <span class="nav-label">Profile & Settings</span>
          </a>
        </nav>

        <div class="sidebar-footer">
          <button class="nav-item logout-btn" (click)="logout()">
            <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
              <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/>
              <polyline points="16 17 21 12 16 7"/>
              <line x1="21" x2="9" y1="12" y2="12"/>
            </svg>
            <span class="nav-label">Sign Out</span>
          </button>
        </div>
      </aside>

      <!-- Main Section -->
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
            <span>Student Portal</span>
          </div>

          <div class="topbar-right">
            <button class="icon-btn" title="Notifications">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" width="18" height="18">
                <path d="M6 8a6 6 0 0 1 12 0c0 7 3 9 3 9H3s3-2 3-9"/>
                <path d="M10.3 21a1.94 1.94 0 0 0 3.4 0"/>
              </svg>
              <span class="notif-badge"></span>
            </button>

            <div class="user-chip">
              <span class="avatar">{{ initial() }}</span>
              <div class="user-meta">
                <span class="user-name">{{ auth.currentUser()?.first_name || 'Student' }}</span>
                <span class="user-role">Resident</span>
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
    .shell.collapsed .brand-badge {
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

      svg {
        width: 17px;
        height: 17px;
      }
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
      background: var(--primary-light);
      color: var(--text-secondary);
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
      border-radius: var(--radius-sm); /* Reduced from md to sm to remove large pill effect */
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

      &:hover {
        background-color: var(--nav-hover-bg); /* Muted neutral tint */
        color: var(--text-primary);
      }

      &.active {
        background-color: transparent; /* Changed from heavy bg */
        color: var(--primary); /* Use primary color for text */
        font-weight: 600;

        &::before {
          content: '';
          position: absolute;
          left: -8px; /* Stick to the left edge of the padding */
          top: 4px;
          bottom: 4px;
          width: 3px;
          background-color: var(--primary);
          border-radius: 3px;
        }
      }
    }

    .nav-icon {
      width: 18px;
      height: 18px;
      flex-shrink: 0;
      transition: color 200ms ease-in-out;
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
      height: 52px; /* Reduced from 60px */
      background: var(--surface-white);
      border-bottom: 1px solid var(--border);
      display: flex;
      align-items: center;
      padding: 0 20px; /* Tighter padding */
      gap: 12px;
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
      display: flex;
      align-items: center;
      gap: 16px;
    }

    .icon-btn {
      position: relative;
      background: none;
      border: none;
      color: var(--text-secondary);
      cursor: pointer;
      padding: 6px;
      border-radius: var(--radius-sm);
      transition: background-color 200ms ease-in-out, color 200ms ease-in-out;

      &:hover {
        background-color: var(--bg);
        color: var(--text-primary);
      }
    }
    .notif-badge {
      position: absolute;
      top: 5px;
      right: 5px;
      width: 6px;
      height: 6px;
      border-radius: 50%;
      background-color: var(--primary);
    }

    .user-chip {
      display: flex;
      align-items: center;
      gap: 10px;
    }
    .avatar {
      width: 28px; /* Reduced from 32px */
      height: 28px; /* Reduced from 32px */
      border-radius: 50%;
      background: var(--bg);
      border: 1px solid var(--border);
      color: var(--text-primary);
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 12px;
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
      padding: 24px; /* Reduced padding slightly for compactness */
      background-color: var(--bg);
    }
  `]
})
export class StudentLayoutComponent {
  collapsed = signal(false);
  constructor(public auth: AuthService) {}
  initial(): string { return (this.auth.currentUser()?.first_name?.[0] || 'S').toUpperCase(); }
  logout(): void { this.auth.logout(); }
}
