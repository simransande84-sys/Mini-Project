import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';
import { AuthService } from '../services/auth.service';

/** Allows only admin (is_staff) users. Redirects students to /student/home */
export const adminGuard: CanActivateFn = () => {
  const auth   = inject(AuthService);
  const router = inject(Router);
  if (auth.isLoggedIn() && auth.isAdmin()) return true;
  if (auth.isLoggedIn()) return router.createUrlTree(['/student/home']);
  return router.createUrlTree(['/login']);
};
