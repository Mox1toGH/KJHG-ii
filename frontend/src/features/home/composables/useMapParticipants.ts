import { computed, ref, watch, type Ref } from 'vue'
import maplibregl from 'maplibre-gl'
import type { UserLocation } from '@/composables/useUserLocation'
import type { ParticipantLocation } from '@/features/activities/tracking/tracking.types'
import {
  accuracyFeatureCollection,
  createAccuracyCircleFeature,
  type AccuracyCircleFeature,
} from '../utils/accuracyCircle'
import {
  PARTICIPANTS_ACCURACY_FILL_LAYER,
  PARTICIPANTS_ACCURACY_LINE_LAYER,
  PARTICIPANTS_ACCURACY_SOURCE,
  PARTICIPANTS_CIRCLE_LAYER,
  PARTICIPANTS_LABEL_LAYER,
  PARTICIPANTS_SOURCE,
  SOS_DISTANCE_SOURCE,
  SOS_SOURCE,
  USER_LOCATION_ACCURACY_FILL_LAYER,
  USER_LOCATION_ACCURACY_LINE_LAYER,
  USER_LOCATION_ACCURACY_SOURCE,
  USER_LOCATION_LAYER,
  USER_LOCATION_SOURCE,
  addAccuracyLayers,
  addParticipantLayers,
  addSosLayers,
  addUserLocationLabelLayer,
  updateAccuracySource,
  type UserLocationGeoJson,
} from '../utils/mapLayers'
import { createUserMarkerElement, setUserMarkerAvatar } from '../utils/userLocationMarker'
import {
  distanceBetweenPoints,
  formatDistance,
} from '@/features/measurements/core/measurement.utils'

type UseMapParticipantsOptions = {
  activityId: Ref<string | undefined>
  currentUserId: Ref<number | undefined>
  currentUserAvatar: Ref<string | null | undefined>
  participants: Ref<Record<string, ParticipantLocation>>
  userPosition: Ref<UserLocation | null>
  locationAgeTick: Ref<number>
  mapReady: Ref<boolean>
  getMap: () => maplibregl.Map | null
  onParticipantClick?: (participantId: string) => void
  hiddenParticipantIds?: Ref<string[]>
}

function formatLocationAge(value: string | null, now: number) {
  if (!value) return 'No update'

  const timestamp = new Date(value).getTime()
  if (Number.isNaN(timestamp)) return 'No update'

  const seconds = Math.max(0, Math.floor((now - timestamp) / 1000))
  if (seconds < 10) return 'Now'
  if (seconds < 60) return `${seconds}s ago`
  if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`
  if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`
  return `${Math.floor(seconds / 86400)}d ago`
}

function participantFeatureCollection(
  participants: Record<string, ParticipantLocation>,
  currentUserId: number | undefined,
  now: number,
  hiddenParticipantIds?: string[],
) {
  return {
    type: 'FeatureCollection' as const,
    features: Object.values(participants).flatMap((participant) => {
      if (!participant.location) return []
      if (hiddenParticipantIds?.includes(participant.participant_id)) return []

      return [
        {
          type: 'Feature' as const,
          geometry: {
            type: 'Point' as const,
            coordinates: [participant.location.longitude, participant.location.latitude] as [
              number,
              number,
            ],
          },
          properties: {
            participantId: participant.participant_id,
            displayName: `${
              participant.user.id === String(currentUserId)
                ? 'You'
                : participant.user.display_name?.trim() || participant.user.username
            } ${formatLocationAge(participant.last_updated, now)}`,
            isCurrentUser: participant.user.id === String(currentUserId),
            role: participant.role?.name ?? '',
            isSos: participant.sos_active,
          },
        },
      ]
    }),
  }
}

function participantAccuracyFeatureCollection(
  participants: Record<string, ParticipantLocation>,
  currentUserId: number | undefined,
  hiddenParticipantIds?: string[],
) {
  return accuracyFeatureCollection(
    Object.values(participants).flatMap((participant) => {
      if (!participant.location) return []
      if (hiddenParticipantIds?.includes(participant.participant_id)) return []

      const coordinates: [number, number] = [
        participant.location.longitude,
        participant.location.latitude,
      ]
      const color = participant.user.id === String(currentUserId) ? '#007AFF' : '#F43F5E'
      const feature = createAccuracyCircleFeature(coordinates, participant.location.accuracy, color)

      return feature ? [feature] : []
    }),
  )
}

export function useMapParticipants({
  activityId,
  currentUserId,
  currentUserAvatar,
  participants,
  userPosition,
  locationAgeTick,
  mapReady,
  getMap,
  onParticipantClick,
  hiddenParticipantIds,
}: UseMapParticipantsOptions) {
  const hasCenteredOnUser = ref(false)
  let participantHandlersAttached = false
  let userMarker: maplibregl.Marker | null = null
  let userMarkerAvatar: string | null | undefined

  const participantsData = computed(() =>
    participantFeatureCollection(participants.value, currentUserId.value, locationAgeTick.value, hiddenParticipantIds?.value),
  )
  const participantsAccuracyData = computed(() =>
    participantAccuracyFeatureCollection(participants.value, currentUserId.value, hiddenParticipantIds?.value),
  )
  const sosData = computed(() => ({
    type: 'FeatureCollection' as const,
    features: Object.values(participants.value).flatMap((participant) =>
      participant.sos_active && participant.location && !hiddenParticipantIds?.value?.includes(participant.participant_id)
        ? [
            {
              type: 'Feature' as const,
              geometry: {
                type: 'Point' as const,
                coordinates: [participant.location.longitude, participant.location.latitude] as [
                  number,
                  number,
                ],
              },
              properties: { participantId: participant.participant_id },
            },
          ]
        : [],
    ),
  }))
  const sosDistanceData = computed(() => {
    if (!userPosition.value) return { type: 'FeatureCollection' as const, features: [] }
    const origin: [number, number] = [userPosition.value.longitude, userPosition.value.latitude]
    return {
      type: 'FeatureCollection' as const,
      features: Object.values(participants.value).flatMap((participant) => {
        if (!participant.sos_active || !participant.location || hiddenParticipantIds?.value?.includes(participant.participant_id)) return []
        const target: [number, number] = [
          participant.location.longitude,
          participant.location.latitude,
        ]
        return [
          {
            type: 'Feature' as const,
            geometry: { type: 'LineString' as const, coordinates: [origin, target] },
            properties: {
              label: `${participant.user.display_name || participant.user.username}: ${formatDistance(distanceBetweenPoints(origin, target))}`,
            },
          },
        ]
      }),
    }
  })

  // Watch for changes in hidden participants to update map immediately
  watch([hiddenParticipantIds, participants], () => {
    if (activityId.value && mapReady.value) {
      updateParticipantLayers()
    }
  })

  function updateUserMarker() {
    const map = getMap()
    if (!map || !mapReady.value) return

    const currentParticipant = Object.values(participants.value).find(
      (participant) => participant.user.id === String(currentUserId.value),
    )
    const location = activityId.value ? currentParticipant?.location : userPosition.value

    if (!location) {
      userMarker?.remove()
      userMarker = null
      return
    }

    if (!userMarker) {
      userMarker = new maplibregl.Marker({
        element: createUserMarkerElement(
          currentUserAvatar.value,
          currentParticipant
            ? () => onParticipantClick?.(currentParticipant.participant_id)
            : undefined,
        ),
        anchor: 'center',
      })
        .setLngLat([location.longitude, location.latitude])
        .addTo(map)
      userMarkerAvatar = currentUserAvatar.value
    } else if (userMarkerAvatar !== currentUserAvatar.value) {
      setUserMarkerAvatar(userMarker.getElement(), currentUserAvatar.value)
      userMarkerAvatar = currentUserAvatar.value
    }

    if (userMarker) userMarker.setLngLat([location.longitude, location.latitude])
  }

  function updateUserLocationLayer() {
    const map = getMap()
    if (activityId.value || !map || !mapReady.value || !userPosition.value) return

    const coordinates: [number, number] = [
      userPosition.value.longitude,
      userPosition.value.latitude,
    ]
    const data: UserLocationGeoJson = {
      type: 'Feature',
      geometry: { type: 'Point', coordinates },
      properties: {
        accuracy: userPosition.value.accuracy,
        label: 'You Now',
      },
    }
    const accuracyData = accuracyFeatureCollection(
      [createAccuracyCircleFeature(coordinates, userPosition.value.accuracy, '#007AFF')].filter(
        (feature): feature is AccuracyCircleFeature => feature !== null,
      ),
    )
    const source = map.getSource(USER_LOCATION_SOURCE)

    if (!hasCenteredOnUser.value) {
      hasCenteredOnUser.value = true
      map.flyTo({ center: coordinates, zoom: 14 })
    }

    if (source) {
      if ('setData' in source) {
        ;(source as maplibregl.GeoJSONSource).setData(data)
        console.info('[map] updated user location source', coordinates)
      } else {
        console.error('[map] user-location source exists but is not a GeoJSON source')
      }
    } else {
      map.addSource(USER_LOCATION_SOURCE, { type: 'geojson', data })
    }

    if (updateAccuracySource(map, USER_LOCATION_ACCURACY_SOURCE, accuracyData)) {
      addAccuracyLayers(
        map,
        USER_LOCATION_ACCURACY_SOURCE,
        USER_LOCATION_ACCURACY_FILL_LAYER,
        USER_LOCATION_ACCURACY_LINE_LAYER,
        map.getLayer(USER_LOCATION_LAYER) ? USER_LOCATION_LAYER : undefined,
      )
    }
    addUserLocationLabelLayer(map)
  }

  function updateParticipantLayers() {
    const map = getMap()
    if (!map || !mapReady.value || !activityId.value) return

    const source = map.getSource(PARTICIPANTS_SOURCE)
    if (source && 'setData' in source) {
      ;(source as maplibregl.GeoJSONSource).setData(participantsData.value)
    } else if (!source) {
      map.addSource(PARTICIPANTS_SOURCE, { type: 'geojson', data: participantsData.value })
    } else {
      console.error('[maplibre] activity participant source is not a GeoJSON source')
      return
    }

    if (updateAccuracySource(map, PARTICIPANTS_ACCURACY_SOURCE, participantsAccuracyData.value)) {
      addAccuracyLayers(
        map,
        PARTICIPANTS_ACCURACY_SOURCE,
        PARTICIPANTS_ACCURACY_FILL_LAYER,
        PARTICIPANTS_ACCURACY_LINE_LAYER,
        map.getLayer(PARTICIPANTS_CIRCLE_LAYER) ? PARTICIPANTS_CIRCLE_LAYER : undefined,
      )
    }

    addParticipantLayers(map)

    const sosSource = map.getSource(SOS_SOURCE)
    if (sosSource && 'setData' in sosSource)
      (sosSource as maplibregl.GeoJSONSource).setData(sosData.value)
    else if (!sosSource) map.addSource(SOS_SOURCE, { type: 'geojson', data: sosData.value })
    const distanceSource = map.getSource(SOS_DISTANCE_SOURCE)
    if (distanceSource && 'setData' in distanceSource)
      (distanceSource as maplibregl.GeoJSONSource).setData(sosDistanceData.value)
    else if (!distanceSource)
      map.addSource(SOS_DISTANCE_SOURCE, { type: 'geojson', data: sosDistanceData.value })
    addSosLayers(map)

    const handleParticipantClick = (event: maplibregl.MapLayerMouseEvent) => {
      event.preventDefault()
      const participantId = event.features?.[0]?.properties?.participantId
      if (participantId) onParticipantClick?.(String(participantId))
    }

    if (!participantHandlersAttached) {
      participantHandlersAttached = true
      map.on('click', PARTICIPANTS_CIRCLE_LAYER, handleParticipantClick)
      map.on('click', PARTICIPANTS_LABEL_LAYER, handleParticipantClick)
      map.on('mouseenter', PARTICIPANTS_CIRCLE_LAYER, () => {
        map.getCanvas().style.cursor = 'pointer'
      })
      map.on('mouseenter', PARTICIPANTS_LABEL_LAYER, () => {
        map.getCanvas().style.cursor = 'pointer'
      })
      map.on('mouseleave', PARTICIPANTS_CIRCLE_LAYER, () => {
        map.getCanvas().style.cursor = ''
      })
      map.on('mouseleave', PARTICIPANTS_LABEL_LAYER, () => {
        map.getCanvas().style.cursor = ''
      })
    }
  }

  function removeUserMarker() {
    userMarker?.remove()
    userMarker = null
  }

  return {
    sosData,
    sosDistanceData,
    updateUserMarker,
    updateUserLocationLayer,
    updateParticipantLayers,
    removeUserMarker,
  }
}
