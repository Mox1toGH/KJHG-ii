import type { MeasurementPoint } from './measurement.utils'

export type MeasurementSegment = {
  from: number
  to: number
  distance: number
}

export type MeasurementState = {
  enabled: boolean
  points: MeasurementPoint[]
  segments: MeasurementSegment[]
  totalDistance: number
}
