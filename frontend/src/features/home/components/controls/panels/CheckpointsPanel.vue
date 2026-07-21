<script setup lang="ts">
import { MARKER_COLORS } from '../../../utils/colors'

defineProps<{
  drawingMode: 'none' | 'checkpoint' | 'route'
  draftCheckpoint: {
    coordinates: [number, number]
    radius: number
    name: string
    description: string
    color: string
    points: number
  } | null
  draftRoutePoints: {
    id: string
    coordinates: [number, number]
    radius: number
    name: string
    description: string
    color: string
    points: number
  }[]
}>()

const emit = defineEmits<{
  setDrawingMode: [mode: 'none' | 'checkpoint' | 'route']
  updateDraftCheckpoint: [
    payload: { name: string; description: string; radius: number; color: string; points: number },
  ]
  saveCheckpoint: []
  updateDraftRoutePoint: [
    id: string,
    payload: { name: string; description: string; radius: number; color: string; points: number },
  ]
  moveRoutePointUp: [id: string]
  moveRoutePointDown: [id: string]
  deleteRoutePoint: [id: string]
  saveRoute: []
}>()
</script>

<template>
  <div class="space-y-4 text-sm text-slate-200">
    <div v-if="drawingMode === 'none'" class="flex flex-col gap-2">
      <button
        @click="emit('setDrawingMode', 'checkpoint')"
        class="rounded-xl bg-purple-600 px-3 py-2.5 text-xs font-semibold text-white transition-colors hover:bg-purple-500"
      >
        Create Checkpoint
      </button>
      <button
        @click="emit('setDrawingMode', 'route')"
        class="rounded-xl bg-purple-600 px-3 py-2.5 text-xs font-semibold text-white transition-colors hover:bg-purple-500"
      >
        Create Route
      </button>
    </div>

    <div v-else-if="drawingMode === 'checkpoint'" class="flex flex-col gap-3">
      <div class="text-xs text-slate-400 mb-2">
        <span v-if="!draftCheckpoint">Click on the map to place the checkpoint.</span>
        <span v-else>Fill out checkpoint details.</span>
      </div>

      <template v-if="draftCheckpoint">
        <label class="flex flex-col gap-1 text-[11px] font-medium text-slate-300">
          Name
          <input
            type="text"
            :value="draftCheckpoint?.name"
            @input="
              (e) =>
                emit('updateDraftCheckpoint', {
                  name: (e.target as HTMLInputElement).value,
                  description: draftCheckpoint?.description || '',
                  radius: draftCheckpoint?.radius || 50,
                  color: draftCheckpoint?.color || '#9333EA',
                  points: draftCheckpoint?.points ?? 0,
                })
            "
            class="rounded-lg border border-white/10 bg-black/30 px-3 py-2 text-xs text-white placeholder:text-slate-500 focus:border-purple-500 focus:outline-none focus:ring-1 focus:ring-purple-500"
          />
        </label>
        <label class="flex flex-col gap-1 text-[11px] font-medium text-slate-300">
          Description (optional)
          <textarea
            :value="draftCheckpoint?.description"
            @input="
              (e) =>
                emit('updateDraftCheckpoint', {
                  name: draftCheckpoint?.name || '',
                  description: (e.target as HTMLTextAreaElement).value,
                  radius: draftCheckpoint?.radius || 50,
                  color: draftCheckpoint?.color || '#9333EA',
                  points: draftCheckpoint?.points ?? 0,
                })
            "
            class="rounded-lg border border-white/10 bg-black/30 px-3 py-2 text-xs text-white placeholder:text-slate-500 focus:border-purple-500 focus:outline-none focus:ring-1 focus:ring-purple-500 resize-none"
            rows="2"
          />
        </label>
        <label class="flex flex-col gap-1 text-[11px] font-medium text-slate-300">
          Radius (m)
          <input
            type="number"
            :value="draftCheckpoint?.radius"
            @input="
              (e) =>
                emit('updateDraftCheckpoint', {
                  name: draftCheckpoint?.name || '',
                  description: draftCheckpoint?.description || '',
                  radius: Number((e.target as HTMLInputElement).value),
                  color: draftCheckpoint?.color || '#9333EA',
                  points: draftCheckpoint?.points ?? 0,
                })
            "
            class="rounded-lg border border-white/10 bg-black/30 px-3 py-2 text-xs text-white focus:border-purple-500 focus:outline-none focus:ring-1 focus:ring-purple-500"
          />
        </label>
        <label class="flex flex-col gap-1 text-[11px] font-medium text-slate-300">
          Points
          <input
            type="number"
            min="0"
            :value="draftCheckpoint?.points ?? 0"
            @input="
              (e) =>
                emit('updateDraftCheckpoint', {
                  name: draftCheckpoint?.name || '',
                  description: draftCheckpoint?.description || '',
                  radius: draftCheckpoint?.radius || 50,
                  color: draftCheckpoint?.color || '#9333EA',
                  points: Number((e.target as HTMLInputElement).value),
                })
            "
            class="rounded-lg border border-white/10 bg-black/30 px-3 py-2 text-xs text-white focus:border-purple-500 focus:outline-none focus:ring-1 focus:ring-purple-500"
          />
        </label>
        <div class="text-[11px] font-medium text-slate-300">
          Color
          <div class="mt-1 flex flex-wrap gap-2">
            <button
              v-for="option in MARKER_COLORS"
              :key="option"
              type="button"
              class="h-6 w-6 rounded-full border-2"
              :class="
                draftCheckpoint?.color === option ? 'scale-110 border-white' : 'border-transparent'
              "
              :style="{ backgroundColor: option }"
              @click="
                emit('updateDraftCheckpoint', {
                  name: draftCheckpoint?.name || '',
                  description: draftCheckpoint?.description || '',
                  radius: draftCheckpoint?.radius || 50,
                  color: option,
                  points: draftCheckpoint?.points ?? 0,
                })
              "
            />
          </div>
        </div>

        <div class="flex gap-2 mt-2">
          <button
            @click="emit('saveCheckpoint')"
            class="flex-1 rounded-lg bg-blue-600 px-3 py-2 text-xs font-semibold text-white transition-colors hover:bg-blue-500 disabled:opacity-50"
            :disabled="!draftCheckpoint?.name"
          >
            Save
          </button>
          <button
            @click="emit('setDrawingMode', 'none')"
            class="rounded-lg bg-slate-700 px-3 py-2 text-xs font-semibold text-white transition-colors hover:bg-slate-600"
          >
            Cancel
          </button>
        </div>
      </template>
      <button
        v-else
        @click="emit('setDrawingMode', 'none')"
        class="rounded-lg bg-slate-700 px-3 py-2 text-xs font-semibold text-white transition-colors hover:bg-slate-600"
      >
        Cancel
      </button>
    </div>

    <div v-else-if="drawingMode === 'route'" class="flex flex-col gap-3">
      <div class="text-xs text-slate-400 mb-2">
        <span v-if="draftRoutePoints.length === 0"
          >Click on the map to place the Main Checkpoint.</span
        >
        <span v-else>Click on the map to add route points.</span>
      </div>

      <div
        v-if="draftRoutePoints.length > 0"
        class="flex flex-col gap-3 max-h-[300px] overflow-y-auto pr-1"
      >
        <div
          v-for="(point, index) in draftRoutePoints"
          :key="point.id"
          class="rounded-xl border border-white/10 bg-white/5 p-3 flex flex-col gap-2 relative"
        >
          <div class="flex justify-between items-center mb-1">
            <span class="text-xs font-bold text-purple-300">{{
              index === 0 ? 'Main Checkpoint' : 'Route Point ' + index
            }}</span>
            <div class="flex gap-1" v-if="index > 0">
              <button
                @click="emit('moveRoutePointUp', point.id)"
                class="flex h-6 w-6 items-center justify-center rounded bg-white/10 hover:bg-white/20 text-white transition-colors disabled:opacity-30"
                :disabled="index === 1"
              >
                ↑
              </button>
              <button
                @click="emit('moveRoutePointDown', point.id)"
                class="flex h-6 w-6 items-center justify-center rounded bg-white/10 hover:bg-white/20 text-white transition-colors disabled:opacity-30"
                :disabled="index === draftRoutePoints.length - 1"
              >
                ↓
              </button>
              <button
                @click="emit('deleteRoutePoint', point.id)"
                class="flex h-6 w-6 items-center justify-center rounded bg-rose-500/20 hover:bg-rose-500/40 text-rose-300 transition-colors"
              >
                ✕
              </button>
            </div>
          </div>
          <label
            class="flex flex-col gap-1 text-[10px] text-slate-300 uppercase tracking-wider font-semibold"
          >
            Name
            <input
              type="text"
              :value="point.name"
              @input="
                (e) =>
                  emit('updateDraftRoutePoint', point.id, {
                    name: (e.target as HTMLInputElement).value,
                    description: point.description,
                    radius: point.radius,
                    color: point.color,
                    points: point.points ?? 0,
                  })
              "
              :placeholder="index > 0 ? String(index) : 'Main Checkpoint'"
              class="rounded bg-black/40 border border-white/10 px-2 py-1.5 text-xs text-white focus:outline-none focus:border-purple-400 normal-case tracking-normal font-normal"
            />
          </label>
          <label
            class="flex flex-col gap-1 text-[10px] text-slate-300 uppercase tracking-wider font-semibold"
          >
            Description
            <input
              type="text"
              :value="point.description"
              @input="
                (e) =>
                  emit('updateDraftRoutePoint', point.id, {
                    name: point.name,
                    description: (e.target as HTMLInputElement).value,
                    radius: point.radius,
                    color: point.color,
                    points: point.points ?? 0,
                  })
              "
              class="rounded bg-black/40 border border-white/10 px-2 py-1.5 text-xs text-white focus:outline-none focus:border-purple-400 normal-case tracking-normal font-normal"
            />
          </label>
          <label
            class="flex flex-col gap-1 text-[10px] text-slate-300 uppercase tracking-wider font-semibold"
          >
            Radius (m)
            <input
              type="number"
              :value="point.radius"
              @input="
                (e) =>
                  emit('updateDraftRoutePoint', point.id, {
                    name: point.name,
                    description: point.description,
                    radius: Number((e.target as HTMLInputElement).value),
                    color: point.color,
                    points: point.points ?? 0,
                  })
              "
              class="rounded bg-black/40 border border-white/10 px-2 py-1.5 text-xs text-white focus:outline-none focus:border-purple-400 normal-case tracking-normal font-normal"
            />
          </label>
          <label
            class="flex flex-col gap-1 text-[10px] text-slate-300 uppercase tracking-wider font-semibold"
          >
            Points
            <input
              type="number"
              min="0"
              :value="point.points ?? 0"
              @input="
                (e) =>
                  emit('updateDraftRoutePoint', point.id, {
                    name: point.name,
                    description: point.description,
                    radius: point.radius,
                    color: point.color,
                    points: Number((e.target as HTMLInputElement).value),
                  })
              "
              class="rounded bg-black/40 border border-white/10 px-2 py-1.5 text-xs text-white focus:outline-none focus:border-purple-400 normal-case tracking-normal font-normal"
            />
          </label>
          <div class="text-[10px] text-slate-300 uppercase tracking-wider font-semibold">
            Color
            <div class="mt-1 flex flex-wrap gap-2">
              <button
                v-for="option in MARKER_COLORS"
                :key="option"
                type="button"
                class="h-5 w-5 rounded-full border-2"
                :class="point.color === option ? 'scale-110 border-white' : 'border-transparent'"
                :style="{ backgroundColor: option }"
                @click="
                  emit('updateDraftRoutePoint', point.id, {
                    name: point.name,
                    description: point.description,
                    radius: point.radius,
                    color: option,
                    points: point.points ?? 0,
                  })
                "
              />
            </div>
          </div>
        </div>
      </div>

      <div class="flex gap-2 mt-2">
        <button
          v-if="draftRoutePoints.length > 0"
          @click="emit('saveRoute')"
          class="flex-1 rounded-lg bg-blue-600 px-3 py-2 text-xs font-semibold text-white transition-colors hover:bg-blue-500 disabled:opacity-50"
          :disabled="!draftRoutePoints[0]?.name"
        >
          Save Route
        </button>
        <button
          @click="emit('setDrawingMode', 'none')"
          class="rounded-lg bg-slate-700 px-3 py-2 text-xs font-semibold text-white transition-colors hover:bg-slate-600"
        >
          Cancel
        </button>
      </div>
    </div>
  </div>
</template>
