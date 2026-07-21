<script setup lang="ts">
import { Check, RotateCcw, Trash2 } from '@lucide/vue'
import { MARKER_COLORS } from '../../../utils/colors'

defineProps<{
  drawingMode: boolean
  activeZonePointCount: number
  activeZoneColor: string
  drawnZoneCount: number
}>()

const emit = defineEmits<{
  undoZonePoint: []
  finishZone: []
  clearActiveZone: []
  clearZones: []
  updateActiveZoneColor: [color: string]
}>()
</script>

<template>
  <p class="mb-3 text-[11px] text-emerald-300">
    Click the map to place zone corners. Close this panel to stop drawing.
  </p>

  <div class="mb-3 flex items-center justify-between rounded-lg bg-emerald-500/10 px-3 py-1.5 text-[11px]">
    <span class="text-emerald-200">{{ activeZonePointCount }} point{{ activeZonePointCount === 1 ? '' : 's' }} placed</span>
    <span class="text-emerald-400">{{ drawnZoneCount }} zone{{ drawnZoneCount === 1 ? '' : 's' }} total</span>
  </div>

  <div class="grid grid-cols-3 gap-2">
    <button
      type="button"
      class="flex h-10 flex-col items-center justify-center gap-0.5 rounded-xl border border-white/15 bg-white/10 text-slate-200 transition-colors hover:bg-white/15 focus:outline-none focus:ring-2 focus:ring-amber-400 disabled:cursor-not-allowed disabled:opacity-40"
      :disabled="activeZonePointCount === 0"
      aria-label="Undo last zone point"
      title="Undo last point"
      @click="emit('undoZonePoint')"
    >
      <RotateCcw class="h-4 w-4" aria-hidden="true" />
      <span class="text-[9px]">Undo</span>
    </button>
    <button
      type="button"
      class="flex h-10 flex-col items-center justify-center gap-0.5 rounded-xl border border-white/15 bg-emerald-600 text-white transition-colors hover:bg-emerald-500 focus:outline-none focus:ring-2 focus:ring-emerald-400 disabled:cursor-not-allowed disabled:opacity-40"
      :disabled="activeZonePointCount < 3"
      aria-label="Finish zone"
      title="Finish zone (need ≥ 3 points)"
      @click="emit('finishZone')"
    >
      <Check class="h-4 w-4" aria-hidden="true" />
      <span class="text-[9px]">Save</span>
    </button>
    <button
      type="button"
      class="flex h-10 flex-col items-center justify-center gap-0.5 rounded-xl border border-white/15 bg-white/10 text-rose-300 transition-colors hover:bg-rose-500/20 focus:outline-none focus:ring-2 focus:ring-rose-400 disabled:cursor-not-allowed disabled:opacity-40"
      :disabled="activeZonePointCount === 0"
      aria-label="Clear current zone draft"
      title="Discard this draft"
      @click="emit('clearActiveZone')"
    >
      <Trash2 class="h-4 w-4" aria-hidden="true" />
      <span class="text-[9px]">Discard</span>
    </button>
  </div>

  <div class="mt-3">
    <span class="mb-1.5 block text-[10px] font-semibold uppercase tracking-wider text-slate-400">Zone color</span>
    <div class="flex flex-wrap items-center gap-1.5">
      <button
        v-for="c in MARKER_COLORS"
        :key="`active-zone-${c}`"
        type="button"
        class="h-5 w-5 rounded-full border transition-all duration-150 hover:scale-110"
        :class="activeZoneColor === c ? 'scale-110 border-white ring-1 ring-emerald-400/50' : 'border-transparent'"
        :style="{ backgroundColor: c }"
        :aria-label="`Use ${c} for new zone`"
        :title="c"
        @click="emit('updateActiveZoneColor', c)"
      />
    </div>
  </div>

  <button
    v-if="drawnZoneCount > 0"
    type="button"
    class="mt-4 w-full rounded-lg border border-rose-500/20 bg-rose-500/10 py-1.5 text-[11px] text-rose-300 transition-colors hover:bg-rose-500/20 focus:outline-none"
    @click="emit('clearZones')"
  >
    Clear all {{ drawnZoneCount }} zone{{ drawnZoneCount === 1 ? '' : 's' }}
  </button>
</template>
