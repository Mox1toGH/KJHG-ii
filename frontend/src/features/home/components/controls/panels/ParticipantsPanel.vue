<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { Eye, EyeOff } from '@lucide/vue'
import type { ParticipantLocation } from '@/features/activities/tracking/tracking.types'
import { useHiddenParticipants } from '@/features/activities/composables/useHiddenParticipants'

const props = defineProps<{
  participants: Record<string, ParticipantLocation>
  currentUserId?: number
  trackingStatus: 'idle' | 'loading' | 'connected' | 'disconnected' | 'error'
  trackingError: string | null
  activityId?: string
  friendIds?: number[]
}>()

const emit = defineEmits<{
  focusParticipant: [participant: ParticipantLocation]
}>()

const activityIdRef = computed(() => props.activityId)
const currentUserIdRef = computed(() => props.currentUserId)
const { isParticipantHidden, hideParticipant, showParticipant } = useHiddenParticipants(activityIdRef, currentUserIdRef)

const currentTime = ref(Date.now())
let ticker: number | null = null

onMounted(() => {
  ticker = window.setInterval(() => {
    currentTime.value = Date.now()
  }, 10_000)
})

onUnmounted(() => {
  if (ticker !== null) window.clearInterval(ticker)
})

const participantList = computed(() =>
  Object.values(props.participants)
    .filter((participant) => !isParticipantHidden.value(participant.participant_id))
    .sort((a, b) => {
      // Sort by name, but don't prioritize current user
      const nameA = participantName(a).toLowerCase()
      const nameB = participantName(b).toLowerCase()
      return nameA.localeCompare(nameB)
    }),
)

const hiddenParticipantsList = computed(() =>
  Object.values(props.participants).filter(
    (participant) => isParticipantHidden.value(participant.participant_id),
  ),
)

const trackingStatusLabel = computed(() => {
  if (props.trackingStatus === 'connected') return 'live'
  if (props.trackingStatus === 'loading') return 'loading'
  return 'saved'
})

function participantName(participant: ParticipantLocation) {
  return participant.user.id === String(props.currentUserId)
    ? 'You'
    : participant.user.display_name?.trim() || participant.user.username
}

function isFriend(participant: ParticipantLocation) {
  return props.friendIds?.includes(Number(participant.user.id)) || false
}

function formatLastUpdated(value: string | null) {
  const now = currentTime.value
  if (!value) return 'No location yet'

  const seconds = Math.max(0, Math.floor((now - new Date(value).getTime()) / 1000))
  if (seconds < 10) return 'now'
  if (seconds < 60) return `${seconds}s ago`
  if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`
  return new Date(value).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

function toggleVisibility(participantId: string) {
  if (isParticipantHidden.value(participantId)) {
    showParticipant(participantId)
  } else {
    hideParticipant(participantId)
  }
}
</script>

<template>
  <div class="flex items-center justify-between gap-3">
    <span class="text-[11px] text-slate-400">Live updates</span>
    <span class="text-[11px] font-medium text-blue-300">{{ trackingStatusLabel }}</span>
  </div>
  <p v-if="trackingError" class="mt-2 text-xs leading-relaxed text-amber-200">
    Live updates paused; showing saved locations.
  </p>
  <div class="mt-3 max-h-44 space-y-2 overflow-y-auto pr-1">
    <div
      v-for="participant in participantList"
      :key="participant.participant_id"
      class="rounded-lg transition-colors"
    >
      <div
        v-if="participant.location"
        class="flex items-center justify-between gap-2 rounded-lg px-2 py-1.5 text-xs"
      >
        <button
          type="button"
          class="flex min-w-0 flex-1 items-center gap-2 rounded-lg px-2 py-1.5 text-left transition-colors hover:bg-white/10 focus:outline-none focus:ring-1 focus:ring-blue-400"
          :aria-label="`Focus map on ${participantName(participant)}`"
          @click="emit('focusParticipant', participant)"
        >
          <span
            class="h-2 w-2 shrink-0 rounded-full"
            :class="participant.user.id === String(currentUserId) ? 'bg-blue-400' : 'bg-rose-400'"
          />
          <span class="truncate text-slate-200">{{ participantName(participant) }}</span>
        </button>
        <button
          v-if="participant.user.id !== String(currentUserId)"
          type="button"
          class="shrink-0 rounded p-1 text-slate-400 transition-colors hover:bg-white/10 hover:text-white"
          :aria-label="`Hide ${participantName(participant)}`"
          @click.stop="toggleVisibility(participant.participant_id)"
        >
          <EyeOff class="size-3.5" />
        </button>
      </div>
      <div v-else class="flex items-center justify-between gap-3 px-2 py-1.5 text-xs opacity-60">
        <span class="flex min-w-0 items-center gap-2">
          <span class="h-2 w-2 shrink-0 rounded-full bg-slate-500" />
          <span class="truncate text-slate-300">{{ participantName(participant) }}</span>
          <span
            v-if="isFriend(participant)"
            class="shrink-0 rounded-full bg-emerald-500/20 px-1.5 py-0.5 text-[10px] font-medium text-emerald-300"
          >
            Друг
          </span>
        </span>
        <span class="shrink-0 text-[10px] text-slate-500">No location</span>
      </div>
    </div>
    <p v-if="!participantList.length && !hiddenParticipantsList.length" class="text-xs text-slate-400">No participants yet</p>
  </div>

  <div v-if="hiddenParticipantsList.length > 0" class="mt-3 border-t border-white/10 pt-3">
    <p class="text-[11px] font-medium text-slate-400 mb-2">Hidden ({{ hiddenParticipantsList.length }})</p>
    <div class="max-h-32 space-y-2 overflow-y-auto pr-1">
      <div
        v-for="participant in hiddenParticipantsList"
        :key="participant.participant_id"
        class="flex items-center justify-between gap-2 rounded-lg px-2 py-1.5 text-xs opacity-60"
      >
        <span class="flex min-w-0 items-center gap-2">
          <span class="h-2 w-2 shrink-0 rounded-full bg-slate-500" />
          <span class="truncate text-slate-300">{{ participantName(participant) }}</span>
        </span>
        <button
          type="button"
          class="shrink-0 rounded p-1 text-slate-400 transition-colors hover:bg-white/10 hover:text-white"
          :aria-label="`Show ${participantName(participant)}`"
          @click.stop="toggleVisibility(participant.participant_id)"
        >
          <Eye class="size-3.5" />
        </button>
      </div>
    </div>
  </div>
</template>
