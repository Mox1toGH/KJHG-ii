import { onUnmounted, ref, watch, type Ref } from 'vue'
import type { UserLocation } from '@/composables/useUserLocation'
import { trackingApi } from './tracking.api'
import type { LocationUpdatedMessage, ParticipantLocation, SosUpdatedMessage } from './tracking.types'

function websocketUrl(activityId: string) {
  const configuredBase = import.meta.env.VITE_WS_BASE_URL as string | undefined
  if (configuredBase) return `${configuredBase.replace(/\/$/, '')}/ws/activities/${activityId}/tracking/`

  const apiBase = (import.meta.env.VITE_API_BASE_URL as string | undefined) ?? window.location.origin
  const origin = apiBase.replace(/\/api\/?$/, '').replace(/^http/, 'ws')
  return `${origin}/ws/activities/${activityId}/tracking/`
}

export function useActivityTracking(
  activityId: Ref<string | undefined>,
  currentUserId: Ref<number | undefined>,
  localPosition: Ref<UserLocation | null>,
) {
  const participants = ref<Record<string, ParticipantLocation>>({})
  const status = ref<'idle' | 'loading' | 'connected' | 'disconnected' | 'error'>('idle')
  const errorMessage = ref<string | null>(null)
  let socket: WebSocket | null = null
  let requestGeneration = 0
  let latestPosition: UserLocation | null = null

  function closeSocket() {
    if (!socket) return
    socket.onopen = null
    socket.onmessage = null
    socket.onerror = null
    socket.onclose = null
    socket.close()
    socket = null
  }

  function replaceParticipantList(items: ParticipantLocation[]) {
    participants.value = Object.fromEntries(items.map((item) => [item.participant_id, item]))
  }

  function updateParticipantLocation(
    participantId: string,
    location: ParticipantLocation['location'],
    updatedAt: string,
    participantInfo?: Pick<ParticipantLocation, 'user' | 'role'>,
  ) {
    const existing = participants.value[participantId]
    if (!location) return

    const participant = existing ?? (participantInfo
      ? {
          participant_id: participantId,
          user: participantInfo.user,
          role: participantInfo.role,
          location: null,
          last_updated: null,
          sos_active: false,
          sos_activated_at: null,
        }
      : null)
    if (!participant) return

    participants.value = {
      ...participants.value,
      [participantId]: { ...participant, location, last_updated: updatedAt },
    }
  }

  function updateSos(message: SosUpdatedMessage['sos']) {
    const existing = participants.value[message.participant_id]
    if (!existing) return
    participants.value = {
      ...participants.value,
      [message.participant_id]: {
        ...existing,
        sos_active: message.active,
        sos_activated_at: message.activated_at,
      },
    }
  }

  function publishCurrentLocation() {
    if (!socket || socket.readyState !== WebSocket.OPEN || !latestPosition) return

    socket.send(
      JSON.stringify({
        type: 'location.update',
        latitude: latestPosition.latitude,
        longitude: latestPosition.longitude,
        accuracy: latestPosition.accuracy,
      }),
    )
  }

  function connect(activity: string) {
    const generation = ++requestGeneration
    closeSocket()
    participants.value = {}
    status.value = 'loading'
    errorMessage.value = null

    trackingApi
      .participantLocations(activity)
      .then((items) => {
        if (generation !== requestGeneration) return
        replaceParticipantList(items)

        socket = new WebSocket(websocketUrl(activity))
        socket.onopen = () => {
          if (generation !== requestGeneration) return
          status.value = 'connected'
          publishCurrentLocation()
        }
        socket.onmessage = (event) => {
          if (generation !== requestGeneration) return
          try {
            const message = JSON.parse(event.data) as LocationUpdatedMessage | SosUpdatedMessage
            if (message.event === 'location.updated') {
              updateParticipantLocation(
                message.participant_id,
                message.location,
                message.updated_at,
                message.participant,
              )
            }
            if (message.event === 'sos.updated') updateSos(message.sos)
          } catch (error) {
            console.error('[tracking] invalid WebSocket message', error)
          }
        }
        socket.onerror = (event) => {
          console.error('[tracking] WebSocket error', event)
          status.value = 'error'
          errorMessage.value = 'Live participant updates are unavailable.'
        }
        socket.onclose = () => {
          if (generation === requestGeneration) status.value = 'disconnected'
        }
      })
      .catch((error: unknown) => {
        if (generation !== requestGeneration) return
        console.error('[tracking] failed to load participant locations', error)
        status.value = 'error'
        errorMessage.value = 'Participant locations could not be loaded.'
      })
  }

  watch(
    activityId,
    (activity) => {
      if (activity) connect(activity)
      else {
        requestGeneration += 1
        closeSocket()
        participants.value = {}
        status.value = 'idle'
      }
    },
    { immediate: true },
  )

  watch(localPosition, (position) => {
    latestPosition = position
    publishCurrentLocation()

    const currentParticipant = Object.values(participants.value).find(
      (participant) => participant.user.id === String(currentUserId.value),
    )
    if (currentParticipant && position) {
      updateParticipantLocation(currentParticipant.participant_id, {
        latitude: position.latitude,
        longitude: position.longitude,
        accuracy: position.accuracy,
        heading: null,
        speed: null,
      }, new Date().toISOString())
    }
  })

  watch(currentUserId, () => {
    if (latestPosition) {
      const currentParticipant = Object.values(participants.value).find(
        (participant) => participant.user.id === String(currentUserId.value),
      )
      if (currentParticipant) {
        updateParticipantLocation(currentParticipant.participant_id, {
          latitude: latestPosition!.latitude,
          longitude: latestPosition!.longitude,
          accuracy: latestPosition!.accuracy,
          heading: null,
          speed: null,
        }, new Date().toISOString())
      }
    }
  })

  onUnmounted(() => {
    requestGeneration += 1
    closeSocket()
  })

  return { participants, status, errorMessage }
}
