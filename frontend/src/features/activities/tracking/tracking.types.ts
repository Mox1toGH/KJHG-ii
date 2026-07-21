export interface ParticipantLocation {
  participant_id: string
  user: {
    id: string
    username: string
    display_name?: string
  }
  role: { id: string; name: string } | null
  location: {
    latitude: number
    longitude: number
    accuracy: number | null
    heading: number | null
    speed: number | null
  } | null
  last_updated: string | null
  sos_active: boolean
  sos_activated_at: string | null
}

export interface LocationUpdatedMessage {
  event: 'location.updated'
  participant_id: string
  participant: Pick<ParticipantLocation, 'user' | 'role'>
  location: NonNullable<ParticipantLocation['location']>
  updated_at: string
}

export interface SosUpdatedMessage {
  event: 'sos.updated'
  sos: {
    activity_id: string
    participant_id: string
    user: ParticipantLocation['user']
    active: boolean
    activated_at: string | null
  }
}
