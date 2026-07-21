import apiClient from '@/lib/api/client'
import type { ParticipantLocation } from './tracking.types'

export const trackingApi = {
  participantLocations: (activityId: string) =>
    apiClient
      .get<ParticipantLocation[]>(`/tracking/activities/${activityId}/participants/locations/`)
      .then((response) => response.data),
}
