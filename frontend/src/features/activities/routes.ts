export const activitiesRoutes = [
  {
    path: '/activities/:activityId/map',
    name: 'activity-map',
    component: () => import('@/features/activities/pages/ActivityMapPage.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/activities/:activityId/settings',
    name: 'activity-settings',
    component: () => import('@/features/activities/pages/ActivitySettingsPage.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/activities',
    component: () => import('@/features/activities/pages/ActivitiesPage.vue'),
    meta: { requiresAuth: true },
  },
]
