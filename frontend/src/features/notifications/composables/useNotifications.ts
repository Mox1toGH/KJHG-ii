import { computed, readonly, ref } from 'vue'
import { notificationApi } from '../core/notification.api'
import type { NotificationEvent } from '../core/notification.types'

const notifications = ref<NotificationEvent[]>([])
const isLoading = ref(false)
const isOpen = ref(false)
let socket: WebSocket | null = null
let reconnectTimer: number | undefined
let reconnectAttempt = 0
let started = false

function websocketUrl() {
  const configured = import.meta.env.VITE_WS_BASE_URL as string | undefined
  if (configured) return `${configured.replace(/\/$/, '')}/ws/notifications/`
  const apiBase =
    (import.meta.env.VITE_API_BASE_URL as string | undefined) ?? window.location.origin
  return `${apiBase.replace(/\/api\/?$/, '').replace(/^http/, 'ws')}/ws/notifications/`
}

function merge(notification: NotificationEvent) {
  notifications.value = [
    notification,
    ...notifications.value.filter((item) => item.id !== notification.id),
  ].sort((a, b) => Date.parse(b.created_at) - Date.parse(a.created_at))
}

function showBrowserNotification(notification: NotificationEvent) {
  if (
    typeof window !== 'undefined' &&
    'Notification' in window &&
    Notification.permission === 'granted'
  ) {
    new Notification(notification.title, { body: notification.body, tag: notification.id })
  }
}

async function load() {
  isLoading.value = true
  try {
    notifications.value = await notificationApi.list()
  } catch {
    // Authentication and network failures are handled by the API client/socket.
  } finally {
    isLoading.value = false
  }
}

function scheduleReconnect() {
  if (reconnectTimer !== undefined || !started) return
  const delay = Math.min(30_000, 1_000 * 2 ** reconnectAttempt++)
  reconnectTimer = window.setTimeout(() => {
    reconnectTimer = undefined
    connect()
  }, delay)
}

function connect() {
  if (typeof window === 'undefined' || !started || socket?.readyState === WebSocket.OPEN) return
  socket?.close()
  socket = new WebSocket(websocketUrl())
  socket.onopen = () => {
    reconnectAttempt = 0
  }
  socket.onmessage = (event) => {
    try {
      const message = JSON.parse(event.data) as { event?: string; notification?: NotificationEvent }
      if (message.event === 'notification.created' && message.notification) {
        merge(message.notification)
        showBrowserNotification(message.notification)
      }
    } catch (error) {
      console.error('[notifications] invalid WebSocket message', error)
    }
  }
  socket.onclose = () => {
    socket = null
    scheduleReconnect()
  }
  socket.onerror = () => socket?.close()
}

async function markRead(notification: NotificationEvent) {
  if (notification.is_read) return
  try {
    merge(await notificationApi.markRead(notification.id))
  } catch {
    /* keep optimistic UI responsive */
  }
}

async function markAllRead() {
  notifications.value = notifications.value.map((item) => ({
    ...item,
    is_read: true,
    read_at: item.read_at ?? new Date().toISOString(),
  }))
  try {
    await notificationApi.markAllRead()
  } catch {
    await load()
  }
}

async function remove(id: string) {
  notifications.value = notifications.value.filter((item) => item.id !== id)
  try {
    await notificationApi.remove(id)
  } catch {
    await load()
  }
}

async function clear() {
  const previous = notifications.value
  notifications.value = []
  try {
    await notificationApi.clear()
  } catch {
    notifications.value = previous
  }
}

function toggle() {
  isOpen.value = !isOpen.value
}

export function useNotifications() {
  if (!started) {
    started = true
    void load()
    connect()
  }

  return {
    notifications: readonly(notifications),
    unreadCount: computed(() => notifications.value.filter((item) => !item.is_read).length),
    isLoading: readonly(isLoading),
    isOpen: readonly(isOpen),
    toggle,
    close: () => {
      isOpen.value = false
    },
    markRead,
    markAllRead,
    remove,
    clear,
  }
}
