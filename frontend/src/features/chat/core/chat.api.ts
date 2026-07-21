import apiClient from '@/lib/api/client'
import type { ChatMessage } from './chat.types'

export const chatApi = {
  listMessages: (activityId: string) =>
    apiClient
      .get<ChatMessage[]>(`/chat/activities/${activityId}/messages/`)
      .then((response) => response.data),
}
