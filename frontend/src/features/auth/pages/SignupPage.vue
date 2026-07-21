<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'

import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { getAuthErrorMessage, useRegister, validateSignupForm } from '@/features/auth'
import PasswordInput from '../components/PasswordInput.vue'

const { t } = useI18n()
const router = useRouter()

const username = ref('')
const email = ref('')
const firstName = ref('')
const lastName = ref('')
const password = ref('')
const confirmPassword = ref('')
const passwordMismatch = ref(false)
const fieldErrors = ref<Record<string, string>>({})

const registerMutation = useRegister({
  onSuccess: () => {
    router.push('/login')
  },
})

const signupError = computed(() => {
  if (passwordMismatch.value) {
    return 'Passwords do not match.'
  }

  return getAuthErrorMessage(registerMutation.error.value)
})

const signup = () => {
  const validation = validateSignupForm({
    firstName: firstName.value,
    lastName: lastName.value,
    username: username.value,
    email: email.value,
    password: password.value,
    confirmPassword: confirmPassword.value,
  })

  fieldErrors.value = validation.errors
  passwordMismatch.value = password.value !== confirmPassword.value

  if (!validation.success || passwordMismatch.value) {
    return
  }

  registerMutation.mutate({
    username: username.value,
    email: email.value,
    first_name: firstName.value,
    last_name: lastName.value,
    password: password.value,
  })
}
</script>

<template>
  <div class="flex min-h-full items-center justify-center p-6">
    <Card class="w-full max-w-md">
      <CardHeader class="space-y-2 text-center">
        <CardTitle class="text-2xl font-bold">{{ t('auth.signup') }}</CardTitle>

        <CardDescription>
          {{ t('auth.email') }}
        </CardDescription>
      </CardHeader>

      <CardContent class="space-y-6">
        <form class="space-y-4" @submit.prevent="signup">
          <div class="grid gap-4 sm:grid-cols-2">
            <div class="space-y-2">
              <Label for="firstName">{{ t('auth.firstName') }}</Label>

              <Input
                id="firstName"
                v-model="firstName"
                type="text"
                autocomplete="given-name"
                :class="fieldErrors.firstName ? 'border-destructive' : ''"
              />
              <p v-if="fieldErrors.firstName" class="text-sm text-destructive">
                {{ fieldErrors.firstName }}
              </p>
            </div>

            <div class="space-y-2">
              <Label for="lastName">{{ t('auth.lastName') }}</Label>

              <Input
                id="lastName"
                v-model="lastName"
                type="text"
                autocomplete="family-name"
                :class="fieldErrors.lastName ? 'border-destructive' : ''"
              />
              <p v-if="fieldErrors.lastName" class="text-sm text-destructive">
                {{ fieldErrors.lastName }}
              </p>
            </div>
          </div>

          <div class="space-y-2">
            <Label for="username">{{ t('auth.username') }}</Label>

            <Input
              id="username"
              v-model="username"
              type="text"
              placeholder="username"
              autocomplete="username"
              :class="fieldErrors.username ? 'border-destructive' : ''"
              required
            />
            <p v-if="fieldErrors.username" class="text-sm text-destructive">
              {{ fieldErrors.username }}
            </p>
          </div>

          <div class="space-y-2">
            <Label for="email">{{ t('auth.email') }}</Label>

            <Input
              id="email"
              v-model="email"
              type="email"
              placeholder="name@example.com"
              autocomplete="email"
              :class="fieldErrors.email ? 'border-destructive' : ''"
              required
            />
            <p v-if="fieldErrors.email" class="text-sm text-destructive">
              {{ fieldErrors.email }}
            </p>
          </div>

          <div class="space-y-2">
            <Label for="password">{{ t('auth.password') }}</Label>

            <PasswordInput
              id="password"
              v-model="password"
              autocomplete="new-password"
              :class="fieldErrors.password ? 'border-destructive' : ''"
              required
            />
            <p v-if="fieldErrors.password" class="text-sm text-destructive">
              {{ fieldErrors.password }}
            </p>
          </div>

          <div class="space-y-2">
            <Label for="confirmPassword">{{ t('auth.password') }}</Label>

            <PasswordInput
              id="confirmPassword"
              v-model="confirmPassword"
              autocomplete="new-password"
              :class="fieldErrors.confirmPassword ? 'border-destructive' : ''"
              required
            />
            <p v-if="fieldErrors.confirmPassword" class="text-sm text-destructive">
              {{ fieldErrors.confirmPassword }}
            </p>
          </div>

          <p v-if="signupError" class="text-sm text-destructive">
            {{ signupError }}
          </p>

          <Button type="submit" class="w-full" :disabled="registerMutation.isPending.value">
            {{ registerMutation.isPending.value ? t('common.loading') : t('auth.signup') }}
          </Button>
        </form>

        <p class="text-center text-sm text-muted-foreground">
          {{ t('auth.login') }}?
          <RouterLink
            to="/login"
            class="font-medium text-foreground underline-offset-4 hover:underline"
          >
            {{ t('auth.login') }}
          </RouterLink>
        </p>
      </CardContent>
    </Card>
  </div>
</template>
