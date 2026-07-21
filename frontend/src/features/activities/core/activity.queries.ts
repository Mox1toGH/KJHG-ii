import { useQueryClient } from '@tanstack/vue-query'
import { computed } from 'vue'
import type { Ref } from 'vue'
import type { MutationOptions } from '@tanstack/query-core'
import { useQueryWithRefs } from '@/lib/query/useQueryWithRefs'
import { useMutationWithRefs } from '@/lib/query/useMutationWithRefs'
import type { RefPayload } from '@/lib/query/refPayload'
import { activityApi } from './activity.api'
import type {
  Activity,
  ActivityParticipant,
  ActivityRole,
  ActivityRolePayload,
  CreateActivityPayload,
} from './activity.types'

export const activityKeys = {
  all: ['activities'] as const,
  list: () => [...activityKeys.all, 'list'] as const,
}
type RefMutationOptions<TData, TPayload> = Omit<
  MutationOptions<TData, Error, RefPayload<TPayload>>,
  'mutationFn'
>

function useInvalidatingMutation<TData, TPayload>(
  mutationFn: (payload: TPayload) => Promise<TData>,
  options?: RefMutationOptions<TData, TPayload>,
) {
  const queryClient = useQueryClient()
  return useMutationWithRefs(mutationFn, {
    ...options,
    onSuccess: (data, variables, onMutateResult, context) => {
      queryClient.invalidateQueries({ queryKey: activityKeys.all })
      options?.onSuccess?.(data, variables, onMutateResult, context)
    },
  })
}

export const useActivities = () => useQueryWithRefs(activityKeys.list(), activityApi.list)
export function useCreateActivity(options?: RefMutationOptions<Activity, CreateActivityPayload>) {
  return useInvalidatingMutation(activityApi.create, options)
}
export function useDeleteActivity(options?: RefMutationOptions<void, string>) {
  return useInvalidatingMutation(activityApi.delete, options)
}
export function useUpdateActivity() {
  return useInvalidatingMutation(
    (payload: { id: string; data: { default_role_id: string | null } }) =>
      activityApi.update(payload.id, payload.data),
  )
}
export function useJoinActivity(options?: RefMutationOptions<{ detail: string }, string>) {
  return useInvalidatingMutation(activityApi.join, options)
}
export function useLeaveActivity(options?: RefMutationOptions<{ detail: string }, string>) {
  return useInvalidatingMutation(activityApi.leave, options)
}

export function useActivityRoles(activityId: Ref<string | undefined>) {
  return useQueryWithRefs(
    computed(() => [...activityKeys.all, 'roles', activityId.value] as const) as any,
    () =>
      activityId.value
        ? activityApi.roles(activityId.value)
        : Promise.resolve([] as ActivityRole[]),
    { enabled: computed(() => !!activityId.value) },
  )
}
export function useActivityParticipants(activityId: Ref<string | undefined>) {
  return useQueryWithRefs(
    computed(() => [...activityKeys.all, 'participants', activityId.value] as const) as any,
    () =>
      activityId.value
        ? activityApi.participants(activityId.value)
        : Promise.resolve([] as ActivityParticipant[]),
    { enabled: computed(() => !!activityId.value) },
  )
}
function useActivityMutation<TData, TPayload>(mutationFn: (payload: TPayload) => Promise<TData>) {
  const queryClient = useQueryClient()
  return useMutationWithRefs(mutationFn, {
    onSuccess: () => queryClient.invalidateQueries({ queryKey: activityKeys.all }),
  })
}
export function useCreateActivityRole() {
  return useActivityMutation((payload: { activityId: string; data: ActivityRolePayload }) =>
    activityApi.createRole(payload.activityId, payload.data),
  )
}
export function useUpdateActivityRole() {
  return useActivityMutation(
    (payload: { activityId: string; roleId: string; data: Partial<ActivityRolePayload> }) =>
      activityApi.updateRole(payload.activityId, payload.roleId, payload.data),
  )
}
export function useDeleteActivityRole() {
  return useActivityMutation((payload: { activityId: string; roleId: string }) =>
    activityApi.deleteRole(payload.activityId, payload.roleId),
  )
}
export function useAssignActivityRole() {
  return useActivityMutation(
    (payload: { activityId: string; participantId: string; roleId: string | null }) =>
      activityApi.assignRole(payload.activityId, payload.participantId, payload.roleId),
  )
}
export function useRemoveActivityParticipant() {
  return useActivityMutation((payload: { activityId: string; participantId: string }) =>
    activityApi.removeParticipant(payload.activityId, payload.participantId),
  )
}

export function useJoinRequests(direction: Ref<'incoming' | 'outgoing'>) {
  return useQueryWithRefs(
    computed(() => [...activityKeys.all, 'joinRequests', direction.value] as const) as any,
    () => activityApi.listJoinRequests(direction.value),
  )
}
export function useApproveJoinRequest(options?: RefMutationOptions<{ detail: string }, string>) {
  return useInvalidatingMutation(activityApi.approveJoinRequest, options)
}
export function useRejectJoinRequest(options?: RefMutationOptions<{ detail: string }, string>) {
  return useInvalidatingMutation(activityApi.rejectJoinRequest, options)
}
