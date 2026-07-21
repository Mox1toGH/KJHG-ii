import { onUnmounted, ref, watch, type Ref } from 'vue'
import { chatApi } from '../core/chat.api'
import type { ChatErrorMessage, ChatMessage, ChatMessageCreatedMessage } from '../core/chat.types'

function websocketUrl(activityId: string) {
  const configuredBase = import.meta.env.VITE_WS_BASE_URL as string | undefined
  if (configuredBase)
    return `${configuredBase.replace(/\/$/, '')}/ws/activities/${activityId}/chat/`

  const apiBase =
    (import.meta.env.VITE_API_BASE_URL as string | undefined) ?? window.location.origin
  const origin = apiBase.replace(/\/api\/?$/, '').replace(/^http/, 'ws')
  return `${origin}/ws/activities/${activityId}/chat/`
}

export function useActivityChat(activityId: Ref<string | undefined>, isChatOpen: Ref<boolean>) {
  const messages = ref<ChatMessage[]>([])
  const status = ref<'idle' | 'loading' | 'connected' | 'disconnected' | 'error'>('idle')
  const errorMessage = ref<string | null>(null)
  const isSending = ref(false)
  const unreadCount = ref(0)
  let socket: WebSocket | null = null
  let requestGeneration = 0

  function closeSocket() {
    if (!socket) return
    socket.onopen = null
    socket.onmessage = null
    socket.onerror = null
    socket.onclose = null
    socket.close()
    socket = null
  }

  function mergeMessage(message: ChatMessage, options?: { countUnread?: boolean }) {
    if (messages.value.some((item) => item.id === message.id)) return
    messages.value = [...messages.value, message].sort((a, b) => {
      const tA = new Date(a.created_at).getTime()
      const tB = new Date(b.created_at).getTime()
      return tA - tB
    })
    if (options?.countUnread && !isChatOpen.value) unreadCount.value += 1
  }

  function markRead() {
    unreadCount.value = 0
  }

  function connect(activity: string) {
    const generation = ++requestGeneration
    closeSocket()
    messages.value = []
    unreadCount.value = 0
    status.value = 'loading'
    errorMessage.value = null

    socket = new WebSocket(websocketUrl(activity))
    socket.onopen = () => {
      if (generation !== requestGeneration) return
      status.value = 'connected'
    }
    socket.onmessage = (event) => {
      if (generation !== requestGeneration) return
      try {
        const message = JSON.parse(event.data) as ChatMessageCreatedMessage | ChatErrorMessage
        if (message.event === 'chat.message_created') {
          mergeMessage(message.message, { countUnread: true })
          errorMessage.value = null
        }
        if (message.event === 'chat.error') errorMessage.value = message.detail
      } catch (error) {
        console.error('[chat] invalid WebSocket message', error)
      }
    }
    socket.onerror = (event) => {
      console.error('[chat] WebSocket error', event)
      status.value = 'error'
      errorMessage.value = 'Live chat updates are unavailable.'
    }
    socket.onclose = () => {
      if (generation === requestGeneration) status.value = 'disconnected'
    }

    chatApi
      .listMessages(activity)
      .then((items) => {
        if (generation !== requestGeneration) return
        items.forEach((item) => mergeMessage(item))
      })
      .catch((error: unknown) => {
        if (generation !== requestGeneration) return
        console.error('[chat] failed to load messages', error)
        errorMessage.value = 'Chat messages could not be loaded.'
      })
  }

  function sendMessage(body: string) {
    const activity = activityId.value
    const trimmed = body.trim()
    if (!activity || !trimmed || isSending.value) return
    if (!socket || socket.readyState !== WebSocket.OPEN) {
      errorMessage.value = 'Chat is not connected.'
      return
    }

    isSending.value = true
    try {
      socket.send(JSON.stringify({ type: 'chat.message.create', body: trimmed }))
      errorMessage.value = null
    } finally {
      isSending.value = false
    }
  }

  watch(
    activityId,
    (activity) => {
      if (activity) connect(activity)
      else {
        requestGeneration += 1
        closeSocket()
        messages.value = []
        unreadCount.value = 0
        status.value = 'idle'
        errorMessage.value = null
      }
    },
    { immediate: true },
  )

  onUnmounted(() => {
    requestGeneration += 1
    closeSocket()
  })

  return { messages, status, errorMessage, isSending, unreadCount, markRead, sendMessage }
}
