import { useMutation, useQuery, useQueryClient } from '@tanstack/vue-query'
import type { Ref } from 'vue'
import apiClient from '@/lib/api/client'
import type {
  Checkpoint, Route, Visit,
  CreateCheckpointPayload, UpdateCheckpointPayload,
  CreateRoutePayload, UpdateRoutePayload,
  CheckInPayload
} from './checkpoint.types'

export function useCheckpoints(activityId: Ref<string | undefined>, options?: { refetchInterval?: number }) {
  return useQuery({
    queryKey: ['checkpoints', activityId],
    queryFn: async () => {
      if (!activityId.value) return []
      const { data } = await apiClient.get<Checkpoint[]>('/checkpoints/checkpoints/', {
        params: { activity_id: activityId.value },
      })
      return data
    },
    enabled: () => !!activityId.value,
    refetchInterval: options?.refetchInterval,
  })
}

export function useRoutes(activityId: Ref<string | undefined>, options?: { refetchInterval?: number }) {
  return useQuery({
    queryKey: ['routes', activityId],
    queryFn: async () => {
      if (!activityId.value) return []
      const { data } = await apiClient.get<Route[]>('/checkpoints/routes/', {
        params: { activity_id: activityId.value },
      })
      return data
    },
    enabled: () => !!activityId.value,
    refetchInterval: options?.refetchInterval,
  })
}

export function useVisits(activityId: Ref<string | undefined>, options?: { refetchInterval?: number }) {
  return useQuery({
    queryKey: ['visits', activityId],
    queryFn: async () => {
      if (!activityId.value) return []
      const { data } = await apiClient.get<Visit[]>('/checkpoints/visits/', {
        params: { activity_id: activityId.value },
      })
      return data
    },
    enabled: () => !!activityId.value,
    refetchInterval: options?.refetchInterval,
  })
}

export function useCreateCheckpoint(options?: { onSuccess?: (data: Checkpoint) => void }) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (payload: CreateCheckpointPayload) => {
      const { data } = await apiClient.post<Checkpoint>('/checkpoints/checkpoints/', payload)
      return data
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['checkpoints'] })
      options?.onSuccess?.(data)
    },
  })
}

export function useUpdateCheckpoint() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async ({ id, payload }: { id: string; payload: UpdateCheckpointPayload }) => {
      const { data } = await apiClient.patch<Checkpoint>(`/checkpoints/checkpoints/${id}/`, payload)
      return data
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['checkpoints'] }),
  })
}

export function useDeleteCheckpoint() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (id: string) => {
      await apiClient.delete(`/checkpoints/checkpoints/${id}/`)
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['checkpoints'] }),
  })
}

export function useCreateRoute(options?: { onSuccess?: (data: Route) => void }) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (payload: CreateRoutePayload) => {
      const { data } = await apiClient.post<Route>('/checkpoints/routes/', payload)
      return data
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['routes'] })
      options?.onSuccess?.(data)
    },
  })
}

export function useUpdateRoute() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async ({ id, payload }: { id: string; payload: UpdateRoutePayload }) => {
      const { data } = await apiClient.patch<Route>(`/checkpoints/routes/${id}/`, payload)
      return data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['routes'] })
      queryClient.invalidateQueries({ queryKey: ['checkpoints'] })
    },
  })
}

export function useDeleteRoute() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (id: string) => {
      await apiClient.delete(`/checkpoints/routes/${id}/`)
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['routes'] }),
  })
}

export function useUploadCheckpointPhotos() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async ({ id, files, kind }: { id: string; files: File[]; kind: 'checkpoint' | 'route_point' }) => {
      const base = kind === 'checkpoint' ? 'checkpoints/checkpoints' : 'checkpoints/route-points'
      return Promise.all(files.map(async (file) => {
        const form = new FormData()
        form.append('image', file)
        const { data } = await apiClient.post(`/${base}/${id}/photos/`, form)
        return data
      }))
    },
    onSuccess: () => { queryClient.invalidateQueries({ queryKey: ['checkpoints'] }); queryClient.invalidateQueries({ queryKey: ['routes'] }) },
  })
}

export function useDeleteCheckpointPhoto() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async ({ id, photoId, kind }: { id: string; photoId: number; kind: 'checkpoint' | 'route_point' }) => {
      const base = kind === 'checkpoint' ? 'checkpoints/checkpoints' : 'checkpoints/route-points'
      await apiClient.delete(`/${base}/${id}/photos/${photoId}/`)
    },
    onSuccess: () => { queryClient.invalidateQueries({ queryKey: ['checkpoints'] }); queryClient.invalidateQueries({ queryKey: ['routes'] }) },
  })
}

export function useCheckIn() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (payload: CheckInPayload) => {
      const { data } = await apiClient.post<Visit>('/checkpoints/check-in/', payload)
      return data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['visits'] })
      queryClient.invalidateQueries({ queryKey: ['activity-points'] })
    },
  })
}
