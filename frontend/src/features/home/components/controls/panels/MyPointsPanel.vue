<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { ShoppingBag } from '@lucide/vue'
import { Button } from '@/components/ui/button'
import type { ActivityPoint } from '@/features/checkpoints'

const props = defineProps<{
  myPoints?: number
  activityPoints?: ActivityPoint[]
  activityId?: string
}>()

const router = useRouter()

function goToShop() {
  if (props.activityId) {
    router.push({ name: 'activity-shop', params: { activityId: props.activityId } })
  }
}
</script>

<template>
  <div class="space-y-4 text-sm text-slate-200">
    <div
      v-if="myPoints !== undefined"
      class="rounded-xl border border-amber-400/20 bg-amber-500/10 px-3 py-2"
    >
      <div class="text-[11px] font-semibold uppercase tracking-wider text-amber-300">
        Your Points
      </div>
      <div class="text-lg font-bold text-amber-100">{{ myPoints }}</div>
    </div>

    <div
      v-if="activityPoints?.length"
      class="rounded-xl border border-white/10 bg-white/5 px-3 py-2"
    >
      <div class="mb-2 text-[11px] font-semibold uppercase tracking-wider text-slate-400">
        Leaderboard
      </div>
      <div class="max-h-28 space-y-1 overflow-y-auto">
        <div
          v-for="(entry, index) in activityPoints"
          :key="entry.id"
          class="flex items-center justify-between gap-2 text-xs"
        >
          <span class="truncate text-slate-300">{{ index + 1 }}. {{ entry.display_name }}</span>
          <span class="shrink-0 font-semibold text-amber-200">{{ entry.points }}</span>
        </div>
      </div>
    </div>

    <Button
      v-if="activityId"
      variant="outline"
      class="w-full"
      @click="goToShop"
    >
      <ShoppingBag class="mr-2 size-4" /> Shop
    </Button>
  </div>
</template>
