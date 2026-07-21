import { computed } from 'vue'
import { useQuery, type QueryKey, type UseQueryOptions } from '@tanstack/vue-query'

import { unwrapRefPayload, type RefPayload } from './refPayload'

type RefQueryOptions<TData, TError, TPayload> = Omit<
  UseQueryOptions<TData, TError, TData, QueryKey>,
  'queryKey' | 'queryFn'
> & {
  payload?: RefPayload<TPayload>
}

export function useQueryWithRefs<TData, TError = Error>(
  queryKey: QueryKey,
  queryFn: () => Promise<TData>,
  options?: Omit<UseQueryOptions<TData, TError, TData, QueryKey>, 'queryKey' | 'queryFn'>,
) {
  return useQuery<TData, TError, TData, QueryKey>({
    ...options,
    queryKey,
    queryFn,
  })
}

export function usePayloadQueryWithRefs<TData, TPayload, TError = Error>(
  queryKey: QueryKey,
  queryFn: (payload: TPayload) => Promise<TData>,
  options: RefQueryOptions<TData, TError, TPayload>,
) {
  const { payload: payloadOption, ...queryOptions } = options
  const payload = computed(() => unwrapRefPayload(payloadOption as RefPayload<TPayload>))
  const dynamicQueryKey = computed(() => [...queryKey, payload.value] as QueryKey)

  return useQuery<TData, TError, TData, QueryKey>({
    ...queryOptions,
    queryKey: dynamicQueryKey,
    queryFn: () => queryFn(payload.value),
  })
}
