<script setup lang="ts">
import { computed, nextTick, ref, watch } from 'vue'
import { LoaderCircle, Send, MessageCircleOff, Wifi } from '@lucide/vue'
import type { ChatMessage } from '@/features/chat/core/chat.types'
import { getMediaUrl } from '@/lib/utils'

const props = defineProps<{
  messages: ChatMessage[]
  status: 'idle' | 'loading' | 'connected' | 'disconnected' | 'error'
  errorMessage: string | null
  currentUserId?: number
  isSending: boolean
}>()

const emit = defineEmits<{
  send: [body: string]
}>()

const body = ref('')
const listEl = ref<HTMLElement | null>(null)

const canSend = computed(() => body.value.trim().length > 0 && !props.isSending)

const isConnected = computed(() => props.status === 'connected')
const isConnecting = computed(() => props.status === 'loading')

function displayName(message: ChatMessage) {
  return (
    [message.sender.first_name, message.sender.last_name].filter(Boolean).join(' ') ||
    message.sender.username ||
    'Unknown'
  )
}

function initials(message: ChatMessage) {
  const name = displayName(message)
  return name
    .split(/\s+/)
    .filter(Boolean)
    .slice(0, 2)
    .map((part) => part[0]?.toUpperCase())
    .join('')
}

function formatTime(value: string) {
  return new Intl.DateTimeFormat(undefined, {
    hour: '2-digit',
    minute: '2-digit',
  }).format(new Date(value))
}

// Group consecutive messages from the same sender
type MessageGroup = {
  senderId: number
  isMine: boolean
  messages: ChatMessage[]
}

const messageGroups = computed<MessageGroup[]>(() => {
  const groups: MessageGroup[] = []
  for (const msg of props.messages) {
    const last = groups.at(-1)
    if (last && last.senderId === msg.sender.id) {
      last.messages.push(msg)
    } else {
      groups.push({
        senderId: msg.sender.id,
        isMine: msg.sender.id === props.currentUserId,
        messages: [msg],
      })
    }
  }
  return groups
})

function handleSubmit() {
  if (!canSend.value) return
  emit('send', body.value)
  body.value = ''
}

function handleKeydown(e: KeyboardEvent) {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    handleSubmit()
  }
}

watch(
  () => props.messages.length,
  () => {
    nextTick(() => {
      if (listEl.value) listEl.value.scrollTop = listEl.value.scrollHeight
    })
  },
  { immediate: true },
)
</script>

<template>
  <div class="flex flex-col gap-0 text-sm text-slate-100">
    <!-- Status bar -->
    <div class="flex items-center justify-between px-1 pb-2.5 border-b border-white/8 mb-1">
      <span class="inline-flex items-center gap-1.5 text-[10px] font-medium">
        <span
          class="h-1.5 w-1.5 rounded-full transition-colors"
          :class="
            isConnected
              ? 'bg-emerald-400 shadow-[0_0_6px_#34d399]'
              : isConnecting
                ? 'bg-amber-400 animate-pulse'
                : 'bg-slate-600'
          "
          aria-hidden="true"
        />
        <span
          :class="
            isConnected ? 'text-emerald-400' : isConnecting ? 'text-amber-400' : 'text-slate-500'
          "
        >
          {{ isConnected ? 'Live' : isConnecting ? 'Connecting…' : 'Offline' }}
        </span>
      </span>
      <span class="text-[10px] text-slate-600">
        {{ messages.length }} {{ messages.length === 1 ? 'msg' : 'msgs' }}
      </span>
    </div>

    <!-- Message list -->
    <div
      ref="listEl"
      class="chat-scroll my-1 h-[min(16rem,calc(100dvh-18rem))] overflow-y-auto overscroll-contain"
    >
      <!-- Error banner (doesn't hide messages) -->
      <div
        v-if="errorMessage"
        class="mx-1 mb-3 flex items-start gap-2 rounded-xl border border-rose-500/20 bg-rose-500/8 px-3 py-2 text-[11px] text-rose-300"
      >
        <Wifi class="mt-0.5 size-3 shrink-0 opacity-70" aria-hidden="true" />
        {{ errorMessage }}
      </div>

      <!-- Loading -->
      <div
        v-if="status === 'loading' && messages.length === 0"
        class="flex flex-col items-center gap-3 py-12 text-slate-500"
      >
        <LoaderCircle class="size-6 animate-spin opacity-50" />
        <span class="text-[11px]">Loading messages…</span>
      </div>

      <!-- Empty -->
      <div
        v-else-if="messages.length === 0"
        class="flex flex-col items-center gap-3 py-12 text-slate-500"
      >
        <MessageCircleOff class="size-7 opacity-30" />
        <span class="text-[11px]"
          >No messages yet.<br /><span class="opacity-60"
            >Be the first to say something!</span
          ></span
        >
      </div>

      <!-- Grouped messages -->
      <template v-else>
        <div
          v-for="group in messageGroups"
          :key="group.messages[0]!.id"
          class="flex gap-2 px-1 mb-3"
          :class="group.isMine ? 'flex-row-reverse' : 'flex-row'"
        >
          <!-- Avatar (only for others, shown once per group) -->
          <div class="flex flex-col justify-end shrink-0 w-7">
            <div
              v-if="!group.isMine"
              class="size-7 overflow-hidden rounded-full flex items-center justify-center text-[9px] font-bold text-white shadow ring-1 ring-white/10"
              :style="{ background: `hsl(${(group.senderId * 47) % 360} 55% 40%)` }"
              :title="displayName(group.messages[0]!)"
              aria-hidden="true"
            >
              <img
                v-if="group.messages[0]!.sender.avatar"
                :src="getMediaUrl(group.messages[0]!.sender.avatar) || undefined"
                alt=""
                class="h-full w-full object-cover"
              />
              <span v-else>{{ initials(group.messages[0]!) }}</span>
            </div>
          </div>

          <!-- Bubble stack -->
          <div
            class="flex flex-col gap-0.5 max-w-[80%]"
            :class="group.isMine ? 'items-end' : 'items-start'"
          >
            <!-- Sender name (only for others) -->
            <span
              v-if="!group.isMine"
              class="px-1 text-[10px] font-semibold text-slate-400 leading-none mb-0.5"
            >
              {{ displayName(group.messages[0]!) }}
            </span>

            <div v-for="(msg, idx) in group.messages" :key="msg.id" class="group/msg relative">
              <div
                class="px-3 py-1.5 text-[13px] leading-snug whitespace-pre-wrap break-words shadow-sm"
                :class="[
                  group.isMine ? 'bg-blue-600 text-white' : 'bg-white/10 text-slate-100',
                  idx === 0 && group.messages.length === 1
                    ? group.isMine
                      ? 'rounded-2xl rounded-br-md'
                      : 'rounded-2xl rounded-bl-md'
                    : idx === 0
                      ? group.isMine
                        ? 'rounded-2xl rounded-br-sm'
                        : 'rounded-2xl rounded-bl-sm'
                      : idx === group.messages.length - 1
                        ? group.isMine
                          ? 'rounded-2xl rounded-tr-sm rounded-br-md'
                          : 'rounded-2xl rounded-tl-sm rounded-bl-md'
                        : group.isMine
                          ? 'rounded-xl rounded-r-sm'
                          : 'rounded-xl rounded-l-sm',
                ]"
              >
                {{ msg.body }}
              </div>

              <!-- Timestamp on last bubble in group -->
              <span
                v-if="idx === group.messages.length - 1"
                class="block mt-1 px-1 text-[9px] text-slate-600 leading-none"
                :class="group.isMine ? 'text-right' : 'text-left'"
              >
                {{ formatTime(msg.created_at) }}
              </span>
            </div>
          </div>
        </div>
      </template>
    </div>

    <!-- Input -->
    <div class="border-t border-white/8 pt-2.5 mt-1">
      <form class="flex items-end gap-2" @submit.prevent="handleSubmit">
        <textarea
          v-model="body"
          rows="1"
          maxlength="2000"
          class="min-h-9 max-h-24 flex-1 resize-none rounded-xl border border-white/10 bg-white/8 px-3 py-2 text-[13px] text-white placeholder:text-slate-600 focus:border-blue-500/50 focus:bg-white/12 focus:outline-none transition-colors"
          placeholder="Message…"
          @keydown="handleKeydown"
        />
        <button
          type="submit"
          class="mb-0.5 flex size-9 shrink-0 items-center justify-center rounded-xl text-white transition-all focus:outline-none focus:ring-2 focus:ring-blue-400/50"
          :class="
            canSend
              ? 'bg-blue-600 hover:bg-blue-500 shadow-md shadow-blue-900/30'
              : 'bg-white/6 text-slate-600 cursor-not-allowed'
          "
          :disabled="!canSend"
          aria-label="Send message"
          title="Send (Enter)"
        >
          <LoaderCircle v-if="isSending" class="size-4 animate-spin" aria-hidden="true" />
          <Send v-else class="size-4" aria-hidden="true" />
        </button>
      </form>
      <p class="mt-1 text-right text-[9px] text-slate-700">
        Enter to send · Shift+Enter for newline
      </p>
    </div>
  </div>
</template>

<style scoped>
.chat-scroll {
  scrollbar-width: thin;
  scrollbar-color: rgba(148, 163, 184, 0.15) transparent;
}
.chat-scroll::-webkit-scrollbar {
  width: 4px;
}
.chat-scroll::-webkit-scrollbar-track {
  background: transparent;
}
.chat-scroll::-webkit-scrollbar-thumb {
  background: rgba(148, 163, 184, 0.18);
  border-radius: 4px;
}
.chat-scroll::-webkit-scrollbar-thumb:hover {
  background: rgba(148, 163, 184, 0.35);
}
</style>
