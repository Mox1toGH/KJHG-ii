export const shopRoutes = [
  {
    path: '/shop',
    name: 'shop',
    component: () => import('@/features/shop/pages/ShopPage.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/activities/:activityId/shop',
    name: 'activity-shop',
    component: () => import('@/features/shop/pages/ShopPage.vue'),
    meta: { requiresAuth: true },
  },
]
