<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { Copy, DoorOpen, LogOut, Plus, RefreshCw, Settings, Trash2, Users, ShoppingBag } from '@lucide/vue'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useCurrentUser } from '@/features/auth'
import {
  useActivities,
  useCreateActivity,
  useDeleteActivity,
  useJoinActivity,
  useLeaveActivity,
  useJoinRequests,
  useApproveJoinRequest,
  useRejectJoinRequest,
} from '@/features/activities'
import type { Activity } from '@/features/activities'

const { t } = useI18n()

const title = ref('')
const description = ref('')
const roomId = ref('')
const notice = ref('')
const copiedId = ref('')
const router = useRouter()
const userQuery = useCurrentUser()
const activitiesQuery = useActivities()
const createMutation = useCreateActivity({
  onSuccess: () => {
    title.value = ''
    description.value = ''
    notice.value = t('activities.activityCreated')
  },
})
const deleteMutation = useDeleteActivity({
  onSuccess: () => {
    notice.value = t('activities.activityDeleted')
  },
})
const joinMutation = useJoinActivity({
  onSuccess: () => {
    roomId.value = ''
    notice.value = t('activities.joinRequestSent')
  },
})
const leaveMutation = useLeaveActivity({
  onSuccess: () => {
    notice.value = t('activities.leftActivity')
  },
})
const activities = computed(() => activitiesQuery.data.value ?? [])

const incomingRequestsQuery = useJoinRequests(ref('incoming'))
const outgoingRequestsQuery = useJoinRequests(ref('outgoing'))
const incomingRequests = computed(() => incomingRequestsQuery.data.value ?? [])
const outgoingRequests = computed(() => outgoingRequestsQuery.data.value ?? [])

const approveMutation = useApproveJoinRequest({
  onSuccess: () => {
    notice.value = t('activities.joinRequestAccepted')
    incomingRequestsQuery.refetch()
    activitiesQuery.refetch()
  },
})
const rejectMutation = useRejectJoinRequest({
  onSuccess: () => {
    notice.value = t('activities.joinRequestRejected')
    incomingRequestsQuery.refetch()
  },
})

const isFetchingAny = computed(
  () =>
    activitiesQuery.isFetching.value ||
    incomingRequestsQuery.isFetching.value ||
    outgoingRequestsQuery.isFetching.value,
)
const refreshAll = () => {
  activitiesQuery.refetch()
  incomingRequestsQuery.refetch()
  outgoingRequestsQuery.refetch()
}

watch(
  userQuery.error,
  (error) => {
    const status = (error as { response?: { status?: number } })?.response?.status
    if (status === 401) router.replace({ path: '/login', query: { redirect: '/activities' } })
  },
  { immediate: true },
)

const errorMessage = (error: unknown) => {
  const response = (error as { response?: { data?: { detail?: string } } })?.response
  return response?.data?.detail || (error instanceof Error ? error.message : t('errors.somethingWentWrong'))
}
const createActivity = () => {
  if (title.value.trim())
    createMutation.mutate({ title: title.value.trim(), description: description.value.trim() })
}
const joinActivity = () => {
  if (roomId.value.trim()) joinMutation.mutate(roomId.value.trim())
}
const isOwner = (activity: Activity) => activity.created_by === userQuery.data.value?.id
const deleteActivity = (activity: Activity) => {
  if (window.confirm(`${t('activities.deleteActivityConfirm')} «${activity.title}»?`)) deleteMutation.mutate(activity.id)
}
const copyRoomId = async (id: string) => {
  await navigator.clipboard?.writeText(id)
  copiedId.value = id
  window.setTimeout(() => {
    if (copiedId.value === id) copiedId.value = ''
  }, 1600)
}
</script>

<template>
  <main class="mx-auto max-w-6xl px-4 py-8 sm:px-6 lg:py-12">
    <header class="mb-8 flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
      <div>
        <p class="mb-2 text-xs font-semibold uppercase tracking-[0.25em] text-muted-foreground">
          MDVL / {{ t('activities.activities') }}
        </p>
        <h1 class="text-3xl font-bold tracking-tight sm:text-4xl">{{ t('activities.myActivities') }}</h1>
        <p class="mt-2 max-w-xl text-muted-foreground">
          {{ t('activities.createActivity') }}
        </p>
      </div>
      <Button variant="outline" size="icon" aria-label="Refresh list" @click="refreshAll"
        ><RefreshCw class="size-4" :class="isFetchingAny ? 'animate-spin' : ''"
      /></Button>
    </header>

    <p
      v-if="notice"
      class="mb-5 rounded-lg border border-emerald-500/30 bg-emerald-500/10 px-4 py-3 text-sm text-emerald-300"
    >
      {{ notice }}
    </p>
    <section class="mb-10 grid gap-5 md:grid-cols-2">
      <Card>
        <CardHeader
          ><CardTitle class="flex items-center gap-2"
            ><Plus class="size-5" /> {{ t('activities.createRoom') }}</CardTitle
          ><CardDescription
            >{{ t('activities.createRoomDesc') }}</CardDescription
          ></CardHeader
        >
        <CardContent
          ><form class="space-y-4" @submit.prevent="createActivity">
            <div class="space-y-2">
              <Label for="activity-title">{{ t('activities.activityTitle') }}</Label
              ><Input
                id="activity-title"
                v-model="title"
                :placeholder="t('activities.activityTitle')"
                required
              />
            </div>
            <div class="space-y-2">
              <Label for="activity-description"
                >{{ t('activities.description') }} <span class="text-muted-foreground">({{ t('common.optional') }})</span></Label
              ><textarea
                id="activity-description"
                v-model="description"
                rows="3"
                :placeholder="t('activities.description')"
                class="w-full resize-none rounded-md border border-input bg-transparent px-3 py-2 text-sm outline-none placeholder:text-muted-foreground focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50"
              />
            </div>
            <p v-if="createMutation.error.value" class="text-sm text-destructive">
              {{ errorMessage(createMutation.error.value) }}
            </p>
            <Button
              type="submit"
              class="w-full"
              :disabled="createMutation.isPending.value || !title.trim()"
              >{{ createMutation.isPending.value ? t('activities.creating') : t('activities.create') }}</Button
            >
          </form></CardContent
        >
      </Card>
      <Card>
        <CardHeader
          ><CardTitle class="flex items-center gap-2"
            ><DoorOpen class="size-5" /> {{ t('activities.join') }}</CardTitle
          ><CardDescription
            >{{ t('activities.joinDesc') }}</CardDescription
          ></CardHeader
        >
        <CardContent
          ><form class="space-y-4" @submit.prevent="joinActivity">
            <div class="space-y-2">
              <Label for="room-id">{{ t('activities.roomId') }}</Label
              ><Input
                id="room-id"
                v-model="roomId"
                placeholder="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
                required
              />
            </div>
            <p v-if="joinMutation.error.value" class="text-sm text-destructive">
              {{ errorMessage(joinMutation.error.value) }}
            </p>
            <Button
              type="submit"
              variant="secondary"
              class="w-full"
              :disabled="joinMutation.isPending.value || !roomId.trim()"
              >{{
                joinMutation.isPending.value ? t('activities.joining') : t('activities.joinRoom')
              }}</Button
            >
          </form></CardContent
        >
      </Card>
    </section>

    <!-- Incoming Join Requests (for Owners) -->
    <section v-if="incomingRequests.length > 0" class="mb-10">
      <div class="mb-4 flex items-center justify-between">
        <h2 class="text-xl font-semibold">{{ t('activities.incomingRequests') }}</h2>
        <span
          class="rounded-full bg-amber-500/10 px-2.5 py-0.5 text-xs font-semibold text-amber-500"
          >{{ incomingRequests.length }}</span
        >
      </div>
      <div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        <Card
          v-for="request in incomingRequests"
          :key="request.id"
          class="border-amber-500/20 bg-amber-500/5"
        >
          <CardContent class="space-y-4 pt-6">
            <div class="flex items-start justify-between gap-3">
              <div>
                <h3 class="font-semibold">
                  {{
                    request.user_profile.first_name || request.user_profile.last_name
                      ? `${request.user_profile.first_name} ${request.user_profile.last_name}`
                      : request.user_profile.username
                  }}
                </h3>
                <p class="text-xs text-muted-foreground">@{{ request.user_profile.username }}</p>
                <p class="mt-2 text-sm text-muted-foreground">{{ t('activities.wantsToJoin') }}</p>
                <p class="text-sm font-medium text-foreground">{{ request.activity_title }}</p>
              </div>
              <span
                class="rounded-full bg-amber-500/20 px-2 py-0.5 text-[10px] uppercase font-mono tracking-wider text-amber-300"
                >{{ t('activities.new') }}</span
              >
            </div>
            <div class="flex gap-2 pt-2">
              <Button
                size="sm"
                class="flex-1 bg-emerald-600 text-white hover:bg-emerald-500 hover:text-white"
                :disabled="approveMutation.isPending.value || rejectMutation.isPending.value"
                @click="approveMutation.mutate(request.id)"
                >{{ t('activities.accept') }}</Button
              >
              <Button
                size="sm"
                variant="outline"
                class="flex-1 border-destructive/30 text-destructive hover:bg-destructive/10"
                :disabled="approveMutation.isPending.value || rejectMutation.isPending.value"
                @click="rejectMutation.mutate(request.id)"
                >{{ t('activities.reject') }}</Button
              >
            </div>
          </CardContent>
        </Card>
      </div>
    </section>

    <!-- Outgoing Join Requests (for Requesters) -->
    <section v-if="outgoingRequests.length > 0" class="mb-10">
      <div class="mb-4 flex items-center justify-between">
        <h2 class="text-xl font-semibold">{{ t('activities.outgoingRequests') }}</h2>
        <span
          class="rounded-full bg-blue-500/10 px-2.5 py-0.5 text-xs font-semibold text-blue-500"
          >{{ outgoingRequests.length }}</span
        >
      </div>
      <div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        <Card
          v-for="request in outgoingRequests"
          :key="request.id"
          class="border-blue-500/20 bg-blue-500/5"
        >
          <CardContent class="space-y-4 pt-6">
            <div>
              <h3 class="font-semibold text-foreground">{{ request.activity_title }}</h3>
              <p class="mt-1 text-xs text-muted-foreground">{{ t('activities.roomId') }}: {{ request.activity }}</p>
              <div class="mt-4 flex items-center gap-2 text-sm text-blue-400">
                <span class="relative flex h-2 w-2">
                  <span
                    class="animate-ping absolute inline-flex h-full w-full rounded-full bg-blue-400 opacity-75"
                  ></span>
                  <span class="relative inline-flex rounded-full h-2 w-2 bg-blue-500"></span>
                </span>
                {{ t('activities.waitingConfirmation') }}
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </section>

    <section>
      <div class="mb-4 flex items-center justify-between">
        <h2 class="text-xl font-semibold">{{ t('activities.myRooms') }}</h2>
        <span class="text-sm text-muted-foreground">{{ activities.length }}</span>
      </div>
      <div
        v-if="activitiesQuery.isPending.value"
        class="rounded-xl border border-dashed border-border p-12 text-center text-muted-foreground"
      >
        {{ t('activities.loadingRooms') }}
      </div>
      <div
        v-else-if="activitiesQuery.error.value"
        class="rounded-xl border border-destructive/40 p-8 text-center text-destructive"
      >
        {{ errorMessage(activitiesQuery.error.value) }}
      </div>
      <div
        v-else-if="!activities.length"
        class="rounded-xl border border-dashed border-border p-12 text-center"
      >
        <Users class="mx-auto mb-3 size-8 text-muted-foreground" />
        <p class="font-medium">{{ t('activities.noRoomsYet') }}</p>
        <p class="mt-1 text-sm text-muted-foreground">{{ t('activities.noRoomsDesc') }}</p>
      </div>
      <div v-else class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        <Card v-for="activity in activities" :key="activity.id" class="overflow-hidden"
          ><CardContent class="space-y-5 pt-6">
            <div class="flex items-start justify-between gap-3">
              <div>
                <h3 class="font-semibold">{{ activity.title }}</h3>
                <p class="mt-1 text-sm text-muted-foreground">
                  {{ activity.description || t('activities.noDescription') }}
                </p>
              </div>
            </div>
            <div
              class="flex items-center gap-2 rounded-md bg-muted/50 px-3 py-2 text-xs text-muted-foreground"
            >
              <span class="min-w-0 flex-1 truncate font-mono">{{ activity.id }}</span
              ><button
                class="hover:text-foreground"
                :aria-label="t('activities.copyId')"
                @click="copyRoomId(activity.id)"
              >
                <Copy class="size-4" />
              </button>
            </div>
            <p v-if="copiedId === activity.id" class="-mt-3 text-xs text-emerald-400">
              {{ t('activities.idCopied') }}
            </p>
            <div class="flex gap-2">
              <RouterLink
                :to="{ name: 'activity-map', params: { activityId: activity.id } }"
                class="inline-flex flex-1 items-center justify-center rounded-md bg-primary px-3 py-2 text-sm font-medium text-primary-foreground transition-colors hover:bg-primary/90"
                >{{ t('activities.map') }}</RouterLink
              ><RouterLink
                :to="{ name: 'activity-shop', params: { activityId: activity.id } }"
                class="inline-flex items-center justify-center rounded-md border px-3 py-2 text-sm font-medium transition-colors hover:bg-muted"
                :title="t('activities.shop')"
                ><ShoppingBag class="size-4" /></RouterLink
              ><RouterLink
                v-if="isOwner(activity)"
                :to="{ name: 'activity-settings', params: { activityId: activity.id } }"
                class="inline-flex items-center justify-center rounded-md border px-3 py-2 text-sm font-medium transition-colors hover:bg-muted"
                :title="t('activities.settings')"
                ><Settings class="size-4" /></RouterLink
              ><Button
                v-if="isOwner(activity)"
                variant="destructive"
                size="sm"
                class="flex-1"
                :disabled="deleteMutation.isPending.value"
                @click="deleteActivity(activity)"
                ><Trash2 class="mr-1 size-4" /> {{ t('activities.delete') }}</Button
              ><Button
                v-else
                variant="outline"
                size="sm"
                class="flex-1"
                :disabled="leaveMutation.isPending.value"
                @click="leaveMutation.mutate(activity.id)"
                ><LogOut class="mr-1 size-4" /> {{ t('activities.leave') }}</Button
              >
            </div>
          </CardContent></Card
        >
      </div>
    </section>
  </main>
</template>
