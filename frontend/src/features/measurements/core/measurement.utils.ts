export type MeasurementPoint = {
  id: string
  coordinates: [number, number]
}

const EARTH_RADIUS_METERS = 6_371_008.8

function toRadians(value: number) {
  return (value * Math.PI) / 180
}

/** Returns the shortest surface distance between two longitude/latitude pairs. */
export function distanceBetweenPoints(
  start: [number, number],
  end: [number, number],
): number {
  const latitudeDelta = toRadians(end[1] - start[1])
  const longitudeDelta = toRadians(end[0] - start[0])
  const startLatitude = toRadians(start[1])
  const endLatitude = toRadians(end[1])
  const haversine =
    Math.sin(latitudeDelta / 2) ** 2 +
    Math.cos(startLatitude) * Math.cos(endLatitude) * Math.sin(longitudeDelta / 2) ** 2

  return 2 * EARTH_RADIUS_METERS * Math.asin(Math.sqrt(Math.min(1, haversine)))
}

export function measurementDistances(points: MeasurementPoint[]) {
  return points.slice(1).map((point, index) =>
    distanceBetweenPoints(points[index]!.coordinates, point.coordinates),
  )
}

export function totalMeasurementDistance(points: MeasurementPoint[]) {
  return measurementDistances(points).reduce((total, distance) => total + distance, 0)
}

export function formatDistance(meters: number) {
  if (meters < 1000) return `${Math.round(meters)} m`
  return `${(meters / 1000).toFixed(meters < 10_000 ? 2 : 1)} km`
}

export function measurementPointId() {
  if (typeof crypto !== 'undefined' && 'randomUUID' in crypto) return crypto.randomUUID()
  return `measurement-${Date.now()}-${Math.random().toString(16).slice(2)}`
}
