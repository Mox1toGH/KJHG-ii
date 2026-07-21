<script setup lang="ts">
import { Clock3, MapPin, RefreshCw, Navigation } from '@lucide/vue'
import type { LocationMarker } from '@/features/locations/core/location.types'

defineProps<{
  isFetching: boolean
  isPending: boolean
  meetingPoints: LocationMarker[]
}>()

const emit = defineEmits<{
  refresh: []
  selectMeetingPoint: [marker: LocationMarker]
  getDirections: [marker: LocationMarker]
}>()

function formatMeetingTime(marker: LocationMarker) {
  return `${marker.meeting_point?.start_time}-${marker.meeting_point?.end_time}`
}
</script>

<template>
  <div class="flex items-center justify-between gap-3">
    <div>
      <h2 class="flex items-center gap-2 text-sm font-semibold">
        <MapPin class="size-4 text-orange-400" /> Meeting Points
      </h2>
      <p class="mt-1 text-[11px] text-slate-400">Upcoming locations for this activity</p>
    </div>
    <button
      type="button"
      class="rounded-lg p-2 text-slate-400 transition hover:bg-white/10 hover:text-white"
      aria-label="Refresh meeting points"
      @click="emit('refresh')"
    >
      <RefreshCw class="size-4" :class="isFetching ? 'animate-spin' : ''" />
    </button>
  </div>

  <div v-if="isPending" class="py-4 text-center text-xs text-slate-400">
    Loading meeting points...
  </div>
  <div
    v-else-if="!meetingPoints.length"
    class="mt-3 rounded-xl border border-dashed border-white/15 px-3 py-4 text-center text-xs text-slate-400"
  >
    No meeting points yet
  </div>
  <div v-else class="mt-3 max-h-48 space-y-1 overflow-y-auto pr-1">
    <button
      v-for="meetingPoint in meetingPoints"
      :key="meetingPoint.id"
      type="button"
      class="flex w-full items-center gap-3 rounded-xl px-3 py-2.5 text-left transition hover:bg-orange-500/15 focus:outline-none focus:ring-2 focus:ring-orange-400"
      @click="emit('selectMeetingPoint', meetingPoint)"
    >
      <span
        class="flex size-8 shrink-0 items-center justify-center rounded-full bg-orange-500/20 text-orange-300"
      >
        <MapPin class="size-4" />
      </span>
      <span class="min-w-0 flex-1">
        <span class="block truncate text-xs font-medium text-slate-100">
          {{ meetingPoint.name }}
        </span>
        <span class="mt-0.5 flex items-center gap-1 text-[11px] text-orange-200">
          <Clock3 class="size-3" />{{ formatMeetingTime(meetingPoint) }}
        </span>
      </span>
      <button
        type="button"
        class="flex size-7 shrink-0 items-center justify-center rounded-lg text-slate-400 transition hover:bg-blue-500/20 hover:text-blue-300 focus:outline-none focus:ring-2 focus:ring-blue-400"
        aria-label="Get directions"
        @click.stop="emit('getDirections', meetingPoint)"
      >
        <Navigation class="size-4" />
      </button>
    </button>
  </div>
</template>
