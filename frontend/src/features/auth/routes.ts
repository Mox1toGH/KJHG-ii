export const authRoutes = [
  {
    path: '/login',
    component: () => import('./pages/LoginPage.vue'),
    meta: { requiresGuest: true },
  },
  {
    path: '/signup',
    component: () => import('./pages/SignupPage.vue'),
    meta: { requiresGuest: true },
  },
  {
    path: '/email/verify',
    component: () => import('./pages/EmailVerifyPage.vue'),
    meta: { requiresGuest: true },
  },
  {
    path: '/profile',
    component: () => import('@/features/auth/pages/ProfilePage.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/profile/:username',
    name: 'public-profile',
    component: () => import('@/features/auth/pages/PublicProfilePage.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/profile/edit',
    component: () => import('@/features/auth/pages/ProfileEditPage.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/friends',
    component: () => import('@/features/auth/pages/FriendsPage.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/password/forgot',
    component: () => import('@/features/auth/pages/ForgotPasswordPage.vue'),
    meta: { requiresGuest: true },
  },
  {
    path: '/password/reset',
    component: () => import('@/features/auth/pages/ResetPasswordPage.vue'),
    meta: { requiresGuest: true },
  },
]
