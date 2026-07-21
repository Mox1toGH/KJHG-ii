import { useQuery, useMutation, useQueryClient } from '@tanstack/vue-query'
import { shopApi } from '../core/shop.api'
import type { CreateShopItemPayload, EquipItemPayload, PurchaseItemPayload } from '../core/shop.types'

export function useShopItems(activityId?: string) {
  return useQuery({
    queryKey: ['shop-items', activityId],
    queryFn: () => shopApi.list(activityId),
  })
}

export function useCreateShopItem() {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: (payload: CreateShopItemPayload) => shopApi.create(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['shop-items'] })
    },
  })
}

export function useDeleteShopItem() {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: (id: string) => shopApi.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['shop-items'] })
    },
  })
}

export function usePurchaseItem() {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: (payload: PurchaseItemPayload) => shopApi.purchase(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['shop-items'] })
      queryClient.invalidateQueries({ queryKey: ['user-items'] })
      queryClient.invalidateQueries({ queryKey: ['points'] })
    },
  })
}

export function useEquipItem() {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: (payload: EquipItemPayload) => shopApi.equip(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['user-items'] })
    },
  })
}

export function useUserItems(activityId?: string, itemType?: string, userId?: string) {
  return useQuery({
    queryKey: ['user-items', activityId, itemType, userId],
    queryFn: () => shopApi.userItems(activityId, itemType, userId),
  })
}
