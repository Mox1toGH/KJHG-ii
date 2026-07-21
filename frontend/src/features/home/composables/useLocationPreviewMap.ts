import { onBeforeUnmount, onMounted, ref, watch, type Ref } from 'vue'
import maplibregl from 'maplibre-gl'
import type { UserLocation } from '@/composables/useUserLocation'
import { createAccuracyCircleFeature, accuracyFeatureCollection } from '../utils/accuracyCircle'
import {
  addAccuracyLayers,
  addUserLocationDotLayer,
  updateAccuracySource,
  USER_LOCATION_ACCURACY_FILL_LAYER,
  USER_LOCATION_ACCURACY_LINE_LAYER,
  USER_LOCATION_ACCURACY_SOURCE,
  USER_LOCATION_SOURCE,
} from '../utils/mapLayers'
import { baseLayerStyle } from '../utils/mapStyles'
import { createUserMarkerElement, setUserMarkerAvatar } from '../utils/userLocationMarker'

const DEFAULT_CENTER: [number, number] = [30.5234, 50.4501]

export function useLocationPreviewMap(
  position: Ref<UserLocation | null>,
  avatar: Ref<string | null | undefined>,
  startTracking: () => void,
) {
  const mapContainer = ref<HTMLDivElement | null>(null)
  const mapReady = ref(false)
  let map: maplibregl.Map | null = null
  let userMarker: maplibregl.Marker | null = null
  let hasCenteredOnUser = false

  function updateLocation() {
    if (!map || !mapReady.value) return

    const location = position.value
    const data = location
      ? {
          type: 'Feature' as const,
          geometry: { type: 'Point' as const, coordinates: [location.longitude, location.latitude] as [number, number] },
          properties: { accuracy: location.accuracy, label: 'You' },
        }
      : { type: 'Feature' as const, geometry: { type: 'Point' as const, coordinates: DEFAULT_CENTER }, properties: { accuracy: 0, label: '' } }

    const source = map.getSource(USER_LOCATION_SOURCE)
    if (source && 'setData' in source) {
      ;(source as maplibregl.GeoJSONSource).setData({ type: 'FeatureCollection', features: [data] })
    }

    if (location && userMarker) {
      userMarker.setLngLat([location.longitude, location.latitude])
    }

    const accuracy = location
      ? accuracyFeatureCollection([createAccuracyCircleFeature([location.longitude, location.latitude], location.accuracy, '#007AFF')].filter((item): item is NonNullable<typeof item> => Boolean(item)))
      : accuracyFeatureCollection([])
    updateAccuracySource(map, USER_LOCATION_ACCURACY_SOURCE, accuracy)

    if (location && !hasCenteredOnUser) {
      hasCenteredOnUser = true
      map.flyTo({ center: [location.longitude, location.latitude], zoom: 14, duration: 700 })
    }
  }

  onMounted(() => {
    if (!mapContainer.value) return
    map = new maplibregl.Map({
      container: mapContainer.value,
      style: baseLayerStyle('carto'),
      center: DEFAULT_CENTER,
      zoom: 10,
      attributionControl: false,
      dragPan: false,
      scrollZoom: false,
      boxZoom: false,
      doubleClickZoom: false,
      keyboard: false,
      touchPitch: false,
      touchZoomRotate: false,
    })
    map.on('load', () => {
      if (!map) return
      map.addSource(USER_LOCATION_SOURCE, {
        type: 'geojson',
        data: { type: 'FeatureCollection', features: [] },
      })
      userMarker = new maplibregl.Marker({ element: createUserMarkerElement(avatar.value) })
        .setLngLat(DEFAULT_CENTER)
        .addTo(map)
      addUserLocationDotLayer(map)
      updateAccuracySource(map, USER_LOCATION_ACCURACY_SOURCE, accuracyFeatureCollection([]))
      addAccuracyLayers(map, USER_LOCATION_ACCURACY_SOURCE, USER_LOCATION_ACCURACY_FILL_LAYER, USER_LOCATION_ACCURACY_LINE_LAYER)
      mapReady.value = true
      updateLocation()
    })
    startTracking()
  })

  watch([position, avatar], ([, currentAvatar]) => {
    if (userMarker) setUserMarkerAvatar(userMarker.getElement(), currentAvatar)
    updateLocation()
  }, { deep: true })

  onBeforeUnmount(() => {
    userMarker?.remove()
    map?.remove()
    map = null
  })

  return { mapContainer }
}
