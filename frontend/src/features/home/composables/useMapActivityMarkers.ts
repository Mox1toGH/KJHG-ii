import type { Ref } from 'vue'
import maplibregl from 'maplibre-gl'
import type { LocationMarker } from '@/features/locations/core/location.types'
import { createdByMarkup } from './mapPopupCreator'

type UseMapActivityMarkersOptions = {
  markers: Ref<LocationMarker[]>
  mapReady: Ref<boolean>
  getMap: () => maplibregl.Map | null
  getMarkerPopup: () => maplibregl.Popup | null
  setMarkerPopup: (popup: maplibregl.Popup | null) => void
  clearPin: () => void
  shouldSuppressContextMenu?: () => boolean
  onMarkerClick?: (markerId: string) => void
  onViewAllPhotos?: (markerId: string) => void
}

function escapeHtml(value: string) {
  return value.replace(
    /[&<>'"]/g,
    (character) =>
      ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;' })[character] ??
      character,
  )
}

export function useMapActivityMarkers({
  markers,
  mapReady,
  getMap,
  getMarkerPopup,
  setMarkerPopup,
  clearPin,
  shouldSuppressContextMenu,
  onMarkerClick,
  onViewAllPhotos,
}: UseMapActivityMarkersOptions) {
  function showMarkerPopup(markerId: string, coordinates: [number, number]) {
    const map = getMap()
    const marker = markers.value.find((item) => item.id === markerId)
    if (!map || !marker) return

    getMarkerPopup()?.remove()
    const photos = marker.photos ?? []
    const mainPhoto = photos.find((photo) => photo.is_main) ?? photos[0]
    const imageMarkup = mainPhoto
      ? `<img src="${escapeHtml(mainPhoto.image)}" alt="${escapeHtml(marker.name)}" style="width:100%;height:140px;object-fit:cover;border-radius:8px;margin-bottom:8px;" />`
      : ''
    const buttonMarkup =
      photos.length > 1
        ? `<button type="button" data-view-photos="${escapeHtml(marker.id)}" style="border:0;background:none;padding:0;color:#2563eb;cursor:pointer;font-size:12px;">View all photos</button>`
        : ''

    const authorMarkup = createdByMarkup(marker.creator)
    const descriptionMarkup = marker.description
      ? `<p style="margin:6px 0 8px;color:#475569;font-size:12px;">${escapeHtml(marker.description)}</p>`
      : ''
    const popup = new maplibregl.Popup({ offset: 12, closeButton: true })
      .setLngLat(coordinates)
      .setHTML(
        `<div style="min-width:180px;color:#0f172a;"><strong>${escapeHtml(marker.name)}</strong>${descriptionMarkup}${imageMarkup}${buttonMarkup}${authorMarkup}</div>`,
      )
      .addTo(map)
    setMarkerPopup(popup)

    popup
      .getElement()
      .querySelector('[data-view-photos]')
      ?.addEventListener('click', () => {
        onViewAllPhotos?.(markerId)
      })
  }

  function markerFeatureDetails(feature: maplibregl.MapGeoJSONFeature) {
    const markerId = feature.properties?.id
    if (!markerId) return null

    return {
      markerId: String(markerId),
      coordinates: (feature.geometry as { coordinates: [number, number] }).coordinates,
    }
  }

  function queryMarkerFeature(point: maplibregl.PointLike) {
    const map = getMap()
    if (!map) return undefined

    const layers = ['activity-markers-circle', 'activity-markers-label'].filter((layerId) =>
      map.getLayer(layerId),
    )
    if (!layers.length) return undefined

    return map.queryRenderedFeatures(point, { layers })[0]
  }

  function openMarkerEditor(markerId: string) {
    getMarkerPopup()?.remove()
    setMarkerPopup(null)
    clearPin()
    onMarkerClick?.(markerId)
  }

  function updateMarkersLayer() {
    const map = getMap()
    if (!map || !mapReady.value) return

    const markersData = {
      type: 'FeatureCollection' as const,
      features: markers.value.map((marker) => ({
        type: 'Feature' as const,
        geometry: {
          type: 'Point' as const,
          coordinates: [marker.longitude, marker.latitude],
        },
        properties: {
          id: marker.id,
          name: marker.name,
          color: marker.color || '#F59E0B',
          photos: JSON.stringify(marker.photos ?? []),
        },
      })),
    }

    const source = map.getSource('activity-markers')
    if (source && 'setData' in source) {
      ;(source as maplibregl.GeoJSONSource).setData(markersData)
    } else if (!source) {
      map.addSource('activity-markers', { type: 'geojson', data: markersData })
      map.addLayer({
        id: 'activity-markers-circle',
        type: 'circle',
        source: 'activity-markers',
        paint: {
          'circle-radius': 8,
          'circle-color': ['get', 'color'],
          'circle-stroke-width': 2,
          'circle-stroke-color': '#FFFFFF',
        },
      })
      map.addLayer({
        id: 'activity-markers-label',
        type: 'symbol',
        source: 'activity-markers',
        layout: {
          'text-field': ['get', 'name'],
          'text-font': ['Open Sans Bold', 'Arial Unicode MS Bold'],
          'text-size': 12,
          'text-offset': [0, 1.5],
          'text-anchor': 'top',
        },
        paint: {
          'text-color': '#FFFFFF',
          'text-halo-color': '#000000',
          'text-halo-width': 2,
        },
      })

      const handleMarkerClick = (event: maplibregl.MapLayerMouseEvent) => {
        event.preventDefault()
        const feature = event.features?.[0]
        if (feature?.properties?.id) {
          const markerId = feature.properties.id as string
          const coordinates = (feature.geometry as { coordinates: [number, number] }).coordinates
          showMarkerPopup(markerId, coordinates)
          onMarkerClick?.(markerId)
        }
      }

      map.on('contextmenu', 'activity-markers-circle', (event) => {
        event.preventDefault()
        if (shouldSuppressContextMenu?.()) return

        const feature = event.features?.[0]
        if (!feature) return

        const details = markerFeatureDetails(feature)
        if (details) showMarkerPopup(details.markerId, details.coordinates)
      })

      const handleMarkerContextMenu = (event: maplibregl.MapLayerMouseEvent) => {
        event.preventDefault()
        const feature = event.features?.[0]
        if (!feature) return

        const details = markerFeatureDetails(feature)
        if (details) openMarkerEditor(details.markerId)
      }

      map.on('click', 'activity-markers-circle', handleMarkerClick)
      map.on('click', 'activity-markers-label', handleMarkerClick)
      map.on('contextmenu', 'activity-markers-circle', handleMarkerContextMenu)
      map.on('contextmenu', 'activity-markers-label', handleMarkerContextMenu)
      map.on('mouseenter', 'activity-markers-circle', () => {
        map.getCanvas().style.cursor = 'pointer'
      })
      map.on('mouseenter', 'activity-markers-label', () => {
        map.getCanvas().style.cursor = 'pointer'
      })
      map.on('mouseleave', 'activity-markers-circle', () => {
        map.getCanvas().style.cursor = ''
      })
      map.on('mouseleave', 'activity-markers-label', () => {
        map.getCanvas().style.cursor = ''
      })
    }
  }

  return {
    markerFeatureDetails,
    queryMarkerFeature,
    showMarkerPopup,
    openMarkerEditor,
    updateMarkersLayer,
  }
}
