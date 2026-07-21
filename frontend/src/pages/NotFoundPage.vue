<script setup lang="ts">
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { onMounted } from 'vue'
import { Button } from '@/components/ui/button'

const router = useRouter()
const { t } = useI18n()

const goHome = () => {
  router.push('/')
}

const goBack = () => {
  if (window.history.length > 1) {
    router.back()
  } else {
    router.push('/')
  }
}

onMounted(() => {
  document.title = t('notFound.heading')
})
</script>

<template>
  <div class="flex min-h-screen flex-col items-center justify-center bg-background px-4 text-center">
    <div class="mx-auto max-w-md space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-700">
      <!-- SVG Illustration -->
      <div class="relative mx-auto h-64 w-64">
        <svg
          viewBox="0 0 200 200"
          xmlns="http://www.w3.org/2000/svg"
          class="h-full w-full drop-shadow-lg"
          aria-hidden="true"
        >
          <!-- Background circle -->
          <circle cx="100" cy="100" r="90" fill="currentColor" class="text-muted opacity-10" />
          
          <!-- 404 Text -->
          <text
            x="100"
            y="115"
            text-anchor="middle"
            class="text-6xl font-bold"
            fill="currentColor"
            style="font-family: system-ui, sans-serif"
          >
            404
          </text>
          
          <!-- Magnifying glass -->
          <g transform="translate(130, 130)">
            <circle cx="20" cy="20" r="18" fill="none" stroke="currentColor" stroke-width="3" class="text-primary" />
            <line x1="34" y1="34" x2="48" y2="48" stroke="currentColor" stroke-width="3" stroke-linecap="round" class="text-primary" />
            <!-- Question mark inside -->
            <text x="20" y="27" text-anchor="middle" class="text-xl font-bold" fill="currentColor" style="font-family: system-ui, sans-serif">
              ?
            </text>
          </g>
          
          <!-- Decorative elements -->
          <circle cx="40" cy="50" r="4" fill="currentColor" class="text-primary opacity-40" />
          <circle cx="160" cy="60" r="3" fill="currentColor" class="text-primary opacity-30" />
          <circle cx="50" cy="150" r="5" fill="currentColor" class="text-primary opacity-20" />
        </svg>
      </div>

      <!-- Content -->
      <div class="space-y-4">
        <h1 class="text-4xl font-bold tracking-tight text-foreground sm:text-5xl">
          {{ t('notFound.heading') }}
        </h1>
        <p class="text-lg text-muted-foreground">
          {{ t('notFound.description') }}
        </p>
      </div>

      <!-- Actions -->
      <div class="flex flex-col gap-3 sm:flex-row sm:justify-center">
        <Button
          @click="goHome"
          variant="default"
          size="lg"
          class="min-w-[140px]"
          aria-label="Go to home page"
        >
          {{ t('notFound.goHome') }}
        </Button>
        <Button
          @click="goBack"
          variant="outline"
          size="lg"
          class="min-w-[140px]"
          aria-label="Go back to previous page"
        >
          {{ t('notFound.goBack') }}
        </Button>
      </div>
    </div>
  </div>
</template>
