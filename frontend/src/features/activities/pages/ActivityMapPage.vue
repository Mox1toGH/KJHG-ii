<script setup lang="ts">
import { computed, nextTick, onMounted, onUnmounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import 'maplibre-gl/dist/maplibre-gl.css'
import { useUserLocation } from '@/composables/useUserLocation'
import { useActivityTracking } from '@/features/activities'
import { useCurrentUser } from '@/features/auth'
import { useHiddenParticipants } from '@/features/activities/composables/useHiddenParticipants'
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
import {
  useCheckpoints,
  useRoutes,
  useVisits,
  useCreateCheckpoint,
  useCreateRoute,
  useUpdateCheckpoint,
  useUpdateRoute,
  useDeleteCheckpoint,
  useDeleteRoute,
  useUploadCheckpointPhotos,
  useDeleteCheckpointPhoto,
  useCheckinLogic,
  useMyActivityPoints,
} from '@/features/checkpoints'
import { useActivities, useActivityRoles } from '@/features/activities'
import type { UpdateRoutePayload } from '@/features/checkpoints'
import type { LocationMarker } from '@/features/locations/core/location.types'
import UserLocationModal from '@/features/home/components/UserLocationModal.vue'
import { useHomeMap } from '@/features/home/composables/useHomeMap'
import MapControlPanel from '@/features/home/components/controls/MapControlPanel.vue'
import CheckpointEditorModal from '@/features/home/components/CheckpointEditorModal.vue'
import {
  requestSosParticipantFocus,
  sosFocusParticipantId,
} from '@/features/activities/sos/sos.state'
import CheckpointQuestModal from '@/features/checkpoints/components/CheckpointQuestModal.vue'

const route = useRoute()
const router = useRouter()
const activityId = computed(() =>
  typeof route.params.activityId === 'string' ? route.params.activityId : undefined,
)
const currentUserQuery = useCurrentUser()
const currentUserId = computed(() => currentUserQuery.data.value?.id)
const { hiddenParticipantIds } = useHiddenParticipants(activityId, currentUserId)
const activitiesQuery = useActivities()
const currentActivity = computed(() =>
  activitiesQuery.data.value?.find((activity) => activity.id === activityId.value),
)
const currentUserAvatar = computed(() => currentUserQuery.data.value?.avatar)
const {
  position: userPosition,
  status: locationStatus,
  errorMessage: locationError,
  startTracking,
} = useUserLocation()
const {
  participants,
  status: trackingStatus,
  errorMessage: trackingError,
} = useActivityTracking(activityId, currentUserId, userPosition)
const markersQuery = useMarkers(activityId, { refetchInterval: 15_000 })
const markers = computed(() => markersQuery.data.value ?? [])
const rolesQuery = useActivityRoles(activityId)
const roles = computed(() => rolesQuery.data.value ?? [])
const zonesQuery = useZones(activityId, { refetchInterval: 15_000 })
const zones = computed(() => zonesQuery.data.value ?? [])
const checkpointsQuery = useCheckpoints(activityId)
const checkpoints = computed(() => checkpointsQuery.data.value || [])
const routesQuery = useRoutes(activityId)
const routes = computed(() => routesQuery.data.value || [])
const visitsQuery = useVisits(activityId)
const visits = computed(() => visitsQuery.data.value || [])
const { myPoints, data: activityPointsData } = useMyActivityPoints(activityId, currentUserId)
const activityPoints = computed(() =>
  [...(activityPointsData.value ?? [])].sort((a, b) => b.points - a.points),
)

const { checkInMutation } = useCheckinLogic(activityId, userPosition)

const currentTime = ref(Date.now())
let currentTimeTicker: number | null = null
const showScratchHexagons = ref(false)
const isSelectingRouteDestination = ref(false)
const timeToMinutes = (value: string) => {
  const [hours = 0, minutes = 0] = value.split(':').map(Number)
  return hours * 60 + minutes
}

const meetingPoints = computed(() => {
  const now = new Date(currentTime.value)
  const nowMinutes = now.getHours() * 60 + now.getMinutes()
  return markers.value
    .filter(
      (marker) => marker.meeting_point && timeToMinutes(marker.meeting_point.end_time) > nowMinutes,
    )
    .sort((a, b) =>
      (a.meeting_point?.start_time ?? '').localeCompare(b.meeting_point?.start_time ?? ''),
    )
})

const selectedMarkerId = ref<string | null>(null)
const selectedMarker = computed(
  () => markers.value.find((marker) => marker.id === selectedMarkerId.value) ?? null,
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
  () => markers.value.find((marker) => marker.id === galleryMarker.value)?.photos ?? [],
)
const checkpointGallery = ref<{ kind: 'checkpoint' | 'route'; id: string } | null>(null)
const checkpointGalleryPhotos = computed(() => {
  if (!checkpointGallery.value) return []
  if (checkpointGallery.value.kind === 'checkpoint')
    return checkpoints.value.find((item) => item.id === checkpointGallery.value?.id)?.photos ?? []
  return routes.value.find((item) => item.id === checkpointGallery.value?.id)?.photos ?? []
})
const markerError = ref('')

watch(
  currentUserQuery.error,
  (error) => {
    if ((error as { response?: { status?: number } })?.response?.status === 401)
      router.replace({ path: '/login', query: { redirect: route.fullPath } })
  },
  { immediate: true },
)

const clearSelection = () => {
  selectedMarkerId.value = null
}
const handleMarkerClick = (markerId: string) => {
  selectedMarkerId.value = markerId
}
const handleParticipantClick = (participantId: string) => {
  selectedParticipantId.value = participantId
}

const handleViewAllPhotos = (markerId: string) => {
  galleryMarker.value = markerId
}

const selectedCheckpointId = ref<string | null>(null)
const selectedCheckpoint = computed(
  () =>
    checkpoints.value.find((checkpoint) => checkpoint.id === selectedCheckpointId.value) ?? null,
)
const selectedRoutePointId = ref<string | null>(null)
const editorKind = ref<'checkpoint' | 'route' | null>(null)
const editorId = ref<string | null>(null)

function handleCheckpointClick(id: string) {
  selectedCheckpointId.value = id
  selectedRoutePointId.value = null
}

function handleRoutePointClick(id: string) {
  selectedRoutePointId.value = id
  selectedCheckpointId.value = null
}

function handleCheckpointAction(
  kind: 'checkpoint' | 'route',
  id: string,
  action: 'checkin' | 'edit' | 'delete' | 'photos' | 'qr',
  checkinId = id,
  checkinKind: 'checkpoint' | 'route_point' = kind === 'checkpoint' ? 'checkpoint' : 'route_point',
) {
  if (action === 'qr') {
    // Open the QR manager modal for this checkpoint
    // For routes, use the main_checkpoint id; for standalone checkpoints, use the id directly
    const checkpointId =
      kind === 'route' ? (routes.value.find((r) => r.id === id)?.main_checkpoint ?? checkinId) : id
    selectedCheckpointId.value = checkpointId
    selectedRoutePointId.value = null
    return
  }
  if (action === 'photos') {
    checkpointGallery.value = { kind, id }
    return
  }
  if (action === 'checkin') {
    if (checkinKind === 'checkpoint') {
      selectedCheckpointId.value = checkinId
      selectedRoutePointId.value = null
    } else {
      selectedRoutePointId.value = checkinId
      selectedCheckpointId.value = null
    }
    handleManualCheckIn()
  } else if (action === 'edit') {
    editorKind.value = kind
    editorId.value = id
  } else if (action === 'delete') {
    const name =
      kind === 'checkpoint'
        ? checkpoints.value.find((c) => c.id === id)?.name || 'чекпоїнт'
        : routes.value.find((r) => r.id === id)?.name || 'маршрут'
    itemToDelete.value = { id, kind, name }
  }
}

const itemToDelete = ref<{ id: string; kind: 'checkpoint' | 'route'; name: string } | null>(null)

function confirmDeleteItem() {
  if (!itemToDelete.value) return
  const { id, kind } = itemToDelete.value
  if (kind === 'checkpoint') {
    deleteCheckpoint.mutate(id, {
      onSuccess: () => {
        itemToDelete.value = null
        updateCheckpointLayers()
      },
    })
  } else {
    deleteRoute.mutate(id, {
      onSuccess: () => {
        itemToDelete.value = null
        updateCheckpointLayers()
      },
    })
  }
}

function handleManualCheckIn() {
  if (!userPosition.value) return
  if (selectedCheckpointId.value) {
    checkInMutation.mutate(
      {
        type: 'checkpoint',
        id: selectedCheckpointId.value,
        latitude: userPosition.value.latitude,
        longitude: userPosition.value.longitude,
        accuracy: userPosition.value.accuracy,
        is_manual: true,
      },
      {
        onSuccess: () => {
          selectedCheckpointId.value = null
          updateCheckpointLayers()
        },
      },
    )
  } else if (selectedRoutePointId.value) {
    checkInMutation.mutate(
      {
        type: 'route_point',
        id: selectedRoutePointId.value,
        latitude: userPosition.value.latitude,
        longitude: userPosition.value.longitude,
        accuracy: userPosition.value.accuracy,
        is_manual: true,
      },
      {
        onSuccess: () => {
          selectedRoutePointId.value = null
          updateCheckpointLayers()
        },
      },
    )
  }
}

const {
  baseLayer,
  focusParticipant,
  focusMeetingPoint,
  handleBaseLayerChange,
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
  updateZoneTrigger,
  deleteZone,
  measurementMode,
  measurementPoints,
  measurementSegmentDistances,
  measurementTotalDistance,
  toggleMeasurementMode,
  clearMeasurements,
  removeMeasurementPoint,
  checkpointDrawingMode,
  draftCheckpoint,
  draftRoutePoints,
  updateCheckpointLayers,
  setDrawingMode,
  setMeasurementMode,
} = useHomeMap({
  activityId,
  currentUserId,
  currentUserAvatar,
  participants,
  userPosition,
  markers,
  meetingPoints,
  zones,
  checkpoints,
  routes,
  visits,
  startTracking,
  onMarkerClick: handleMarkerClick,
  onParticipantClick: handleParticipantClick,
  onViewAllPhotos: handleViewAllPhotos,
  onCheckpointClick: handleCheckpointClick,
  onRoutePointClick: handleRoutePointClick,
  onCheckpointAction: handleCheckpointAction,
  onCreateZone: (payload) => createZone.mutate(payload),
  onUpdateZone: (payload) => updateZone.mutate(payload),
  onDeleteZone: (id) => deleteZoneMutation.mutate(id),
  hiddenParticipantIds,
  onMapClick: handleMapClick,
})

const focusParticipantId = computed(() => sosFocusParticipantId.value)
watch(
  [participants, focusParticipantId],
  async ([participantList, participantId]) => {
    if (!participantId) return
    const participant = Object.values(participantList).find(
      (item) => item.participant_id === participantId,
    )
    if (!participant) return
    await nextTick()
    focusParticipant(participant)
    requestSosParticipantFocus(undefined)
  },
  { immediate: true },
)

const createMarker = useCreateMarker({
  onSuccess: clearPin,
  onError: (error) => {
    markerError.value = getApiError(error)
  },
})
const updateMarker = useUpdateMarker({
  onSuccess: clearSelection,
  onError: (error) => {
    markerError.value = getApiError(error)
  },
})
const deleteMarker = useDeleteMarker({ onSuccess: clearSelection })
const uploadMarkerPhotos = useUploadMarkerPhotos()
const deleteMarkerPhoto = useDeleteMarkerPhoto()
const createZone = useCreateZone()
const updateZone = useUpdateZone()
const deleteZoneMutation = useDeleteZone()
const createCheckpoint = useCreateCheckpoint()
const createRoute = useCreateRoute()
const updateCheckpoint = useUpdateCheckpoint()
const updateRoute = useUpdateRoute()
const deleteCheckpoint = useDeleteCheckpoint()
const deleteRoute = useDeleteRoute()
const uploadCheckpointPhotos = useUploadCheckpointPhotos()
const deleteCheckpointPhoto = useDeleteCheckpointPhoto()

const editorCheckpoint = computed(
  () => checkpoints.value.find((item) => item.id === editorId.value) ?? null,
)
const editorRoute = computed(() => routes.value.find((item) => item.id === editorId.value) ?? null)
function saveEditedCheckpoint(payload: {
  id: string
  name: string
  description: string
  radius: number
  color: string
  points: number
}) {
  updateCheckpoint.mutate(
    { id: payload.id, payload },
    {
      onSuccess: () => {
        editorKind.value = null
      },
    },
  )
}
function saveEditedRoute(payload: {
  id: string
  name: string
  description: string
  color: string
  main_checkpoint: string
  main_checkpoint_points: number
  points: UpdateRoutePayload['points']
}) {
  updateRoute.mutate(
    { id: payload.id, payload },
    {
      onSuccess: () => {
        updateCheckpoint.mutate({
          id: payload.main_checkpoint,
          payload: { points: payload.main_checkpoint_points },
        })
        editorKind.value = null
      },
    },
  )
}
function uploadEditedPhotos(payload: {
  id: string
  kind: 'checkpoint' | 'route_point'
  files: File[]
}) {
  if (payload.id && payload.kind)
    uploadCheckpointPhotos.mutate({ id: payload.id, files: payload.files, kind: payload.kind })
}
function deleteEditedPhoto(payload: {
  id: string
  kind: 'checkpoint' | 'route_point'
  photoId: number
}) {
  if (payload.id && payload.kind)
    deleteCheckpointPhoto.mutate({ id: payload.id, photoId: payload.photoId, kind: payload.kind })
}

function handleSaveMarker(payload: {
  name: string
  description: string
  color: string
  meetingPoint: { name?: string; description?: string; start_time: string; end_time: string } | null
}) {
  if (!activityId.value || !pinCoords.value) return
  markerError.value = ''
  console.info('[activity-map] save marker', {
    activityId: activityId.value,
    pinCoords: pinCoords.value,
    payload,
  })
  createMarker.mutate({
    activity: activityId.value,
    name: payload.name,
    description: payload.description,
    color: payload.color,
    meeting_point: payload.meetingPoint,
    longitude: pinCoords.value[0],
    latitude: pinCoords.value[1],
  })
}
function handleUpdateMarker(payload: {
  id: string
  name: string
  description: string
  color: string
  meetingPoint: { name?: string; description?: string; start_time: string; end_time: string } | null
}) {
  markerError.value = ''
  console.info('[activity-map] update marker', payload)
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
function handleUploadMarkerPhotos(payload: { id: string; files: File[] }) {
  uploadMarkerPhotos.mutate({ markerId: payload.id, files: payload.files })
}
function handleDeleteMarkerPhoto(payload: { markerId: string; photoId: number }) {
  deleteMarkerPhoto.mutate(payload)
}
function editMeetingPoint(marker: LocationMarker) {
  handleMarkerClick(marker.id)
  focusMeetingPoint(marker)
}

function getDirectionsToMarker(marker: LocationMarker) {
  if (!userPosition.value) {
    alert('User location not available')
    return
  }

  const destLat = marker.latitude
  const destLng = marker.longitude
  const originLat = userPosition.value.latitude
  const originLng = userPosition.value.longitude

  const url = `https://map.project-osrm.org/?loc=${originLat},${originLng}&loc=${destLat},${destLng}`
  window.open(url, '_blank')
}
function getApiError(reason: unknown) {
  const response = reason as { response?: { data?: { detail?: string } } }
  console.error('[activity-map] marker mutation error', response.response?.data ?? reason)
  return response.response?.data?.detail ?? 'Не вдалося зберегти точку зустрічі.'
}

function handleSaveCheckpoint() {
  if (!activityId.value || !draftCheckpoint.value) return
  createCheckpoint.mutate(
    {
      activity: activityId.value,
      name: draftCheckpoint.value.name,
      description: draftCheckpoint.value.description,
      color: draftCheckpoint.value.color,
      radius: draftCheckpoint.value.radius,
      points: draftCheckpoint.value.points ?? 0,
      latitude: draftCheckpoint.value.coordinates[1],
      longitude: draftCheckpoint.value.coordinates[0],
    },
    {
      onSuccess: () => {
        checkpointDrawingMode.value = 'none'
        draftCheckpoint.value = null
        updateCheckpointLayers()
      },
    },
  )
}

function handleSaveRoute() {
  if (!activityId.value || draftRoutePoints.value.length === 0) return

  // Create Main Checkpoint first
  const mainPoint = draftRoutePoints.value[0]
  if (!mainPoint) return
  createCheckpoint.mutate(
    {
      activity: activityId.value,
      name: mainPoint.name,
      description: mainPoint.description,
      color: mainPoint.color,
      radius: mainPoint.radius,
      points: mainPoint.points ?? 0,
      latitude: mainPoint.coordinates[1],
      longitude: mainPoint.coordinates[0],
    },
    {
      onSuccess: (mainCp) => {
        // Create Route
        createRoute.mutate(
          {
            activity: activityId.value!,
            name: mainPoint.name + ' Route',
            description: mainPoint.description,
            main_checkpoint: mainCp.id,
            points: draftRoutePoints.value.slice(1).map((p, i) => ({
              sequence_number: i + 1,
              name: p.name,
              description: p.description,
              radius: p.radius,
              points: p.points ?? 0,
              latitude: p.coordinates[1],
              longitude: p.coordinates[0],
            })),
          },
          {
            onSuccess: () => {
              checkpointDrawingMode.value = 'none'
              draftRoutePoints.value.splice(0, draftRoutePoints.value.length)
              updateCheckpointLayers()
            },
          },
        )
      },
    },
  )
}

function updateDraftCheckpoint(payload: {
  name: string
  description: string
  radius: number
  color: string
  points: number
}) {
  if (draftCheckpoint.value) {
    draftCheckpoint.value.name = payload.name
    draftCheckpoint.value.description = payload.description
    draftCheckpoint.value.radius = payload.radius
    draftCheckpoint.value.color = payload.color
    draftCheckpoint.value.points = payload.points
    updateCheckpointLayers()
  }
}

function updateDraftRoutePoint(
  id: string,
  payload: { name: string; description: string; radius: number; color: string; points: number },
) {
  const p = draftRoutePoints.value.find((p) => p.id === id)
  if (p) {
    p.name = payload.name
    p.description = payload.description
    p.radius = payload.radius
    p.color = payload.color
    p.points = payload.points
    updateCheckpointLayers()
  }
}

function moveRoutePointUp(id: string) {
  const idx = draftRoutePoints.value.findIndex((p) => p.id === id)
  if (idx > 1) {
    // Cannot move main checkpoint (idx 0)
    const previous = draftRoutePoints.value[idx - 1]
    const current = draftRoutePoints.value[idx]
    if (!previous || !current) return
    draftRoutePoints.value[idx - 1] = current
    draftRoutePoints.value[idx] = previous
    updateCheckpointLayers()
  }
}

function moveRoutePointDown(id: string) {
  const idx = draftRoutePoints.value.findIndex((p) => p.id === id)
  if (idx > 0 && idx < draftRoutePoints.value.length - 1) {
    const next = draftRoutePoints.value[idx + 1]
    const current = draftRoutePoints.value[idx]
    if (!next || !current) return
    draftRoutePoints.value[idx + 1] = current
    draftRoutePoints.value[idx] = next
    updateCheckpointLayers()
  }
}

function deleteRoutePoint(id: string) {
  const idx = draftRoutePoints.value.findIndex((p) => p.id === id)
  if (idx > 0) {
    draftRoutePoints.value.splice(idx, 1)
    updateCheckpointLayers()
  }
}

function handleMapClick(e: maplibregl.MapMouseEvent | maplibregl.MapTouchEvent) {
  if (!isSelectingRouteDestination.value) return

  if (!userPosition.value) {
    alert('User location not available')
    isSelectingRouteDestination.value = false
    return
  }

  const destLat = e.lngLat.lat
  const destLng = e.lngLat.lng
  const originLat = userPosition.value.latitude
  const originLng = userPosition.value.longitude

  const url = `https://map.project-osrm.org/?loc=${originLat},${originLng}&loc=${destLat},${destLng}`
  window.open(url, '_blank')

  isSelectingRouteDestination.value = false
}

function startRouteDestinationSelection() {
  isSelectingRouteDestination.value = true
}

onMounted(() => {
  currentTimeTicker = window.setInterval(() => {
    currentTime.value = Date.now()
  }, 10_000)
})

onUnmounted(() => {
  if (currentTimeTicker !== null) window.clearInterval(currentTimeTicker)
})
</script>

<template>
  <div class="relative min-h-full">
    <div ref="mapContainer" class="h-screen w-full overflow-hidden rounded-md" />
    <p
      v-if="markerError"
      class="absolute left-4 right-4 top-4 z-50 rounded-lg border border-rose-400/30 bg-slate-950/90 px-4 py-3 text-sm text-rose-200 shadow-xl sm:left-4 sm:right-auto sm:max-w-md"
    >
      {{ markerError }}
    </p>

    <MapControlPanel
      :activity-id="activityId"
      :base-layer="baseLayer"
      :current-user-id="currentUserId"
      :location-error="locationError"
      :location-status="locationStatus"
      :participants="participants"
      :pin-coords="pinCoords"
      :status="status"
      :tracking-error="trackingError"
      :tracking-status="trackingStatus"
      :selected-marker="selectedMarker"
      :meeting-points="meetingPoints"
      :meeting-points-fetching="markersQuery.isFetching.value"
      :meeting-points-pending="markersQuery.isPending.value"
      :drawing-mode="drawingMode"
      :active-zone-point-count="activeZonePointCount"
      :active-zone-color="activeZoneColor"
      :drawn-zone-count="drawnZoneCount"
      :drawn-zones="drawnZoneSummaries"
      :measurement-mode="measurementMode"
      :measurement-points="measurementPoints"
      :measurement-segment-distances="measurementSegmentDistances"
      :measurement-total-distance="measurementTotalDistance"
      :roles="roles"
      :show-scratch-hexagons="showScratchHexagons"
      :is-selecting-route-destination="isSelectingRouteDestination"
      @focus-participant="focusParticipant"
      @locate-user="locateUser"
      @switch-to-osm="switchToOsm"
      @update-base-layer="handleBaseLayerChange"
      @save-marker="handleSaveMarker"
      @update-marker="handleUpdateMarker"
      @delete-marker="(id) => deleteMarker.mutate(id)"
      @upload-photos="handleUploadMarkerPhotos"
      @delete-photo="handleDeleteMarkerPhoto"
      @refresh-meeting-points="markersQuery.refetch()"
      @select-meeting-point="editMeetingPoint"
      @get-directions="getDirectionsToMarker"
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
      @update-zone-trigger="updateZoneTrigger"
      @delete-zone="deleteZone"
      @toggle-measurement-mode="toggleMeasurementMode"
      @clear-measurements="clearMeasurements"
      @remove-measurement-point="removeMeasurementPoint"
      :checkpoint-drawing-mode="checkpointDrawingMode || 'none'"
      :draft-checkpoint="draftCheckpoint || null"
      :draft-route-points="draftRoutePoints || []"
      :my-points="myPoints"
      :activity-points="activityPoints"
      @set-checkpoint-drawing-mode="(mode) => (checkpointDrawingMode = mode)"
      @update-draft-checkpoint="updateDraftCheckpoint"
      @save-checkpoint="handleSaveCheckpoint"
      @update-draft-route-point="updateDraftRoutePoint"
      @move-route-point-up="moveRoutePointUp"
      @move-route-point-down="moveRoutePointDown"
      @delete-route-point="deleteRoutePoint"
      @save-route="handleSaveRoute"
      @set-drawing-mode="setDrawingMode"
      @set-measurement-mode="setMeasurementMode"
      @get-directions-from-map="startRouteDestinationSelection"
    />

    <div
      v-if="isSelectingRouteDestination"
      class="absolute right-4 top-4 z-50 rounded-lg border border-amber-400/30 bg-slate-950/90 px-4 py-3 text-sm text-amber-200 shadow-xl"
    >
      Click on map to set destination
      <button
        type="button"
        class="ml-2 text-amber-400 hover:text-amber-300"
        @click="isSelectingRouteDestination = false"
      >
        Cancel
      </button>
    </div>

    <div
      v-if="galleryMarker"
      class="absolute inset-0 z-60 flex items-center justify-center bg-black/70 p-6"
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

    <div
      v-if="isSelectingRouteDestination"
      class="absolute right-4 top-4 z-51 rounded-lg border border-amber-400/30 bg-slate-950/90 px-4 py-3 text-sm text-amber-200 shadow-xl"
    >
      Click on map to set destination
      <button
        type="button"
        class="ml-2 text-amber-400 hover:text-amber-300"
        @click="isSelectingRouteDestination = false"
      >
        Cancel
      </button>
    </div>
    <UserLocationModal
      v-if="selectedParticipant"
      :participant="selectedParticipant"
      :activity-id="activityId"
      @close="selectedParticipantId = null"
    />

    <div
      v-if="false"
      class="absolute bottom-6 left-1/2 -translate-x-1/2 bg-slate-900/90 rounded-2xl p-4 text-white z-50 shadow-2xl border border-white/10 flex flex-col gap-3 min-w-62.5 backdrop-blur"
    >
      <div class="flex justify-between items-start gap-4">
        <div class="font-semibold text-sm">
          <template v-if="selectedCheckpointId">
            Checkpoint: {{ checkpoints.find((c) => c.id === selectedCheckpointId)?.name }}
          </template>
          <template v-else>
            Route Point:
            {{ routes.flatMap((r) => r.points).find((p) => p.id === selectedRoutePointId)?.name }}
          </template>
        </div>
        <button
          @click="((selectedCheckpointId = null), (selectedRoutePointId = null))"
          class="text-slate-400 hover:text-white"
        >
          ✕
        </button>
      </div>
      <template
        v-if="
          (selectedCheckpointId && visits.some((v) => v.checkpoint === selectedCheckpointId)) ||
          (selectedRoutePointId && visits.some((v) => v.route_point === selectedRoutePointId))
        "
      >
        <div
          class="w-full bg-emerald-500 text-white rounded-lg px-4 py-2 font-semibold text-sm text-center"
        >
          Visited
        </div>
      </template>
      <template v-else>
        <button
          @click="handleManualCheckIn"
          :disabled="checkInMutation.isPending.value"
          class="w-full bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white rounded-lg px-4 py-2 font-semibold text-sm transition-colors"
        >
          {{ checkInMutation.isPending.value ? 'Checking in...' : 'Manual Check In' }}
        </button>
      </template>
    </div>

    <CheckpointEditorModal
      v-if="editorKind"
      :kind="editorKind"
      :checkpoint="editorCheckpoint"
      :route="editorRoute"
      :checkpoints="checkpoints"
      @close="editorKind = null"
      @save-checkpoint="saveEditedCheckpoint"
      @save-route="saveEditedRoute"
      @upload-photos="uploadEditedPhotos"
      @delete-photo="deleteEditedPhoto"
    />

    <CheckpointQuestModal
      v-if="selectedCheckpoint"
      :checkpoint="selectedCheckpoint"
      :current-user-id="currentUserId"
      :activity-owner-id="currentActivity?.created_by"
      :location="userPosition"
      @close="selectedCheckpointId = null"
      @progress-changed="checkpointsQuery.refetch()"
    />

    <div
      v-if="checkpointGallery"
      class="absolute inset-0 z-70 flex items-center justify-center bg-black/70 p-6"
      @click.self="checkpointGallery = null"
    >
      <div
        class="max-h-[85vh] w-full max-w-3xl overflow-y-auto rounded-2xl bg-slate-950 p-4 text-white shadow-2xl"
      >
        <div class="mb-3 flex items-center justify-between">
          <h2 class="text-sm font-semibold">Photos</h2>
          <button class="text-slate-400 hover:text-white" @click="checkpointGallery = null">
            Close
          </button>
        </div>
        <div class="grid grid-cols-2 gap-3 sm:grid-cols-3">
          <img
            v-for="photo in checkpointGalleryPhotos"
            :key="photo.id"
            :src="photo.image"
            alt="Checkpoint photo"
            class="aspect-square w-full rounded-lg object-cover"
          />
        </div>
      </div>
    </div>

    <Teleport to="body">
      <div
        v-if="itemToDelete"
        class="fixed inset-0 z-50 flex items-end bg-black/60 p-0 sm:items-center sm:justify-center sm:p-4"
        role="presentation"
        @click.self="itemToDelete = null"
      >
        <section
          class="w-full rounded-t-2xl border bg-background p-5 shadow-xl sm:max-w-md sm:rounded-2xl"
          role="dialog"
          aria-modal="true"
          aria-labelledby="delete-item-title"
        >
          <h2 id="delete-item-title" class="text-lg font-semibold text-foreground">
            Видалити {{ itemToDelete.kind === 'checkpoint' ? 'точку підтвердження' : 'маршрут' }}?
          </h2>
          <p class="mt-2 text-sm leading-6 text-muted-foreground">
            Ви впевнені, що хочете видалити «{{ itemToDelete.name }}»? Цю дію не можна скасувати.
          </p>
          <div class="mt-6 flex flex-col-reverse gap-2 sm:flex-row sm:justify-end">
            <Button
              type="button"
              variant="outline"
              class="min-h-11 w-full sm:w-auto"
              @click="itemToDelete = null"
              >Скасувати</Button
            >
            <Button
              type="button"
              variant="destructive"
              class="min-h-11 w-full sm:w-auto"
              :disabled="deleteCheckpoint.isPending.value || deleteRoute.isPending.value"
              @click="confirmDeleteItem"
            >
              {{
                deleteCheckpoint.isPending.value || deleteRoute.isPending.value
                  ? 'Видалення...'
                  : 'Видалити'
              }}
            </Button>
          </div>
        </section>
      </div>
    </Teleport>
  </div>
</template>

<style scoped>
.maplibregl-ctrl-top-right {
  transform: translateY(0.5rem);
}
</style>
