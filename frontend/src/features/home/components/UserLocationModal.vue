<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import { UserRound, X } from '@lucide/vue'
import { usePublicUserProfile, useFriendStatus, useCurrentUser } from '@/features/auth'
import { useUserItems } from '@/features/shop/composables/useShop'
import type { ParticipantLocation } from '@/features/activities'

const props = defineProps<{
  participant: ParticipantLocation
  activityId?: string
}>()

const emit = defineEmits<{
  close: []
}>()

const router = useRouter()
const username = computed(() => props.participant.user.username)
const profileQuery = usePublicUserProfile(username, {
  enabled: computed(() => Boolean(username.value)),
})
const currentUserQuery = useCurrentUser()
const friendStatusQuery = useFriendStatus(computed(() => profileQuery.data.value?.id || 0))

const isFriend = computed(() => {
  return friendStatusQuery.data.value?.is_friend || false
})

const isOwnProfile = computed(() => {
  return currentUserQuery.data.value?.id === profileQuery.data.value?.id
})

const displayName = computed(() => {
  const profile = profileQuery.data.value
  return profile
    ? [profile.first_name, profile.last_name].filter(Boolean).join(' ') || profile.username
    : props.participant.user.display_name?.trim() || props.participant.user.username
})

const location = computed(() => props.participant.location)
const imageFailed = ref(false)

// Fetch user's equipped items for this activity
const { data: userItems } = useUserItems(props.activityId, undefined, props.participant.user.id.toString())

const equippedAvatar = computed(() => {
  if (!userItems.value) return null
  return userItems.value.find(
    ui => ui.is_equipped && ui.shop_item.item_type === 'AVATAR'
  )?.shop_item
})

const equippedBadge = computed(() => {
  if (!userItems.value) return null
  return userItems.value.find(
    ui => ui.is_equipped && ui.shop_item.item_type === 'BADGE'
  )?.shop_item
})

function shareLocation() {
  if (!location.value) return
  const { latitude, longitude } = location.value
  window.open(
    `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(`${latitude},${longitude}`)}`,
    '_blank',
    'noopener,noreferrer',
  )
}

function openProfile() {
  router.push({ name: 'public-profile', params: { username: username.value } })
  emit('close')
}
</script>

<template>
  <div
    class="fixed inset-0 z-[200] flex items-center justify-center bg-slate-950/60 p-4 backdrop-blur-sm"
    @click.self="emit('close')"
  >
    <section
      role="dialog"
      aria-modal="true"
      aria-labelledby="user-location-title"
      class="w-full max-w-sm rounded-3xl border border-white/15 bg-slate-950 p-6 text-white shadow-2xl"
    >
      <div class="flex items-start justify-between gap-4">
        <div class="flex min-w-0 items-center gap-4">
          <div class="relative size-16 shrink-0 overflow-hidden rounded-2xl bg-blue-600">
            <img
              v-if="profileQuery.data.value?.avatar && !imageFailed"
              :src="profileQuery.data.value.avatar"
              :alt="`${displayName}'s avatar`"
              class="size-full object-cover"
              @error="imageFailed = true"
            />
            <UserRound v-else class="absolute inset-0 m-auto size-6 text-white/50" aria-hidden="true" />
            <img
              v-if="equippedAvatar?.avatar?.icon_file && !imageFailed"
              :src="equippedAvatar.avatar.icon_file"
              :alt="`${displayName}'s avatar frame`"
              class="absolute inset-0 size-full object-contain pointer-events-none"
              @error="imageFailed = true"
            />
          </div>
          <div class="min-w-0">
            <div class="flex items-center gap-2">
              <h2 id="user-location-title" class="truncate text-xl font-semibold">
                {{ displayName }}
              </h2>
              <div
                v-if="equippedBadge?.badge"
                class="shrink-0 rounded-lg px-2 py-0.5 text-xs font-medium"
                :style="{ backgroundColor: equippedBadge.badge.color, color: 'white' }"
              >
                {{ equippedBadge.badge.text }}
              </div>
              <span
                v-if="isFriend && !isOwnProfile"
                class="shrink-0 rounded-full bg-emerald-500/20 px-2 py-0.5 text-xs font-medium text-emerald-400"
              >
                Друг
              </span>
            </div>
            <p class="truncate text-sm text-slate-400">@{{ username }}</p>
          </div>
        </div>
        <button
          type="button"
          class="rounded-lg p-1 text-slate-400 transition-colors hover:bg-white/10 hover:text-white"
          aria-label="Close"
          @click="emit('close')"
        >
          <X class="size-5" />
        </button>
      </div>

      <div class="mt-5 rounded-2xl border border-white/10 bg-white/5 px-4 py-3">
        <p class="text-xs uppercase tracking-[0.16em] text-slate-400">Status</p>
        <p class="mt-1 text-sm text-slate-100">
          {{ profileQuery.data.value?.current_status || 'No status' }}
        </p>
      </div>

      <p v-if="profileQuery.isPending.value" class="mt-3 text-xs text-slate-400">
        Loading profile details…
      </p>

      <div v-if="location" class="mt-4 text-xs text-slate-400">
        {{ location.latitude.toFixed(5) }}, {{ location.longitude.toFixed(5) }}
      </div>

      <div class="mt-5 flex flex-col gap-2 sm:flex-row">
        <button
          type="button"
          class="flex-1 rounded-xl bg-blue-600 px-4 py-2.5 text-sm font-medium transition-colors hover:bg-blue-500 disabled:cursor-not-allowed disabled:opacity-50"
          :disabled="!location"
          @click="shareLocation"
        >
          Share location
        </button>
        <button
          type="button"
          class="flex-1 rounded-xl border border-white/15 bg-white/10 px-4 py-2.5 text-sm font-medium transition-colors hover:bg-white/15"
          @click="openProfile"
        >
          View profile
        </button>
      </div>
    </section>
  </div>
</template>
