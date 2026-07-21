<script setup lang="ts">
import { computed } from 'vue'
import { UserRound, UserPlus, UserMinus, Clock } from '@lucide/vue'
import { useRoute } from 'vue-router'
import { Button } from '@/components/ui/button'
import { usePublicUserProfile, useCurrentUser, useFriendStatus, useAddFriend, useRemoveFriend } from '@/features/auth'

const route = useRoute()
const username = computed(() => String(route.params.username || ''))
const userQuery = usePublicUserProfile(username)
const currentUserQuery = useCurrentUser()
const friendStatusQuery = useFriendStatus(computed(() => userQuery.data.value?.id || 0))
const addFriendMutation = useAddFriend()
const removeFriendMutation = useRemoveFriend()

const displayName = computed(() => {
  const user = userQuery.data.value
  return user ? [user.first_name, user.last_name].filter(Boolean).join(' ') || user.username : ''
})

const isOwnProfile = computed(() => {
  return currentUserQuery.data.value?.id === userQuery.data.value?.id
})

const isFriend = computed(() => {
  return friendStatusQuery.data.value?.is_friend || false
})

const friendStatus = computed(() => {
  return friendStatusQuery.data.value?.status || null
})

const formatDate = (value: string | null) => value
  ? new Intl.DateTimeFormat('uk-UA', { dateStyle: 'long', timeStyle: 'short' }).format(new Date(value))
  : 'Ще не заходив у мережу'

const handleAddFriend = () => {
  if (userQuery.data.value?.id) {
    addFriendMutation.mutate({ friend_id: userQuery.data.value.id })
  }
}

const handleRemoveFriend = () => {
  if (userQuery.data.value?.id) {
    removeFriendMutation.mutate(userQuery.data.value.id)
  }
}
</script>

<template>
  <main class="mx-auto max-w-2xl px-4 py-8 sm:px-6 lg:py-12">
    <div v-if="userQuery.isPending.value" class="py-12 text-center text-muted-foreground">
      Loading profile…
    </div>
    <div v-else-if="userQuery.error.value" class="py-12 text-center text-destructive">
      Profile could not be loaded.
    </div>
    <section
      v-else-if="userQuery.data.value"
      class="rounded-3xl border border-border bg-card p-6 shadow-sm sm:p-8"
    >
      <div class="flex items-center gap-5">
        <div
          class="size-20 shrink-0 overflow-hidden rounded-2xl bg-primary text-primary-foreground"
        >
          <img
            v-if="userQuery.data.value.avatar"
            :src="userQuery.data.value.avatar"
            :alt="`${displayName}'s avatar`"
            class="size-full object-cover"
          />
          <UserRound v-else class="m-7 size-6" aria-hidden="true" />
        </div>
        <div class="min-w-0 flex-1">
          <div class="flex items-center gap-2">
            <h1 class="text-2xl font-bold">{{ displayName }}</h1>
            <span
              v-if="isFriend && !isOwnProfile"
              class="rounded-full bg-primary/10 px-2 py-0.5 text-xs font-medium text-primary"
            >
              Друг
            </span>
          </div>
          <p class="text-muted-foreground">@{{ userQuery.data.value.username }}</p>
          <p class="text-sm text-muted-foreground">{{ userQuery.data.value.email }}</p>
        </div>
        <div v-if="!isOwnProfile" class="shrink-0">
          <Button
            v-if="friendStatus === 'pending'"
            type="button"
            variant="outline"
            size="sm"
            disabled
          >
            <Clock class="mr-2 size-4" />
            Очікує підтвердження
          </Button>
          <Button
            v-else-if="!isFriend"
            type="button"
            size="sm"
            :disabled="addFriendMutation.isPending.value"
            @click="handleAddFriend"
          >
            <UserPlus class="mr-2 size-4" />
            Додати в друзі
          </Button>
          <Button
            v-else
            type="button"
            variant="outline"
            size="sm"
            :disabled="removeFriendMutation.isPending.value"
            @click="handleRemoveFriend"
          >
            <UserMinus class="mr-2 size-4" />
            Видалити з друзів
          </Button>
        </div>
      </div>
      <div class="mt-6 rounded-2xl border border-border px-4 py-3">
        <p class="text-xs uppercase tracking-wider text-muted-foreground">Status</p>
        <p class="mt-1">{{ userQuery.data.value.current_status || 'No status' }}</p>
      </div>
      <div class="mt-4 grid gap-3 sm:grid-cols-2">
        <div class="rounded-2xl border border-border px-4 py-3">
          <p class="text-xs uppercase tracking-wider text-muted-foreground">Приєднався</p>
          <p class="mt-1 text-sm">{{ formatDate(userQuery.data.value.created_at) }}</p>
        </div>
        <div class="rounded-2xl border border-border px-4 py-3">
          <p class="text-xs uppercase tracking-wider text-muted-foreground">Statistics</p>
          <div class="mt-2 flex items-center gap-4">
            <div class="flex items-center gap-2">
              <div class="flex h-8 w-8 items-center justify-center rounded-lg bg-purple-500/20 text-purple-400">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/>
                </svg>
              </div>
              <div>
                <p class="text-xs text-muted-foreground">Scratches</p>
                <p class="text-sm font-semibold">{{ userQuery.data.value.hexagons_explored || 0 }}</p>
              </div>
            </div>
            <div class="flex items-center gap-2">
              <div class="flex h-8 w-8 items-center justify-center rounded-lg bg-emerald-500/20 text-emerald-400">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M3 11l3-3 3 3 5-5 5 5"/>
                  <circle cx="12" cy="5" r="2"/>
                </svg>
              </div>
              <div>
                <p class="text-xs text-muted-foreground">Checkpoints</p>
                <p class="text-sm font-semibold">{{ userQuery.data.value.checkpoints_visited || 0 }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  </main>
</template>
