<script setup lang="ts">
import {
  CalendarClock,
  Flag,
  Info,
  Layers,
  List,
  MapPin,
  Menu,
  Ruler,
  Shapes,
  Trophy,
  Users,
  X,
} from '@lucide/vue'
import { ref, computed, nextTick, onBeforeUnmount, watch } from 'vue'
import type { ActivePanelKey } from './types'

const props = defineProps<{
  openPanels: Set<ActivePanelKey>
  hasActivity: boolean
  hasLocationError: boolean
  measurementModeActive: boolean
}>()

const emit = defineEmits<{
  toggle: [key: ActivePanelKey]
}>()

const isCollapsed = ref(true)

function isOpen(key: ActivePanelKey) {
  return props.openPanels.has(key)
}

const hasActivePanels = computed(() => props.openPanels.size > 0)

// --- scroll fade indicators ---
const scrollListEl = ref<HTMLElement | null>(null)
const canScrollUp = ref(false)
const canScrollDown = ref(false)

function updateScrollFade() {
  const node = scrollListEl.value
  if (!node) return
  const { scrollTop, scrollHeight, clientHeight } = node
  canScrollUp.value = scrollTop > 1
  canScrollDown.value = scrollTop + clientHeight < scrollHeight - 1
}

let resizeObserver: ResizeObserver | null = null

function attachScrollListeners(node: HTMLElement) {
  node.addEventListener('scroll', updateScrollFade, { passive: true })
  resizeObserver = new ResizeObserver(updateScrollFade)
  resizeObserver.observe(node)
  updateScrollFade()
}

function detachScrollListeners(node: HTMLElement) {
  node.removeEventListener('scroll', updateScrollFade)
  resizeObserver?.disconnect()
  resizeObserver = null
}

watch(isCollapsed, async (collapsed) => {
  if (!collapsed) {
    await nextTick()
    if (scrollListEl.value) attachScrollListeners(scrollListEl.value)
  } else if (scrollListEl.value) {
    detachScrollListeners(scrollListEl.value)
  }
})

onBeforeUnmount(() => {
  if (scrollListEl.value) detachScrollListeners(scrollListEl.value)
})
</script>

<template>
  <div
    class="flex flex-col items-stretch rounded-2xl border border-white/15 bg-slate-950/80 shadow-2xl shadow-slate-950/20 backdrop-blur-xl transition-all duration-300"
  >
    <button
      type="button"
      class="relative flex h-11 w-11 m-2 shrink-0 items-center justify-center rounded-xl transition-colors focus:outline-none focus:ring-2 focus:ring-blue-400"
      :class="!isCollapsed ? 'bg-white/10 text-white' : 'text-slate-300 hover:bg-white/10'"
      :aria-label="isCollapsed ? 'Expand menu' : 'Collapse menu'"
      :title="isCollapsed ? 'Expand menu' : 'Collapse menu'"
      @click="isCollapsed = !isCollapsed"
    >
      <component :is="isCollapsed ? Menu : X" class="h-5 w-5" aria-hidden="true" />

      <span
        v-if="isCollapsed && (hasActivePanels || hasLocationError || measurementModeActive)"
        class="absolute right-2 top-2 h-2 w-2 rounded-full ring-2 ring-slate-950"
        :class="
          hasLocationError ? 'bg-rose-400' : measurementModeActive ? 'bg-sky-400' : 'bg-blue-500'
        "
        aria-hidden="true"
      />
    </button>

    <Transition
      enter-active-class="transition-all duration-300 ease-out-back"
      leave-active-class="transition-all duration-200 ease-in-quad"
      enter-from-class="opacity-0 max-h-0 translate-y-[-10px] scale-95"
      enter-to-class="opacity-100 max-h-[450px] translate-y-0 scale-100"
      leave-from-class="opacity-100 max-h-[450px] translate-y-0 scale-100"
      leave-to-class="opacity-0 max-h-0 translate-y-[-10px] scale-95"
    >
      <div
        v-if="!isCollapsed"
        class="flex flex-col items-center gap-2 overflow-hidden border-t border-white/5"
      >
        <div class="relative w-full overflow-hidden rounded-b-2xl">
          <!-- top scroll fade -->
          <div
            class="pointer-events-none absolute inset-x-0 top-0 z-10 h-6 bg-linear-to-b from-white/25 to-transparent transition-opacity duration-200"
            :class="canScrollUp ? 'opacity-100' : 'opacity-0'"
            aria-hidden="true"
          />

          <div
            ref="scrollListEl"
            class="flex flex-col w-full items-center gap-2 max-h-[calc(100dvh-16.5rem)] overflow-y-auto overscroll-contain scrollbar-none [&::-webkit-scrollbar]:hidden py-2"
          >
            <button
              type="button"
              class="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl transition-colors focus:outline-none focus:ring-2 focus:ring-blue-400"
              :class="
                isOpen('status') ? 'bg-blue-600 text-white' : 'text-slate-300 hover:bg-white/10'
              "
              aria-label="Map status"
              title="Map status"
              @click="emit('toggle', 'status')"
            >
              <Info class="h-5 w-5" aria-hidden="true" />
            </button>

            <button
              type="button"
              class="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl transition-colors focus:outline-none focus:ring-2 focus:ring-blue-400"
              :class="[
                isOpen('location') ? 'bg-blue-600 text-white' : 'text-slate-300 hover:bg-white/10',
                hasLocationError && !isOpen('location') ? 'text-rose-300' : '',
              ]"
              aria-label="Your location"
              title="Your location"
              @click="emit('toggle', 'location')"
            >
              <MapPin class="h-5 w-5" aria-hidden="true" />
            </button>

            <button
              v-if="hasActivity"
              type="button"
              class="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl transition-colors focus:outline-none focus:ring-2 focus:ring-blue-400"
              :class="
                isOpen('participants')
                  ? 'bg-blue-600 text-white'
                  : 'text-slate-300 hover:bg-white/10'
              "
              aria-label="Participants"
              title="Participants"
              @click="emit('toggle', 'participants')"
            >
              <Users class="h-5 w-5" aria-hidden="true" />
            </button>

            <button
              v-if="hasActivity"
              type="button"
              class="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl transition-colors focus:outline-none focus:ring-2 focus:ring-orange-400"
              :class="
                isOpen('meetingPoints')
                  ? 'bg-orange-600 text-white'
                  : 'text-slate-300 hover:bg-white/10'
              "
              aria-label="Meeting points"
              title="Meeting points"
              @click="emit('toggle', 'meetingPoints')"
            >
              <CalendarClock class="h-5 w-5" aria-hidden="true" />
            </button>

            <button
              type="button"
              class="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl transition-colors focus:outline-none focus:ring-2 focus:ring-blue-400"
              :class="
                isOpen('layer') ? 'bg-blue-600 text-white' : 'text-slate-300 hover:bg-white/10'
              "
              aria-label="Base layer"
              title="Base layer"
              @click="emit('toggle', 'layer')"
            >
              <Layers class="h-5 w-5" aria-hidden="true" />
            </button>

            <button
              type="button"
              class="relative flex h-11 w-11 shrink-0 items-center justify-center rounded-xl transition-colors focus:outline-none focus:ring-2 focus:ring-sky-400"
              :class="
                isOpen('measurement') ? 'bg-sky-500 text-white' : 'text-slate-300 hover:bg-white/10'
              "
              aria-label="Measure distance"
              title="Measure distance"
              @click="emit('toggle', 'measurement')"
            >
              <Ruler class="h-5 w-5" aria-hidden="true" />
              <span
                v-if="measurementModeActive"
                class="absolute right-1.5 top-1.5 h-1.5 w-1.5 rounded-full bg-sky-400 shadow-[0_0_6px_#38bdf8]"
                aria-hidden="true"
              />
            </button>

            <button
              type="button"
              class="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl transition-colors focus:outline-none focus:ring-2 focus:ring-emerald-400"
              :class="
                isOpen('zones') ? 'bg-emerald-600 text-white' : 'text-slate-300 hover:bg-white/10'
              "
              aria-label="Draw zone"
              title="Draw zone"
              @click="emit('toggle', 'zones')"
            >
              <Shapes class="h-5 w-5" aria-hidden="true" />
            </button>

            <button
              type="button"
              class="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl transition-colors focus:outline-none focus:ring-2 focus:ring-emerald-400"
              :class="
                isOpen('zonesList')
                  ? 'bg-emerald-700 text-white'
                  : 'text-slate-300 hover:bg-white/10'
              "
              aria-label="Zone list"
              title="Zone list"
              @click="emit('toggle', 'zonesList')"
            >
              <List class="h-5 w-5" aria-hidden="true" />
            </button>

            <button
              v-if="hasActivity"
              type="button"
              class="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl transition-colors focus:outline-none focus:ring-2 focus:ring-purple-400"
              :class="
                isOpen('checkpoints')
                  ? 'bg-purple-600 text-white'
                  : 'text-slate-300 hover:bg-white/10'
              "
              aria-label="Checkpoints"
              title="Checkpoints"
              @click="emit('toggle', 'checkpoints')"
            >
              <Flag class="h-5 w-5" aria-hidden="true" />
            </button>

            <button
              v-if="hasActivity"
              type="button"
              class="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl transition-colors focus:outline-none focus:ring-2 focus:ring-amber-400"
              :class="
                isOpen('activity') ? 'bg-amber-600 text-white' : 'text-slate-300 hover:bg-white/10'
              "
              aria-label="Activity"
              title="Activity"
              @click="emit('toggle', 'activity')"
            >
              <Trophy class="h-5 w-5" aria-hidden="true" />
            </button>
          </div>

          <!-- bottom scroll fade -->
          <div
            class="pointer-events-none absolute inset-x-0 bottom-0 z-10 h-6 bg-linear-to-t from-white/25 to-transparent transition-opacity duration-200"
            :class="canScrollDown ? 'opacity-100' : 'opacity-0'"
            aria-hidden="true"
          />
        </div>
      </div>
    </Transition>
  </div>
</template>
