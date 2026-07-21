<script setup lang="ts">
import type { BaseLayer } from '../../../utils/mapStyles'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import Switch from '@/components/ui/switch/Switch.vue'

const props = defineProps<{
  baseLayer: BaseLayer
  showScratchHexagons: boolean
  showScratchMapToggle: boolean
}>()

const emit = defineEmits<{
  'update:baseLayer': [value: string]
  'update:showScratchHexagons': [value: boolean]
}>()
</script>

<template>
  <Select :model-value="baseLayer" @update:model-value="emit('update:baseLayer', $event as string)">
    <SelectTrigger
      class="flex h-10 w-full items-center justify-between rounded-xl border border-white/15 bg-white/10 px-3 text-sm text-white outline-none transition-colors hover:bg-white/15 focus:ring-2 focus:ring-blue-400"
      aria-label="Base layer"
    >
      <SelectValue placeholder="Choose layer" />
    </SelectTrigger>

    <SelectContent
      position="popper"
      :side-offset="4"
      class="z-[100] rounded-xl border-white/15 bg-slate-950/95 text-white shadow-2xl backdrop-blur-xl"
    >
      <SelectItem
        value="sat"
        class="relative flex cursor-pointer select-none items-center rounded-lg px-3 py-2 text-sm outline-none data-[highlighted]:bg-blue-500/20 data-[highlighted]:text-blue-200"
      >
        Satellite
      </SelectItem>
      <SelectItem
        value="carto"
        class="relative flex cursor-pointer select-none items-center rounded-lg px-3 py-2 text-sm outline-none data-[highlighted]:bg-blue-500/20 data-[highlighted]:text-blue-200"
      >
        Carto
      </SelectItem>
      <SelectItem
        value="osm"
        class="relative flex cursor-pointer select-none items-center rounded-lg px-3 py-2 text-sm outline-none data-[highlighted]:bg-blue-500/20 data-[highlighted]:text-blue-200"
      >
        OpenStreetMap
      </SelectItem>
    </SelectContent>
  </Select>

  <div
    v-if="props.showScratchMapToggle"
    class="mt-4 flex items-center justify-between gap-3 border-t border-white/10 pt-4"
  >
    <div>
      <p class="text-sm font-medium text-white">Show Hexagons</p>
      <p class="mt-0.5 text-xs text-slate-400">Display discovered map cells</p>
    </div>
    <Switch
      :checked="props.showScratchHexagons"
      aria-label="Show Hexagons"
      @update:checked="emit('update:showScratchHexagons', $event)"
    />
  </div>
</template>
