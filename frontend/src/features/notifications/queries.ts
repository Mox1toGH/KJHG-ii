import type { UseQueryOptions } from '@tanstack/vue-query'
import { useQueryWithRefs } from '@/lib/query/useQueryWithRefs'
import { notificationApi } from './core/notification.api'
import { notificationKeys } from './keys'
import type { NotificationPreferences } from './core/notification.types'

export function useNotificationPreferences(
  options?: Omit<UseQueryOptions<NotificationPreferences, Error>, 'queryKey' | 'queryFn'>,
) {
  return useQueryWithRefs(notificationKeys.preferences(), notificationApi.getPreferences, options)
}
