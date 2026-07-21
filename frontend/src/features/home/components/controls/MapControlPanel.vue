<script setup lang="ts">
import { computed, ref, toRef, watch } from 'vue'
import { MessageCircle, Route } from '@lucide/vue'
import type { LocationStatus } from '@/composables/useUserLocation'
import type { ParticipantLocation, ActivityRole } from '@/features/activities'
import type { BaseLayer } from '../../utils/mapStyles'
import type { LocationMarker } from '@/features/locations/core/location.types.ts'
import type { DrawnZoneSummary } from '../../composables/useHomeMap'
import type { MeasurementPoint } from '@/features/measurements/core/measurement.utils.ts'
import type { ActivityPoint } from '@/features/checkpoints'
import type { ActivePanelKey } from './types'
import { useActivityChat } from '@/features/chat/composables/useActivityChat.ts'
import { useFriends } from '@/features/auth'

import ControlIconBar from './ControlIconBar.vue'
import DraggablePanel from './DraggablePanel.vue'
import MarkerFormPanel from './panels/MarkerFormPanel.vue'
import StatusPanel from './panels/StatusPanel.vue'
import LocationPanel from './panels/LocationPanel.vue'
import ParticipantsPanel from './panels/ParticipantsPanel.vue'
import BaseLayerPanel from './panels/BaseLayerPanel.vue'
import ZonesPanel from './panels/ZonesPanel.vue'
import ZonesListPanel from './panels/ZonesListPanel.vue'
import MeasurementPanel from './panels/MeasurementPanel.vue'
import CheckpointsPanel from './panels/CheckpointsPanel.vue'
import MeetingPointsPanel from './panels/MeetingPointsPanel.vue'
import ChatPanel from './panels/ChatPanel.vue'
import MyPointsPanel from './panels/MyPointsPanel.vue'

const props = defineProps<{
  activityId?: string
  baseLayer: BaseLayer
  showScratchHexagons: boolean
  currentUserId?: number
  locationError: string | null
  locationStatus: LocationStatus
  participants: Record<string, ParticipantLocation>
  pinCoords: [number, number] | null
  status: string
  trackingError: string | null
  trackingStatus: 'idle' | 'loading' | 'connected' | 'disconnected' | 'error'
  selectedMarker?: LocationMarker | null
  meetingPoints?: LocationMarker[]
  meetingPointsFetching?: boolean
  meetingPointsPending?: boolean
  drawingMode: boolean
  activeZonePointCount: number
  activeZoneColor: string
  drawnZoneCount: number
  drawnZones: DrawnZoneSummary[]
  measurementMode: boolean
  isSelectingRouteDestination?: boolean
  measurementPoints: MeasurementPoint[]
  measurementSegmentDistances: number[]
  measurementTotalDistance: number
  checkpointDrawingMode?: 'none' | 'checkpoint' | 'route'
  draftCheckpoint?: {
    coordinates: [number, number]
    radius: number
    name: string
    description: string
    color: string
    points: number
  } | null
  draftRoutePoints?: {
    id: string
    coordinates: [number, number]
    radius: number
    name: string
    description: string
    color: string
    points: number
  }[]
  myPoints?: number
  activityPoints?: ActivityPoint[]
  roles?: ActivityRole[]
}>()

const emit = defineEmits<{
  focusParticipant: [participant: ParticipantLocation]
  locateUser: []
  switchToOsm: []
  updateBaseLayer: [value: string]
  updateShowScratchHexagons: [value: boolean]
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
  refreshMeetingPoints: []
  selectMeetingPoint: [marker: LocationMarker]
  getDirections: [marker: LocationMarker]
  getDirectionsFromMap: []
  clearPin: []
  clearSelection: []
  toggleDrawingMode: []
  undoZonePoint: []
  finishZone: []
  clearActiveZone: []
  clearZones: []
  updateActiveZoneColor: [color: string]
  updateZoneColor: [payload: { id: string; color: string }]
  updateZoneName: [payload: { id: string; name: string }]
  updateZoneTrigger: [
    payload: {
      id: string
      trigger_action: 'no_action' | 'on_exit' | 'on_entry'
      trigger_subject_role: string | null
      trigger_notify_role: string | null
    },
  ]
  deleteZone: [id: string]
  toggleMeasurementMode: []
  clearMeasurements: []
  removeMeasurementPoint: [id: string]
  setCheckpointDrawingMode: [mode: 'none' | 'checkpoint' | 'route']
  updateDraftCheckpoint: [
    payload: { name: string; description: string; radius: number; color: string; points: number },
  ]
  saveCheckpoint: []
  updateDraftRoutePoint: [
    id: string,
    payload: { name: string; description: string; radius: number; color: string; points: number },
  ]
  moveRoutePointUp: [id: string]
  moveRoutePointDown: [id: string]
  deleteRoutePoint: [id: string]
  saveRoute: []
  setDrawingMode: [value: boolean]
  setMeasurementMode: [value: boolean]
}>()

const PANEL_TITLES: Record<ActivePanelKey, string> = {
  status: 'Map status',
  location: 'Your location',
  participants: 'Participants',
  chat: 'Activity chat',
  meetingPoints: 'Meeting points',
  layer: 'Base layer',
  measurement: 'Measure distance',
  zones: 'Draw zone',
  zonesList: 'Zone list',
  checkpoints: 'Checkpoints & Routes',
  activity: 'Activity',
}

const PANEL_KEYS: ActivePanelKey[] = [
  'status',
  'location',
  'participants',
  'chat',
  'meetingPoints',
  'layer',
  'measurement',
  'zones',
  'zonesList',
  'checkpoints',
  'activity',
]

type PanelState = { open: boolean; x: number; y: number; z: number; collapsed: boolean }

const PANEL_WIDTH = 272
const CASCADE = 24
const PANEL_Z = 52

const panels = ref<Record<ActivePanelKey, PanelState>>(
  Object.fromEntries(
    PANEL_KEYS.map((key) => [key, { open: false, x: 0, y: 0, z: PANEL_Z, collapsed: false }]),
  ) as Record<ActivePanelKey, PanelState>,
)

const menuOpenPanelsSet = computed<Set<ActivePanelKey>>(
  () => new Set(PANEL_KEYS.filter((k) => k !== 'chat' && panels.value[k].open)),
)

function spawnPosition(): { x: number; y: number } {
  const openCount = PANEL_KEYS.filter((k) => panels.value[k].open).length
  const vw = window.innerWidth
  const iconBarWidth = 72
  const margin = 28
  const baseX = Math.max(8, vw - iconBarWidth - margin - PANEL_WIDTH)
  const baseY = 96
  return {
    x: Math.max(8, baseX - openCount * CASCADE),
    y: Math.min(baseY + openCount * CASCADE, window.innerHeight - 200),
  }
}

function togglePanel(key: ActivePanelKey) {
  if (panels.value[key].open) {
    panels.value[key].open = false
    if (key === 'zones') emit('setDrawingMode', false)
    if (key === 'measurement') emit('setMeasurementMode', false)
  } else {
    const pos = spawnPosition()
    panels.value[key].x = pos.x
    panels.value[key].y = pos.y
    panels.value[key].open = true
    panels.value[key].collapsed = false
    bringToFront(key)
    if (key === 'zones') emit('setDrawingMode', true)
    if (key === 'measurement') emit('setMeasurementMode', true)
  }
}

function closePanel(key: ActivePanelKey) {
  panels.value[key].open = false
  if (key === 'zones') emit('setDrawingMode', false)
  if (key === 'measurement') emit('setMeasurementMode', false)
  if (key === 'checkpoints') emit('setCheckpointDrawingMode', 'none')
}

function bringToFront(key: ActivePanelKey) {
  // Static z-index - no changes needed
}

const markerPanelPos = ref({
  x: Math.max(8, window.innerWidth - 72 - 28 - 272),
  y: 142,
  z: PANEL_Z,
})

function bringMarkerPanelToFront() {
  // Static z-index - no changes needed
}

function handleCloseMarkerPanel() {
  if (props.selectedMarker) {
    emit('clearSelection')
  } else {
    emit('clearPin')
  }
}

const showMarkerPanel = computed(() => !!(props.pinCoords || props.selectedMarker))

const isChatOpen = computed(() => panels.value.chat.open && !panels.value.chat.collapsed)

const {
  messages: chatMessages,
  status: chatStatus,
  errorMessage: chatError,
  isSending: chatIsSending,
  unreadCount: chatUnreadCount,
  markRead: markChatRead,
  sendMessage,
} = useActivityChat(toRef(props, 'activityId'), isChatOpen)

const friendsQuery = useFriends()

const friendIds = computed(() => {
  return friendsQuery.data.value?.map(f => f.friend_id) || []
})

const showNewChatIndicator = ref(false)
const chatButtonLabel = computed(() =>
  chatUnreadCount.value > 0 ? `Activity chat, ${chatUnreadCount.value} unread` : 'Activity chat',
)

watch(chatUnreadCount, (count, previousCount) => {
  if (isChatOpen.value) {
    showNewChatIndicator.value = false
    return
  }

  if (count > previousCount) showNewChatIndicator.value = true
})

watch(isChatOpen, (open) => {
  if (open) {
    showNewChatIndicator.value = false
    markChatRead()
  }
})
</script>

<template>
  <div class="pointer-events-none fixed inset-0 z-50">
    <template v-for="key in PANEL_KEYS" :key="key">
      <DraggablePanel
        v-if="panels[key].open"
        :title="PANEL_TITLES[key]"
        :initial-x="panels[key].x"
        :initial-y="panels[key].y"
        :z-index="panels[key].z"
        :unread-count="key === 'chat' ? chatUnreadCount : undefined"
        v-model:collapsed="panels[key].collapsed"
        class="pointer-events-auto"
        :class="key === 'chat' ? '!w-[min(22rem,calc(100vw-2rem))]' : ''"
        @close="closePanel(key)"
        @focus="bringToFront(key)"
      >
        <StatusPanel v-if="key === 'status'" :status="status" />

        <LocationPanel
          v-else-if="key === 'location'"
          :location-error="locationError"
          :location-status="locationStatus"
        />

        <ParticipantsPanel
          v-else-if="key === 'participants'"
          :participants="participants"
          :current-user-id="currentUserId"
          :tracking-status="trackingStatus"
          :tracking-error="trackingError"
          :activity-id="activityId"
          :friend-ids="friendIds"
          @focus-participant="
            (p) => {
              emit('focusParticipant', p)
              closePanel(key)
            }
          "
        />

        <BaseLayerPanel
          v-else-if="key === 'layer'"
          :base-layer="baseLayer"
          :show-scratch-hexagons="showScratchHexagons"
          :show-scratch-map-toggle="!activityId"
          @update:base-layer="
            (v) => {
              emit('updateBaseLayer', v)
              closePanel(key)
            }
          "
          @update:show-scratch-hexagons="emit('updateShowScratchHexagons', $event)"
        />

        <ChatPanel
          v-else-if="key === 'chat'"
          :messages="chatMessages"
          :status="chatStatus"
          :error-message="chatError"
          :current-user-id="currentUserId"
          :is-sending="chatIsSending"
          @send="sendMessage"
        />

        <MeetingPointsPanel
          v-else-if="key === 'meetingPoints'"
          :meeting-points="meetingPoints ?? []"
          :is-fetching="!!meetingPointsFetching"
          :is-pending="!!meetingPointsPending"
          @refresh="emit('refreshMeetingPoints')"
          @select-meeting-point="
            (marker) => {
              emit('selectMeetingPoint', marker)
              closePanel(key)
            }
          "
          @get-directions="emit('getDirections', $event)"
        />

        <MeasurementPanel
          v-else-if="key === 'measurement'"
          :measurement-mode="measurementMode"
          :measurement-points="measurementPoints"
          :measurement-segment-distances="measurementSegmentDistances"
          :measurement-total-distance="measurementTotalDistance"
          @toggle-measurement-mode="
            () => {
              emit('toggleMeasurementMode')
              closePanel(key)
            }
          "
          @clear-measurements="
            () => {
              emit('clearMeasurements')
              closePanel(key)
            }
          "
          @remove-measurement-point="(id) => emit('removeMeasurementPoint', id)"
        />

        <ZonesPanel
          v-else-if="key === 'zones'"
          :drawing-mode="drawingMode"
          :active-zone-point-count="activeZonePointCount"
          :active-zone-color="activeZoneColor"
          :drawn-zone-count="drawnZoneCount"
          :drawn-zones="drawnZones"
          :roles="roles || []"
          @toggle-drawing-mode="
            () => {
              emit('toggleDrawingMode')
              closePanel(key)
            }
          "
          @undo-zone-point="emit('undoZonePoint')"
          @finish-zone="emit('finishZone')"
          @clear-active-zone="emit('clearActiveZone')"
          @update-active-zone-color="(c) => emit('updateActiveZoneColor', c)"
          @clear-zones="emit('clearZones')"
        />

        <ZonesListPanel
          v-else-if="key === 'zonesList'"
          :drawn-zone-count="drawnZoneCount"
          :drawn-zones="drawnZones"
          :roles="roles || []"
          @update-zone-color="(p) => emit('updateZoneColor', p)"
          @update-zone-name="(p) => emit('updateZoneName', p)"
          @update-zone-trigger="(p) => emit('updateZoneTrigger', p)"
          @delete-zone="(id) => emit('deleteZone', id)"
        />

        <CheckpointsPanel
          v-else-if="key === 'checkpoints'"
          :drawing-mode="checkpointDrawingMode || 'none'"
          :draft-checkpoint="draftCheckpoint || null"
          :draft-route-points="draftRoutePoints || []"
          @set-checkpoint-drawing-mode="
            (mode) => {
              emit('setCheckpointDrawingMode', mode)
            }
          "
          @update-draft-checkpoint="emit('updateDraftCheckpoint', $event)"
          @save-checkpoint="
            () => {
              emit('saveCheckpoint')
              closePanel(key)
            }
          "
          @update-draft-route-point="(id, payload) => emit('updateDraftRoutePoint', id, payload)"
          @move-route-point-up="emit('moveRoutePointUp', $event)"
          @move-route-point-down="emit('moveRoutePointDown', $event)"
          @delete-route-point="emit('deleteRoutePoint', $event)"
          @save-route="
            () => {
              emit('saveRoute')
              closePanel(key)
            }
          "
        />

        <MyPointsPanel
          v-else-if="key === 'activity'"
          :my-points="myPoints"
          :activity-points="activityPoints"
          :activity-id="activityId"
        />
      </DraggablePanel>
    </template>

    <DraggablePanel
      v-if="showMarkerPanel"
      :title="selectedMarker ? 'Edit marker' : 'Dropped pin'"
      :initial-x="markerPanelPos.x"
      :initial-y="markerPanelPos.y"
      :z-index="markerPanelPos.z"
      class="pointer-events-auto"
      @close="handleCloseMarkerPanel"
      @focus="bringMarkerPanelToFront"
    >
      <MarkerFormPanel
        :activity-id="activityId"
        :pin-coords="pinCoords"
        :selected-marker="selectedMarker"
        @save-marker="(p) => emit('saveMarker', p)"
        @update-marker="(p) => emit('updateMarker', p)"
        @delete-marker="(id) => emit('deleteMarker', id)"
        @upload-photos="(p) => emit('uploadPhotos', p)"
        @delete-photo="(p) => emit('deletePhoto', p)"
        @clear-pin="emit('clearPin')"
        @clear-selection="emit('clearSelection')"
      />
    </DraggablePanel>

    <div
      class="pointer-events-auto absolute right-4 top-17 flex flex-col items-end gap-2 sm:right-6 sm:top-20"
    >
      <div class="flex flex-row items-end gap-2">
        <button
          v-if="activityId"
          type="button"
          class="group relative flex h-12 w-12 shrink-0 items-center justify-center self-end rounded-2xl border border-white/15 bg-slate-950/85 text-slate-200 shadow-2xl shadow-slate-950/25 backdrop-blur-xl transition hover:bg-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-400"
          :class="
            isChatOpen
              ? 'border-blue-400/60 bg-blue-600 text-white hover:bg-blue-600'
              : chatUnreadCount > 0
                ? 'border-blue-400/50 text-white ring-2 ring-blue-400/40'
                : ''
          "
          :aria-label="chatButtonLabel"
          title="Activity chat"
          @click="togglePanel('chat')"
        >
          <span
            v-if="showNewChatIndicator"
            class="absolute right-full top-1/2 mr-2 -translate-y-1/2 rounded-full border border-blue-300/50 bg-blue-500 px-2 py-1 text-[10px] font-bold uppercase tracking-wide text-white shadow-lg shadow-blue-950/30"
            aria-hidden="true"
          >
            New
          </span>
          <MessageCircle class="h-5 w-5" aria-hidden="true" />
          <span
            class="absolute -bottom-0.5 -right-0.5 h-3 w-3 rounded-full border-2 border-slate-950"
            :class="chatStatus === 'connected' ? 'bg-emerald-400' : 'bg-slate-500'"
            aria-hidden="true"
          />
          <span
            v-if="chatUnreadCount > 0"
            class="absolute -right-2 -top-2 min-w-5 rounded-full bg-blue-500 px-1.5 py-0.5 text-center text-[10px] font-bold leading-none text-white ring-2 ring-slate-950"
            aria-hidden="true"
          >
            {{ chatUnreadCount > 9 ? '9+' : chatUnreadCount }}
          </span>
        </button>

        <button
          type="button"
          class="group relative flex h-12 w-12 shrink-0 items-center justify-center self-end rounded-2xl border border-white/15 bg-slate-950/85 text-slate-200 shadow-2xl shadow-slate-950/25 backdrop-blur-xl transition hover:bg-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-400"
          :class="
            isSelectingRouteDestination
              ? 'border-blue-400/60 bg-blue-600 text-white hover:bg-blue-600'
              : ''
          "
          aria-label="Get directions"
          title="Get directions"
          @click="emit('getDirectionsFromMap')"
        >
          <Route class="h-5 w-5" aria-hidden="true" />
        </button>
      </div>

      <ControlIconBar
        :open-panels="menuOpenPanelsSet"
        :has-activity="!!activityId"
        :has-location-error="!!locationError"
        :measurement-mode-active="measurementMode"
        @toggle="togglePanel"
      />

      <button
        v-if="status === 'error'"
        class="rounded-xl border border-white/15 bg-slate-950/80 px-4 py-2 text-xs font-medium text-white shadow-2xl backdrop-blur-xl transition-colors hover:bg-slate-800"
        @click="emit('switchToOsm')"
      >
        Use OSM tiles
      </button>
    </div>
  </div>
</template>
