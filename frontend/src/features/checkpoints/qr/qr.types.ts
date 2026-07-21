export interface CheckpointQrCode {
  id: string
  checkpoint: string
  name: string
  image: string
  scan_count: number
  points: number
  created_by: number
  created_at: string
}

export interface CreateCheckpointQrPayload {
  name?: string
  points?: number
}

export interface ScanCheckpointQrPayload {
  token: string
  latitude: number
  longitude: number
}

export interface CheckpointQrScan {
  id: string
  scanned_at: string
}
