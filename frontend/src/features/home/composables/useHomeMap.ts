import { onBeforeUnmount, onMounted, ref, watch, type Ref } from 'vue'
import maplibregl, { Point } from 'maplibre-gl'
import type { UserLocation } from '@/composables/useUserLocation'
import type { ParticipantLocation } from '@/features/activities'
import {
  addScratchMapLayers,
  animateScratchMapFeatures,
  SCRATCH_MAP_SOURCE,
  setScratchMapLayersVisibility,
} from '../utils/mapLayers'
import {
  safeDiscoveryFeature,
  scratchMapFeatureCollection,
} from '@/features/exploration/core/scratchMapGeoJson'
import type { ScratchDiscovery } from '@/features/exploration/core/scratchMap.types'
import { baseLayerStyle, type BaseLayer } from '../utils/mapStyles'

import type {
  ActivityZone,
  CreateActivityZonePayload,
  LocationMarker,
  UpdateActivityZonePayload,
} from '@/features/locations/core/location.types'
import type { Checkpoint, Route, Visit } from '@/features/checkpoints'
import { useMapActivityMarkers } from './useMapActivityMarkers'
import { useMapCheckpoints } from './useMapCheckpoints'
import { useMapMeasurements } from './useMapMeasurements'
import { useMapMeetingPoints } from './useMapMeetingPoints'
import { useMapParticipants } from './useMapParticipants'
import { useMapZones } from './useMapZones'

export type { DrawnZoneSummary } from './useMapZones'

const SCRATCH_MAP_VISIBILITY_STORAGE_KEY = 'mdvl-scratch-map-hexagons-visible'

function readScratchMapVisibilityPreference() {
  if (typeof window === 'undefined') return true
  return window.localStorage.getItem(SCRATCH_MAP_VISIBILITY_STORAGE_KEY) !== 'false'
}

type UseHomeMapOptions = {
  activityId: Ref<string | undefined>
  currentUserId: Ref<number | undefined>
  currentUserAvatar: Ref<string | null | undefined>
  participants: Ref<Record<string, ParticipantLocation>>
  userPosition: Ref<UserLocation | null>
  markers: Ref<LocationMarker[]>
  meetingPoints?: Ref<LocationMarker[]>
  zones?: Ref<ActivityZone[]>
  startTracking: () => void
  onMarkerClick?: (markerId: string) => void
  onClearMarkerSelection?: () => void
  onParticipantClick?: (participantId: string) => void
  onViewAllPhotos?: (markerId: string) => void
  onCreateZone?: (payload: CreateActivityZonePayload) => void
  onUpdateZone?: (payload: { id: string; payload: UpdateActivityZonePayload }) => void
  onDeleteZone?: (id: string) => void
  checkpoints?: Ref<Checkpoint[]>
  routes?: Ref<Route[]>
  visits?: Ref<Visit[]>
  scratchDiscoveries?: Ref<readonly ScratchDiscovery[]>
  onCheckpointClick?: (id: string) => void
  onRoutePointClick?: (id: string) => void
  onCheckpointAction?: (
    kind: 'checkpoint' | 'route',
    id: string,
    action: 'checkin' | 'edit' | 'delete' | 'photos' | 'qr',
    checkinId?: string,
    checkinKind?: 'checkpoint' | 'route_point',
  ) => void
  hiddenParticipantIds?: Ref<string[]>
  onMapClick?: (e: maplibregl.MapMouseEvent | maplibregl.MapTouchEvent) => void
}

function createPinElement() {
  const wrapper = document.createElement('div')
  wrapper.style.display = 'inline-flex'
  wrapper.style.flexDirection = 'column'
  wrapper.style.alignItems = 'center'
  wrapper.style.justifyContent = 'center'
  wrapper.style.pointerEvents = 'auto'

  const svgNS = 'http://www.w3.org/2000/svg'
  const svg = document.createElementNS(svgNS, 'svg')
  svg.setAttribute('width', '30')
  svg.setAttribute('height', '40')
  svg.setAttribute('viewBox', '0 0 24 24')

  svg.innerHTML = `
    <path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7z" fill="#ef4444"/>
    <circle cx="12" cy="9" r="2.5" fill="white"/>
  `

  const shadow = document.createElement('div')
  shadow.style.width = '10px'
  shadow.style.height = '4px'
  shadow.style.background = 'rgba(0,0,0,0.25)'
  shadow.style.borderRadius = '50%'
  shadow.style.marginTop = '-6px'
  shadow.style.filter = 'blur(2px)'

  wrapper.appendChild(svg)
  wrapper.appendChild(shadow)

  return wrapper
}

export function useHomeMap({
  activityId,
  currentUserId,
  currentUserAvatar,
  participants,
  userPosition,
  markers,
  meetingPoints,
  zones,
  startTracking,
  onMarkerClick,
  onClearMarkerSelection,
  onParticipantClick,
  onViewAllPhotos,
  onCreateZone,
  onUpdateZone,
  onDeleteZone,
  checkpoints,
  routes,
  visits,
  scratchDiscoveries,
  onRoutePointClick,
  onCheckpointAction,
  hiddenParticipantIds,
  onMapClick,
}: UseHomeMapOptions) {
  const mapContainer = ref<HTMLDivElement | null>(null)
  const status = ref('initializing')
  const pinCoords = ref<[number, number] | null>(null)
  const baseLayer = ref<BaseLayer>('osm')
  const showScratchHexagons = ref(readScratchMapVisibilityPreference())
  const mapReady = ref(false)
  const locationAgeTick = ref(Date.now())
  let map: maplibregl.Map | null = null
  const pendingFocusParticipant = ref<ParticipantLocation | null>(null)
  let pinMarker: maplibregl.Marker | null = null
  let locationAgeInterval: number | null = null
  let markerPopup: maplibregl.Popup | null = null
  let longPressTimer: number | null = null
  let longPressStart: {
    x: number
    y: number
    point: [number, number]
    lngLat: [number, number]
  } | null = null
  let suppressNextMapClick = false
  const renderedScratchCells = new Set<string>()

  let setMeasurementModeFromApi: ((value: boolean) => void) | null = null
  const zonesApi = useMapZones({
    activityId,
    mapReady,
    getMap: () => map,
    onCreateZone,
    onUpdateZone,
    onDeleteZone,
    onEnableDrawing: () => {
      setMeasurementModeFromApi?.(false)
      clearPin()
      markerPopup?.remove()
      markerPopup = null
    },
  })

  const measurementsApi = useMapMeasurements({
    mapReady,
    getMap: () => map,
    isDrawingMode: () => zonesApi.drawingMode.value,
    onEnableMeasurement: () => {
      zonesApi.setDrawingMode(false)
      clearPin()
      markerPopup?.remove()
      markerPopup = null
    },
  })

  const {
    drawingMode,
    activeZonePoints,
    activeZoneColor,
    drawnZones,
    activeZonePointCount,
    drawnZoneCount,
    drawnZoneSummaries,
    addZonePoint,
    setDrawingMode,
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
    updateZoneLayers,
    syncZonesFromRecords,
  } = zonesApi

  const {
    measurementMode,
    measurementPoints,
    measurementSegmentDistances,
    measurementTotalDistance,
    addMeasurementPoint,
    removeMeasurementPoint,
    clearMeasurements,
    setMeasurementMode,
    toggleMeasurementMode,
    updateMeasurementLayers,
    updateMeasurementMarkers,
    removeMeasurementMarkers,
  } = measurementsApi
  setMeasurementModeFromApi = setMeasurementMode

  const checkpointsApi = useMapCheckpoints({
    checkpoints,
    routes,
    visits,
    mapReady,
    getMap: () => map,
    getMarkerPopup: () => markerPopup,
    setMarkerPopup: (popup) => {
      markerPopup = popup
    },
    onRoutePointClick,
    onCheckpointAction,
  })
  const {
    checkpointDrawingMode,
    draftCheckpoint,
    draftRoutePoints,
    updateCheckpointLayers,
    addDraftCheckpoint,
    addDraftRoutePoint,
  } = checkpointsApi

  const activityMarkersApi = useMapActivityMarkers({
    markers,
    mapReady,
    getMap: () => map,
    getMarkerPopup: () => markerPopup,
    setMarkerPopup: (popup) => {
      markerPopup = popup
    },
    clearPin,
    shouldSuppressContextMenu: () => suppressNextMapClick,
    onMarkerClick,
    onViewAllPhotos,
  })
  const {
    markerFeatureDetails,
    queryMarkerFeature,
    showMarkerPopup,
    openMarkerEditor,
    updateMarkersLayer,
  } = activityMarkersApi

  const meetingPointsApi = useMapMeetingPoints({
    meetingPoints,
    mapReady,
    getMap: () => map,
    getMarkerPopup: () => markerPopup,
    setMarkerPopup: (popup) => {
      markerPopup = popup
    },
  })
  const { focusMeetingPoint, updateMeetingPointsLayer } = meetingPointsApi

  const participantsApi = useMapParticipants({
    activityId,
    currentUserId,
    currentUserAvatar,
    participants,
    userPosition,
    locationAgeTick,
    mapReady,
    getMap: () => map,
    onParticipantClick,
    hiddenParticipantIds,
  })
  const {
    sosData,
    sosDistanceData,
    updateUserMarker,
    updateUserLocationLayer,
    updateParticipantLayers,
    removeUserMarker,
  } = participantsApi
  function updateScratchMapLayer() {
    if (activityId.value || !map || !mapReady.value || !scratchDiscoveries) return

    const data = scratchMapFeatureCollection(scratchDiscoveries.value)
    const source = map.getSource(SCRATCH_MAP_SOURCE)
    if (!source) {
      map.addSource(SCRATCH_MAP_SOURCE, { type: 'geojson', data })
      renderedScratchCells.clear()
      data.features.forEach((feature) => renderedScratchCells.add(feature.properties.h3_index))
      addScratchMapLayers(map)
      setScratchMapLayersVisibility(map, showScratchHexagons.value)
      return
    }

    if (!('setData' in source)) return
    const newFeatures = scratchDiscoveries.value
      .filter((discovery) => !renderedScratchCells.has(discovery.h3_index))
      .flatMap((discovery) => {
        const feature = safeDiscoveryFeature(discovery)
        return feature ? [feature] : []
      })
    if (newFeatures.length === 0) return

    const incrementalSource = source as maplibregl.GeoJSONSource & {
      updateData?: (data: { add?: unknown[]; remove?: string[] }) => void
    }
    if (typeof incrementalSource.updateData !== 'function') {
      console.warn('[scratch-map] MapLibre incremental source updates unavailable, falling back to full data update')
      const data = scratchMapFeatureCollection(scratchDiscoveries.value)
      ;(source as maplibregl.GeoJSONSource).setData(data)
      renderedScratchCells.clear()
      data.features.forEach((feature) => renderedScratchCells.add(feature.properties.h3_index))
      addScratchMapLayers(map)
      setScratchMapLayersVisibility(map, showScratchHexagons.value)
      return
    }
    incrementalSource.updateData({ add: newFeatures })
    newFeatures.forEach((feature) => renderedScratchCells.add(feature.properties.h3_index))
    addScratchMapLayers(map)
    setScratchMapLayersVisibility(map, showScratchHexagons.value)
    animateScratchMapFeatures(
      map,
      newFeatures.map((feature) => feature.properties.h3_index),
    )
  }

  function setShowScratchHexagons(value: boolean) {
    showScratchHexagons.value = value
    if (typeof window !== 'undefined') {
      window.localStorage.setItem(SCRATCH_MAP_VISIBILITY_STORAGE_KEY, String(value))
    }
    if (map) setScratchMapLayersVisibility(map, value)
  }

  function restoreRuntimeLayersAfterStyleLoad() {
    if (!map) return

    mapReady.value = true
    if (pinMarker) pinMarker.addTo(map)
    updateUserMarker()
    updateUserLocationLayer()
    updateScratchMapLayer()
    updateParticipantLayers()
    updateMarkersLayer()
    updateMeetingPointsLayer()
    updateZoneLayers()
    updateCheckpointLayers()
    updateMeasurementLayers()
    updateMeasurementMarkers()
  }

  if (scratchDiscoveries) {
    watch(scratchDiscoveries, updateScratchMapLayer, { deep: true })
  }

  function setBaseLayer(name: BaseLayer) {
    baseLayer.value = name
    if (!map) return

    status.value = 'loading'
    mapReady.value = false
    map.once('style.load', () => {
      restoreRuntimeLayersAfterStyleLoad()
      status.value = name === 'sat' ? 'loaded' : `loaded (${name})`
    })
    map.setStyle(baseLayerStyle(name))
  }

  function handleBaseLayerChange(value: string) {
    if (value === 'sat' || value === 'osm' || value === 'carto') {
      setBaseLayer(value)
    }
  }

  function addPin(lngLat: [number, number]) {
    if (!map) return

    onClearMarkerSelection?.()

    if (!pinMarker) {
      const el = createPinElement()
      pinMarker = new maplibregl.Marker({ element: el, anchor: 'bottom', draggable: true })
        .setLngLat(lngLat)
        .addTo(map)

      pinMarker.on('dragend', () => {
        const ll = pinMarker?.getLngLat()
        if (ll) pinCoords.value = [ll.lng, ll.lat]
      })
    } else {
      pinMarker.setLngLat(lngLat)
    }

    pinCoords.value = [lngLat[0], lngLat[1]]
    try {
      map.easeTo({ center: lngLat, offset: [0, -100], duration: 700 })
    } catch {
      map.flyTo({ center: lngLat, zoom: Math.max(map.getZoom(), 14) })
    }
  }

  function canOpenMarkerByHold() {
    return checkpointDrawingMode.value === 'none' && !measurementMode.value && !drawingMode.value
  }

  function clearLongPressTimer() {
    if (longPressTimer !== null) {
      window.clearTimeout(longPressTimer)
      longPressTimer = null
    }
    longPressStart = null
  }

  function handleMapLongPress() {
    if (!map || !longPressStart || !canOpenMarkerByHold()) return

    const markerFeature = queryMarkerFeature(longPressStart.point)

    if (markerFeature) {
      const details = markerFeatureDetails(markerFeature)
      if (details) openMarkerEditor(details.markerId)
    } else {
      addPin(longPressStart.lngLat)
    }

    suppressNextMapClick = true
  }

  function bindLongPressMarkerInteraction() {
    if (!map) return

    const canvas = map.getCanvas()
    const holdDelay = 450
    const moveTolerance = 16

    canvas.addEventListener('pointerdown', (event) => {
      if (event.button !== 0 || !canOpenMarkerByHold()) return

      clearLongPressTimer()
      const rect = canvas.getBoundingClientRect()
      const point: [number, number] = [event.clientX - rect.left, event.clientY - rect.top]
      const lngLat = map!.unproject(point)
      longPressStart = {
        x: event.clientX,
        y: event.clientY,
        point,
        lngLat: [lngLat.lng, lngLat.lat],
      }
      longPressTimer = window.setTimeout(() => {
        longPressTimer = null
        handleMapLongPress()
      }, holdDelay)
    })

    canvas.addEventListener('pointermove', (event) => {
      if (!longPressStart) return

      const distance = Math.hypot(
        event.clientX - longPressStart.x,
        event.clientY - longPressStart.y,
      )
      if (distance > moveTolerance) clearLongPressTimer()
    })

    canvas.addEventListener('pointerup', clearLongPressTimer)
    canvas.addEventListener('pointercancel', clearLongPressTimer)
    canvas.addEventListener('pointerleave', clearLongPressTimer)
  }

  function locateUser() {
    if (userPosition.value && map) {
      map.flyTo({
        center: [userPosition.value.longitude, userPosition.value.latitude],
        zoom: Math.max(map.getZoom(), 14),
      })
    } else {
      startTracking()
    }
  }

  function switchToOsm() {
    setBaseLayer('osm')
  }

  function focusParticipant(participant: ParticipantLocation) {
    if (!participant.location) return
    if (!map || !mapReady.value) {
      pendingFocusParticipant.value = participant
      return
    }

    map.flyTo({
      center: [participant.location.longitude, participant.location.latitude],
      zoom: Math.max(map.getZoom(), 15),
      duration: 700,
    })
  }

  watch(mapReady, (ready) => {
    if (!ready || !pendingFocusParticipant.value) return
    const participant = pendingFocusParticipant.value
    pendingFocusParticipant.value = null
    focusParticipant(participant)
  })

  onMounted(() => {
    if (!mapContainer.value) return

    window.addEventListener('mdvl:locate-user', locateUser)

    map = new maplibregl.Map({
      container: mapContainer.value,
      style: baseLayerStyle('osm'),
      center: [30.5234, 50.4501],
      zoom: 10,
    })

    map.addControl(new maplibregl.NavigationControl({ showCompass: false }), 'top-right')
    bindLongPressMarkerInteraction()

    map.on('load', () => {
      status.value = 'loaded'
      restoreRuntimeLayersAfterStyleLoad()
    })

    map.on('error', (e) => {
      console.error('[maplibre] error', e)
      status.value = 'error'
    })

    map.on('click', (e) => {
      if (suppressNextMapClick) {
        suppressNextMapClick = false
        return
      }
      if (e.defaultPrevented) return
      if (checkpointDrawingMode.value === 'checkpoint') {
        addDraftCheckpoint([e.lngLat.lng, e.lngLat.lat])
        return
      }
      if (checkpointDrawingMode.value === 'route') {
        addDraftRoutePoint([e.lngLat.lng, e.lngLat.lat])
        return
      }
      if (measurementMode.value) {
        addMeasurementPoint([e.lngLat.lng, e.lngLat.lat])
        return
      }
      if (drawingMode.value) {
        addZonePoint([e.lngLat.lng, e.lngLat.lat])
        return
      }
      onMapClick?.(e)
    })

    // Right-click on map to drop a pin
    map.on('contextmenu', (e) => {
      if (e.defaultPrevented) return
      if (drawingMode.value || measurementMode.value || checkpointDrawingMode.value !== 'none')
        return
      e.preventDefault()
      addPin([e.lngLat.lng, e.lngLat.lat])
    })

    // Touch hold (long press) to drop pin or edit marker on mobile/tablet
    let touchTimeout: number | null = null
    let touchStartLngLat: maplibregl.LngLat | null = null
    let touchStartPoint: Point | null = null

    function clearTouchTimeout() {
      if (touchTimeout) {
        window.clearTimeout(touchTimeout)
        touchTimeout = null
      }
      touchStartLngLat = null
      touchStartPoint = null
    }

    map.on('touchstart', (e) => {
      if (e.originalEvent.touches.length !== 1) {
        clearTouchTimeout()
        return
      }
      touchStartLngLat = e.lngLat
      touchStartPoint = e.point

      touchTimeout = window.setTimeout(() => {
        if (!map || !touchStartLngLat || !touchStartPoint) return

        // Check if user touched an activity marker
        const features = map.queryRenderedFeatures(touchStartPoint, {
          layers: ['activity-markers-circle'],
        })

        const markerFeature = features[0]
        if (markerFeature?.properties?.id) {
          const markerId = markerFeature.properties.id as string
          const coords = (markerFeature.geometry as { coordinates: [number, number] }).coordinates
          showMarkerPopup(markerId, coords)
          onMarkerClick?.(markerId)
          if (navigator.vibrate) {
            navigator.vibrate(50)
          }
        } else {
          if (drawingMode.value || measurementMode.value || checkpointDrawingMode.value !== 'none')
            return
          addPin([touchStartLngLat.lng, touchStartLngLat.lat])
          if (navigator.vibrate) {
            navigator.vibrate(50)
          }
        }
        clearTouchTimeout()
      }, 700)
    })

    map.on('touchmove', (e) => {
      if (touchStartPoint && e.point) {
        const dx = e.point.x - touchStartPoint.x
        const dy = e.point.y - touchStartPoint.y
        const distance = Math.sqrt(dx * dx + dy * dy)
        if (distance > 10) {
          clearTouchTimeout()
        }
      }
    })

    map.on('touchend', () => {
      clearTouchTimeout()
    })

    map.on('touchcancel', () => {
      clearTouchTimeout()
    })

    startTracking()
    locationAgeInterval = window.setInterval(() => {
      locationAgeTick.value = Date.now()
    }, 10_000)
  })

  function clearPin() {
    if (pinMarker) {
      pinMarker.remove()
      pinMarker = null
    }
    pinCoords.value = null
  }

  watch(
    [
      userPosition,
      mapReady,
      activityId,
      participants,
      currentUserId,
      currentUserAvatar,
      locationAgeTick,
      sosData,
      sosDistanceData,
      markers,
      drawingMode,
      activeZonePoints,
      activeZoneColor,
      drawnZones,
      ...(meetingPoints ? [meetingPoints] : []),
    ],
    () => {
      updateUserLocationLayer()
      updateUserMarker()
      updateParticipantLayers()
      updateMarkersLayer()
      updateMeetingPointsLayer()
      updateZoneLayers()
      updateCheckpointLayers()
      updateMeasurementLayers()
    },
    { deep: true },
  )

  watch(
    sosData,
    (value, previous) => {
      const newest = value.features.find(
        (feature) =>
          !new Set((previous?.features ?? []).map((item) => item.properties?.participantId)).has(
            feature.properties?.participantId,
          ),
      )
      if (!newest) return
      const participant = Object.values(participants.value).find(
        (item) => item.participant_id === newest.properties?.participantId,
      )
      if (participant) focusParticipant(participant)
    },
    { deep: true },
  )

  watch(
    () => [checkpoints?.value, routes?.value, visits?.value],
    () => {
      updateCheckpointLayers()
    },
    { deep: true, immediate: true },
  )

  watch(
    () => zones?.value,
    (value) => {
      syncZonesFromRecords(value)
    },
    { deep: true, immediate: true },
  )

  onBeforeUnmount(() => {
    window.removeEventListener('mdvl:locate-user', locateUser)
    if (locationAgeInterval !== null) window.clearInterval(locationAgeInterval)
    if (map) {
      removeMeasurementMarkers()
      removeUserMarker()
      markerPopup?.remove()
      map.remove()
      map = null
    }
  })

  return {
    baseLayer,
    focusParticipant,
    focusMeetingPoint,
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
    drawnZoneCount,
    drawnZoneSummaries,
    activeZoneColor,
    toggleDrawingMode,
    undoZonePoint,
    finishZone,
    clearActiveZone,
    clearZones,
    measurementMode,
    measurementPoints,
    measurementSegmentDistances,
    measurementTotalDistance,
    toggleMeasurementMode,
    clearMeasurements,
    removeMeasurementPoint,
    updateActiveZoneColor,
    updateZoneColor,
    updateZoneName,
    updateZoneTrigger,
    deleteZone,
    checkpointDrawingMode,
    draftCheckpoint,
    draftRoutePoints,
    updateCheckpointLayers,
    setDrawingMode,
    setMeasurementMode,
  }
}
