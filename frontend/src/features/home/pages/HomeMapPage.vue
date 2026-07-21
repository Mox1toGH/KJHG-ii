<script setup lang="ts">
import { ArrowLeft } from '@lucide/vue'
import 'maplibre-gl/dist/maplibre-gl.css'
import HomeMapView from './HomePage.vue'
</script>

<template>
  <div class="relative min-h-screen">
    <HomeMapView />
    <RouterLink
      to="/"
      aria-label="Back to home"
      class="absolute left-4 top-4 z-40 inline-flex size-11 items-center justify-center rounded-full border border-white/30 bg-slate-950/75 text-white shadow-lg backdrop-blur transition hover:bg-slate-950 focus:outline-none focus:ring-2 focus:ring-white/80"
    >
      <ArrowLeft class="size-5" aria-hidden="true" />
    </RouterLink>
  </div>
</template>
