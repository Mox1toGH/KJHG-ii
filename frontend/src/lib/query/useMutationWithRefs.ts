import { useMutation } from '@tanstack/vue-query'
import type { MutationOptions } from '@tanstack/query-core'

import { unwrapRefPayload, type RefPayload } from './refPayload'

export function useMutationWithRefs<TData, TError = Error, TPayload = void, TContext = unknown>(
  mutationFn: (payload: TPayload) => Promise<TData>,
  options?: Omit<MutationOptions<TData, TError, RefPayload<TPayload>, TContext>, 'mutationFn'>,
) {
  return useMutation<TData, TError, RefPayload<TPayload>, TContext>({
    ...options,
    mutationFn: (payload) => mutationFn(unwrapRefPayload(payload)),
  })
}
