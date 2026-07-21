<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'

import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { getAuthErrorMessage, useGoogleLogin, useLogin } from '@/features/auth'
import PasswordInput from '../components/PasswordInput.vue'
import { renderGoogleButton, type GoogleCredentialResponse } from '@/lib/googleAuth'

const { t } = useI18n()

const identifier = ref('')
const password = ref('')
const router = useRouter()
const googleButtonRef = ref<HTMLDivElement | null>(null)
const googleErrorMessage = ref('')

const loginMutation = useLogin({
  onSuccess: () => {
    router.push((router.currentRoute.value.query.redirect as string) || '/')
  },
})

const googleLoginMutation = useGoogleLogin({
  onSuccess: () => {
    router.push((router.currentRoute.value.query.redirect as string) || '/')
  },
})

const login = () => {
  loginMutation.mutate({
    identifier: identifier.value,
    password: password.value,
  })
}

const handleGoogleCredential = (response: GoogleCredentialResponse) => {
  if (!response?.credential) {
    googleErrorMessage.value = 'Google did not return a credential token.'
    return
  }

  googleErrorMessage.value = ''
  googleLoginMutation.mutate({ credential: response.credential })
}

onMounted(async () => {
  try {
    if (!googleButtonRef.value) {
      throw new Error('Google button container is not mounted.')
    }

    await renderGoogleButton({
      container: googleButtonRef.value,
      clientId: import.meta.env.VITE_GOOGLE_CLIENT_ID ?? '',
      callback: handleGoogleCredential,
      width: 200,
    })
  } catch (error) {
    googleErrorMessage.value =
      (error instanceof Error && error.message) || 'Google auth initialization failed.'
  }
})

const loginError = computed(() => getAuthErrorMessage(loginMutation.error.value))
const googleLoginError = computed(() => getAuthErrorMessage(googleLoginMutation.error.value))
</script>

<template>
  <div class="flex min-h-full items-center justify-center p-6">
    <Card class="w-full max-w-md">
      <CardHeader class="space-y-2 text-center">
        <CardTitle class="text-2xl font-bold">{{ t('auth.login') }}</CardTitle>

        <CardDescription>{{ t('auth.email') }} {{ t('common.or') }} {{ t('auth.username') }}</CardDescription>
      </CardHeader>

      <CardContent class="space-y-6">
        <form class="space-y-4" @submit.prevent="login">
          <div class="space-y-2">
            <Label for="identifier">{{ t('auth.email') }} {{ t('common.or') }} {{ t('auth.username') }}</Label>

            <Input
              id="identifier"
              v-model="identifier"
              type="text"
              placeholder="name@example.com"
              autocomplete="username"
              required
            />
          </div>

          <div class="space-y-2">
            <Label for="password">{{ t('auth.password') }}</Label>

            <PasswordInput
              id="password"
              v-model="password"
              placeholder="••••••••"
              autocomplete="current-password"
              required
            />
          </div>

          <p v-if="loginError" class="text-sm text-destructive">
            {{ loginError }}
          </p>

          <Button type="submit" class="w-full" :disabled="loginMutation.isPending.value">
            {{ loginMutation.isPending.value ? t('common.loading') : t('auth.login') }}
          </Button>
        </form>

        <div class="relative">
          <div class="absolute inset-0 flex items-center">
            <span class="w-full border-t" />
          </div>

          <div class="relative flex justify-center text-xs uppercase">
            <span class="px-2 text-muted-foreground">{{ t('common.or') }} {{ t('auth.login') }}</span>
          </div>
        </div>

        <div class="space-y-2">
          <div class="flex justify-center">
            <div ref="googleButtonRef" class="google-slot" />
          </div>

          <p v-if="googleLoginError || googleErrorMessage" class="text-sm text-destructive">
            {{ googleLoginError || googleErrorMessage }}
          </p>
        </div>

        <p class="text-center text-sm text-muted-foreground">
          {{ t('auth.signup') }}?
          <RouterLink
            to="/signup"
            class="font-medium text-foreground underline-offset-4 hover:underline"
          >
            {{ t('auth.signup') }}
          </RouterLink>
        </p>
      </CardContent>
    </Card>
  </div>
</template>
