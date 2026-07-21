import type { PublicUser } from '@/features/auth'

export interface ChatMessage {
  id: string
  activity: string
  sender: PublicUser
  body: string
  created_at: string
}

export interface ChatMessageCreatedMessage {
  event: 'chat.message_created'
  message: ChatMessage
}

export interface ChatErrorMessage {
  event: 'chat.error'
  detail: string
}
