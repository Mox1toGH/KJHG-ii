import { computed, ref, type Ref } from 'vue'
import type maplibregl from 'maplibre-gl'
import type {
  ActivityZone,
  CreateActivityZonePayload,
  UpdateActivityZonePayload,
} from '@/features/locations/core/location.types'

type ZoneFeatureCollection = {
  type: 'FeatureCollection'
  features: Array<{
    type: 'Feature'
    geometry:
      | { type: 'Polygon'; coordinates: [number, number][][] }
      | { type: 'LineString'; coordinates: [number, number][] }
      | { type: 'Point'; coordinates: [number, number] }
    properties: Record<string, string | number>
  }>
}

export type DrawnZoneSummary = {
  id: string
  name: string
  color: string
  pointCount: number
  trigger_action: 'no_action' | 'on_exit' | 'on_entry'
  trigger_subject_role: string | null
  trigger_notify_role: string | null
}

type DrawnZone = {
  id: string
  name: string
  points: [number, number][]
  color: string
  trigger_action: 'no_action' | 'on_exit' | 'on_entry'
  trigger_subject_role: string | null
  trigger_notify_role: string | null
}

type UseMapZonesOptions = {
  activityId: Ref<string | undefined>
  mapReady: Ref<boolean>
  getMap: () => maplibregl.Map | null
  onCreateZone?: (payload: CreateActivityZonePayload) => void
  onUpdateZone?: (payload: { id: string; payload: UpdateActivityZonePayload }) => void
  onDeleteZone?: (id: string) => void
  onEnableDrawing?: () => void
}

function zoneId() {
  if (typeof crypto !== 'undefined' && 'randomUUID' in crypto) return crypto.randomUUID()
  return `zone-${Date.now()}-${Math.random().toString(16).slice(2)}`
}

function zoneRecordToDrawnZone(zone: ActivityZone): DrawnZone {
  return {
    id: zone.id,
    name: zone.name,
    points: zone.points,
    color: zone.color,
    trigger_action: zone.trigger_action,
    trigger_subject_role: zone.trigger_subject_role,
    trigger_notify_role: zone.trigger_notify_role,
  }
}

export function useMapZones({
  activityId,
  mapReady,
  getMap,
  onCreateZone,
  onUpdateZone,
  onDeleteZone,
  onEnableDrawing,
}: UseMapZonesOptions) {
  const drawingMode = ref(false)
  const activeZonePoints = ref<[number, number][]>([])
  const activeZoneColor = ref('#10B981')
  const drawnZones = ref<DrawnZone[]>([])

  const activeZonePointCount = computed(() => activeZonePoints.value.length)
  const drawnZoneCount = computed(() => drawnZones.value.length)
  const drawnZoneSummaries = computed<DrawnZoneSummary[]>(() =>
    drawnZones.value.map((zone) => ({
      id: zone.id,
      name: zone.name,
      color: zone.color,
      pointCount: zone.points.length,
      trigger_action: zone.trigger_action,
      trigger_subject_role: zone.trigger_subject_role,
      trigger_notify_role: zone.trigger_notify_role,
    })),
  )

  function completedZonesData(): ZoneFeatureCollection {
    return {
      type: 'FeatureCollection',
      features: drawnZones.value.flatMap((zone) => {
        const firstPoint = zone.points[0]
        if (!firstPoint) return []

        return [
          {
            type: 'Feature',
            geometry: {
              type: 'Polygon',
              coordinates: [[...zone.points, firstPoint]],
            },
            properties: { id: zone.id, label: zone.name, color: zone.color },
          },
        ]
      }),
    }
  }

  function activeZoneLineData(): ZoneFeatureCollection {
    return {
      type: 'FeatureCollection',
      features:
        activeZonePoints.value.length > 1
          ? [
              {
                type: 'Feature',
                geometry: { type: 'LineString', coordinates: activeZonePoints.value },
                properties: { id: 'active-zone-line', color: activeZoneColor.value },
              },
            ]
          : [],
    }
  }

  function activeZoneVerticesData(): ZoneFeatureCollection {
    return {
      type: 'FeatureCollection',
      features: activeZonePoints.value.map((point, index) => ({
        type: 'Feature',
        geometry: { type: 'Point', coordinates: point },
        properties: {
          id: `active-zone-point-${index}`,
          index: index + 1,
          color: activeZoneColor.value,
        },
      })),
    }
  }

  function updateZoneLayers() {
    const map = getMap()
    if (!map || !mapReady.value) return

    const zonesSource = map.getSource('drawn-zones')
    if (zonesSource && 'setData' in zonesSource) {
      ;(zonesSource as maplibregl.GeoJSONSource).setData(completedZonesData())
    } else if (!zonesSource) {
      map.addSource('drawn-zones', { type: 'geojson', data: completedZonesData() })
      map.addLayer({
        id: 'drawn-zones-fill',
        type: 'fill',
        source: 'drawn-zones',
        paint: {
          'fill-color': ['get', 'color'],
          'fill-opacity': 0.18,
        },
      })
      map.addLayer({
        id: 'drawn-zones-outline',
        type: 'line',
        source: 'drawn-zones',
        paint: {
          'line-color': ['get', 'color'],
          'line-width': 3,
        },
      })
      map.addLayer({
        id: 'drawn-zones-label',
        type: 'symbol',
        source: 'drawn-zones',
        layout: {
          'text-field': ['get', 'label'],
          'text-font': ['Open Sans Bold', 'Arial Unicode MS Bold'],
          'text-size': 12,
        },
        paint: {
          'text-color': '#ECFDF5',
          'text-halo-color': '#052E16',
          'text-halo-width': 2,
        },
      })
    }

    const activeLineSource = map.getSource('active-zone-line')
    if (activeLineSource && 'setData' in activeLineSource) {
      ;(activeLineSource as maplibregl.GeoJSONSource).setData(activeZoneLineData())
    } else if (!activeLineSource) {
      map.addSource('active-zone-line', { type: 'geojson', data: activeZoneLineData() })
      map.addLayer({
        id: 'active-zone-line',
        type: 'line',
        source: 'active-zone-line',
        paint: {
          'line-color': ['get', 'color'],
          'line-width': 4,
          'line-dasharray': [1.2, 1],
        },
      })
    }

    const verticesSource = map.getSource('active-zone-vertices')
    if (verticesSource && 'setData' in verticesSource) {
      ;(verticesSource as maplibregl.GeoJSONSource).setData(activeZoneVerticesData())
    } else if (!verticesSource) {
      map.addSource('active-zone-vertices', { type: 'geojson', data: activeZoneVerticesData() })
      map.addLayer({
        id: 'active-zone-vertices',
        type: 'circle',
        source: 'active-zone-vertices',
        paint: {
          'circle-radius': 6,
          'circle-color': ['get', 'color'],
          'circle-stroke-color': '#FFFFFF',
          'circle-stroke-width': 2,
        },
      })
    }

    map.getCanvas().style.cursor = drawingMode.value ? 'crosshair' : ''
  }

  function addZonePoint(lngLat: [number, number]) {
    activeZonePoints.value = [...activeZonePoints.value, lngLat]
    updateZoneLayers()
  }

  function setDrawingMode(value: boolean) {
    drawingMode.value = value
    if (value) onEnableDrawing?.()
    updateZoneLayers()
  }

  function toggleDrawingMode() {
    setDrawingMode(!drawingMode.value)
  }

  function undoZonePoint() {
    activeZonePoints.value = activeZonePoints.value.slice(0, -1)
    updateZoneLayers()
  }

  function finishZone() {
    if (activeZonePoints.value.length < 3) return
    const zone: DrawnZone = {
      id: zoneId(),
      name: `Zone ${drawnZones.value.length + 1}`,
      points: activeZonePoints.value,
      color: activeZoneColor.value,
      trigger_action: 'no_action',
      trigger_subject_role: null,
      trigger_notify_role: null,
    }

    if (activityId.value && onCreateZone) {
      onCreateZone({
        activity: activityId.value,
        name: zone.name,
        color: zone.color,
        points: zone.points,
        trigger_action: zone.trigger_action,
        trigger_subject_role: zone.trigger_subject_role,
        trigger_notify_role: zone.trigger_notify_role,
      })
    } else {
      drawnZones.value = [...drawnZones.value, zone]
    }

    activeZonePoints.value = []
    updateZoneLayers()
  }

  function clearActiveZone() {
    activeZonePoints.value = []
    updateZoneLayers()
  }

  function clearZones() {
    activeZonePoints.value = []
    drawnZones.value = []
    updateZoneLayers()
  }

  function updateActiveZoneColor(color: string) {
    activeZoneColor.value = color
    updateZoneLayers()
  }

  function updateZoneColor(payload: { id: string; color: string }) {
    drawnZones.value = drawnZones.value.map((zone) =>
      zone.id === payload.id ? { ...zone, color: payload.color } : zone,
    )
    onUpdateZone?.({ id: payload.id, payload: { color: payload.color } })
    updateZoneLayers()
  }

  function updateZoneName(payload: { id: string; name: string }) {
    const name = payload.name.trim()
    if (!name) return

    drawnZones.value = drawnZones.value.map((zone) =>
      zone.id === payload.id ? { ...zone, name } : zone,
    )
    onUpdateZone?.({ id: payload.id, payload: { name } })
    updateZoneLayers()
  }

  function updateZoneTrigger(payload: {
    id: string
    trigger_action: 'no_action' | 'on_exit' | 'on_entry'
    trigger_subject_role: string | null
    trigger_notify_role: string | null
  }) {
    drawnZones.value = drawnZones.value.map((zone) =>
      zone.id === payload.id
        ? {
            ...zone,
            trigger_action: payload.trigger_action,
            trigger_subject_role: payload.trigger_subject_role,
            trigger_notify_role: payload.trigger_notify_role,
          }
        : zone,
    )
    onUpdateZone?.({ id: payload.id, payload })
  }

  function deleteZone(id: string) {
    drawnZones.value = drawnZones.value.filter((zone) => zone.id !== id)
    onDeleteZone?.(id)
    updateZoneLayers()
  }

  function syncZonesFromRecords(value: ActivityZone[] | undefined) {
    if (!value) return
    drawnZones.value = value.map(zoneRecordToDrawnZone)
    updateZoneLayers()
  }

  return {
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
  }
}
