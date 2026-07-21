export interface NotificationEvent {
  id: string
  type: string
  title: string
  body: string
  data: Record<string, unknown>
  created_at: string
  read_at: string | null
  is_read: boolean
}

export interface NotificationPreferences {
  email_enabled: boolean
  in_app_enabled: boolean
}
