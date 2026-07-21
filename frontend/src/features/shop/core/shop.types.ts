export type ShopItemType = 'AVATAR' | 'BADGE'

export interface ShopItem {
  id: string
  item_type: ShopItemType
  activity: string
  activity_title?: string
  price: number
  created_at: string
  updated_at: string
  avatar?: AvatarItem
  badge?: BadgeItem
}

export interface AvatarItem {
  id: string
  icon_file: string | null
}

export interface BadgeItem {
  id: string
  text: string
  color: string
}

export interface UserItem {
  id: string
  user: string
  shop_item: ShopItem
  is_equipped: boolean
  purchased_at: string
}

export interface CreateShopItemPayload {
  item_type: ShopItemType
  activity: string
  price: number
  icon_file?: File
  text?: string
  color?: string
}

export interface PurchaseItemPayload {
  shop_item_id: string
}

export interface EquipItemPayload {
  user_item_id: string
}
