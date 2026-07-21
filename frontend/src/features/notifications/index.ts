// Core
export type { NotificationEvent, NotificationPreferences } from './core/notification.types'

export { notificationApi } from './core/notification.api'

// Composables
export { useNotifications } from './composables/useNotifications'
export { useUpdateNotificationPreferences } from './mutations'
export { useNotificationPreferences } from './queries'
