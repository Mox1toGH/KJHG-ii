import apiClient from '@/lib/api/client'
import type { NotificationEvent, NotificationPreferences } from './notification.types'

export const notificationApi = {
  list: () => apiClient.get<NotificationEvent[]>('/notifications/').then(({ data }) => data),
  markRead: (id: string) =>
    apiClient.post<NotificationEvent>(`/notifications/${id}/read/`).then(({ data }) => data),
  markAllRead: () => apiClient.post('/notifications/read-all/').then(() => undefined),
  remove: (id: string) => apiClient.delete(`/notifications/${id}/`).then(() => undefined),
  clear: () => apiClient.post('/notifications/clear/').then(() => undefined),
  getPreferences: () => apiClient.get<NotificationPreferences>('/notifications/preferences/').then(({ data }) => data),
  updatePreferences: (data: Partial<NotificationPreferences>) =>
    apiClient.put<NotificationPreferences>('/notifications/preferences/', data).then(({ data }) => data),
}
