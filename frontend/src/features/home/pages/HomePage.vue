<script setup lang="ts">
import { computed, watch, ref } from 'vue'
import { useRoute } from 'vue-router'
import { useUserLocation } from '@/composables/useUserLocation'
import { useActivityTracking } from '@/features/activities'
import { useCurrentUser } from '@/features/auth'
import {
  useCreateMarker,
  useCreateZone,
  useDeleteMarker,
  useDeleteMarkerPhoto,
  useDeleteZone,
  useMarkers,
  useUpdateMarker,
  useUpdateZone,
  useUploadMarkerPhotos,
  useZones,
} from '@/features/locations/core/location.queries'
import UserLocationModal from '../components/UserLocationModal.vue'
import { useHomeMap } from '../composables/useHomeMap.ts'
import MapControlPanel from '../components/controls/MapControlPanel.vue'
import { useScratchMapSync } from '@/features/exploration/composables/useScratchMapSync.ts'

const route = useRoute()
const activityId = computed(() => {
  const value = route.params.activityId
  return typeof value === 'string' ? value : undefined
})
const currentUserQuery = useCurrentUser()
const currentUserId = computed(() => currentUserQuery.data.value?.id)
const currentUserAvatar = computed(() => currentUserQuery.data.value?.avatar)

watch(
  () => currentUserQuery.data.value,
  (user) => {
    if (!import.meta.env.DEV) return

    console.info('[home] current user profile', {
      id: user?.id,
      avatar: user?.avatar,
      avatarType: typeof user?.avatar,
      hasAvatar: typeof user?.avatar === 'string' && user.avatar.trim().length > 0,
    })
  },
  { immediate: true },
)
const {
  position: userPosition,
  status: locationStatus,
  errorMessage: locationError,
  startTracking,
} = useUserLocation()
const scratchMapEnabled = computed(() => !activityId.value)
const { discoveries: scratchDiscoveries } = useScratchMapSync(scratchMapEnabled, userPosition)
const {
  participants,
  status: trackingStatus,
  errorMessage: trackingError,
} = useActivityTracking(activityId, currentUserId, userPosition)

const markersQuery = useMarkers(activityId)
const markers = computed(() => markersQuery.data.value || [])
const zonesQuery = useZones(activityId)
const zones = computed(() => zonesQuery.data.value || [])

// Selection state for editing an existing marker
const selectedMarkerId = ref<string | null>(null)
const selectedMarker = computed(
  () => markers.value.find((m) => m.id === selectedMarkerId.value) ?? null,
)
const selectedParticipantId = ref<string | null>(null)
const selectedParticipant = computed(() =>
  selectedParticipantId.value
    ? (Object.values(participants.value).find(
        (participant) => participant.participant_id === selectedParticipantId.value,
      ) ?? null)
    : null,
)
const galleryMarker = ref<string | null>(null)
const galleryPhotos = computed(
  () => markers.value.find((m) => m.id === galleryMarker.value)?.photos ?? [],
)

function clearSelection() {
  selectedMarkerId.value = null
}

function handleMarkerClick(markerId: string) {
  selectedMarkerId.value = markerId
}

function handleParticipantClick(participantId: string) {
  selectedParticipantId.value = participantId
}

function handleViewAllPhotos(markerId: string) {
  galleryMarker.value = markerId
}

const {
  baseLayer,
  focusParticipant,
  handleBaseLayerChange,
  showScratchHexagons,
  setShowScratchHexagons,
  locateUser,
  mapContainer,
  pinCoords,
  status,
  switchToOsm,
  clearPin,
  drawingMode,
  activeZonePointCount,
  activeZoneColor,
  drawnZoneCount,
  drawnZoneSummaries,
  toggleDrawingMode,
  undoZonePoint,
  finishZone,
  clearActiveZone,
  clearZones,
  updateActiveZoneColor,
  updateZoneColor,
  updateZoneName,
  deleteZone,
  measurementMode,
  measurementPoints,
  measurementSegmentDistances,
  measurementTotalDistance,
  toggleMeasurementMode,
  clearMeasurements,
  removeMeasurementPoint,
  setDrawingMode,
  setMeasurementMode,
} = useHomeMap({
  activityId,
  currentUserId,
  currentUserAvatar,
  participants,
  userPosition,
  markers,
  zones,
  scratchDiscoveries,
  startTracking,
  onMarkerClick: handleMarkerClick,
  onParticipantClick: handleParticipantClick,
  onViewAllPhotos: handleViewAllPhotos,
  onCreateZone: (payload) => createZone.mutate(payload),
  onUpdateZone: (payload) => updateZone.mutate(payload),
  onDeleteZone: (id) => deleteZoneMutation.mutate(id),
})

const createMarker = useCreateMarker({ onSuccess: clearPin })
const updateMarker = useUpdateMarker({ onSuccess: clearSelection })
const deleteMarker = useDeleteMarker({ onSuccess: clearSelection })
const uploadMarkerPhotos = useUploadMarkerPhotos()
const deleteMarkerPhoto = useDeleteMarkerPhoto()
const createZone = useCreateZone()
const updateZone = useUpdateZone()
const deleteZoneMutation = useDeleteZone()

function handleSaveMarker(payload: {
  name: string
  description: string
  color: string
  meetingPoint: { start_time: string; end_time: string } | null
}) {
  if (!activityId.value || !pinCoords.value) return
  createMarker.mutate({
    activity: activityId.value,
    name: payload.name,
    description: payload.description,
    color: payload.color,
    longitude: pinCoords.value[0],
    latitude: pinCoords.value[1],
    meeting_point: payload.meetingPoint,
  })
}

function handleUpdateMarker(payload: {
  id: string
  name: string
  description: string
  color: string
  meetingPoint: { start_time: string; end_time: string } | null
}) {
  updateMarker.mutate({
    id: payload.id,
    payload: {
      name: payload.name,
      description: payload.description,
      color: payload.color,
      meeting_point: payload.meetingPoint,
    },
  })
}

function handleDeleteMarker(id: string) {
  deleteMarker.mutate(id)
}

function handleUploadMarkerPhotos(payload: { id: string; files: File[] }) {
  uploadMarkerPhotos.mutate({ markerId: payload.id, files: payload.files })
}

function handleDeleteMarkerPhoto(payload: { markerId: string; photoId: number }) {
  deleteMarkerPhoto.mutate(payload)
}
</script>

<template>
  <div class="min-h-full relative">
    <div ref="mapContainer" class="w-full h-screen rounded-md overflow-hidden" />

    <MapControlPanel
      :activity-id="activityId"
      :base-layer="baseLayer"
      :show-scratch-hexagons="showScratchHexagons"
      :current-user-id="currentUserId"
      :location-error="locationError"
      :location-status="locationStatus"
      :participants="participants"
      :pin-coords="pinCoords"
      :status="status"
      :tracking-error="trackingError"
      :tracking-status="trackingStatus"
      :selected-marker="selectedMarker"
      :drawing-mode="drawingMode"
      :active-zone-point-count="activeZonePointCount"
      :active-zone-color="activeZoneColor"
      :drawn-zone-count="drawnZoneCount"
      :drawn-zones="drawnZoneSummaries"
      :measurement-mode="measurementMode"
      :measurement-points="measurementPoints"
      :measurement-segment-distances="measurementSegmentDistances"
      :measurement-total-distance="measurementTotalDistance"
      @focus-participant="focusParticipant"
      @locate-user="locateUser"
      @switch-to-osm="switchToOsm"
      @update-base-layer="handleBaseLayerChange"
      @update-show-scratch-hexagons="setShowScratchHexagons"
      @save-marker="handleSaveMarker"
      @update-marker="handleUpdateMarker"
      @delete-marker="handleDeleteMarker"
      @upload-photos="handleUploadMarkerPhotos"
      @delete-photo="handleDeleteMarkerPhoto"
      @clear-pin="clearPin"
      @clear-selection="clearSelection"
      @toggle-drawing-mode="toggleDrawingMode"
      @undo-zone-point="undoZonePoint"
      @finish-zone="finishZone"
      @clear-active-zone="clearActiveZone"
      @clear-zones="clearZones"
      @update-active-zone-color="updateActiveZoneColor"
      @update-zone-color="updateZoneColor"
      @update-zone-name="updateZoneName"
      @delete-zone="deleteZone"
      @toggle-measurement-mode="toggleMeasurementMode"
      @clear-measurements="clearMeasurements"
      @remove-measurement-point="removeMeasurementPoint"
      @set-drawing-mode="setDrawingMode"
      @set-measurement-mode="setMeasurementMode"
    />

    <div
      v-if="galleryMarker"
      class="absolute inset-0 z-[60] flex items-center justify-center bg-black/70 p-6"
      @click.self="galleryMarker = null"
    >
      <div
        class="max-h-[85vh] w-full max-w-3xl overflow-y-auto rounded-2xl bg-slate-950 p-4 text-white shadow-2xl"
      >
        <div class="mb-3 flex items-center justify-between">
          <h2 class="text-sm font-semibold">Marker photos</h2>
          <button
            type="button"
            class="text-slate-400 hover:text-white"
            @click="galleryMarker = null"
          >
            Close
          </button>
        </div>
        <div class="grid grid-cols-2 gap-3 sm:grid-cols-3">
          <img
            v-for="photo in galleryPhotos"
            :key="photo.id"
            :src="photo.image"
            alt="Marker photo"
            class="aspect-square w-full rounded-lg object-cover"
          />
        </div>
      </div>
    </div>

    <UserLocationModal
      v-if="selectedParticipant"
      :participant="selectedParticipant"
      @close="selectedParticipantId = null"
    />
  </div>
</template>

<style scoped>
.maplibregl-ctrl-top-right {
  transform: translateY(0.5rem);
}
</style>
