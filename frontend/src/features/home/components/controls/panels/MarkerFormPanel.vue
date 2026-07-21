<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { Checkbox } from '@/components/ui/checkbox'
import type { LocationMarker } from '@/features/locations/core/location.types'
import { MARKER_COLORS } from '../../../utils/colors'

const props = defineProps<{
  activityId?: string
  pinCoords: [number, number] | null
  selectedMarker?: LocationMarker | null
}>()

const emit = defineEmits<{
  saveMarker: [
    payload: {
      name: string
      description: string
      color: string
      meetingPoint: { start_time: string; end_time: string } | null
    },
  ]
  updateMarker: [
    payload: {
      id: string
      name: string
      description: string
      color: string
      meetingPoint: { start_time: string; end_time: string } | null
    },
  ]
  deleteMarker: [id: string]
  uploadPhotos: [payload: { id: string; files: File[] }]
  deletePhoto: [payload: { markerId: string; photoId: number }]
  clearPin: []
  clearSelection: []
}>()

const markerName = ref('')
const markerColor = ref('#F59E0B')
const markerDescription = ref('')
const meetingPointEnabled = ref(false)
const meetingStartTime = ref('')
const meetingEndTime = ref('')
const isSavingMarker = ref(false)
const photoInput = ref<HTMLInputElement | null>(null)

// Sync form fields when selectedMarker changes
watch(
  () => props.selectedMarker,
  (marker) => {
    if (marker) {
      markerName.value = marker.name
      markerDescription.value = marker.description || ''
      markerColor.value = marker.color || '#F59E0B'
      meetingPointEnabled.value = !!marker.meeting_point
      meetingStartTime.value = marker.meeting_point?.start_time ?? ''
      meetingEndTime.value = marker.meeting_point?.end_time ?? ''
    } else {
      markerName.value = ''
      markerDescription.value = ''
      markerColor.value = '#F59E0B'
      meetingPointEnabled.value = false
      meetingStartTime.value = ''
      meetingEndTime.value = ''
    }
  },
  { immediate: true },
)

// Reset form when pin drops (new marker)
watch(
  () => props.pinCoords,
  (coords) => {
    if (coords && !props.selectedMarker) {
      markerName.value = ''
      markerColor.value = '#F59E0B'
      meetingPointEnabled.value = false
      meetingStartTime.value = ''
      meetingEndTime.value = ''
    }
  },
)

const panelLng = computed(() => props.selectedMarker?.longitude ?? props.pinCoords?.[0])
const panelLat = computed(() => props.selectedMarker?.latitude ?? props.pinCoords?.[1])

const meetingRangeInvalid = computed(
  () =>
    meetingPointEnabled.value &&
    !!meetingStartTime.value &&
    !!meetingEndTime.value &&
    meetingEndTime.value <= meetingStartTime.value,
)

function handleSaveMarker() {
  if (!markerName.value.trim() || isSavingMarker.value) return
  if (
    meetingPointEnabled.value &&
    (!meetingStartTime.value || !meetingEndTime.value || meetingRangeInvalid.value)
  )
    return

  isSavingMarker.value = true
  const meetingPoint = meetingPointEnabled.value
    ? { start_time: meetingStartTime.value, end_time: meetingEndTime.value }
    : null

  if (props.selectedMarker) {
    emit('updateMarker', {
      id: props.selectedMarker.id,
      name: markerName.value.trim(),
      description: markerDescription.value.trim(),
      color: markerColor.value,
      meetingPoint,
    })
  } else {
    emit('saveMarker', {
      name: markerName.value.trim(),
      description: markerDescription.value.trim(),
      color: markerColor.value,
      meetingPoint,
    })
  }
  isSavingMarker.value = false
}

function handlePhotoChange(event: Event) {
  const files = Array.from((event.target as HTMLInputElement).files ?? [])
  if (files.length && props.selectedMarker) {
    emit('uploadPhotos', { id: props.selectedMarker.id, files })
  }
  ;(event.target as HTMLInputElement).value = ''
}
</script>

<template>
  <div class="flex flex-col gap-2">
    <div class="mb-2 space-y-0.5">
      <div v-if="panelLng != null" class="text-xs text-slate-400">
        Lng: {{ panelLng.toFixed(5) }}
      </div>
      <div v-if="panelLat != null" class="text-xs text-slate-400">
        Lat: {{ panelLat.toFixed(5) }}
      </div>
    </div>
    <form class="flex flex-col gap-2" @submit.prevent="handleSaveMarker">
      <input
        v-model="markerName"
        type="text"
        placeholder="Marker name..."
        required
        class="w-full rounded-lg border border-white/10 bg-black/30 px-3 py-1.5 text-xs text-white placeholder:text-slate-500 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
      />
      <textarea
        v-model="markerDescription"
        rows="3"
        placeholder="Description (optional)..."
        class="w-full resize-none rounded-lg border border-white/10 bg-black/30 px-3 py-1.5 text-xs text-white placeholder:text-slate-500 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
      />
      <div class="flex flex-wrap items-center gap-1.5">
        <button
          v-for="c in MARKER_COLORS"
          :key="c"
          type="button"
          class="h-6 w-6 rounded-full border-2 transition-all duration-150 hover:scale-110"
          :class="markerColor === c ? 'scale-110 border-white' : 'border-transparent'"
          :style="{ backgroundColor: c }"
          :title="c"
          @click="markerColor = c"
        />
      </div>
      <div class="rounded-xl border border-orange-300/20 bg-orange-500/10 p-3">
        <label
          class="flex cursor-pointer items-center gap-2 text-xs font-medium text-orange-100"
          @click="meetingPointEnabled = !meetingPointEnabled"
        >
          <Checkbox
            :checked="meetingPointEnabled"
            class="border-orange-200/40 data-[state=checked]:border-orange-500 data-[state=checked]:bg-orange-500"
          />
          Mark as meeting point
        </label>
        <div v-if="meetingPointEnabled" class="mt-2 grid grid-cols-2 gap-2">
          <label class="text-[10px] text-orange-100/80"
            >Start
            <input
              v-model="meetingStartTime"
              type="time"
              required
              class="mt-1 w-full rounded-lg border border-white/10 bg-black/30 px-2 py-1.5 text-xs text-white focus:border-orange-400 focus:outline-none"
          /></label>
          <label class="text-[10px] text-orange-100/80"
            >End
            <input
              v-model="meetingEndTime"
              type="time"
              required
              class="mt-1 w-full rounded-lg border border-white/10 bg-black/30 px-2 py-1.5 text-xs text-white focus:border-orange-400 focus:outline-none"
          /></label>
        </div>
        <p v-if="meetingRangeInvalid" class="mt-2 text-[10px] text-rose-200">
          End time must be after start time.
        </p>
        <button
          v-if="selectedMarker?.meeting_point"
          type="button"
          class="mt-2 text-[10px] text-orange-200 underline decoration-orange-300/40 underline-offset-2 hover:text-white"
          @click="meetingPointEnabled = false"
        >
          Remove meeting point
        </button>
      </div>
      <div class="flex gap-2">
        <button
          type="submit"
          :disabled="isSavingMarker || !markerName.trim() || meetingRangeInvalid"
          class="w-full rounded-lg bg-blue-600 px-3 py-1.5 text-xs font-medium text-white transition-colors hover:bg-blue-500 disabled:opacity-50"
        >
          {{ selectedMarker ? 'Update' : 'Save' }}
        </button>
        <button
          v-if="selectedMarker"
          type="button"
          class="rounded-lg bg-red-600/80 px-3 py-1.5 text-xs font-medium text-white transition-colors hover:bg-red-500"
          @click="emit('deleteMarker', selectedMarker.id)"
        >
          Delete
        </button>
      </div>
      <template v-if="selectedMarker">
        <label class="mt-1 text-[10px] font-semibold uppercase tracking-[0.15em] text-slate-400"
          >Photos</label
        >
        <input
          ref="photoInput"
          type="file"
          accept="image/*"
          multiple
          class="w-full text-xs text-slate-300 file:mr-2 file:rounded-lg file:border-0 file:bg-white/10 file:px-2 file:py-1 file:text-xs file:text-white"
          @change="handlePhotoChange"
        />
        <span v-if="selectedMarker.photos.length" class="text-[11px] text-slate-400"
          >{{ selectedMarker.photos.length }} photo{{
            selectedMarker.photos.length === 1 ? '' : 's'
          }}
          uploaded</span
        >
        <div v-if="selectedMarker.photos.length" class="space-y-1">
          <div
            v-for="photo in selectedMarker.photos"
            :key="photo.id"
            class="flex items-center justify-between gap-2 text-[11px] text-slate-300"
          >
            <span class="truncate">{{ photo.is_main ? 'Main photo' : 'Photo' }}</span>
            <button
              type="button"
              class="shrink-0 text-rose-300 hover:text-rose-200"
              @click="emit('deletePhoto', { markerId: selectedMarker!.id, photoId: photo.id })"
            >
              Delete
            </button>
          </div>
        </div>
      </template>
    </form>
  </div>
</template>
