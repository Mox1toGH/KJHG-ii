import apiClient from '@/lib/api/client'
import type { CreateShopItemPayload, EquipItemPayload, PurchaseItemPayload, ShopItem, UserItem } from './shop.types'

let csrfPromise: Promise<unknown> | undefined

function ensureCsrfCookie() {
  if (typeof document !== 'undefined' && document.cookie.includes('csrftoken=')) return Promise.resolve()
  csrfPromise ??= apiClient.get('/accounts/csrf/').finally(() => { csrfPromise = undefined })
  return csrfPromise
}

function withCsrf<T>(request: () => Promise<T>) { return ensureCsrfCookie().then(request) }

export const shopApi = {
  list: (activityId?: string) => {
    const params = activityId ? { activity_id: activityId } : undefined
    return apiClient.get<ShopItem[]>('/shop/items/', { params }).then((response) => response.data)
  },
  create: (payload: CreateShopItemPayload) => {
    const formData = new FormData()
    formData.append('item_type', payload.item_type)
    formData.append('activity', payload.activity)
    formData.append('price', payload.price.toString())
    
    if (payload.icon_file) {
      formData.append('icon_file', payload.icon_file)
    }
    if (payload.text) {
      formData.append('text', payload.text)
    }
    if (payload.color) {
      formData.append('color', payload.color)
    }
    
    return withCsrf(() => apiClient.post<ShopItem>('/shop/items/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    }).then((response) => response.data))
  },
  delete: (id: string) => withCsrf(() => apiClient.delete(`/shop/items/${id}/`).then(() => undefined)),
  purchase: (payload: PurchaseItemPayload) => withCsrf(() => apiClient.post<UserItem>('/shop/items/purchase/', payload).then((response) => response.data)),
  equip: (payload: EquipItemPayload) => withCsrf(() => apiClient.post<UserItem>('/shop/items/equip/', payload).then((response) => response.data)),
  userItems: (activityId?: string, itemType?: string, userId?: string) => {
    const params: Record<string, string> = {}
    if (activityId) params.activity_id = activityId
    if (itemType) params.item_type = itemType
    if (userId) params.user_id = userId
    return apiClient.get<UserItem[]>('/shop/user-items/', { params }).then((response) => response.data)
  },
}
