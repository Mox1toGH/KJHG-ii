export const homeRoutes = [
  {
    path: '/',
    component: () => import('@/features/home/pages/HomeDashboardPage.vue'),
  },
  {
    path: '/map',
    name: 'home-map',
    component: () => import('@/features/home/pages/HomeMapPage.vue'),
  },
]
