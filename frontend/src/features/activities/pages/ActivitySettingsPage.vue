<script setup lang="ts">
import { computed, reactive, ref, watch } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'
import { ArrowLeft, Eye, Save, Shield, Trash2, Users } from '@lucide/vue'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { useCurrentUser } from '@/features/auth'
import {
  useActivities,
  useActivityParticipants,
  useActivityRoles,
  useAssignActivityRole,
  useCreateActivityRole,
  useDeleteActivityRole,
  useRemoveActivityParticipant,
  useUpdateActivity,
  useUpdateActivityRole,
} from '@/features/activities'
import { useHiddenParticipants } from '@/features/activities/composables/useHiddenParticipants'
import type {
  ActivityRole,
  ActivityRolePayload,
  ActivityPermissionCode,
} from '@/features/activities'

const route = useRoute()
const router = useRouter()
const activityId = computed(() =>
  typeof route.params.activityId === 'string' ? route.params.activityId : undefined,
)
const currentUser = useCurrentUser()
const activities = useActivities()
const roles = useActivityRoles(activityId)
const participants = useActivityParticipants(activityId)
const createRole = useCreateActivityRole()
const updateRole = useUpdateActivityRole()
const deleteRole = useDeleteActivityRole()
const assignRole = useAssignActivityRole()
const removeParticipant = useRemoveActivityParticipant()
const updateActivity = useUpdateActivity()
const currentUserId = computed(() => currentUser.data.value?.id)
const { hiddenParticipantIds, showParticipant, clearHiddenParticipants } = useHiddenParticipants(activityId, currentUserId)

const activity = computed(() => activities.data.value?.find((item) => item.id === activityId.value))
const isOwner = computed(() => activity.value?.created_by === currentUser.data.value?.id)
const selectedRoleId = ref<string | null>(null)
const defaultRoleId = ref<string | null>(null)
const notice = ref('')
const error = ref('')
const participantToRemove = ref<{ id: string; user_profile: { username: string } } | null>(null)
const form = reactive({
  name: '',
  description: '',
  color: '',
  canCreate: false,
  canCreateLocations: false,
  canCreateRoutes: false,
  canManageQrCodes: false,
  canUploadPhotos: false,
  canSetMeetingPoints: false,
  canView: false,
  visibility: 'everyone' as 'everyone' | 'roles',
  roleIds: [] as string[],
})

const selectedRole = computed(() =>
  roles.data.value?.find((role) => role.id === selectedRoleId.value),
)
const editing = computed(() => !!selectedRoleId.value)
const viewRoles = computed(() =>
  (roles.data.value ?? []).filter((role) => role.name.toLowerCase() !== 'owner'),
)

const hiddenParticipantsList = computed(() => {
  if (!participants.data.value) return []
  return hiddenParticipantIds.value
    .map((id) => participants.data.value?.find((p) => p.id === id))
    .filter((p): p is Exclude<typeof p, undefined> => p !== undefined && p.user !== currentUser.data.value?.id)
})
function participantName(participant: {
  user_profile: { first_name: string; last_name: string; username: string }
}) {
  return (
    [participant.user_profile.first_name, participant.user_profile.last_name]
      .filter(Boolean)
      .join(' ') || participant.user_profile.username
  )
}
watch(
  activity,
  (value) => {
    defaultRoleId.value = value?.default_role_id ?? null
  },
  { immediate: true },
)

function grant(role: ActivityRole | undefined, code: ActivityPermissionCode) {
  return role?.permission_grants.find((item) => item.code === code)
}
function resetForm() {
  selectedRoleId.value = null
  Object.assign(form, {
    name: '',
    description: '',
    color: '',
    canCreate: false,
    canCreateLocations: false,
    canCreateRoutes: false,
    canManageQrCodes: false,
    canUploadPhotos: false,
    canSetMeetingPoints: false,
    canView: false,
    visibility: 'everyone',
    roleIds: [],
  })
}
function selectRole(role: ActivityRole) {
  selectedRoleId.value = role.id
  const create = grant(role, 'checkpoints.create')
  const createLocations = grant(role, 'locations.create')
  const createRoutes = grant(role, 'routes.create')
  const manageQrCodes = grant(role, 'checkpoints.qrcodes.manage')
  const uploadPhotos = grant(role, 'checkpoints.photos.upload')
  const setMeetingPoints = grant(role, 'meeting_points.set')
  const view = grant(role, 'participants.map.view')
  Object.assign(form, {
    name: role.name,
    description: role.description,
    color: role.color,
    canCreate: !!create,
    canCreateLocations: !!createLocations,
    canCreateRoutes: !!createRoutes,
    canManageQrCodes: !!manageQrCodes,
    canUploadPhotos: !!uploadPhotos,
    canSetMeetingPoints: !!setMeetingPoints,
    canView: !!view,
    visibility: view?.scope?.visibility ?? 'everyone',
    roleIds: [...(view?.scope?.role_ids ?? [])],
  })
  error.value = ''
}
watch(selectedRole, (role) => {
  if (role && role.id !== selectedRoleId.value) selectRole(role)
})

function payload(): ActivityRolePayload {
  const permissions: ActivityRolePayload['permissions'] = []
  if (form.canCreate) permissions.push({ code: 'checkpoints.create' })
  if (form.canCreateLocations) permissions.push({ code: 'locations.create' })
  if (form.canCreateRoutes) permissions.push({ code: 'routes.create' })
  if (form.canManageQrCodes) permissions.push({ code: 'checkpoints.qrcodes.manage' })
  if (form.canUploadPhotos) permissions.push({ code: 'checkpoints.photos.upload' })
  if (form.canSetMeetingPoints) permissions.push({ code: 'meeting_points.set' })
  if (form.canView)
    permissions.push({
      code: 'participants.map.view',
      scope:
        form.visibility === 'everyone'
          ? { visibility: 'everyone' }
          : { visibility: 'roles', role_ids: form.roleIds },
    })
  return {
    name: form.name.trim(),
    description: form.description.trim(),
    color: form.color.trim(),
    permissions,
  }
}
function saveRole() {
  if (!activityId.value || !form.name.trim()) return
  error.value = ''
  const onSuccess = () => {
    notice.value = editing.value ? 'Роль оновлено.' : 'Роль створено.'
    resetForm()
  }
  const onError = (reason: unknown) => {
    error.value = errorMessage(reason)
  }
  if (selectedRoleId.value)
    updateRole.mutate(
      { activityId: activityId.value, roleId: selectedRoleId.value, data: payload() },
      { onSuccess, onError },
    )
  else createRole.mutate({ activityId: activityId.value, data: payload() }, { onSuccess, onError })
}
function removeRole(role: ActivityRole) {
  if (!activityId.value || !window.confirm(`Видалити роль «${role.name}»?`)) return
  deleteRole.mutate(
    { activityId: activityId.value, roleId: role.id },
    {
      onSuccess: () => {
        notice.value = 'Роль видалено.'
        resetForm()
      },
      onError: (reason) => {
        error.value = errorMessage(reason)
      },
    },
  )
}
function changeParticipantRole(participantId: string, roleId: string | null) {
  if (!activityId.value) return
  assignRole.mutate(
    { activityId: activityId.value, participantId, roleId },
    {
      onError: (reason) => {
        error.value = errorMessage(reason)
      },
    },
  )
}
function toggleVisibleRole(roleId: string, checked: boolean) {
  form.roleIds = checked
    ? Array.from(new Set([...form.roleIds, roleId]))
    : form.roleIds.filter((id) => id !== roleId)
}
function openRemoveParticipantDialog(participant: {
  id: string
  user_profile: { username: string }
}) {
  participantToRemove.value = participant
}
function closeRemoveParticipantDialog() {
  if (!removeParticipant.isPending.value) participantToRemove.value = null
}
function removeParticipantFromRoom() {
  if (!activityId.value || !participantToRemove.value) return
  removeParticipant.mutate(
    { activityId: activityId.value, participantId: participantToRemove.value.id },
    {
      onSuccess: () => {
        participantToRemove.value = null
        notice.value = 'Користувача видалено з кімнати.'
      },
      onError: (reason) => {
        error.value = errorMessage(reason)
      },
    },
  )
}
function saveDefaultRole() {
  if (!activityId.value) return
  updateActivity.mutate(
    { id: activityId.value, data: { default_role_id: defaultRoleId.value } },
    {
      onSuccess: () => {
        notice.value = 'Дефолтну роль оновлено.'
      },
      onError: (reason) => {
        error.value = errorMessage(reason)
      },
    },
  )
}
function errorMessage(reason: unknown) {
  const response = reason as { response?: { data?: { detail?: string; [key: string]: unknown } } }
  const data = response.response?.data
  if (data?.detail) return data.detail
  if (data) {
    const formatValue = (value: unknown) =>
      typeof value === 'object' ? JSON.stringify(value) : String(value)
    const messages = Object.entries(data).flatMap(([field, value]) =>
      Array.isArray(value)
        ? value.map((item) => `${field}: ${formatValue(item)}`)
        : [`${field}: ${formatValue(value)}`],
    )
    if (messages.length) return messages.join(' ')
  }
  return reason instanceof Error ? reason.message : 'Щось пішло не так.'
}
</script>

<template>
  <main class="mx-auto max-w-6xl px-4 py-8 sm:px-6 lg:py-12">
    <div class="mb-8 flex items-start gap-4">
      <Button variant="outline" size="icon" aria-label="Назад" @click="router.push('/activities')"
        ><ArrowLeft class="size-4"
      /></Button>
      <div>
        <p class="mb-2 text-xs font-semibold uppercase tracking-[0.25em] text-muted-foreground">
          MDVL / ROOM SETTINGS
        </p>
        <h1 class="text-3xl font-bold tracking-tight">
          {{ activity?.title || 'Налаштування кімнати' }}
        </h1>
        <p class="mt-2 text-muted-foreground">Ролі, дозволи та учасники кімнати.</p>
      </div>
    </div>
    <p
      v-if="notice"
      class="mb-5 rounded-lg border border-emerald-500/30 bg-emerald-500/10 px-4 py-3 text-sm text-emerald-300"
    >
      {{ notice }}
    </p>
    <p
      v-if="error"
      class="mb-5 rounded-lg border border-destructive/40 px-4 py-3 text-sm text-destructive"
    >
      {{ error }}
    </p>
    <div
      v-if="roles.isPending.value || participants.isPending.value"
      class="rounded-xl border border-dashed p-12 text-center text-muted-foreground"
    >
      Завантаження налаштувань...
    </div>
    <div v-else class="grid gap-6 lg:grid-cols-[minmax(0,1fr)_minmax(0,1.2fr)]">
      <Card>
        <CardHeader
          ><CardTitle class="flex items-center gap-2"><Shield class="size-5" /> Ролі</CardTitle
          ><CardDescription>Кожна роль має власний набір дозволів.</CardDescription></CardHeader
        >
        <CardContent class="space-y-3">
          <div v-if="!viewRoles.length" class="text-sm text-muted-foreground">Ролей ще немає.</div>
          <button
            v-for="role in viewRoles"
            :key="role.id"
            class="flex w-full items-center justify-between rounded-lg border px-3 py-3 text-left transition-colors hover:bg-muted/50"
            :class="selectedRoleId === role.id ? 'border-primary bg-muted/50' : ''"
            @click="selectRole(role)"
          >
            <span
              ><span class="block font-medium">{{ role.name }}</span
              ><span class="text-xs text-muted-foreground"
                >{{ role.permission_grants.length }} дозволів</span
              ></span
            ><Trash2
              v-if="isOwner && role.name.toLowerCase() !== 'owner'"
              class="size-4 text-muted-foreground hover:text-destructive"
              @click.stop="removeRole(role)"
            />
          </button>

          <div v-if="isOwner" class="space-y-2 rounded-lg border p-3">
            <Label for="default-role">Дефолтна роль для нових учасників</Label>
            <div class="flex gap-2">
              <Select v-model="defaultRoleId">
                <SelectTrigger id="default-role" class="min-w-0 flex-1">
                  <SelectValue placeholder="Choose role" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem
                    v-for="role in viewRoles"
                    :key="role.id"
                    :value="role.id"
                    :disabled="role.name.toLowerCase() === 'owner'"
                  >
                    {{ role.name }}
                  </SelectItem>
                </SelectContent> </Select
              ><Button
                type="button"
                variant="outline"
                :disabled="updateActivity.isPending.value"
                @click="saveDefaultRole"
                >Зберегти</Button
              >
            </div>
          </div>
        </CardContent>
      </Card>

      <Card v-if="isOwner">
        <CardHeader
          ><CardTitle>{{ editing ? 'Редагувати роль' : 'Створити роль' }}</CardTitle
          ><CardDescription>Дозволи застосовуються лише в цій кімнаті.</CardDescription></CardHeader
        >
        <CardContent
          ><form class="space-y-5" @submit.prevent="saveRole">
            <div class="grid gap-4 sm:grid-cols-2">
              <div class="space-y-2">
                <Label for="role-name">Назва</Label
                ><Input
                  id="role-name"
                  v-model="form.name"
                  placeholder="Наприклад, Координатор"
                  required
                />
              </div>
              <div class="space-y-2">
                <Label for="role-color">Колір</Label
                ><Input id="role-color" v-model="form.color" placeholder="#3B82F6" />
              </div>
            </div>
            <div class="space-y-2">
              <Label for="role-description">Опис</Label
              ><textarea
                id="role-description"
                v-model="form.description"
                rows="2"
                class="w-full resize-none rounded-md border border-input bg-transparent px-3 py-2 text-sm outline-none focus-visible:ring-3 focus-visible:ring-ring/50"
              />
            </div>
            <label class="flex items-start gap-3 rounded-lg border p-3"
              ><input type="checkbox" v-model="form.canCreate" class="mt-1" /><span
                ><span class="block text-sm font-medium">Створювати чекпоїнти</span
                ><span class="text-xs text-muted-foreground"
                  >Учасник може створювати та керувати власними чекпоїнтами.</span
                ></span
              ></label
            >
            <label class="flex items-start gap-3 rounded-lg border p-3"
              ><input type="checkbox" v-model="form.canCreateLocations" class="mt-1" /><span
                ><span class="block text-sm font-medium">Створювати локації</span
                ><span class="text-xs text-muted-foreground"
                  >Учасник може створювати та керувати власними локаціями.</span
                ></span
              ></label
            >
            <label class="flex items-start gap-3 rounded-lg border p-3"
              ><input type="checkbox" v-model="form.canCreateRoutes" class="mt-1" /><span
                ><span class="block text-sm font-medium">Створювати маршрути</span
                ><span class="text-xs text-muted-foreground"
                  >Учасник може створювати та керувати власними маршрутами.</span
                ></span
              ></label
            >
            <label class="flex items-start gap-3 rounded-lg border p-3"
              ><input type="checkbox" v-model="form.canManageQrCodes" class="mt-1" /><span
                ><span class="block text-sm font-medium">Керувати QR-кодами чекпоїнтів</span
                ><span class="text-xs text-muted-foreground"
                  >Учасник може створювати та видаляти QR-коди.</span
                ></span
              ></label
            >
            <label class="flex items-start gap-3 rounded-lg border p-3"
              ><input type="checkbox" v-model="form.canUploadPhotos" class="mt-1" /><span
                ><span class="block text-sm font-medium"
                  >Завантажувати фото чекпоїнтів / локацій</span
                ><span class="text-xs text-muted-foreground"
                  >Учасник може додавати фото до точок на карті.</span
                ></span
              ></label
            >
            <label class="flex items-start gap-3 rounded-lg border p-3"
              ><input type="checkbox" v-model="form.canSetMeetingPoints" class="mt-1" /><span
                ><span class="block text-sm font-medium">Встановлювати точки зустрічі</span
                ><span class="text-xs text-muted-foreground"
                  >Учасник може додавати, змінювати та видаляти точки зустрічі.</span
                ></span
              ></label
            >
            <div class="rounded-lg border p-3">
              <label class="flex items-start gap-3"
                ><input type="checkbox" v-model="form.canView" class="mt-1" /><span
                  ><span class="block text-sm font-medium">Бачити учасників на карті</span
                  ><span class="text-xs text-muted-foreground"
                    >Налаштуй, кого бачить ця роль.</span
                  ></span
                ></label
              >
              <div v-if="form.canView" class="mt-4 space-y-3 pl-6">
                <Select v-model="form.visibility">
                  <SelectTrigger class="w-full">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="everyone">Усіх учасників</SelectItem>
                    <SelectItem value="roles">Лише вибрані ролі</SelectItem>
                  </SelectContent>
                </Select>
                <div v-if="form.visibility === 'roles'" class="grid gap-2 sm:grid-cols-2">
                  <label
                    v-for="role in viewRoles"
                    :key="role.id"
                    class="flex items-center gap-2 text-sm"
                    ><input
                      type="checkbox"
                      :checked="form.roleIds.includes(role.id)"
                      @change="toggleVisibleRole(role.id, ($event.target as HTMLInputElement).checked)"
                    />{{ role.name }}</label
                  >
                </div>
              </div>
            </div>
            <div class="flex gap-2">
              <Button
                type="submit"
                :disabled="
                  !form.name.trim() || createRole.isPending.value || updateRole.isPending.value
                "
                ><Save class="mr-2 size-4" />{{
                  editing ? 'Зберегти зміни' : 'Створити роль'
                }}</Button
              ><Button v-if="editing" type="button" variant="outline" @click="resetForm"
                >Скасувати</Button
              >
            </div>
          </form></CardContent
        >
      </Card>
      <Card v-else
        ><CardHeader
          ><CardTitle>Доступні ролі</CardTitle
          ><CardDescription>Керувати ролями може лише власник кімнати.</CardDescription></CardHeader
        ><CardContent
          ><p class="text-sm text-muted-foreground">
            Твоя роль визначає доступ до карти та чекпоїнтів.
          </p></CardContent
        ></Card
      >
    </div>

    <Card class="mt-6"
      ><CardHeader
        ><CardTitle class="flex items-center gap-2"><Users class="size-5" /> Учасники</CardTitle
        ><CardDescription
          >Нові учасники автоматично отримують вибрану дефолтну роль.</CardDescription
        ></CardHeader
      ><CardContent
        ><div class="divide-y divide-border">
          <div
            v-for="participant in participants.data.value"
            :key="participant.id"
            class="flex items-center justify-between gap-4 py-3"
          >
            <div>
              <RouterLink
                :to="{
                  name: 'public-profile',
                  params: { username: participant.user_profile.username },
                }"
                class="font-medium text-primary underline-offset-4 hover:underline"
                >{{ participantName(participant) }}</RouterLink
              ><span
                v-if="participant.user === activity?.created_by"
                class="ml-2 text-xs font-semibold text-primary"
                >Власник кімнати</span
              >
              <p class="text-xs text-muted-foreground">
                Приєднався {{ new Date(participant.joined_at).toLocaleDateString('uk-UA') }}
              </p>
            </div>
            <div v-if="participant.user !== activity?.created_by" class="flex items-center gap-2">
              <Select
                :model-value="participant.role?.id ?? '__none'"
                :disabled="
                  !isOwner || assignRole.isPending.value || removeParticipant.isPending.value
                "
                @update:model-value="
                  changeParticipantRole(participant.id, $event === '__none' ? null : $event)
                "
              >
                <SelectTrigger class="w-[12rem]">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="__none">Без ролі</SelectItem>
                  <SelectItem v-for="role in viewRoles" :key="role.id" :value="role.id">
                    {{ role.name }}
                  </SelectItem>
                </SelectContent> </Select
              ><Button
                v-if="isOwner"
                type="button"
                variant="ghost"
                size="icon"
                :disabled="removeParticipant.isPending.value"
                :aria-label="`Видалити ${participant.user_profile.username} з кімнати`"
                @click="openRemoveParticipantDialog(participant)"
                ><Trash2 class="size-4 text-destructive"
              /></Button>
            </div>
          </div></div></CardContent
    ></Card>

    <Card v-if="hiddenParticipantsList.length > 0" class="mt-6"
      ><CardHeader
        ><CardTitle class="flex items-center gap-2"><Eye class="size-5" /> Hidden participants</CardTitle
        ><CardDescription
          >These participants are hidden from your map view. You can restore them at any time.</CardDescription
        ></CardHeader
      ><CardContent
        ><div class="divide-y divide-border">
          <div
            v-for="participant in hiddenParticipantsList"
            :key="participant.id"
            class="flex items-center justify-between gap-4 py-3"
          >
            <div>
              <RouterLink
                :to="{
                  name: 'public-profile',
                  params: { username: participant.user_profile.username },
                }"
                class="font-medium text-primary underline-offset-4 hover:underline"
                >{{ participantName(participant) }}</RouterLink
              >
              <p class="text-xs text-muted-foreground">
                Приєднався {{ new Date(participant.joined_at).toLocaleDateString('uk-UA') }}
              </p>
            </div>
            <Button
              type="button"
              variant="outline"
              size="sm"
              @click="showParticipant(participant.id)"
            >
              Show
            </Button>
          </div>
        </div>
        <div v-if="hiddenParticipantsList.length > 0" class="mt-4 pt-4 border-t">
          <Button
            type="button"
            variant="ghost"
            size="sm"
            class="text-destructive hover:text-destructive"
            @click="clearHiddenParticipants"
          >
            Show all participants
          </Button>
        </div></CardContent
    ></Card>
  </main>
  <Teleport to="body">
    <div
      v-if="participantToRemove"
      class="fixed inset-0 z-50 flex items-end bg-black/60 p-0 sm:items-center sm:justify-center sm:p-4"
      role="presentation"
      @click.self="closeRemoveParticipantDialog"
    >
      <section
        class="w-full rounded-t-2xl border bg-background p-5 shadow-xl sm:max-w-md sm:rounded-2xl"
        role="dialog"
        aria-modal="true"
        aria-labelledby="remove-participant-title"
      >
        <h2 id="remove-participant-title" class="text-lg font-semibold">Видалити учасника?</h2>
        <p class="mt-2 text-sm leading-6 text-muted-foreground">
          Користувач «{{ participantToRemove.user_profile.username }}» втратить доступ до цієї
          кімнати.
        </p>
        <div class="mt-6 flex flex-col-reverse gap-2 sm:flex-row sm:justify-end">
          <Button
            type="button"
            variant="outline"
            class="min-h-11 w-full sm:w-auto"
            :disabled="removeParticipant.isPending.value"
            @click="closeRemoveParticipantDialog"
            >Скасувати</Button
          >
          <Button
            type="button"
            variant="destructive"
            class="min-h-11 w-full sm:w-auto"
            :disabled="removeParticipant.isPending.value"
            @click="removeParticipantFromRoom"
            >{{ removeParticipant.isPending.value ? 'Видаляємо...' : 'Видалити з кімнати' }}</Button
          >
        </div>
      </section>
    </div>
  </Teleport>
</template>
