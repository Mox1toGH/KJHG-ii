import { computed } from 'vue'
import { useQuery } from '@tanstack/vue-query'
import type { Ref } from 'vue'
import apiClient from '@/lib/api/client'

export interface ActivityPoint {
  id: string
  user: number
  username: string
  display_name: string
  room: string
  points: number
  created_at: string
  updated_at: string
}

export function useActivityPoints(activityId: Ref<string | undefined>) {
  return useQuery({
    queryKey: ['activity-points', activityId],
    queryFn: async () => {
      if (!activityId.value) return []
      const { data } = await apiClient.get<ActivityPoint[]>('/points/', {
        params: { room_id: activityId.value },
      })
      return data
    },
    enabled: () => !!activityId.value,
  })
}

export function useMyActivityPoints(
  activityId: Ref<string | undefined>,
  currentUserId: Ref<number | undefined>,
) {
  const query = useActivityPoints(activityId)
  const myPoints = computed(() => {
    if (!currentUserId.value) return 0
    const entry = query.data.value?.find((item) => item.user === currentUserId.value)
    return entry?.points ?? 0
  })
  return { ...query, myPoints }
}
