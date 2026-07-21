<script setup lang="ts">
import { ref, watch } from 'vue'
import { ArrowLeft, UserRound } from '@lucide/vue'
import { useRouter } from 'vue-router'

import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { getAuthErrorMessage, useChangePassword, useUpdateProfile, useCurrentUser } from '@/features/auth'
import PasswordInput from '../components/PasswordInput.vue'

const router = useRouter()
const userQuery = useCurrentUser()
const form = ref({ username: '', email: '', first_name: '', last_name: '' })
const selectedAvatar = ref<File | undefined>()
const avatarPreview = ref<string | null>(null)
const currentPassword = ref('')
const newPassword = ref('')
const confirmPassword = ref('')
const passwordMismatch = ref(false)

watch(
  userQuery.data,
  (user) => {
    if (!user) return
    form.value = {
      username: user.username,
      email: user.email,
      first_name: user.first_name,
      last_name: user.last_name,
    }
  },
  { immediate: true },
)

watch(
  userQuery.error,
  (error) => {
    const status = (error as { response?: { status?: number } })?.response?.status
    if (status === 401) router.replace({ path: '/login', query: { redirect: '/profile/edit' } })
  },
  { immediate: true },
)

const errorMessage = (error: unknown) => {
  const data = (error as { response?: { data?: Record<string, unknown> } })?.response?.data
  if (data?.detail && typeof data.detail === 'string') return data.detail
  if (data) {
    const firstError = Object.values(data).flat()[0]
    if (typeof firstError === 'string') return firstError
  }
  return error instanceof Error ? error.message : 'Something went wrong.'
}

const updateMutation = useUpdateProfile({
  onSuccess: () => router.push('/profile'),
})
const passwordMutation = useChangePassword()

const saveProfile = () => {
  updateMutation.mutate({
    username: form.value.username.trim(),
    email: form.value.email.trim(),
    first_name: form.value.first_name.trim(),
    last_name: form.value.last_name.trim(),
    avatar: selectedAvatar.value,
  })
}

const selectAvatar = (event: Event) => {
  const file = (event.target as HTMLInputElement).files?.[0]
  if (!file) return
  selectedAvatar.value = file
  avatarPreview.value = URL.createObjectURL(file)
}

const changePassword = () => {
  passwordMismatch.value = newPassword.value !== confirmPassword.value
  if (passwordMismatch.value) return

  passwordMutation.mutate({
    current_password: currentPassword.value,
    new_password: newPassword.value,
  })
}
</script>

<template>
  <main class="mx-auto max-w-2xl px-4 py-8 sm:px-6 lg:py-12">
    <Button variant="ghost" class="mb-5 -ml-3" @click="router.push('/profile')">
      <ArrowLeft class="mr-2 size-4" /> Back to profile
    </Button>

    <Card>
      <CardHeader>
        <CardTitle>Edit profile</CardTitle>
        <CardDescription>Update your basic account information.</CardDescription>
      </CardHeader>
      <CardContent v-if="userQuery.isPending.value" class="text-muted-foreground">
        Loading your profile...
      </CardContent>
      <CardContent v-else-if="userQuery.error.value" class="text-destructive">
        {{ errorMessage(userQuery.error.value) }}
      </CardContent>
      <CardContent v-else class="space-y-5">
        <form class="space-y-5" @submit.prevent="saveProfile">
          <div class="flex items-center gap-4">
            <div
              class="size-20 shrink-0 overflow-hidden rounded-2xl bg-primary text-primary-foreground"
            >
              <img
                v-if="avatarPreview || userQuery.data.value?.avatar"
                :src="avatarPreview || userQuery.data.value?.avatar || undefined"
                alt="Profile avatar"
                class="size-full object-cover"
              />
              <UserRound v-else class="m-5 size-10" aria-hidden="true" />
            </div>
            <div class="space-y-2">
              <Label for="profile-avatar">Avatar</Label>
              <Input id="profile-avatar" type="file" accept="image/*" @change="selectAvatar" />
              <p class="text-xs text-muted-foreground">
                Choose an image to use as your profile avatar.
              </p>
            </div>
          </div>
          <div class="grid gap-5 sm:grid-cols-2">
            <div class="space-y-2">
              <Label for="profile-first-name">First name</Label>
              <Input id="profile-first-name" v-model="form.first_name" autocomplete="given-name" />
            </div>
            <div class="space-y-2">
              <Label for="profile-last-name">Last name</Label>
              <Input id="profile-last-name" v-model="form.last_name" autocomplete="family-name" />
            </div>
          </div>
          <div class="space-y-2">
            <Label for="profile-username">Username</Label>
            <Input id="profile-username" v-model="form.username" autocomplete="username" required />
          </div>
          <div class="space-y-2">
            <Label for="profile-email">Email</Label>
            <Input
              id="profile-email"
              v-model="form.email"
              type="email"
              autocomplete="email"
              required
            />
            <p class="text-xs text-muted-foreground">
              Changing your email will require verification again.
            </p>
          </div>
          <p v-if="updateMutation.error.value" class="text-sm text-destructive">
            {{ errorMessage(updateMutation.error.value) }}
          </p>
          <div class="flex flex-col gap-3 sm:flex-row sm:justify-end">
            <Button type="button" variant="outline" @click="router.push('/profile')">Cancel</Button>
            <Button type="submit" :disabled="updateMutation.isPending.value">
              {{ updateMutation.isPending.value ? 'Saving...' : 'Save changes' }}
            </Button>
          </div>
        </form>

        <div class="border-t border-border pt-5">
          <h2 class="font-semibold">Change password</h2>
          <p class="mt-1 text-sm text-muted-foreground">
            Update your password or recover it if you do not know the current one.
          </p>
          <form class="mt-5 space-y-5" @submit.prevent="changePassword">
            <div class="space-y-2">
              <Label for="current-password">Current password</Label
              ><PasswordInput
                id="current-password"
                v-model="currentPassword"
                autocomplete="current-password"
                required
              />
            </div>
            <div class="space-y-2">
              <Label for="new-password">New password</Label
              ><PasswordInput
                id="new-password"
                v-model="newPassword"
                autocomplete="new-password"
                required
              />
            </div>
            <div class="space-y-2">
              <Label for="confirm-password">Confirm new password</Label
              ><PasswordInput
                id="confirm-password"
                v-model="confirmPassword"
                autocomplete="new-password"
                required
              />
            </div>
            <p v-if="passwordMismatch" class="text-sm text-destructive">Passwords do not match.</p>
            <p v-if="passwordMutation.error.value" class="text-sm text-destructive">
              {{ getAuthErrorMessage(passwordMutation.error.value) }}
            </p>
            <div class="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
              <Button as-child variant="link" class="justify-start px-0"
                ><RouterLink to="/password/forgot"
                  >I don't know my current password</RouterLink
                ></Button
              >
              <Button type="submit" :disabled="passwordMutation.isPending.value">{{
                passwordMutation.isPending.value ? 'Changing password...' : 'Change password'
              }}</Button>
            </div>
          </form>
        </div>
      </CardContent>
    </Card>
  </main>
</template>
