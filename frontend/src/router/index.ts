import { activitiesRoutes } from '@/features/activities/routes'
import { authRoutes } from '@/features/auth/routes'
import { homeRoutes } from '@/features/home/routes'
import { shopRoutes } from '@/features/shop/routes'
import { createRouter, createWebHistory } from 'vue-router'
import NotFoundPage from '@/pages/NotFoundPage.vue'

const routes = [
  ...homeRoutes,
  ...activitiesRoutes,
  ...shopRoutes,
  ...authRoutes,
  {
    path: '/:pathMatch(.*)*',
    name: 'not-found',
    component: NotFoundPage,
    meta: {
      title: 'Page not found'
    }
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
})

router.beforeEach(async (to, from, next) => {
  const requiresAuth = to.meta.requiresAuth
  const requiresGuest = to.meta.requiresGuest

  if (requiresAuth || requiresGuest) {
    try {
      const { authApi } = await import('@/features/auth/core/auth.api')
      await authApi.getCurrentUser()

      if (requiresGuest) {
        next('/')
        return
      }
    } catch {
      if (requiresAuth) {
        next('/login')
        return
      }
    }
  }

  next()
})

export default router
