<script setup lang="ts">
import { Trash2 } from '@lucide/vue'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import type { DrawnZoneSummary } from '../../../composables/useHomeMap'
import type { ActivityRole } from '@/features/activities/core/activity.types'
import { MARKER_COLORS } from '../../../utils/colors'

defineProps<{
  drawnZoneCount: number
  drawnZones: DrawnZoneSummary[]
  roles: ActivityRole[]
}>()

const emit = defineEmits<{
  updateZoneColor: [payload: { id: string; color: string }]
  updateZoneName: [payload: { id: string; name: string }]
  updateZoneTrigger: [
    payload: {
      id: string
      trigger_action: 'no_action' | 'on_exit' | 'on_entry'
      trigger_subject_role: string | null
      trigger_notify_role: string | null
    },
  ]
  deleteZone: [id: string]
}>()
</script>

<template>
  <div class="mb-3 flex items-center justify-between gap-3 border-b border-white/5 pb-2">
    <span class="text-[11px] text-slate-400">Total zones</span>
    <span class="text-[11px] font-medium text-emerald-300">{{ drawnZoneCount }}</span>
  </div>

  <div v-if="!drawnZones.length" class="py-4 text-center text-xs text-slate-500">
    No zones defined yet.
  </div>

  <div v-else class="max-h-[min(20rem,calc(100dvh-10rem))] space-y-2.5 overflow-y-auto pr-1">
    <details
      v-for="zone in drawnZones"
      :key="zone.id"
      class="group rounded-xl border border-white/10 bg-black/20 px-3 py-2 transition-colors hover:border-white/20"
    >
      <summary
        class="flex cursor-pointer list-none items-center justify-between gap-2 text-xs text-slate-100 focus:outline-none"
      >
        <span class="flex min-w-0 items-center gap-2">
          <span class="h-3 w-3 shrink-0 rounded-full" :style="{ backgroundColor: zone.color }" />
          <span class="truncate font-medium">{{ zone.name }}</span>
        </span>
        <span class="shrink-0 text-[10px] text-slate-500 group-open:hidden">
          {{ zone.pointCount }} pts · Settings
        </span>
        <span class="hidden shrink-0 text-[10px] text-emerald-400 group-open:inline">
          Collapse
        </span>
      </summary>

      <div class="mt-3 space-y-3 border-t border-white/5 pt-2.5">
        <label
          class="flex flex-col gap-1 text-[10px] font-semibold uppercase tracking-wider text-slate-400"
        >
          Zone Name
          <input
            :value="zone.name"
            type="text"
            class="mt-1 w-full rounded-lg border border-white/10 bg-black/30 px-2.5 py-1.5 text-xs text-white placeholder:text-slate-500 focus:border-emerald-500 focus:outline-none focus:ring-1 focus:ring-emerald-500"
            placeholder="Zone name..."
            @click.stop
            @keydown.enter.prevent="
              emit('updateZoneName', {
                id: zone.id,
                name: ($event.target as HTMLInputElement).value,
              })
            "
            @blur="
              emit('updateZoneName', {
                id: zone.id,
                name: ($event.target as HTMLInputElement).value,
              })
            "
          />
        </label>

        <div class="flex flex-col gap-1">
          <span class="text-[10px] font-semibold uppercase tracking-wider text-slate-400"
            >Zone Color</span
          >
          <div class="mt-1 flex flex-wrap gap-1.5">
            <button
              v-for="c in MARKER_COLORS"
              :key="`${zone.id}-${c}`"
              type="button"
              class="h-5 w-5 rounded-full border border-transparent transition-all duration-150 hover:scale-110"
              :class="zone.color === c ? 'scale-115 border-white ring-1 ring-emerald-500/50' : ''"
              :style="{ backgroundColor: c }"
              :aria-label="`Set ${zone.name} color to ${c}`"
              :title="c"
              @click="emit('updateZoneColor', { id: zone.id, color: c })"
            />
          </div>
        </div>

        <div class="flex flex-col gap-2 border-t border-white/5 pt-2">
          <span class="text-[10px] font-semibold uppercase tracking-wider text-slate-400"
            >Geofence Triggers</span
          >

          <label class="flex flex-col gap-1 text-xs text-slate-300">
            Action
            <Select
              :model-value="zone.trigger_action"
              @update:model-value="
                emit('updateZoneTrigger', {
                  id: zone.id,
                  trigger_action: $event as any,
                  trigger_subject_role: zone.trigger_subject_role,
                  trigger_notify_role: zone.trigger_notify_role,
                })
              "
            >
              <SelectTrigger class="h-8 rounded-lg border-white/10 bg-black/30 text-xs text-white">
                <SelectValue />
              </SelectTrigger>
              <SelectContent class="z-[100] border-white/10 bg-slate-950 text-white">
                <SelectItem value="no_action">No Action</SelectItem>
                <SelectItem value="on_entry">On Entry</SelectItem>
                <SelectItem value="on_exit">On Exit</SelectItem>
              </SelectContent>
            </Select>
          </label>

          <label
            v-if="zone.trigger_action !== 'no_action'"
            class="flex flex-col gap-1 text-xs text-slate-300"
          >
            Subject Role (Who enters/exits)
            <Select
              :model-value="zone.trigger_subject_role || '__none'"
              @update:model-value="
                emit('updateZoneTrigger', {
                  id: zone.id,
                  trigger_action: zone.trigger_action,
                  trigger_subject_role: $event === '__none' ? null : $event,
                  trigger_notify_role: zone.trigger_notify_role,
                })
              "
            >
              <SelectTrigger class="h-8 rounded-lg border-white/10 bg-black/30 text-xs text-white">
                <SelectValue />
              </SelectTrigger>
              <SelectContent class="z-[100] border-white/10 bg-slate-950 text-white">
                <SelectItem value="__none">-- None (Everyone) --</SelectItem>
                <SelectItem v-for="role in roles" :key="role.id" :value="role.id">{{
                  role.name
                }}</SelectItem>
              </SelectContent>
            </Select>
          </label>

          <label
            v-if="zone.trigger_action !== 'no_action'"
            class="flex flex-col gap-1 text-xs text-slate-300"
          >
            Notify Role (Who is notified)
            <Select
              :model-value="zone.trigger_notify_role || '__none'"
              @update:model-value="
                emit('updateZoneTrigger', {
                  id: zone.id,
                  trigger_action: zone.trigger_action,
                  trigger_subject_role: zone.trigger_subject_role,
                  trigger_notify_role: $event === '__none' ? null : $event,
                })
              "
            >
              <SelectTrigger class="h-8 rounded-lg border-white/10 bg-black/30 text-xs text-white">
                <SelectValue />
              </SelectTrigger>
              <SelectContent class="z-[100] border-white/10 bg-slate-950 text-white">
                <SelectItem value="__none">-- None --</SelectItem>
                <SelectItem v-for="role in roles" :key="role.id" :value="role.id">{{
                  role.name
                }}</SelectItem>
              </SelectContent>
            </Select>
          </label>
        </div>

        <button
          type="button"
          class="mt-1 inline-flex h-8 w-full items-center justify-center gap-1.5 rounded-lg bg-red-600/80 text-xs font-medium text-white transition-colors hover:bg-red-500 focus:outline-none"
          @click="emit('deleteZone', zone.id)"
        >
          <Trash2 class="size-3.5" />
          Delete zone
        </button>
      </div>
    </details>
  </div>
</template>
