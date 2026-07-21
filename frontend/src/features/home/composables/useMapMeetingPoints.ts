import type { Ref } from 'vue'
import maplibregl from 'maplibre-gl'
import type { LocationMarker } from '@/features/locations/core/location.types'
import { createdByMarkup } from './mapPopupCreator'

type UseMapMeetingPointsOptions = {
  meetingPoints?: Ref<LocationMarker[]>
  mapReady: Ref<boolean>
  getMap: () => maplibregl.Map | null
  getMarkerPopup: () => maplibregl.Popup | null
  setMarkerPopup: (popup: maplibregl.Popup | null) => void
}

function escapeHtml(value: string) {
  return value.replace(
    /[&<>'"]/g,
    (character) =>
      ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;' })[character] ??
      character,
  )
}

export function useMapMeetingPoints({
  meetingPoints,
  mapReady,
  getMap,
  getMarkerPopup,
  setMarkerPopup,
}: UseMapMeetingPointsOptions) {
  let meetingPointHandlersAttached = false

  function showMeetingPointPopup(marker: LocationMarker, coordinates: [number, number]) {
    const map = getMap()
    if (!map || !marker.meeting_point) return
    getMarkerPopup()?.remove()
    const authorMarkup = createdByMarkup(marker.creator)
    const popup = new maplibregl.Popup({ offset: 14, closeButton: true })
      .setLngLat(coordinates)
      .setHTML(
        `<div style="min-width:170px;color:#0f172a;"><strong>${escapeHtml(marker.meeting_point.name || 'Meeting point')}</strong>${authorMarkup}${marker.meeting_point.description ? `<p style="margin:6px 0 0;color:#475569;font-size:12px;">${escapeHtml(marker.meeting_point.description)}</p>` : ''}<p style="margin:6px 0 0;color:#475569;font-size:12px;">${escapeHtml(marker.meeting_point.start_time)}-${escapeHtml(marker.meeting_point.end_time)}</p></div>`,
      )
      .addTo(map)
    setMarkerPopup(popup)
  }

  function updateMeetingPointsLayer() {
    const map = getMap()
    if (!map || !mapReady.value || !meetingPoints) return

    const data = {
      type: 'FeatureCollection' as const,
      features: meetingPoints.value.map((marker) => ({
        type: 'Feature' as const,
        geometry: { type: 'Point' as const, coordinates: [marker.longitude, marker.latitude] },
        properties: {
          id: marker.id,
          name: marker.name,
          time: `${marker.meeting_point?.start_time ?? ''}-“${marker.meeting_point?.end_time ?? ''}`,
        },
      })),
    }
    const source = map.getSource('activity-meeting-points')
    if (source && 'setData' in source) {
      ;(source as maplibregl.GeoJSONSource).setData(data)
    } else if (!source) {
      map.addSource('activity-meeting-points', { type: 'geojson', data })
      map.addLayer({
        id: 'activity-meeting-points-halo',
        type: 'circle',
        source: 'activity-meeting-points',
        paint: { 'circle-radius': 13, 'circle-color': '#F97316', 'circle-opacity': 0.25 },
      })
      map.addLayer({
        id: 'activity-meeting-points-circle',
        type: 'circle',
        source: 'activity-meeting-points',
        paint: {
          'circle-radius': 8,
          'circle-color': '#F97316',
          'circle-stroke-width': 3,
          'circle-stroke-color': '#FFF7ED',
        },
      })
      map.addLayer({
        id: 'activity-meeting-points-label',
        type: 'symbol',
        source: 'activity-meeting-points',
        layout: {
          'text-field': ['concat', ['get', 'name']],
          'text-font': ['Open Sans Bold', 'Arial Unicode MS Bold'],
          'text-size': 12,
          'text-offset': [0, 1.7],
          'text-anchor': 'top',
        },
        paint: { 'text-color': '#FFF7ED', 'text-halo-color': '#7C2D12', 'text-halo-width': 2 },
      })
    }

    if (!meetingPointHandlersAttached) {
      meetingPointHandlersAttached = true
      const handleClick = (event: maplibregl.MapLayerMouseEvent) => {
        event.preventDefault()
        const feature = event.features?.[0]
        const marker = meetingPoints.value.find((item) => item.id === feature?.properties?.id)
        if (!marker || !feature) return
        const coordinates = (feature.geometry as { coordinates: [number, number] }).coordinates
        showMeetingPointPopup(marker, coordinates)
      }
      map.on('click', 'activity-meeting-points-circle', handleClick)
      map.on('click', 'activity-meeting-points-label', handleClick)
      map.on('mouseenter', 'activity-meeting-points-circle', () => {
        map.getCanvas().style.cursor = 'pointer'
      })
      map.on('mouseenter', 'activity-meeting-points-label', () => {
        map.getCanvas().style.cursor = 'pointer'
      })
      map.on('mouseleave', 'activity-meeting-points-circle', () => {
        map.getCanvas().style.cursor = ''
      })
      map.on('mouseleave', 'activity-meeting-points-label', () => {
        map.getCanvas().style.cursor = ''
      })
    }
  }

  function focusMeetingPoint(marker: LocationMarker) {
    const map = getMap()
    if (!map || !marker.meeting_point) return
    const coordinates: [number, number] = [marker.longitude, marker.latitude]
    map.flyTo({ center: coordinates, zoom: Math.max(map.getZoom(), 15), duration: 800 })
    showMeetingPointPopup(marker, coordinates)
  }

  return {
    focusMeetingPoint,
    showMeetingPointPopup,
    updateMeetingPointsLayer,
  }
}
