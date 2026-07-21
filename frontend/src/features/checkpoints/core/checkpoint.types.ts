import type { MapObjectCreator } from '@/features/auth/core/auth.types'

export interface RoutePoint {
  id: string
  route: string
  sequence_number: number
  name: string
  description: string
  points: number
  latitude: number
  longitude: number
  radius: number
  photos: CheckpointPhoto[]
  created_by_name?: string
  creator?: MapObjectCreator | null
}

export interface Route {
  id: string
  activity: string
  name: string
  description: string
  color: string
  main_checkpoint: string // ID
  points: RoutePoint[]
  created_by: number | null
  created_by_name?: string
  creator?: MapObjectCreator | null
  created_at: string
  photos?: CheckpointPhoto[]
}

export interface Checkpoint {
  id: string
  activity: string
  name: string
  description: string
  points: number
  color: string
  latitude: number
  longitude: number
  radius: number
  route: Route | null
  photos: CheckpointPhoto[]
  created_by: number | null
  created_by_name?: string
  creator?: MapObjectCreator | null
  created_at: string
  qr_progress: QrProgress
}

export interface QrProgress {
  scanned: number
  total: number
}

export interface Visit {
  id: string
  participant_id: string
  checkpoint: string | null
  route_point: string | null
  visited_at: string
  is_manual: boolean
  deviation: number | null
  points_awarded?: number
  total_points?: number
}

export interface CreateCheckpointPayload {
  activity: string
  name: string
  description?: string
  color?: string
  points?: number
  latitude: number
  longitude: number
  radius?: number
}

export interface UpdateCheckpointPayload {
  name?: string
  description?: string
  color?: string
  points?: number
  radius?: number
}

export interface CreateRoutePointPayload {
  sequence_number: number
  name?: string
  description?: string
  points?: number
  latitude: number
  longitude: number
  radius?: number
}

export interface CreateRoutePayload {
  activity: string
  name: string
  description?: string
  color?: string
  main_checkpoint: string
  points: CreateRoutePointPayload[]
}

export interface UpdateRoutePayload {
  name?: string
  description?: string
  color?: string
  main_checkpoint?: string
  points?: CreateRoutePointPayload[]
}

export interface CheckInPayload {
  type: 'checkpoint' | 'route_point'
  id: string
  latitude: number
  longitude: number
  accuracy: number
  is_manual?: boolean
}
export interface CheckpointPhoto {
  id: number
  image: string
  is_main: boolean
  created_at: string
}
