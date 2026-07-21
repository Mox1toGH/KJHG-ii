<script setup lang="ts">
import { computed } from 'vue'
import type { Checkpoint } from '../core/checkpoint.types'
import CheckpointQrManager from './CheckpointQrManager.vue'
import type { UserLocation } from '@/composables/useUserLocation'

const props = defineProps<{
  checkpoint: Checkpoint
  currentUserId?: number
  activityOwnerId?: number
  location: UserLocation | null
}>()
const emit = defineEmits<{ close: []; progressChanged: [] }>()

const canManage = computed(() =>
  props.currentUserId !== undefined && (
    props.checkpoint.created_by === props.currentUserId || props.activityOwnerId === props.currentUserId
  ),
)
</script>

<template>
  <div class="absolute inset-0 z-80 flex items-center justify-center bg-black/65 p-4" @click.self="emit('close')">
    <div class="max-h-[90vh] w-full max-w-xl overflow-y-auto rounded-2xl border border-white/10 bg-slate-950 p-5 text-white shadow-2xl">
      <div class="flex items-start justify-between gap-4">
        <div>
          <p class="text-xs font-medium uppercase tracking-wider text-purple-300">Checkpoint</p>
          <h2 class="mt-1 text-xl font-bold">{{ checkpoint.name }}</h2>
          <p v-if="checkpoint.description" class="mt-1 text-sm text-slate-400">{{ checkpoint.description }}</p>
        </div>
        <button type="button" class="rounded-lg px-2 py-1 text-slate-400 hover:bg-white/10 hover:text-white" aria-label="Close checkpoint" @click="emit('close')">✕</button>
      </div>

      <div class="mt-5 rounded-xl border border-emerald-400/20 bg-emerald-500/5 px-4 py-3">
        <p class="text-xs uppercase tracking-wider text-emerald-300">Progress</p>
        <p class="mt-1 text-2xl font-bold text-white">{{ checkpoint.qr_progress.scanned }} / {{ checkpoint.qr_progress.total }}</p>
      </div>

      <CheckpointQrManager
        :checkpoint-id="checkpoint.id"
        :checkpoint-name="checkpoint.name"
        :can-manage="canManage"
        :location="location"
        @progress-changed="emit('progressChanged')"
      />
    </div>
  </div>
</template>
