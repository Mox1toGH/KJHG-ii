<script setup lang="ts">
import { ref, watch, computed } from 'vue'
import { X, Trash2, Crosshair, Map } from '@lucide/vue'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import type { Checkpoint, Route, RoutePoint, CreateRoutePointPayload } from '@/features/checkpoints'
import { MARKER_COLORS } from '../utils/colors'

const props = defineProps<{
  kind: 'checkpoint' | 'route'
  checkpoint?: Checkpoint | null
  route?: Route | null
  checkpoints: Checkpoint[]
  pickingCoordFor?: string | null
  pickedCoord?: { pointId: string; lat: number; lng: number } | null
}>()

const emit = defineEmits<{
  close: []
  saveCheckpoint: [
    payload: {
      id: string
      name: string
      description: string
      radius: number
      color: string
      points: number
    },
  ]
  saveRoute: [
    payload: {
      id: string
      name: string
      description: string
      color: string
      main_checkpoint: string
      main_checkpoint_points: number
      points: (CreateRoutePointPayload & { id?: string })[]
    },
  ]

  uploadPhotos: [payload: { id: string; kind: 'checkpoint' | 'route_point'; files: File[] }]
  deletePhoto: [payload: { id: string; kind: 'checkpoint' | 'route_point'; photoId: number }]
  startPickingCoord: [pointId: string]
}>()

const name = ref(
  props.kind === 'checkpoint' ? (props.checkpoint?.name ?? '') : (props.route?.name ?? ''),
)
const description = ref(
  props.kind === 'checkpoint'
    ? (props.checkpoint?.description ?? '')
    : (props.route?.description ?? ''),
)
const color = ref(
  props.kind === 'checkpoint'
    ? (props.checkpoint?.color ?? '#9333EA')
    : (props.route?.color ?? '#8B5CF6'),
)
const radius = ref(props.checkpoint?.radius ?? 50)
const checkpointPoints = ref(props.checkpoint?.points ?? 0)
const mainCheckpointPoints = ref(
  props.route
    ? (props.checkpoints.find((c) => c.id === props.route?.main_checkpoint)?.points ?? 0)
    : 0,
)
const mainCheckpoint = ref(props.route?.main_checkpoint ?? '')
const points = ref<RoutePoint[]>(
  props.route?.points.map((p) => ({ ...p, photos: [...(p.photos ?? [])] })) ?? [],
)

watch(
  () => props.route?.points,
  (newPoints) => {
    if (!newPoints) return
    points.value = points.value.map((existing) => {
      const updated = newPoints.find((p) => p.id === existing.id)
      if (updated) return { ...existing, photos: [...(updated.photos ?? [])] }
      return existing
    })
  },
  { deep: true },
)

watch(
  () => props.pickedCoord,
  (coord) => {
    if (!coord) return
    const point = points.value.find((p) => p.id === coord.pointId)
    if (point) {
      point.latitude = coord.lat
      point.longitude = coord.lng
    }
  },
)
const availableCheckpoints = computed(() => props.checkpoints)

const selectedMainCheckpointObj = computed(
  () => props.checkpoints.find((c) => c.id === mainCheckpoint.value) ?? null,
)

function save() {
  if (props.kind === 'checkpoint' && props.checkpoint) {
    emit('saveCheckpoint', {
      id: props.checkpoint.id,
      name: name.value.trim(),
      description: description.value.trim(),
      radius: radius.value,
      color: color.value,
      points: checkpointPoints.value,
    })
  } else if (props.route) {
    emit('saveRoute', {
      id: props.route.id,
      name: name.value.trim(),
      description: description.value.trim(),
      color: color.value,
      main_checkpoint: mainCheckpoint.value,
      main_checkpoint_points: mainCheckpointPoints.value,
      points: points.value.map((point, index) => ({
        id: point.id.startsWith('new-') ? undefined : point.id,
        sequence_number: index + 1,
        name: point.name,
        description: point.description,
        latitude: point.latitude,
        longitude: point.longitude,
        radius: point.radius,
        points: point.points ?? 0,
      })),
    })
  }
}

function filesChanged(event: Event, kind: 'checkpoint' | 'route_point', id?: string) {
  if (!id) return
  const files = Array.from((event.target as HTMLInputElement).files ?? [])
  if (files.length) emit('uploadPhotos', { id, kind, files })
  ;(event.target as HTMLInputElement).value = ''
}
</script>

<template>
  <div
    class="absolute inset-0 z-[70] flex items-center justify-center bg-black/50 p-4 transition-opacity duration-200"
    :class="pickingCoordFor ? 'opacity-0 pointer-events-none' : 'opacity-100'"
    @click.self="emit('close')"
  >
    <div
      class="max-h-[90vh] w-full max-w-lg overflow-y-auto rounded-2xl bg-slate-950 p-5 text-white shadow-2xl"
    >
      <div class="mb-4 flex items-center justify-between">
        <h2 class="font-semibold">Edit {{ kind === 'checkpoint' ? 'checkpoint' : 'route' }}</h2>
        <button class="rounded p-1 text-slate-400 hover:text-white" @click="emit('close')">
          <X class="size-4" />
        </button>
      </div>

      <div class="space-y-3">
        <label class="block text-xs text-slate-300"
          >Name<input v-model="name" class="mt-1 w-full rounded-lg bg-white/10 px-3 py-2 text-sm"
        /></label>
        <label class="block text-xs text-slate-300"
          >Description<textarea
            v-model="description"
            rows="2"
            class="mt-1 w-full rounded-lg bg-white/10 px-3 py-2 text-sm"
          />
        </label>
        <div class="text-xs text-slate-300">
          Color
          <div class="mt-2 flex flex-wrap gap-2">
            <button
              v-for="option in MARKER_COLORS"
              :key="option"
              type="button"
              class="h-7 w-7 rounded-full border-2 transition-transform"
              :class="color === option ? 'scale-110 border-white' : 'border-transparent'"
              :style="{ backgroundColor: option }"
              :aria-label="`Use ${option}`"
              @click="color = option"
            />
          </div>
        </div>

        <!-- CHECKPOINT mode -->
        <template v-if="kind === 'checkpoint'">
          <label class="block text-xs text-slate-300"
            >Radius (m)<input
              v-model.number="radius"
              type="number"
              min="1"
              class="mt-1 w-full rounded-lg bg-white/10 px-3 py-2 text-sm"
          /></label>
          <label class="block text-xs text-slate-300"
            >Points<input
              v-model.number="checkpointPoints"
              type="number"
              min="0"
              class="mt-1 w-full rounded-lg bg-white/10 px-3 py-2 text-sm"
          /></label>
          <label class="block text-xs text-slate-300"
            >Attach photos<input
              type="file"
              accept="image/*"
              multiple
              class="mt-1 block w-full text-xs"
              @change="filesChanged($event, 'checkpoint', checkpoint?.id)"
          /></label>
          <div v-if="checkpoint?.photos?.length" class="grid grid-cols-3 gap-2">
            <div v-for="photo in checkpoint.photos" :key="photo.id" class="relative">
              <img :src="photo.image" alt="Photo" class="h-20 w-full rounded object-cover" />
              <button
                type="button"
                class="absolute top-0.5 right-0.5 rounded bg-rose-600/80 p-0.5 text-white hover:bg-rose-500"
                @click="
                  emit('deletePhoto', { id: checkpoint!.id, kind: 'checkpoint', photoId: photo.id })
                "
              >
                <Trash2 class="size-3" />
              </button>
              <span
                v-if="photo.is_main"
                class="absolute bottom-0.5 left-0.5 rounded bg-emerald-600/80 px-1 text-[10px] text-white"
                >Main</span
              >
            </div>
          </div>
        </template>

        <!-- ROUTE mode -->
        <template v-if="kind === 'route'">
          <!-- Main checkpoint section -->
          <div class="rounded-lg border border-white/10 bg-white/5 p-3 space-y-2">
            <div class="text-xs font-semibold text-slate-300">Main checkpoint</div>
            <Select v-model="mainCheckpoint">
              <SelectTrigger class="w-full rounded-lg border-white/10 bg-white/10 text-white">
                <SelectValue placeholder="Choose checkpoint" />
              </SelectTrigger>
              <SelectContent class="z-[100] border-white/10 bg-slate-950 text-white">
                <SelectItem v-for="cp in availableCheckpoints" :key="cp.id" :value="cp.id">
                  {{ cp.name }}
                </SelectItem>
              </SelectContent>
            </Select>
            <template v-if="selectedMainCheckpointObj">
              <label class="block text-xs text-slate-400 mt-2"
                >Points for main checkpoint
                <input
                  v-model.number="mainCheckpointPoints"
                  type="number"
                  min="0"
                  class="mt-1 w-full rounded-lg bg-white/10 px-3 py-2 text-sm"
                />
              </label>
              <label class="block text-xs text-slate-400 mt-2"
                >Photos for main checkpoint
                <input
                  type="file"
                  accept="image/*"
                  multiple
                  class="mt-1 block w-full text-xs"
                  @change="filesChanged($event, 'checkpoint', selectedMainCheckpointObj?.id)"
                />
              </label>
              <div
                v-if="selectedMainCheckpointObj.photos?.length"
                class="grid grid-cols-3 gap-2 mt-1"
              >
                <div
                  v-for="photo in selectedMainCheckpointObj.photos"
                  :key="photo.id"
                  class="relative"
                >
                  <img
                    :src="photo.image"
                    alt="Main checkpoint photo"
                    class="h-20 w-full rounded object-cover"
                  />
                  <button
                    type="button"
                    class="absolute top-0.5 right-0.5 rounded bg-rose-600/80 p-0.5 text-white hover:bg-rose-500"
                    @click="
                      emit('deletePhoto', {
                        id: selectedMainCheckpointObj!.id,
                        kind: 'checkpoint',
                        photoId: photo.id,
                      })
                    "
                  >
                    <Trash2 class="size-3" />
                  </button>
                  <span
                    v-if="photo.is_main"
                    class="absolute bottom-0.5 left-0.5 rounded bg-emerald-600/80 px-1 text-[10px] text-white"
                    >Main</span
                  >
                </div>
              </div>
            </template>
          </div>

          <!-- Route points -->
          <div class="text-xs font-semibold text-slate-300 mb-1">Route points</div>

          <div
            v-for="(point, index) in points"
            :key="point.id"
            class="space-y-2 rounded-lg border border-white/10 p-3"
          >
            <div class="text-xs text-slate-400">Point {{ index + 1 }}</div>
            <input
              v-model="point.name"
              placeholder="Name"
              class="w-full rounded bg-white/10 px-2 py-1 text-xs"
            />
            <textarea
              v-model="point.description"
              rows="2"
              placeholder="Description"
              class="w-full rounded bg-white/10 px-2 py-1 text-xs"
            />
            <div class="flex gap-1 items-center">
              <input
                v-model.number="point.latitude"
                type="number"
                step="any"
                placeholder="Lat"
                class="flex-1 min-w-0 rounded bg-white/10 px-2 py-1 text-xs"
              />
              <input
                v-model.number="point.longitude"
                type="number"
                step="any"
                placeholder="Lon"
                class="flex-1 min-w-0 rounded bg-white/10 px-2 py-1 text-xs"
              />
              <button
                type="button"
                class="shrink-0 rounded px-2 py-1 text-xs font-medium transition-colors flex items-center gap-1"
                :class="
                  pickingCoordFor === point.id
                    ? 'bg-amber-500 text-white animate-pulse'
                    : 'bg-blue-700 hover:bg-blue-600 text-white'
                "
                @click="emit('startPickingCoord', point.id)"
              >
                <Crosshair v-if="pickingCoordFor === point.id" class="size-3" />
                <Map v-else class="size-3" />
                {{ pickingCoordFor === point.id ? 'Cancel' : 'Pick' }}
              </button>
            </div>
            <input
              v-model.number="point.radius"
              type="number"
              min="1"
              placeholder="Radius (m)"
              class="w-full rounded bg-white/10 px-2 py-1 text-xs"
            />
            <input
              v-model.number="point.points"
              type="number"
              min="0"
              placeholder="Points"
              class="w-full rounded bg-white/10 px-2 py-1 text-xs"
            />
            <template v-if="!point.id.startsWith('new-')">
              <label class="block text-xs text-slate-400 mt-2"
                >Photos<input
                  type="file"
                  accept="image/*"
                  multiple
                  class="mt-1 block w-full text-xs"
                  @change="filesChanged($event, 'route_point', point.id)"
              /></label>
              <div v-if="point.photos?.length" class="grid grid-cols-3 gap-2 mt-1">
                <div v-for="photo in point.photos" :key="photo.id" class="relative">
                  <img :src="photo.image" alt="Photo" class="h-20 w-full rounded object-cover" />
                  <button
                    type="button"
                    class="absolute top-0.5 right-0.5 rounded bg-rose-600/80 p-0.5 text-white hover:bg-rose-500"
                    @click="
                      emit('deletePhoto', { id: point.id, kind: 'route_point', photoId: photo.id })
                    "
                  >
                    <Trash2 class="size-3" />
                  </button>
                  <span
                    v-if="photo.is_main"
                    class="absolute bottom-0.5 left-0.5 rounded bg-emerald-600/80 px-1 text-[10px] text-white"
                    >Main</span
                  >
                </div>
              </div>
            </template>
            <div v-else class="text-xs text-slate-400 mt-2 italic">
              Save route first to attach photos to this point
            </div>
          </div>
        </template>
      </div>

      <div class="mt-5 flex justify-end gap-2">
        <button class="rounded-lg bg-slate-700 px-3 py-2 text-sm" @click="emit('close')">
          Cancel
        </button>
        <button
          class="rounded-lg bg-blue-600 px-3 py-2 text-sm"
          :disabled="!name.trim()"
          @click="save"
        >
          Save
        </button>
      </div>
    </div>
  </div>
</template>
