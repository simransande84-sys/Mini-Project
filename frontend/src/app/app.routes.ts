import { Routes } from '@angular/router';
import { authGuard } from './core/guards/auth.guard';
import { adminGuard } from './core/guards/admin.guard';

export const routes: Routes = [
  // Default redirect
  { path: '', redirectTo: 'login', pathMatch: 'full' },

  // Auth pages (public)
  {
    path: 'login',
    loadComponent: () => import('./auth/login/login.component').then(m => m.LoginComponent)
  },
  {
    path: 'register',
    loadComponent: () => import('./auth/register/register.component').then(m => m.RegisterComponent)
  },
  {
    path: 'complete-profile',
    canActivate: [authGuard],
    loadComponent: () => import('./auth/complete-profile/complete-profile.component').then(m => m.CompleteProfileComponent)
  },

  // Admin routes (admin guard)
  {
    path: 'admin',
    canActivate: [adminGuard],
    loadComponent: () => import('./admin/layout/admin-layout.component').then(m => m.AdminLayoutComponent),
    children: [
      { path: '', redirectTo: 'dashboard', pathMatch: 'full' },
      {
        path: 'dashboard',
        loadComponent: () => import('./admin/dashboard/admin-dashboard.component').then(m => m.AdminDashboardComponent)
      },
      {
        path: 'complaints',
        loadComponent: () => import('./admin/complaints/admin-complaints.component').then(m => m.AdminComplaintsComponent)
      },
      {
        path: 'analytics',
        loadComponent: () => import('./admin/analytics/admin-analytics.component').then(m => m.AdminAnalyticsComponent)
      },
    ]
  },

  // Student routes (auth guard)
  {
    path: 'student',
    canActivate: [authGuard],
    loadComponent: () => import('./student/layout/student-layout.component').then(m => m.StudentLayoutComponent),
    children: [
      { path: '', redirectTo: 'home', pathMatch: 'full' },
      {
        path: 'home',
        loadComponent: () => import('./student/home/student-home.component').then(m => m.StudentHomeComponent)
      },
      {
        path: 'submit',
        loadComponent: () => import('./student/submit-complaint/submit-complaint.component').then(m => m.SubmitComplaintComponent)
      },
      {
        path: 'mine',
        loadComponent: () => import('./student/my-complaints/my-complaints.component').then(m => m.MyComplaintsComponent)
      },
      {
        path: 'public',
        loadComponent: () => import('./student/public-feed/public-feed.component').then(m => m.PublicFeedComponent)
      },
      {
        path: 'profile',
        loadComponent: () => import('./student/profile/student-profile.component').then(m => m.StudentProfileComponent)
      },
    ]
  },

  // Fallback
  { path: '**', redirectTo: 'login' }
];
