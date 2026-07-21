<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'

import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { getAuthErrorMessage, useVerifyEmail } from '@/features/auth'

const route = useRoute()
const { t } = useI18n()

const uid = computed(() => getSingleQueryValue(route.query.uid))
const token = computed(() => getSingleQueryValue(route.query.token))
const hasVerificationParams = computed(() => Boolean(uid.value && token.value))

const verifyMutation = useVerifyEmail()

const verifyEmail = () => {
  if (!uid.value || !token.value || verifyMutation.isPending.value) {
    return
  }

  verifyMutation.mutate({
    uid,
    token,
  })
}

const statusTitle = computed(() => {
  if (!hasVerificationParams.value) {
    return t('auth.invalidVerificationLink')
  }

  if (verifyMutation.isSuccess.value) {
    return t('auth.emailVerified')
  }

  if (verifyMutation.isError.value) {
    return t('auth.verificationFailed')
  }

  return t('auth.verifyingEmail')
})

const statusDescription = computed(() => {
  if (!hasVerificationParams.value) {
    return t('auth.verificationLinkMissingInfo')
  }

  if (verifyMutation.isSuccess.value) {
    return t('auth.emailConfirmed')
  }

  if (verifyMutation.isError.value) {
    return getAuthErrorMessage(verifyMutation.error.value)
  }

  return t('auth.confirmingAccount')
})

onMounted(verifyEmail)

function getSingleQueryValue(value: unknown) {
  if (Array.isArray(value)) {
    return typeof value[0] === 'string' ? value[0] : ''
  }

  return typeof value === 'string' ? value : ''
}
</script>

<template>
  <div class="flex min-h-full items-center justify-center p-6">
    <Card class="w-full max-w-md">
      <CardHeader class="space-y-2 text-center">
        <CardTitle class="text-2xl font-bold">
          {{ statusTitle }}
        </CardTitle>

        <CardDescription>
          {{ statusDescription }}
        </CardDescription>
      </CardHeader>

      <CardContent class="space-y-4">
        <Button
          v-if="verifyMutation.isError.value && hasVerificationParams"
          type="button"
          variant="outline"
          class="w-full"
          :disabled="verifyMutation.isPending.value"
          @click="verifyEmail"
        >
          {{ t('common.tryAgain') }}
        </Button>

        <Button as-child class="w-full">
          <RouterLink to="/login">{{ t('auth.login') }}</RouterLink>
        </Button>
      </CardContent>
    </Card>
  </div>
</template>
