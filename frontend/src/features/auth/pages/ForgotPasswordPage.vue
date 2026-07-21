<script setup lang="ts">
import { ref } from 'vue'

import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { getAuthErrorMessage, useRequestPasswordReset } from '@/features/auth'

const email = ref('')
const sent = ref(false)
const mutation = useRequestPasswordReset({
  onSuccess: () => {
    sent.value = true
  },
})
const submit = () => mutation.mutate({ email: email.value.trim() })
</script>

<template>
  <div class="flex min-h-full items-center justify-center p-6">
    <Card class="w-full max-w-md">
      <CardHeader class="space-y-2 text-center">
        <CardTitle>{{ sent ? 'Check your email' : 'Recover your password' }}</CardTitle>
        <CardDescription>{{
          sent
            ? 'If an account exists for this email, a reset link has been sent.'
            : 'Enter your account email and we will send you a reset link.'
        }}</CardDescription>
      </CardHeader>
      <CardContent v-if="sent" class="space-y-4"
        ><Button as-child class="w-full"
          ><RouterLink to="/login">Back to sign in</RouterLink></Button
        ></CardContent
      >
      <CardContent v-else>
        <form class="space-y-5" @submit.prevent="submit">
          <div class="space-y-2">
            <Label for="recovery-email">Email</Label
            ><Input
              id="recovery-email"
              v-model="email"
              type="email"
              autocomplete="email"
              required
            />
          </div>
          <p v-if="mutation.error.value" class="text-sm text-destructive">
            {{ getAuthErrorMessage(mutation.error.value) }}
          </p>
          <Button type="submit" class="w-full" :disabled="mutation.isPending.value">{{
            mutation.isPending.value ? 'Sending...' : 'Send reset link'
          }}</Button>
        </form>
      </CardContent>
    </Card>
  </div>
</template>
