import type maplibregl from 'maplibre-gl'
import type { AccuracyCircleFeatureCollection } from './accuracyCircle'

export const USER_LOCATION_SOURCE = 'user-location'
export const USER_LOCATION_ACCURACY_SOURCE = 'user-location-accuracy'
export const USER_LOCATION_ACCURACY_FILL_LAYER = 'user-location-accuracy-fill'
export const USER_LOCATION_ACCURACY_LINE_LAYER = 'user-location-accuracy-line'
export const USER_LOCATION_LAYER = 'user-location-circle'
export const USER_LOCATION_LABEL_LAYER = 'user-location-label'
export const PARTICIPANTS_SOURCE = 'activity-participants'
export const PARTICIPANTS_ACCURACY_SOURCE = 'activity-participant-accuracy'
export const PARTICIPANTS_ACCURACY_FILL_LAYER = 'activity-participant-accuracy-fill'
export const PARTICIPANTS_ACCURACY_LINE_LAYER = 'activity-participant-accuracy-line'
export const PARTICIPANTS_CIRCLE_LAYER = 'activity-participant-circles'
export const PARTICIPANTS_LABEL_LAYER = 'activity-participant-labels'
export const SOS_SOURCE = 'activity-sos'
export const SOS_LAYER = 'activity-sos-pulse'
export const SOS_DISTANCE_SOURCE = 'activity-sos-distances'
export const SOS_DISTANCE_LAYER = 'activity-sos-distance-lines'
export const SOS_DISTANCE_LABEL_LAYER = 'activity-sos-distance-labels'
export const SCRATCH_MAP_SOURCE = 'scratch-map-discovered'
export const SCRATCH_MAP_FILL_LAYER = 'scratch-map-discovered-fill'
export const SCRATCH_MAP_LINE_CASING_LAYER = 'scratch-map-discovered-line-casing'
export const SCRATCH_MAP_LINE_LAYER = 'scratch-map-discovered-line'
export const SCRATCH_MAP_LAYER_IDS = [
  SCRATCH_MAP_FILL_LAYER,
  SCRATCH_MAP_LINE_CASING_LAYER,
  SCRATCH_MAP_LINE_LAYER,
] as const

export type UserLocationGeoJson = {
  type: 'Feature'
  geometry: { type: 'Point'; coordinates: [number, number] }
  properties: { accuracy: number; label: string }
}

export function updateAccuracySource(
  map: maplibregl.Map,
  sourceId: string,
  data: AccuracyCircleFeatureCollection,
) {
  const source = map.getSource(sourceId)
  if (source && 'setData' in source) {
    ;(source as maplibregl.GeoJSONSource).setData(data)
    return true
  }

  if (!source) {
    map.addSource(sourceId, { type: 'geojson', data })
    return true
  }

  console.error(`[maplibre] ${sourceId} source is not a GeoJSON source`)
  return false
}

export function addScratchMapLayers(map: maplibregl.Map) {
  if (!map.getLayer(SCRATCH_MAP_FILL_LAYER)) {
    map.addLayer({
      id: SCRATCH_MAP_FILL_LAYER,
      type: 'fill',
      source: SCRATCH_MAP_SOURCE,
      paint: {
        'fill-color': '#2DD4BF',
        'fill-opacity': ['coalesce', ['feature-state', 'opacity'], 0.28],
      },
    })
  }

  if (!map.getLayer(SCRATCH_MAP_LINE_CASING_LAYER)) {
    map.addLayer({
      id: SCRATCH_MAP_LINE_CASING_LAYER,
      type: 'line',
      source: SCRATCH_MAP_SOURCE,
      paint: {
        'line-color': '#FFFFFF',
        'line-opacity': 0.82,
        'line-width': ['interpolate', ['linear'], ['zoom'], 8, 1.8, 14, 2.6, 18, 3.4],
      },
    })
  }

  if (!map.getLayer(SCRATCH_MAP_LINE_LAYER)) {
    map.addLayer({
      id: SCRATCH_MAP_LINE_LAYER,
      type: 'line',
      source: SCRATCH_MAP_SOURCE,
      paint: {
        'line-color': '#0F766E',
        'line-opacity': 0.95,
        'line-width': ['interpolate', ['linear'], ['zoom'], 8, 0.8, 14, 1.4, 18, 2],
      },
    })
  }
}

export function setScratchMapLayersVisibility(map: maplibregl.Map, visible: boolean) {
  const visibility = visible ? 'visible' : 'none'
  SCRATCH_MAP_LAYER_IDS.forEach((layerId) => {
    if (map.getLayer(layerId)) map.setLayoutProperty(layerId, 'visibility', visibility)
  })
}

export function animateScratchMapFeatures(map: maplibregl.Map, h3Indexes: string[]) {
  h3Indexes.forEach((h3Index) => {
    const target = { source: SCRATCH_MAP_SOURCE, id: h3Index }
    map.setFeatureState(target, { opacity: 0 })
    window.requestAnimationFrame(() => {
      map.setFeatureState(target, { opacity: 0.28 })
    })
  })
}

export function addAccuracyLayers(
  map: maplibregl.Map,
  sourceId: string,
  fillLayerId: string,
  lineLayerId: string,
  beforeLayerId?: string,
) {
  if (!map.getLayer(fillLayerId)) {
    map.addLayer(
      {
        id: fillLayerId,
        type: 'fill',
        source: sourceId,
        paint: {
          'fill-color': ['get', 'color'],
          'fill-opacity': 0.16,
        },
      },
      beforeLayerId,
    )
  }

  if (!map.getLayer(lineLayerId)) {
    map.addLayer(
      {
        id: lineLayerId,
        type: 'line',
        source: sourceId,
        paint: {
          'line-color': ['get', 'color'],
          'line-opacity': 0.45,
          'line-width': ['interpolate', ['linear'], ['zoom'], 8, 0.75, 14, 1.25, 18, 2],
        },
      },
      beforeLayerId,
    )
  }
}

export function addUserLocationDotLayer(map: maplibregl.Map) {
  if (map.getLayer(USER_LOCATION_LAYER)) return

  map.addLayer({
    id: USER_LOCATION_LAYER,
    type: 'circle',
    source: USER_LOCATION_SOURCE,
    paint: {
      'circle-radius': 8,
      'circle-color': '#007AFF',
      'circle-stroke-width': 2,
      'circle-stroke-color': '#FFFFFF',
    },
  })
}

export function addUserLocationLabelLayer(map: maplibregl.Map) {
  if (map.getLayer(USER_LOCATION_LABEL_LAYER)) return

  map.addLayer({
    id: USER_LOCATION_LABEL_LAYER,
    type: 'symbol',
    source: USER_LOCATION_SOURCE,
    layout: {
      'text-field': ['get', 'label'],
      'text-size': ['interpolate', ['linear'], ['zoom'], 8, 11, 14, 13, 18, 15],
      'text-anchor': 'bottom',
      'text-offset': [0, -1.8],
      'text-allow-overlap': true,
      'text-ignore-placement': true,
    },
    paint: {
      'text-color': '#FFFFFF',
      'text-halo-color': '#0F172A',
      'text-halo-width': 2,
    },
  })
}

export function addParticipantLayers(map: maplibregl.Map) {
  if (!map.getLayer(PARTICIPANTS_CIRCLE_LAYER)) {
    map.addLayer({
      id: PARTICIPANTS_CIRCLE_LAYER,
      type: 'circle',
      source: PARTICIPANTS_SOURCE,
      filter: ['!', ['boolean', ['get', 'isCurrentUser'], false]],
      paint: {
        'circle-radius': 8,
        'circle-color': [
          'case',
          ['boolean', ['get', 'isCurrentUser'], false],
          '#007AFF',
          '#F43F5E',
        ],
        'circle-stroke-width': 2,
        'circle-stroke-color': '#FFFFFF',
      },
    })
  }

  if (!map.getLayer(PARTICIPANTS_LABEL_LAYER)) {
    map.addLayer({
      id: PARTICIPANTS_LABEL_LAYER,
      type: 'symbol',
      source: PARTICIPANTS_SOURCE,
      layout: {
        'text-field': ['get', 'displayName'],
        'text-size': ['interpolate', ['linear'], ['zoom'], 8, 10, 14, 13, 18, 15],
        'text-anchor': 'bottom',
        'text-offset': [0, -1.8],
        'text-allow-overlap': true,
        'text-ignore-placement': true,
      },
      paint: {
        'text-color': '#FFFFFF',
        'text-halo-color': '#0F172A',
        'text-halo-width': 2,
        'text-halo-blur': 0.2,
      },
    })
  }
}

export function addSosLayers(map: maplibregl.Map) {
  if (!map.getLayer(SOS_LAYER)) map.addLayer({ id: SOS_LAYER, type: 'circle', source: SOS_SOURCE, paint: { 'circle-radius': ['interpolate', ['linear'], ['zoom'], 8, 12, 16, 19], 'circle-color': '#DC2626', 'circle-opacity': 0.88, 'circle-stroke-color': '#FEF2F2', 'circle-stroke-width': 3, 'circle-blur': 0.08 } })
  if (!map.getLayer(SOS_DISTANCE_LAYER)) map.addLayer({ id: SOS_DISTANCE_LAYER, type: 'line', source: SOS_DISTANCE_SOURCE, paint: { 'line-color': '#EF4444', 'line-width': 2.5, 'line-dasharray': [1, 1.5], 'line-opacity': 0.9 } })
  if (!map.getLayer(SOS_DISTANCE_LABEL_LAYER)) map.addLayer({ id: SOS_DISTANCE_LABEL_LAYER, type: 'symbol', source: SOS_DISTANCE_SOURCE, layout: { 'text-field': ['get', 'label'], 'text-size': 11, 'text-anchor': 'center', 'text-allow-overlap': true }, paint: { 'text-color': '#FEE2E2', 'text-halo-color': '#7F1D1D', 'text-halo-width': 2 } })
}
