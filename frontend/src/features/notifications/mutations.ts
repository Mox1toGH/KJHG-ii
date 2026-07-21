import { useQueryClient } from '@tanstack/vue-query'
import type { MutationOptions } from '@tanstack/query-core'
import { useMutationWithRefs } from '@/lib/query/useMutationWithRefs'
import type { RefPayload } from '@/lib/query/refPayload'
import { notificationApi } from './core/notification.api'
import { notificationKeys } from './keys'
import type { NotificationPreferences } from './core/notification.types'

type RefMutationOptions<TData, TPayload> = Omit<
  MutationOptions<TData, Error, RefPayload<TPayload>>,
  'mutationFn'
>

export function useUpdateNotificationPreferences(
  options?: RefMutationOptions<NotificationPreferences, Partial<NotificationPreferences>>,
) {
  const queryClient = useQueryClient()

  return useMutationWithRefs(notificationApi.updatePreferences, {
    ...options,
    onSuccess: (data, variables, onMutateResult, context) => {
      queryClient.setQueryData(notificationKeys.preferences(), data)
      options?.onSuccess?.(data, variables, onMutateResult, context)
    },
  })
}
