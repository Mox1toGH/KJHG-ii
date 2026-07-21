<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Plus, Trash2, ShoppingCart, Check, Upload, Palette, ShoppingBag, ArrowLeft } from '@lucide/vue'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { useShopItems, useCreateShopItem, useDeleteShopItem, usePurchaseItem, useEquipItem, useUserItems } from '../composables/useShop'
import { useActivities } from '@/features/activities'
import { useCurrentUser } from '@/features/auth'
import type { ShopItemType } from '../core/shop.types'

const route = useRoute()
const router = useRouter()
const activityId = computed(() => route.params.activityId as string | undefined)

const { data: activities } = useActivities()
const { data: currentUser } = useCurrentUser()
const { data: shopItems, isLoading: isLoadingItems } = useShopItems(activityId.value)
const { data: userItems, isLoading: isLoadingUserItems } = useUserItems(activityId.value)
const createMutation = useCreateShopItem()
const deleteMutation = useDeleteShopItem()
const purchaseMutation = usePurchaseItem()
const equipMutation = useEquipItem()

const showCreateModal = ref(false)
const newItemType = ref<ShopItemType>('AVATAR')
const newItemActivity = ref('')
const newItemPrice = ref(0)
const newItemText = ref('')
const newItemColor = ref('#3B82F6')
const newItemFile = ref<File | null>(null)

const selectedActivity = computed(() => {
  if (!newItemActivity.value || !activities.value) return null
  return activities.value.find(a => a.id === newItemActivity.value)
})

const currentActivity = computed(() => {
  if (!activityId.value || !activities.value) return null
  return activities.value.find(a => a.id === activityId.value)
})

const isActivityOwner = computed(() => {
  if (!currentActivity.value || !currentUser.value) return false
  return String(currentActivity.value.created_by) === String(currentUser.value.id)
})

const ownedItemIds = computed(() => {
  if (!userItems.value) return new Set()
  return new Set(userItems.value.map(ui => ui.shop_item.id))
})

const equippedItemIds = computed(() => {
  if (!userItems.value) return new Set()
  return new Set(userItems.value.filter(ui => ui.is_equipped).map(ui => ui.shop_item.id))
})

function openCreateModal() {
  if (activityId.value) {
    newItemActivity.value = activityId.value
  }
  showCreateModal.value = true
}

function closeCreateModal() {
  showCreateModal.value = false
  newItemType.value = 'AVATAR'
  newItemPrice.value = 0
  newItemText.value = ''
  newItemColor.value = '#3B82F6'
  newItemFile.value = null
}

function handleFileUpload(event: Event) {
  const target = event.target as HTMLInputElement
  if (target.files && target.files[0]) {
    const file = target.files[0]
    if (!file.name.endsWith('.svg')) {
      alert('Будь ласка, завантажте .svg файл')
      return
    }
    newItemFile.value = file
  }
}

async function handleCreateItem() {
  if (!newItemActivity.value || !newItemPrice.value) {
    alert('Будь ласка, заповніть всі обов\'язкові поля')
    return
  }

  if (newItemType.value === 'AVATAR' && !newItemFile.value) {
    alert('Будь ласка, завантажте іконку для рамки аватара')
    return
  }

  if (newItemType.value === 'BADGE' && !newItemText.value) {
    alert('Будь ласка, введіть текст для бейджу')
    return
  }

  try {
    await createMutation.mutateAsync({
      item_type: newItemType.value,
      activity: newItemActivity.value,
      price: newItemPrice.value,
      icon_file: newItemFile.value || undefined,
      text: newItemText.value || undefined,
      color: newItemColor.value,
    })
    closeCreateModal()
  } catch (error) {
    console.error('Failed to create item:', error)
    alert('Не вдалося створити предмет')
  }
}

async function handlePurchase(itemId: string) {
  try {
    await purchaseMutation.mutateAsync({ shop_item_id: itemId })
  } catch (error) {
    console.error('Failed to purchase item:', error)
    alert('Не вдалося придбати предмет')
  }
}

async function handleEquip(userItemId: string) {
  try {
    await equipMutation.mutateAsync({ user_item_id: userItemId })
  } catch (error) {
    console.error('Failed to equip item:', error)
    alert('Не вдалося надіти предмет')
  }
}

async function handleUnequip(userItemId: string) {
  try {
    await equipMutation.mutateAsync({ user_item_id: userItemId })
  } catch (error) {
    console.error('Failed to unequip item:', error)
    alert('Не вдалося зняти предмет')
  }
}

async function handleDeleteItem(itemId: string) {
  if (!confirm('Ви впевнені, що хочете видалити цей предмет?')) return
  try {
    await deleteMutation.mutateAsync(itemId)
  } catch (error) {
    console.error('Failed to delete item:', error)
    alert('Не вдалося видалити предмет')
  }
}

function getUserItemId(itemId: string): string | undefined {
  if (!userItems.value) return undefined
  return userItems.value.find(ui => ui.shop_item.id === itemId)?.id
}

const errorMessage = (error: unknown) => {
  const response = (error as { response?: { data?: { detail?: string } } })?.response
  return response?.data?.detail || (error instanceof Error ? error.message : 'Щось пішло не так.')
}
</script>

<template>
  <main class="mx-auto max-w-6xl px-4 py-8 sm:px-6 lg:py-12">
    <header class="mb-8 flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
      <div class="flex items-center gap-4">
        <Button variant="ghost" size="icon" @click="router.back()">
          <ArrowLeft class="size-5" />
        </Button>
        <div>
          <p class="mb-2 text-xs font-semibold uppercase tracking-[0.25em] text-muted-foreground">
            MDVL / SHOP
          </p>
          <h1 class="text-3xl font-bold tracking-tight sm:text-4xl">Магазин</h1>
          <p class="mt-2 max-w-xl text-muted-foreground">
            Купуй рамки аватарів та бейджі для своїх кімнат.
          </p>
        </div>
      </div>
      <Button v-if="isActivityOwner" @click="openCreateModal">
        <Plus class="mr-2 size-4" /> Створити предмет
      </Button>
    </header>

    <div
      v-if="isLoadingItems || isLoadingUserItems"
      class="rounded-xl border border-dashed p-12 text-center text-muted-foreground"
    >
      Завантаження предметів...
    </div>

    <div
      v-else-if="!shopItems?.length"
      class="rounded-xl border border-dashed p-12 text-center"
    >
      <ShoppingBag class="mx-auto mb-3 size-8 text-muted-foreground" />
      <p class="font-medium">Предметів ще немає</p>
      <p class="mt-1 text-sm text-muted-foreground">Створіть перший предмет для магазину.</p>
    </div>

    <div v-else class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
      <Card v-for="item in shopItems" :key="item.id" class="overflow-hidden">
        <CardContent class="space-y-5 pt-6">
          <div class="flex items-start justify-between gap-3">
            <div class="flex items-center gap-3">
              <div v-if="item.item_type === 'AVATAR'" class="size-14 shrink-0 rounded-xl bg-primary/10 flex items-center justify-center">
                <img
                  v-if="item.avatar?.icon_file"
                  :src="item.avatar.icon_file"
                  alt="Avatar"
                  class="size-10 object-contain"
                />
                <Upload v-else class="size-6 text-primary" />
              </div>
              <div v-else class="size-14 shrink-0 rounded-xl flex items-center justify-center" :style="{ backgroundColor: item.badge?.color + '20' }">
                <Palette class="size-6" :style="{ color: item.badge?.color }" />
              </div>
              <div>
                <h3 class="font-semibold">{{ item.item_type === 'AVATAR' ? 'Рамка аватара' : 'Бейдж' }}</h3>
                <p class="text-sm text-muted-foreground">{{ item.activity_title || 'Кімната' }}</p>
              </div>
            </div>
            <Button
              v-if="isActivityOwner"
              variant="ghost"
              size="icon"
              class="shrink-0 text-muted-foreground hover:text-destructive"
              @click="handleDeleteItem(item.id)"
            >
              <Trash2 class="size-4" />
            </Button>
          </div>

          <div v-if="item.item_type === 'BADGE'" class="flex items-center gap-2">
            <div
              class="inline-block rounded-lg px-3 py-1 text-sm font-medium"
              :style="{ backgroundColor: item.badge?.color, color: 'white' }"
            >
              {{ item.badge?.text }}
            </div>
          </div>

          <div class="text-2xl font-bold">{{ item.price }} очок</div>

          <div v-if="ownedItemIds.has(item.id)" class="flex gap-2">
            <Button
              v-if="equippedItemIds.has(item.id)"
              variant="outline"
              class="flex-1"
              @click="handleUnequip(getUserItemId(item.id)!)"
            >
              Зняти
            </Button>
            <Button
              v-else
              variant="secondary"
              class="flex-1"
              @click="handleEquip(getUserItemId(item.id)!)"
            >
              Надіти
            </Button>
          </div>
          <Button
            v-else
            class="w-full"
            :disabled="purchaseMutation.isPending.value"
            @click="handlePurchase(item.id)"
          >
            <ShoppingCart class="mr-2 size-4" />
            Купити
          </Button>
        </CardContent>
      </Card>
    </div>

    <!-- Create Item Modal -->
    <div
      v-if="showCreateModal"
      class="fixed inset-0 z-[200] flex items-center justify-center bg-background/80 p-4 backdrop-blur-sm"
      @click.self="closeCreateModal"
    >
      <Card class="w-full max-w-md">
        <CardHeader>
          <CardTitle class="flex items-center gap-2">
            <Plus class="size-5" /> Створити предмет
          </CardTitle>
          <CardDescription>Додайте новий аватар або бейдж до магазину</CardDescription>
        </CardHeader>
        <CardContent>
          <form class="space-y-4" @submit.prevent="handleCreateItem">
            <div class="space-y-2">
              <Label for="item-type">Тип предмета</Label>
              <select
                id="item-type"
                v-model="newItemType"
                class="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
              >
                <option value="AVATAR">Рамка аватара</option>
                <option value="BADGE">Бейдж</option>
              </select>
            </div>

            <div class="space-y-2">
              <Label for="activity">Кімната</Label>
              <select
                id="activity"
                v-model="newItemActivity"
                class="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
              >
                <option value="">Оберіть кімнату</option>
                <option v-for="activity in activities" :key="activity.id" :value="activity.id">
                  {{ activity.title }}
                </option>
              </select>
            </div>

            <div class="space-y-2">
              <Label for="price">Ціна (очок)</Label>
              <Input
                id="price"
                v-model.number="newItemPrice"
                type="number"
                min="0"
                placeholder="0"
              />
            </div>

            <div v-if="newItemType === 'AVATAR'" class="space-y-2">
              <Label for="icon-file">Файл іконки (.svg)</Label>
              <Input
                id="icon-file"
                type="file"
                accept=".svg"
                @change="handleFileUpload"
              />
            </div>

            <div v-if="newItemType === 'BADGE'" class="space-y-4">
              <div class="space-y-2">
                <Label for="badge-text">Текст бейджу</Label>
                <Input
                  id="badge-text"
                  v-model="newItemText"
                  type="text"
                  maxlength="50"
                  placeholder="Введіть текст"
                />
              </div>
              <div class="space-y-2">
                <Label for="badge-color">Колір бейджу</Label>
                <Input
                  id="badge-color"
                  v-model="newItemColor"
                  type="color"
                  class="h-10 w-full"
                />
              </div>
            </div>

            <p v-if="createMutation.error.value" class="text-sm text-destructive">
              {{ errorMessage(createMutation.error.value) }}
            </p>

            <div class="flex gap-3 pt-2">
              <Button
                type="button"
                variant="outline"
                class="flex-1"
                @click="closeCreateModal"
              >
                Скасувати
              </Button>
              <Button
                type="submit"
                class="flex-1"
                :disabled="createMutation.isPending.value"
              >
                {{ createMutation.isPending.value ? 'Створюємо...' : 'Створити' }}
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  </main>
</template>
