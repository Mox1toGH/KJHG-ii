import { watch, type Ref } from 'vue'
import type { UserLocation } from '@/composables/useUserLocation'
import { useCheckIn, useCheckpoints, useRoutes, useVisits } from '../core/checkpoint.queries'

export function calculateDistance(lat1: number, lon1: number, lat2: number, lon2: number) {
  const R = 6371000
  const phi1 = (lat1 * Math.PI) / 180
  const phi2 = (lat2 * Math.PI) / 180
  const deltaPhi = ((lat2 - lat1) * Math.PI) / 180
  const deltaLambda = ((lon2 - lon1) * Math.PI) / 180

  const a =
    Math.sin(deltaPhi / 2) * Math.sin(deltaPhi / 2) +
    Math.cos(phi1) * Math.cos(phi2) * Math.sin(deltaLambda / 2) * Math.sin(deltaLambda / 2)
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a))
  return R * c
}

export function useCheckinLogic(
  activityId: Ref<string | undefined>,
  userPosition: Ref<UserLocation | null>
) {
  const { data: checkpoints } = useCheckpoints(activityId)
  const { data: routes } = useRoutes(activityId)
  const { data: visits } = useVisits(activityId)
  const checkInMutation = useCheckIn()

  watch(
    () => userPosition.value,
    (pos) => {
      if (!pos || !checkpoints.value || !routes.value || !visits.value) return

      const visitedCheckpointIds = new Set(visits.value.filter(v => v.checkpoint).map(v => v.checkpoint))
      const visitedRoutePointIds = new Set(visits.value.filter(v => v.route_point).map(v => v.route_point))

      // Check all unvisited checkpoints
      for (const cp of checkpoints.value) {
        if (!visitedCheckpointIds.has(cp.id) && !cp.route) {
          const dist = calculateDistance(pos.latitude, pos.longitude, cp.latitude, cp.longitude)
          if (dist <= cp.radius && pos.accuracy <= 50) {
            checkInMutation.mutate({
              type: 'checkpoint',
              id: cp.id,
              latitude: pos.latitude,
              longitude: pos.longitude,
              accuracy: pos.accuracy,
              is_manual: false
            })
          }
        }
      }

      // Check all unvisited route points
      for (const route of routes.value) {
        let allRoutePointsVisited = true

        for (const rp of route.points) {
          if (!visitedRoutePointIds.has(rp.id)) {
             allRoutePointsVisited = false
             const dist = calculateDistance(pos.latitude, pos.longitude, rp.latitude, rp.longitude)
             if (dist <= rp.radius && pos.accuracy <= 50) {
               checkInMutation.mutate({
                  type: 'route_point',
                  id: rp.id,
                  latitude: pos.latitude,
                  longitude: pos.longitude,
                  accuracy: pos.accuracy,
                  is_manual: false
               })
             }
          }
        }

        // If all route points visited, try check into main checkpoint
        if (allRoutePointsVisited && route.main_checkpoint) {
            // Find the actual checkpoint data for main_checkpoint
            const cp = checkpoints.value.find(c => c.id === route.main_checkpoint)
            if (cp && !visitedCheckpointIds.has(cp.id)) {
                const dist = calculateDistance(pos.latitude, pos.longitude, cp.latitude, cp.longitude)
                if (dist <= cp.radius && pos.accuracy <= 50) {
                    checkInMutation.mutate({
                        type: 'checkpoint',
                        id: cp.id,
                        latitude: pos.latitude,
                        longitude: pos.longitude,
                        accuracy: pos.accuracy,
                        is_manual: false
                    })
                }
            }
        }
      }
    },
    { deep: true }
  )
  
  return {
    checkInMutation
  }
}
