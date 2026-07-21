export const homeRoutes = [
  {
    path: '/',
    component: () => import('@/features/home/pages/HomeDashboardPage.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/map',
    name: 'home-map',
    component: () => import('@/features/home/pages/HomeMapPage.vue'),
    meta: { requiresAuth: true },
  },
]
