import { computed } from 'vue'
import { useCurrentUser } from '../core/auth.queries'

export function useAuth() {
  const { data: user, isLoading, isError } = useCurrentUser()

  const isAuthenticated = computed(() => !!user.value)
  const isGuest = computed(() => !isAuthenticated.value && !isLoading.value)

  return {
    user,
    isAuthenticated,
    isGuest,
    isLoading,
    isError,
  }
}
