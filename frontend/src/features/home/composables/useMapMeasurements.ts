import { computed, ref, type Ref } from 'vue'
import maplibregl from 'maplibre-gl'
import {
  formatDistance,
  measurementDistances,
  measurementPointId,
  totalMeasurementDistance,
  type MeasurementPoint,
} from '@/features/measurements/core/measurement.utils'

type UseMapMeasurementsOptions = {
  mapReady: Ref<boolean>
  getMap: () => maplibregl.Map | null
  isDrawingMode: () => boolean
  onEnableMeasurement?: () => void
}

export function useMapMeasurements({
  mapReady,
  getMap,
  isDrawingMode,
  onEnableMeasurement,
}: UseMapMeasurementsOptions) {
  const measurementMode = ref(false)
  const measurementPoints = ref<MeasurementPoint[]>([])
  const measurementSegmentDistances = computed(() => measurementDistances(measurementPoints.value))
  const measurementTotalDistance = computed(() => totalMeasurementDistance(measurementPoints.value))
  let measurementMarkers: maplibregl.Marker[] = []

  function measurementLineData() {
    return {
      type: 'FeatureCollection' as const,
      features:
        measurementPoints.value.length > 1
          ? [
              {
                type: 'Feature' as const,
                geometry: {
                  type: 'LineString' as const,
                  coordinates: measurementPoints.value.map((point) => point.coordinates),
                },
                properties: {},
              },
            ]
          : [],
    }
  }

  function measurementLabelData() {
    return {
      type: 'FeatureCollection' as const,
      features: measurementPoints.value.slice(1).map((point, index) => {
        const previous = measurementPoints.value[index]!
        return {
          type: 'Feature' as const,
          geometry: {
            type: 'Point' as const,
            coordinates: [
              (previous.coordinates[0] + point.coordinates[0]) / 2,
              (previous.coordinates[1] + point.coordinates[1]) / 2,
            ] as [number, number],
          },
          properties: { label: formatDistance(measurementSegmentDistances.value[index] ?? 0) },
        }
      }),
    }
  }

  function updateMeasurementLayers() {
    const map = getMap()
    if (!map || !mapReady.value) return

    const lineData = measurementLineData()
    const lineSource = map.getSource('distance-measurement-line')
    if (lineSource && 'setData' in lineSource) {
      ;(lineSource as maplibregl.GeoJSONSource).setData(lineData)
    } else if (!lineSource) {
      map.addSource('distance-measurement-line', { type: 'geojson', data: lineData })
      map.addLayer({
        id: 'distance-measurement-line',
        type: 'line',
        source: 'distance-measurement-line',
        paint: { 'line-color': '#38BDF8', 'line-width': 4, 'line-dasharray': [1, 1] },
      })
    }

    const labelData = measurementLabelData()
    const labelSource = map.getSource('distance-measurement-labels')
    if (labelSource && 'setData' in labelSource) {
      ;(labelSource as maplibregl.GeoJSONSource).setData(labelData)
    } else if (!labelSource) {
      map.addSource('distance-measurement-labels', { type: 'geojson', data: labelData })
      map.addLayer({
        id: 'distance-measurement-labels',
        type: 'symbol',
        source: 'distance-measurement-labels',
        layout: { 'text-field': ['get', 'label'], 'text-size': 12, 'text-allow-overlap': true },
        paint: { 'text-color': '#E0F2FE', 'text-halo-color': '#082F49', 'text-halo-width': 2 },
      })
    }
  }

  function createMeasurementPointElement(index: number, pointId: string) {
    const element = document.createElement('button')
    element.type = 'button'
    element.className = 'distance-measurement-point'
    element.textContent = String(index + 1)
    element.title = `Remove measurement point ${index + 1}`
    element.setAttribute('aria-label', `Remove measurement point ${index + 1}`)
    element.addEventListener('click', (event) => {
      event.stopPropagation()
      removeMeasurementPoint(pointId)
    })
    return element
  }

  function updateMeasurementMarkers() {
    const map = getMap()
    if (!map || !mapReady.value) return
    measurementMarkers.forEach((marker) => marker.remove())
    measurementMarkers = measurementPoints.value.map((point, index) => {
      const marker = new maplibregl.Marker({
        element: createMeasurementPointElement(index, point.id),
        anchor: 'center',
        draggable: measurementMode.value,
      })
        .setLngLat(point.coordinates)
        .addTo(map)
      marker.on('drag', () => {
        const position = marker.getLngLat()
        measurementPoints.value = measurementPoints.value.map((item) =>
          item.id === point.id ? { ...item, coordinates: [position.lng, position.lat] } : item,
        )
        updateMeasurementLayers()
      })
      return marker
    })
  }

  function addMeasurementPoint(coordinates: [number, number]) {
    measurementPoints.value = [
      ...measurementPoints.value,
      { id: measurementPointId(), coordinates },
    ]
    updateMeasurementMarkers()
    updateMeasurementLayers()
  }

  function removeMeasurementPoint(id: string) {
    measurementPoints.value = measurementPoints.value.filter((point) => point.id !== id)
    updateMeasurementMarkers()
    updateMeasurementLayers()
  }

  function clearMeasurements() {
    measurementPoints.value = []
    updateMeasurementMarkers()
    updateMeasurementLayers()
  }

  function setMeasurementMode(value: boolean) {
    measurementMode.value = value
    if (value) onEnableMeasurement?.()
    updateMeasurementMarkers()
    updateMeasurementLayers()

    const map = getMap()
    if (map) map.getCanvas().style.cursor = value ? 'crosshair' : isDrawingMode() ? 'crosshair' : ''
  }

  function toggleMeasurementMode() {
    setMeasurementMode(!measurementMode.value)
  }

  function removeMeasurementMarkers() {
    measurementMarkers.forEach((marker) => marker.remove())
    measurementMarkers = []
  }

  return {
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
  }
}
