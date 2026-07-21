<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { Check, LogOut, Pencil, Plus, ShieldCheck, Trash2, UserRound, X, Users } from '@lucide/vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'

import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { useCurrentUser, useUserStatuses, useCreateStatus, useDeleteStatus, useLogout, useSetCurrentStatus } from '@/features/auth'
import LanguageSwitcher from '@/components/LanguageSwitcher.vue'
import ThemeSwitcher from '@/components/ThemeSwitcher.vue'
import { Switch } from '@/components/ui/switch'
import { Mail } from '@lucide/vue'
import { useUpdateNotificationPreferences } from '@/features/notifications/mutations'
import { useNotificationPreferences } from '@/features/notifications/queries'

const { t } = useI18n()

const router = useRouter()
const userQuery = useCurrentUser()
const statusesQuery = useUserStatuses()
const newStatusName = ref('')
const preferencesQuery = useNotificationPreferences()
const updatePreferencesMutation = useUpdateNotificationPreferences()
const emailNotificationsEnabled = ref(false)

watch(
  preferencesQuery.data,
  (preferences) => {
    if (preferences) {
      emailNotificationsEnabled.value = preferences.email_enabled
    }
  },
  { immediate: true },
)

watch(
  emailNotificationsEnabled,
  (newValue) => {
    if (preferencesQuery.data.value && preferencesQuery.data.value.email_enabled !== newValue) {
      updatePreferencesMutation.mutate({
        email_enabled: newValue,
      })
    }
  },
)

watch(
  userQuery.error,
  (error) => {
    const status = (error as { response?: { status?: number } })?.response?.status
    if (status === 401) router.replace({ path: '/login', query: { redirect: '/profile' } })
  },
  { immediate: true },
)

const logoutMutation = useLogout({
  onSuccess: () => router.replace('/login'),
})

const createStatusMutation = useCreateStatus({
  onSuccess: () => {
    newStatusName.value = ''
  },
})
const deleteStatusMutation = useDeleteStatus()
const setCurrentStatusMutation = useSetCurrentStatus()

const errorMessage = (error: unknown) => {
  const response = (error as { response?: { data?: { detail?: string; [key: string]: unknown } } })
    ?.response
  const data = response?.data
  if (data?.detail) return data.detail
  if (data) {
    const firstError = Object.values(data).flat()[0]
    if (typeof firstError === 'string') return firstError
  }
  return error instanceof Error ? error.message : t('errors.somethingWentWrong')
}

const displayName = computed(() => {
  const user = userQuery.data.value
  if (!user) return ''
  return [user.first_name, user.last_name].filter(Boolean).join(' ') || user.username
})
const formatDate = (value: string | null) => value
  ? new Intl.DateTimeFormat(t('common.locale'), { dateStyle: 'long', timeStyle: 'short' }).format(new Date(value))
  : t('profile.neverLoggedIn')

const submitStatus = () => {
  const name = newStatusName.value.trim()
  if (!name || createStatusMutation.isPending.value) return
  createStatusMutation.mutate(name)
}

const selectStatus = (statusId: number) => {
  if (setCurrentStatusMutation.isPending.value) return
  setCurrentStatusMutation.mutate({ status_id: statusId })
}

const clearStatus = () => {
  if (setCurrentStatusMutation.isPending.value) return
  setCurrentStatusMutation.mutate({ status_id: null })
}
</script>

<template>
  <main class="mx-auto max-w-3xl px-4 py-8 sm:px-6 lg:py-12">
    <header class="mb-8">
      <p class="mb-2 text-xs font-semibold uppercase tracking-[0.25em] text-muted-foreground">
        MDVL / {{ t('profile.myProfile') }}
      </p>
      <h1 class="text-3xl font-bold tracking-tight sm:text-4xl">{{ t('profile.myProfile') }}</h1>
      <p class="mt-2 text-muted-foreground">{{ t('profile.accountActionsDesc') }}</p>
    </header>

    <div
      v-if="userQuery.isPending.value"
      class="rounded-xl border border-dashed border-border p-12 text-center text-muted-foreground"
    >
      {{ t('common.loading') }}
    </div>

    <div
      v-else-if="userQuery.error.value"
      class="rounded-xl border border-destructive/40 p-8 text-center text-destructive"
    >
      {{ errorMessage(userQuery.error.value) }}
    </div>

    <template v-else-if="userQuery.data.value">
      <Card class="mb-5 overflow-hidden">
        <CardContent class="flex flex-col gap-5 p-6 sm:flex-row sm:items-center">
          <div
            class="size-16 shrink-0 overflow-hidden rounded-2xl bg-primary text-primary-foreground"
          >
            <img
              v-if="userQuery.data.value.avatar"
              :src="userQuery.data.value.avatar"
              :alt="`${displayName}'s ${t('profile.avatar')}`"
              class="size-full object-cover"
            />
            <UserRound v-else class="m-5 size-6" aria-hidden="true" />
          </div>
          <div class="min-w-0 flex-1">
            <h2 class="truncate text-2xl font-semibold">{{ displayName }}</h2>
            <p class="text-muted-foreground">@{{ userQuery.data.value.username }}</p>
            <p class="truncate text-sm text-muted-foreground">{{ userQuery.data.value.email }}</p>
          </div>
          <div
            class="flex items-center gap-2 text-sm"
            :class="userQuery.data.value.is_email_verified ? 'text-emerald-400' : 'text-amber-400'"
          >
            <ShieldCheck class="size-4" aria-hidden="true" />
            {{ userQuery.data.value.is_email_verified ? t('profile.emailVerified') : t('profile.emailNotVerified') }}
          </div>
        </CardContent>
      </Card>

      <div class="mb-5 grid gap-3 sm:grid-cols-2">
        <Card>
          <CardContent class="p-4">
            <p class="text-xs uppercase tracking-wider text-muted-foreground">{{ t('profile.joined') }}</p>
            <p class="mt-1 text-sm">{{ formatDate(userQuery.data.value.created_at) }}</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent class="p-4">
            <p class="text-xs uppercase tracking-wider text-muted-foreground">Statistics</p>
            <div class="mt-2 flex items-center gap-4">
              <div class="flex items-center gap-2">
                <div class="flex h-8 w-8 items-center justify-center rounded-lg bg-purple-500/20 text-purple-400">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/>
                  </svg>
                </div>
                <div>
                  <p class="text-xs text-muted-foreground">Scratches</p>
                  <p class="text-sm font-semibold">{{ userQuery.data.value.hexagons_explored || 0 }}</p>
                </div>
              </div>
              <div class="flex items-center gap-2">
                <div class="flex h-8 w-8 items-center justify-center rounded-lg bg-emerald-500/20 text-emerald-400">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M3 11l3-3 3 3 5-5 5 5"/>
                    <circle cx="12" cy="5" r="2"/>
                  </svg>
                </div>
                <div>
                  <p class="text-xs text-muted-foreground">Checkpoints</p>
                  <p class="text-sm font-semibold">{{ userQuery.data.value.checkpoints_visited || 0 }}</p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      <Card class="mb-5">
        <CardHeader>
          <CardTitle class="flex items-center justify-between gap-3">
            <span>{{ t('profile.status') }}</span>
            <span
              v-if="userQuery.data.value.current_status"
              class="rounded-full bg-primary/10 px-3 py-1 text-sm font-medium text-primary"
            >
              {{ userQuery.data.value.current_status }}
            </span>
            <span v-else class="text-sm font-normal text-muted-foreground">{{ t('profile.clearStatus') }}</span>
          </CardTitle>
          <CardDescription>{{ t('profile.statusDescription') }}</CardDescription>
        </CardHeader>
        <CardContent class="space-y-4">
          <form class="flex gap-2" @submit.prevent="submitStatus">
            <Input
              v-model="newStatusName"
              maxlength="50"
              :placeholder="t('profile.createStatus')"
              aria-label="New status name"
            />
            <Button
              type="submit"
              size="icon"
              :disabled="!newStatusName.trim() || createStatusMutation.isPending.value"
              aria-label="Create status"
            >
              <Plus class="size-4" />
            </Button>
          </form>

          <p v-if="createStatusMutation.error.value" class="text-sm text-destructive">
            {{ errorMessage(createStatusMutation.error.value) }}
          </p>

          <div v-if="statusesQuery.isPending.value" class="text-sm text-muted-foreground">
            {{ t('profile.loadingStatuses') }}
          </div>
          <p v-else-if="statusesQuery.error.value" class="text-sm text-destructive">
            {{ errorMessage(statusesQuery.error.value) }}
          </p>
          <div v-else class="space-y-2">
            <div
              v-for="userStatus in statusesQuery.data.value"
              :key="userStatus.id"
              class="flex items-center gap-2 rounded-lg border border-border p-3"
              :class="userStatus.name === userQuery.data.value.current_status ? 'border-primary/50 bg-primary/5' : ''"
            >
              <span class="min-w-0 flex-1 truncate">{{ userStatus.name }}</span>
              <Button
                v-if="userStatus.name !== userQuery.data.value.current_status"
                type="button"
                variant="outline"
                size="sm"
                :disabled="setCurrentStatusMutation.isPending.value"
                @click="selectStatus(userStatus.id)"
              >
                <Check class="mr-1 size-4" /> {{ t('profile.use') }}
              </Button>
              <Button
                v-else
                type="button"
                variant="ghost"
                size="sm"
                :disabled="setCurrentStatusMutation.isPending.value"
                @click="clearStatus"
              >
                <X class="mr-1 size-4" /> {{ t('profile.clearStatus') }}
              </Button>
              <Button
                type="button"
                variant="ghost"
                size="icon"
                :disabled="deleteStatusMutation.isPending.value"
                :aria-label="`Delete ${userStatus.name}`"
                @click="deleteStatusMutation.mutate(userStatus.id)"
              >
                <Trash2 class="size-4 text-destructive" />
              </Button>
            </div>
          </div>
          <p v-if="setCurrentStatusMutation.error.value" class="text-sm text-destructive">
            {{ errorMessage(setCurrentStatusMutation.error.value) }}
          </p>
          <p v-if="deleteStatusMutation.error.value" class="text-sm text-destructive">
            {{ errorMessage(deleteStatusMutation.error.value) }}
          </p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>{{ t('profile.settings') }}</CardTitle>
          <CardDescription>{{ t('profile.settingsDesc') }}</CardDescription>
        </CardHeader>
        <CardContent class="space-y-4">
          <div class="flex items-center justify-between">
            <span class="text-sm font-medium">{{ t('language.selectLanguage') }}</span>
            <LanguageSwitcher />
          </div>
          <div class="flex items-center justify-between">
            <span class="text-sm font-medium">{{ t('common.toggleTheme') }}</span>
            <ThemeSwitcher />
          </div>
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-3">
              <Mail class="size-5 text-muted-foreground" />
              <div>
                <span class="text-sm font-medium">{{ t('notifications.emailNotifications') }}</span>
                <p class="text-xs text-muted-foreground">{{ t('notifications.receiveEmailNotifications') }}</p>
              </div>
            </div>
            <Switch
              v-model:checked="emailNotificationsEnabled"
              :disabled="updatePreferencesMutation.isPending.value"
            />
          </div>
          <p v-if="updatePreferencesMutation.error.value" class="text-sm text-destructive">
            {{ errorMessage(updatePreferencesMutation.error.value) }}
          </p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>{{ t('profile.accountActions') }}</CardTitle>
          <CardDescription>{{ t('profile.accountActionsDesc') }}</CardDescription>
        </CardHeader>
        <CardContent class="space-y-4">
          <div class="flex flex-col gap-3 sm:flex-row">
            <Button as-child class="flex-1">
              <RouterLink to="/profile/edit"
                ><Pencil class="mr-2 size-4" /> {{ t('profile.editProfile') }}</RouterLink
              >
            </Button>
            <Button as-child variant="outline" class="flex-1">
              <RouterLink to="/friends"
                ><Users class="mr-2 size-4" /> Friends</RouterLink
              >
            </Button>
            <Button
              type="button"
              variant="outline"
              class="flex-1"
              :disabled="logoutMutation.isPending.value"
              @click="logoutMutation.mutate(undefined)"
            >
              <LogOut class="mr-2 size-4" />
              {{ logoutMutation.isPending.value ? t('profile.signingOut') : t('profile.signOut') }}
            </Button>
          </div>
          <p v-if="logoutMutation.error.value" class="text-sm text-destructive">
            {{ errorMessage(logoutMutation.error.value) }}
          </p>
        </CardContent>
      </Card>
    </template>
  </main>
</template>
