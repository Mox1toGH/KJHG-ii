import apiClient from '@/lib/api/client'
import type { Activity, ActivityMessage, ActivityParticipant, ActivityRole, ActivityRolePayload, CreateActivityPayload, JoinRequest } from './activity.types'

let csrfPromise: Promise<unknown> | undefined

function ensureCsrfCookie() {
  if (typeof document !== 'undefined' && document.cookie.includes('csrftoken=')) return Promise.resolve()
  csrfPromise ??= apiClient.get('/accounts/csrf/').finally(() => { csrfPromise = undefined })
  return csrfPromise
}

function withCsrf<T>(request: () => Promise<T>) { return ensureCsrfCookie().then(request) }

export const activityApi = {
  list: () => apiClient.get<Activity[]>('/activities/').then((response) => response.data),
  create: (payload: CreateActivityPayload) => withCsrf(() => apiClient.post<Activity>('/activities/', payload).then((response) => response.data)),
  delete: (id: string) => withCsrf(() => apiClient.delete(`/activities/${id}/`).then(() => undefined)),
  update: (id: string, payload: { default_role_id: string | null }) => withCsrf(() => apiClient.patch<Activity>(`/activities/${id}/`, payload).then((response) => response.data)),
  join: (id: string) => withCsrf(() => apiClient.post<ActivityMessage>(`/activities/${id}/join/`).then((response) => response.data)),
  leave: (id: string) => withCsrf(() => apiClient.post<ActivityMessage>(`/activities/${id}/leave/`).then((response) => response.data)),
  roles: (activityId: string) => apiClient.get<ActivityRole[]>(`/activities/${activityId}/roles/`).then((response) => response.data),
  createRole: (activityId: string, payload: ActivityRolePayload) => withCsrf(() => apiClient.post<ActivityRole>(`/activities/${activityId}/roles/`, payload).then((response) => response.data)),
  updateRole: (activityId: string, roleId: string, payload: Partial<ActivityRolePayload>) => withCsrf(() => apiClient.patch<ActivityRole>(`/activities/${activityId}/roles/${roleId}/`, payload).then((response) => response.data)),
  deleteRole: (activityId: string, roleId: string) => withCsrf(() => apiClient.delete(`/activities/${activityId}/roles/${roleId}/`).then(() => undefined)),
  participants: (activityId: string) => apiClient.get<ActivityParticipant[]>(`/activities/${activityId}/participants/`).then((response) => response.data),
  assignRole: (activityId: string, participantId: string, roleId: string | null) => withCsrf(() => apiClient.patch<ActivityParticipant>(`/activities/${activityId}/participants/${participantId}/`, { role_id: roleId }).then((response) => response.data)),
  removeParticipant: (activityId: string, participantId: string) => withCsrf(() => apiClient.delete(`/activities/${activityId}/participants/${participantId}/`).then(() => undefined)),
  listJoinRequests: (direction: 'incoming' | 'outgoing') => apiClient.get<JoinRequest[]>(`/activities/join-requests/?direction=${direction}`).then((response) => response.data),
  approveJoinRequest: (id: string) => withCsrf(() => apiClient.post<ActivityMessage>(`/activities/join-requests/${id}/approve/`).then((response) => response.data)),
  rejectJoinRequest: (id: string) => withCsrf(() => apiClient.post<ActivityMessage>(`/activities/join-requests/${id}/reject/`).then((response) => response.data)),
}
