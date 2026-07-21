<script setup lang="ts">
import { computed } from 'vue'
import { Ruler, Trash2, X } from '@lucide/vue'
import {
  formatDistance,
  type MeasurementPoint,
} from '@/features/measurements/core/measurement.utils'

const props = defineProps<{
  measurementMode: boolean
  measurementPoints: MeasurementPoint[]
  measurementSegmentDistances: number[]
  measurementTotalDistance: number
}>()

const emit = defineEmits<{
  toggleMeasurementMode: []
  clearMeasurements: []
  removeMeasurementPoint: [id: string]
}>()

const measurementTotalLabel = computed(() => formatDistance(props.measurementTotalDistance))
</script>

<template>
  <div class="mb-3 flex items-center justify-between gap-3">
    <span class="text-[11px] text-slate-400">Total distance</span>
    <span class="text-[11px] font-medium text-sky-300">{{ measurementTotalLabel }}</span>
  </div>
  <p class="mb-3 text-[11px] text-sky-200">
    Click the map to add points. Drag a point to adjust it.
  </p>
  <div v-if="measurementPoints.length" class="mt-3 space-y-1.5">
    <div
      v-for="(point, index) in measurementPoints"
      :key="point.id"
      class="flex items-center gap-2 rounded-lg bg-white/5 px-2 py-1.5 text-xs"
    >
      <span
        class="flex size-5 shrink-0 items-center justify-center rounded-full bg-sky-500 text-[10px] font-bold"
        >{{ index + 1 }}</span
      >
      <span class="min-w-0 flex-1 truncate text-slate-300"
        >{{ point.coordinates[1].toFixed(5) }}, {{ point.coordinates[0].toFixed(5) }}</span
      >
      <span v-if="index > 0" class="shrink-0 text-sky-200">{{
        formatDistance(measurementSegmentDistances[index - 1] ?? 0)
      }}</span>
      <button
        type="button"
        class="rounded p-1 text-slate-400 hover:bg-white/10 hover:text-rose-200"
        :aria-label="`Remove measurement point ${index + 1}`"
        @click="emit('removeMeasurementPoint', point.id)"
      >
        <X class="size-3.5" aria-hidden="true" />
      </button>
    </div>
    <button
      type="button"
      class="mt-2 inline-flex h-8 w-full items-center justify-center gap-1 rounded-lg bg-rose-600/80 text-xs font-medium hover:bg-rose-500 disabled:opacity-40"
      :disabled="!measurementPoints.length"
      @click="emit('clearMeasurements')"
    >
      <Trash2 class="size-3.5" aria-hidden="true" />
      Clear measurements
    </button>
  </div>
</template>
