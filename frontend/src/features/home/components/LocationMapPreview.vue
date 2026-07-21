<script setup lang="ts">
import { computed } from 'vue'
import { Expand } from '@lucide/vue'
import { useRouter } from 'vue-router'
import { useUserLocation } from '@/composables/useUserLocation'
import { useCurrentUser } from '@/features/auth'
import { useLocationPreviewMap } from '../composables/useLocationPreviewMap'

const router = useRouter()
const { position, startTracking } = useUserLocation()
const currentUserQuery = useCurrentUser()
const avatar = computed(() => currentUserQuery.data.value?.avatar)
const { mapContainer } = useLocationPreviewMap(position, avatar, startTracking)
</script>

<template>
  <button
    type="button"
    class="group relative block h-64 w-full overflow-hidden rounded-2xl border border-border bg-muted text-left shadow-sm transition hover:shadow-md focus:outline-none focus:ring-2 focus:ring-ring sm:h-72"
    aria-label="Open fullscreen map"
    @click="router.push({ name: 'home-map' })"
  >
    <div ref="mapContainer" class="h-full w-full" aria-hidden="true" />
    <div
      class="pointer-events-none absolute inset-0 bg-gradient-to-t from-slate-950/45 via-transparent to-transparent"
    />
    <div
      class="pointer-events-none absolute bottom-4 left-4 flex items-center gap-2 text-sm font-medium text-white drop-shadow"
    >
      <span class="size-2 rounded-full bg-blue-400 ring-4 ring-blue-400/20" />
      Your location
    </div>
    <span
      class="pointer-events-none absolute right-4 top-4 rounded-full bg-background/90 p-2 text-foreground shadow-sm transition group-hover:scale-105"
    >
      <Expand class="size-4" aria-hidden="true" />
    </span>
  </button>
</template>
