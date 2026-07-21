import type { UseQueryOptions } from '@tanstack/vue-query'
import { usePayloadQueryWithRefs, useQueryWithRefs } from '@/lib/query/useQueryWithRefs'
import type { RefPayload } from '@/lib/query/refPayload'
import { authApi } from './auth.api'
import { authKeys } from './auth.keys'
import type { Friend, FriendStatusResponse, PublicUser, UserProfile, UserStatus } from './auth.types'

export function useCurrentUser(
  options?: Omit<UseQueryOptions<UserProfile, Error>, 'queryKey' | 'queryFn'>,
) {
  return useQueryWithRefs(authKeys.user(), authApi.getCurrentUser, options)
}

export function usePublicUserProfile(
  username: RefPayload<string>,
  options?: Omit<UseQueryOptions<PublicUser, Error>, 'queryKey' | 'queryFn'>,
) {
  return usePayloadQueryWithRefs(authKeys.publicUser(), authApi.getPublicUserProfile, {
    ...options,
    payload: username,
  })
}

export function useUserStatuses(
  options?: Omit<UseQueryOptions<UserStatus[], Error>, 'queryKey' | 'queryFn'>,
) {
  return useQueryWithRefs(authKeys.statuses(), authApi.getStatuses, options)
}

export function useFriends(
  options?: Omit<UseQueryOptions<Friend[], Error>, 'queryKey' | 'queryFn'>,
) {
  return useQueryWithRefs(authKeys.friends(), authApi.getFriends, options)
}

export function useFriendStatus(
  userId: RefPayload<number>,
  options?: Omit<UseQueryOptions<FriendStatusResponse, Error>, 'queryKey' | 'queryFn'>,
) {
  return usePayloadQueryWithRefs(authKeys.friendStatus(0), authApi.checkFriendStatus, {
    ...options,
    payload: userId,
  })
}

export function useFriendRequests(
  options?: Omit<UseQueryOptions<Friend[], Error>, 'queryKey' | 'queryFn'>,
) {
  return useQueryWithRefs(authKeys.friendRequests(), authApi.getFriendRequests, options)
}
