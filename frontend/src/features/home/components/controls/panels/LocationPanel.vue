<script setup lang="ts">
import type { LocationStatus } from '@/composables/useUserLocation'

defineProps<{
  locationError: string | null
  locationStatus: LocationStatus
}>()
</script>

<template>
  <div v-if="locationError" class="text-xs leading-relaxed text-rose-100" role="status">
    {{ locationError }}
  </div>
  <div v-else class="flex items-center justify-between gap-3 text-sm">
    <span class="text-slate-300">Tracking status</span>
    <span class="text-[11px] font-medium capitalize text-blue-300">{{ locationStatus }}</span>
  </div>
</template>
