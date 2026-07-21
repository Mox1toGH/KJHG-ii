<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Label } from '@/components/ui/label'
import { getAuthErrorMessage, useConfirmPasswordReset } from '@/features/auth'
import PasswordInput from '../components/PasswordInput.vue'

const route = useRoute()
const router = useRouter()
const newPassword = ref('')
const confirmPassword = ref('')
const mismatch = ref(false)
const uid = computed(() => getQueryValue(route.query.uid))
const token = computed(() => getQueryValue(route.query.token))
const mutation = useConfirmPasswordReset({ onSuccess: () => router.replace('/login') })

const submit = () => {
  mismatch.value = newPassword.value !== confirmPassword.value
  if (mismatch.value || !uid.value || !token.value) return
  mutation.mutate({ uid: uid.value, token: token.value, new_password: newPassword.value })
}

function getQueryValue(value: unknown) {
  return Array.isArray(value)
    ? typeof value[0] === 'string'
      ? value[0]
      : ''
    : typeof value === 'string'
      ? value
      : ''
}
</script>

<template>
  <div class="flex min-h-full items-center justify-center p-6">
    <Card class="w-full max-w-md">
      <CardHeader class="space-y-2 text-center"
        ><CardTitle>Set a new password</CardTitle
        ><CardDescription>Choose a new password for your account.</CardDescription></CardHeader
      >
      <CardContent>
        <form class="space-y-5" @submit.prevent="submit">
          <div class="space-y-2">
            <Label for="reset-password">New password</Label
            ><PasswordInput
              id="reset-password"
              v-model="newPassword"
              autocomplete="new-password"
              required
            />
          </div>
          <div class="space-y-2">
            <Label for="reset-confirm-password">Confirm new password</Label
            ><PasswordInput
              id="reset-confirm-password"
              v-model="confirmPassword"
              autocomplete="new-password"
              required
            />
          </div>
          <p v-if="mismatch" class="text-sm text-destructive">Passwords do not match.</p>
          <p v-if="!uid || !token" class="text-sm text-destructive">
            This reset link is invalid or incomplete.
          </p>
          <p v-if="mutation.error.value" class="text-sm text-destructive">
            {{ getAuthErrorMessage(mutation.error.value) }}
          </p>
          <Button
            type="submit"
            class="w-full"
            :disabled="mutation.isPending.value || !uid || !token"
            >{{ mutation.isPending.value ? 'Saving...' : 'Set new password' }}</Button
          >
        </form>
      </CardContent>
    </Card>
  </div>
</template>
