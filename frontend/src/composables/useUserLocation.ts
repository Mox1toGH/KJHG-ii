import { onUnmounted, ref } from 'vue'

export type UserLocation = {
  latitude: number
  longitude: number
  accuracy: number
}

export type LocationStatus = 'idle' | 'requesting' | 'tracking' | 'denied' | 'unavailable' | 'error'

export function useUserLocation() {
  const position = ref<UserLocation | null>(null)
  const status = ref<LocationStatus>('idle')
  const errorMessage = ref<string | null>(null)
  let watchId: number | null = null

  function stopTracking() {
    if (watchId === null || !('geolocation' in navigator)) return

    navigator.geolocation.clearWatch(watchId)
    watchId = null
  }

  function startTracking() {
    if (watchId !== null) return

    if (!('geolocation' in navigator)) {
      status.value = 'unavailable'
      errorMessage.value = 'Location is not supported by this browser.'
      return
    }

    if (typeof window !== 'undefined' && !window.isSecureContext) {
      status.value = 'unavailable'
      errorMessage.value = 'Location requires HTTPS or localhost.'
      return
    }

    status.value = 'requesting'
    errorMessage.value = null
    watchId = navigator.geolocation.watchPosition(
      ({ coords }) => {
        console.info('[geolocation] received coordinates', {
          latitude: coords.latitude,
          longitude: coords.longitude,
          accuracy: coords.accuracy,
        })
        position.value = {
          latitude: coords.latitude,
          longitude: coords.longitude,
          accuracy: coords.accuracy,
        }
        status.value = 'tracking'
      },
      (error) => {
        console.error('[geolocation] watchPosition error', error)
        status.value = error.code === error.PERMISSION_DENIED ? 'denied' : 'error'
        errorMessage.value =
          error.code === error.PERMISSION_DENIED
            ? 'Location access was denied. Enable it in your browser settings and try again.'
            : 'We could not determine your location.'

        if (error.code === error.PERMISSION_DENIED) stopTracking()
      },
      { enableHighAccuracy: true, maximumAge: 5_000, timeout: 15_000 },
    )
  }

  onUnmounted(stopTracking)

  return { position, status, errorMessage, startTracking, stopTracking }
}
