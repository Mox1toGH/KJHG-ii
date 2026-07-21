<script setup lang="ts">
import BottomNav from '@/components/BottomNav.vue'
import SosAlertBanner from '@/components/SosAlertBanner.vue'
import NotificationCenter from '@/features/notifications/components/NotificationCenter.vue'
</script>

<template>
  <div class="min-h-screen bg-background">
    <RouterView />
    <SosAlertBanner />
    <BottomNav />
    <NotificationCenter />
  </div>
</template>
