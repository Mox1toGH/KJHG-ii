import { useMutation, useQuery, useQueryClient } from '@tanstack/vue-query'
import type { Ref } from 'vue'
import apiClient from '@/lib/api/client'
import type {
  ActivityZone,
  CreateActivityZonePayload,
  CreateLocationMarkerPayload,
  LocationMarker,
  UpdateActivityZonePayload,
  UpdateLocationMarkerPayload,
} from './location.types'

type MarkerMutationOptions = {
  onSuccess?: () => void
  onError?: (error: unknown) => void
}

export function useMarkers(activityId: Ref<string | undefined>, options?: { refetchInterval?: number }) {
  return useQuery({
    queryKey: ['markers', activityId],
    queryFn: async () => {
      if (!activityId.value) return []
      const { data } = await apiClient.get<LocationMarker[]>('/locations/markers/', {
        params: { activity_id: activityId.value },
      })
      return data
    },
    enabled: () => !!activityId.value,
    refetchInterval: options?.refetchInterval,
  })
}

export function useZones(activityId: Ref<string | undefined>, options?: { refetchInterval?: number }) {
  return useQuery({
    queryKey: ['zones', activityId],
    queryFn: async () => {
      if (!activityId.value) return []
      const { data } = await apiClient.get<ActivityZone[]>('/locations/zones/', {
        params: { activity_id: activityId.value },
      })
      return data
    },
    enabled: () => !!activityId.value,
    refetchInterval: options?.refetchInterval,
  })
}

export function useCreateZone(options?: { onSuccess?: () => void }) {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (payload: CreateActivityZonePayload) => {
      const { data } = await apiClient.post<ActivityZone>('/locations/zones/', payload)
      return data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['zones'] })
      options?.onSuccess?.()
    },
  })
}

export function useUpdateZone() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async ({ id, payload }: { id: string; payload: UpdateActivityZonePayload }) => {
      const { data } = await apiClient.patch<ActivityZone>(`/locations/zones/${id}/`, payload)
      return data
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['zones'] }),
  })
}

export function useDeleteZone() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (id: string) => {
      await apiClient.delete(`/locations/zones/${id}/`)
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['zones'] }),
  })
}

export function useCreateMarker(options?: MarkerMutationOptions) {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (payload: CreateLocationMarkerPayload) => {
      console.info('[locations] POST marker payload', payload)
      try {
        const { data } = await apiClient.post<LocationMarker>('/locations/markers/', payload)
        console.info('[locations] POST marker response', data)
        return data
      } catch (error) {
        console.error('[locations] POST marker failed', error)
        throw error
      }
    },
    onSuccess: (_data, variables) => {
      queryClient.invalidateQueries({ queryKey: ['markers', variables.activity] })
      options?.onSuccess?.()
    },
    onError: options?.onError,
  })
}

export function useUpdateMarker(options?: MarkerMutationOptions) {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async ({ id, payload }: { id: string; payload: UpdateLocationMarkerPayload }) => {
      console.info('[locations] PATCH marker payload', { id, payload })
      try {
        const { data } = await apiClient.patch<LocationMarker>(`/locations/markers/${id}/`, payload)
        console.info('[locations] PATCH marker response', data)
        return data
      } catch (error) {
        console.error('[locations] PATCH marker failed', error)
        throw error
      }
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['markers', data.activity] })
      options?.onSuccess?.()
    },
    onError: options?.onError,
  })
}

export function useDeleteMarker(options?: { onSuccess?: () => void }) {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (id: string) => {
      await apiClient.delete(`/locations/markers/${id}/`)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['markers'] })
      options?.onSuccess?.()
    },
  })
}

export function useUploadMarkerPhotos() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async ({ markerId, files }: { markerId: string; files: File[] }) => {
      const uploads = files.map(async (file) => {
        const formData = new FormData()
        formData.append('image', file)
        const { data } = await apiClient.post(`/locations/markers/${markerId}/photos/`, formData)
        return data
      })
      return Promise.all(uploads)
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['markers'] }),
  })
}

export function useDeleteMarkerPhoto() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async ({ markerId, photoId }: { markerId: string; photoId: number }) => {
      await apiClient.delete(`/locations/markers/${markerId}/photos/${photoId}/`)
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['markers'] }),
  })
}
