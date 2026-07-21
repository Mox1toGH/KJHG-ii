<script setup lang="ts">
import { Bell, CheckCheck, CircleDot, Flag, MapPin, Trash2, UserPlus, X } from '@lucide/vue'
import type { Component } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { computed } from 'vue'
import type { NotificationEvent } from '../core/notification.types'
import { useNotifications } from '../composables/useNotifications'
import LocateButton from '@/features/home/components/LocateButton.vue'

const router = useRouter()
const route = useRoute()
const store = useNotifications()

const isMapPage = computed(
  () =>
    route.path === '/map' || (route.path.startsWith('/activities/') && route.path.endsWith('/map')),
)

function onLocate() {
  window.dispatchEvent(new CustomEvent('mdvl:locate-user'))
}

const iconByType: Record<string, Component> = {
  'meeting_point.created': MapPin,
  'participant.joined': UserPlus,
  'checkpoint.created': Flag,
  'activity.join_request.created': UserPlus,
  'activity.join_request.accepted': UserPlus,
  'activity.join_request.rejected': X,
}
const iconFor = (type: string) => iconByType[type] ?? CircleDot
const relativeTime = (date: string) => {
  const seconds = Math.round((Date.now() - Date.parse(date)) / 1000)
  if (seconds < 60) return 'just now'
  if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`
  if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`
  return `${Math.floor(seconds / 86400)}d ago`
}
const { notifications, unreadCount, isLoading, isOpen } = store

async function openNotification(notification: NotificationEvent) {
  await store.markRead(notification)
  const data = notification.data
  const route =
    typeof data.route === 'string'
      ? data.route
      : data.activity_id
        ? `/activities/${data.activity_id}/map`
        : undefined
  store.close()
  if (route) await router.push(route)
}
</script>

<template>
  <div class="fixed right-4 top-4 z-50 flex items-center gap-2 sm:right-6 sm:top-6">
    <LocateButton v-if="isMapPage" @locate="onLocate" />

    <button
      type="button"
      class="relative flex size-11 items-center justify-center rounded-full border border-border bg-card text-foreground shadow-lg transition hover:bg-accent"
      aria-label="Notifications"
      :aria-expanded="isOpen"
      @click="store.toggle"
    >
      <Bell class="size-5" />
      <span
        v-if="unreadCount"
        class="absolute -right-1 -top-1 flex min-w-5 items-center justify-center rounded-full bg-orange-500 px-1.5 text-[10px] font-bold text-white"
        >{{ unreadCount > 99 ? '99+' : unreadCount }}</span
      >
    </button>

    <Transition name="notification-panel">
      <section
        v-if="isOpen"
        class="fixed inset-x-0 bottom-0 max-h-[min(80vh,38rem)] overflow-hidden rounded-t-2xl border border-border bg-card shadow-2xl sm:absolute sm:inset-x-auto sm:bottom-auto sm:top-0 sm:right-0 sm:w-[min(25rem,calc(100vw-2rem))] sm:rounded-2xl"
        aria-label="Notification Center"
      >
        <header class="flex items-center justify-between border-b border-border px-4 py-3">
          <div>
            <h2 class="font-semibold">Notifications</h2>
            <p class="text-xs text-muted-foreground">{{ unreadCount }} unread</p>
          </div>
          <div class="flex items-center gap-1">
            <button
              type="button"
              class="rounded p-2 text-xs text-muted-foreground hover:bg-accent hover:text-foreground"
              :disabled="!unreadCount"
              @click="store.markAllRead"
            >
              <CheckCheck class="size-4" />
            </button>
            <button
              type="button"
              class="rounded p-2 text-muted-foreground hover:bg-accent"
              aria-label="Close notifications"
              @click="store.close"
            >
              <X class="size-4" />
            </button>
          </div>
        </header>
        <div class="max-h-[calc(min(80vh,38rem)-7rem)] overflow-y-auto">
          <div v-if="isLoading" class="p-8 text-center text-sm text-muted-foreground">
            Loading notifications…
          </div>
          <div v-else-if="!notifications.length" class="p-10 text-center">
            <Bell class="mx-auto mb-3 size-8 text-muted-foreground" />
            <p class="font-medium">You’re all caught up</p>
            <p class="mt-1 text-sm text-muted-foreground">New activity will appear here.</p>
          </div>
          <div
            v-for="notification in notifications"
            :key="notification.id"
            role="button"
            tabindex="0"
            class="group flex w-full cursor-pointer gap-3 border-b border-border p-4 text-left transition hover:bg-accent/60"
            :class="{ 'bg-orange-500/5': !notification.is_read }"
            @click="openNotification(notification)"
            @keydown.enter="openNotification(notification)"
            @keydown.space.prevent="openNotification(notification)"
          >
            <component
              :is="iconFor(notification.type)"
              class="mt-0.5 size-5 shrink-0 text-orange-400"
            />
            <span class="min-w-0 flex-1"
              ><span class="flex items-start justify-between gap-2"
                ><span class="truncate font-medium">{{ notification.title }}</span
                ><span class="shrink-0 text-[11px] text-muted-foreground">{{
                  relativeTime(notification.created_at)
                }}</span></span
              ><span class="mt-1 block text-sm text-muted-foreground">{{
                notification.body
              }}</span></span
            >
            <span
              v-if="!notification.is_read"
              class="mt-2 size-2 shrink-0 rounded-full bg-orange-500"
              aria-label="Unread"
            />
            <span class="hidden shrink-0 items-center gap-1 group-hover:flex" @click.stop
              ><button
                type="button"
                class="rounded p-1 text-muted-foreground hover:text-destructive"
                aria-label="Delete notification"
                @click="store.remove(notification.id)"
              >
                <Trash2 class="size-4" /></button
            ></span>
          </div>
        </div>
        <footer v-if="notifications.length" class="border-t border-border px-4 py-2 text-right">
          <button
            type="button"
            class="text-xs text-muted-foreground hover:text-foreground"
            @click="store.clear"
          >
            Clear all
          </button>
        </footer>
      </section>
    </Transition>
  </div>
</template>

<style scoped>
.notification-panel-enter-active,
.notification-panel-leave-active {
  transition:
    opacity 0.18s ease,
    transform 0.18s ease;
}
.notification-panel-enter-from,
.notification-panel-leave-to {
  opacity: 0;
  transform: translateY(-0.5rem);
}
@media (max-width: 639px) {
  .notification-panel-enter-from,
  .notification-panel-leave-to {
    transform: translateY(1rem);
  }
}
</style>
