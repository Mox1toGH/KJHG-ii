export interface LocationMarkerPhoto {
  id: number
  image: string
  is_main: boolean
  created_at: string
}

import type { MapObjectCreator } from '@/features/auth/core/auth.types'

export interface LocationMarker {
  id: string
  activity: string
  name: string
  description: string
  color: string
  latitude: number
  longitude: number
  created_by: number | null
  created_by_name?: string
  creator?: MapObjectCreator | null
  created_at: string
  photos: LocationMarkerPhoto[]
  meeting_point: MeetingPoint | null
}

export interface MeetingPoint {
  name?: string
  description?: string
  start_time: string
  end_time: string
}

export type MeetingPointPayload = MeetingPoint | null

export interface CreateLocationMarkerPayload {
  activity: string
  name: string
  description?: string
  color: string
  latitude: number
  longitude: number
  meeting_point?: MeetingPointPayload
}

export interface UpdateLocationMarkerPayload {
  name?: string
  description?: string
  color?: string
  meeting_point?: MeetingPointPayload
}

export interface UploadLocationMarkerPhotoPayload {
  markerId: string
  files: File[]
}

export type ZonePoint = [number, number]

export interface ActivityZone {
  id: string
  activity: string
  name: string
  color: string
  points: ZonePoint[]
  trigger_action: 'no_action' | 'on_exit' | 'on_entry'
  trigger_subject_role: string | null
  trigger_notify_role: string | null
  created_by: number | null
  created_at: string
}

export interface CreateActivityZonePayload {
  activity: string
  name: string
  color: string
  points: ZonePoint[]
  trigger_action?: 'no_action' | 'on_exit' | 'on_entry'
  trigger_subject_role?: string | null
  trigger_notify_role?: string | null
}

export interface UpdateActivityZonePayload {
  name?: string
  color?: string
  points?: ZonePoint[]
  trigger_action?: 'no_action' | 'on_exit' | 'on_entry'
  trigger_subject_role?: string | null
  trigger_notify_role?: string | null
}
