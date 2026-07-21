export type LngLatTuple = [number, number]

export type AccuracyCircleFeature = {
  type: 'Feature'
  geometry: { type: 'Polygon'; coordinates: LngLatTuple[][] }
  properties: { color: string }
}

export type AccuracyCircleFeatureCollection = {
  type: 'FeatureCollection'
  features: AccuracyCircleFeature[]
}

const EARTH_RADIUS_METERS = 6_371_008.8
const ACCURACY_CIRCLE_SEGMENTS = 96

function toRadians(value: number) {
  return (value * Math.PI) / 180
}

function toDegrees(value: number) {
  return (value * 180) / Math.PI
}

function normalizeLongitude(value: number) {
  return ((((value + 180) % 360) + 360) % 360) - 180
}

export function accuracyFeatureCollection(
  features: AccuracyCircleFeature[],
): AccuracyCircleFeatureCollection {
  return { type: 'FeatureCollection', features }
}

export function createAccuracyCircleFeature(
  coordinates: LngLatTuple,
  accuracyMeters: number | null,
  color: string,
): AccuracyCircleFeature | null {
  if (!accuracyMeters || !Number.isFinite(accuracyMeters) || accuracyMeters <= 0) return null

  const [longitude, latitude] = coordinates
  const centerLat = toRadians(latitude)
  const centerLng = toRadians(longitude)
  const angularDistance = accuracyMeters / EARTH_RADIUS_METERS
  const ring: LngLatTuple[] = []

  for (let index = 0; index <= ACCURACY_CIRCLE_SEGMENTS; index += 1) {
    const bearing = (2 * Math.PI * index) / ACCURACY_CIRCLE_SEGMENTS
    const pointLat = Math.asin(
      Math.sin(centerLat) * Math.cos(angularDistance) +
        Math.cos(centerLat) * Math.sin(angularDistance) * Math.cos(bearing),
    )
    const pointLng =
      centerLng +
      Math.atan2(
        Math.sin(bearing) * Math.sin(angularDistance) * Math.cos(centerLat),
        Math.cos(angularDistance) - Math.sin(centerLat) * Math.sin(pointLat),
      )

    ring.push([normalizeLongitude(toDegrees(pointLng)), toDegrees(pointLat)])
  }

  return {
    type: 'Feature',
    geometry: { type: 'Polygon', coordinates: [ring] },
    properties: { color },
  }
}
