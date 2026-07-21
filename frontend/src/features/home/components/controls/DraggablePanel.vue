<script setup lang="ts">
import { nextTick, ref, watch, onMounted, onBeforeUnmount } from 'vue'

const props = defineProps<{
  title: string
  initialX?: number
  initialY?: number
  zIndex?: number
  collapsed?: boolean
}>()

const emit = defineEmits<{
  close: []
  focus: []
  'update:collapsed': [value: boolean]
}>()

const panelEl = ref<HTMLDivElement | null>(null)
const x = ref(0)
const y = ref(0)
const isDragging = ref(false)

const localCollapsed = ref(props.collapsed ?? false)

watch(
  () => props.collapsed,
  (val) => {
    if (val !== undefined) localCollapsed.value = val
  },
)

watch(localCollapsed, (val) => {
  emit('update:collapsed', val)
})

const isCollapsed = localCollapsed

let startMouseX = 0
let startMouseY = 0
let startX = 0
let startY = 0

function clamp() {
  if (!panelEl.value) return
  const vw = window.innerWidth
  const vh = window.innerHeight
  const { offsetWidth, offsetHeight } = panelEl.value
  const margin = 8

  x.value = Math.max(margin, Math.min(x.value, vw - offsetWidth - margin))
  y.value = Math.max(margin, Math.min(y.value, vh - offsetHeight - margin))
}

function onPointerDown(e: PointerEvent) {
  if ((e.target as HTMLElement).closest('[data-drag-handle]') === null) return
  isDragging.value = true
  startMouseX = e.clientX
  startMouseY = e.clientY
  startX = x.value
  startY = y.value

  const el = e.currentTarget as HTMLElement
  el.setPointerCapture(e.pointerId)
  emit('focus')
}

function onPointerMove(e: PointerEvent) {
  if (!isDragging.value) return
  if (!panelEl.value) return

  const vw = window.innerWidth
  const vh = window.innerHeight
  const { offsetWidth, offsetHeight } = panelEl.value
  const margin = 8

  const rawX = startX + (e.clientX - startMouseX)
  const rawY = startY + (e.clientY - startMouseY)

  x.value = Math.max(margin, Math.min(rawX, vw - offsetWidth - margin))
  y.value = Math.max(margin, Math.min(rawY, vh - offsetHeight - margin))
}

function onPointerUp(e: PointerEvent) {
  isDragging.value = false
  const el = e.currentTarget as HTMLElement
  try {
    el.releasePointerCapture(e.pointerId)
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
  } catch (err) {
    // Ignore if not captured
  }
}

function handleKeyDown(e: KeyboardEvent) {
  if (e.key === 'Escape') {
    emit('close')
  }
}

onMounted(async () => {
  x.value = props.initialX ?? 0
  y.value = props.initialY ?? 0
  await nextTick()
  clamp()
  window.addEventListener('resize', clamp)
  window.addEventListener('keydown', handleKeyDown)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', clamp)
  window.removeEventListener('keydown', handleKeyDown)
})
</script>

<template>
  <div
    ref="panelEl"
    class="fixed w-64 select-none rounded-2xl border bg-slate-950/90 text-white shadow-2xl backdrop-blur-xl transition-[opacity,transform,border-color,box-shadow] duration-200"
    :class="[
      isDragging
        ? 'opacity-75 scale-[0.98] border-blue-500/40 shadow-blue-500/10'
        : 'border-white/15 shadow-slate-950/40 hover:border-white/25',
      isCollapsed ? 'pb-0' : '',
    ]"
    :style="{ left: `${x}px`, top: `${y}px`, zIndex: zIndex ?? 52 }"
    @pointerdown="emit('focus')"
    @click="emit('focus')"
  >
    <div
      data-drag-handle
      class="flex cursor-grab items-center justify-between gap-2 rounded-t-2xl border-b border-white/5 px-4 py-2.5 active:cursor-grabbing touch-none select-none"
      @pointerdown="onPointerDown"
      @pointermove="onPointerMove"
      @pointerup="onPointerUp"
    >
      <div class="flex items-center gap-2 pointer-events-none select-none">
        <svg
          class="h-3.5 w-2.5 shrink-0 text-slate-500"
          viewBox="0 0 10 14"
          fill="currentColor"
          aria-hidden="true"
        >
          <circle cx="2" cy="2" r="1.2" />
          <circle cx="8" cy="2" r="1.2" />
          <circle cx="2" cy="7" r="1.2" />
          <circle cx="8" cy="7" r="1.2" />
          <circle cx="2" cy="12" r="1.2" />
          <circle cx="8" cy="12" r="1.2" />
        </svg>
        <span class="text-[10px] font-semibold uppercase tracking-[0.18em] text-slate-400">
          {{ title }}
        </span>
      </div>

      <div class="flex items-center gap-0.5">
        <button
          type="button"
          class="flex h-6 w-6 items-center justify-center rounded-lg text-slate-500 transition-colors hover:bg-white/10 hover:text-white"
          :aria-label="isCollapsed ? 'Expand panel' : 'Collapse panel'"
          @pointerdown.stop
          @click.stop="isCollapsed = !isCollapsed"
        >
          <svg
            class="h-3 w-3 transition-transform duration-200"
            :class="isCollapsed ? 'rotate-180' : ''"
            viewBox="0 0 12 12"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
          >
            <polyline points="2 4 6 8 10 4" />
          </svg>
        </button>

        <button
          type="button"
          class="flex h-6 w-6 items-center justify-center rounded-lg text-slate-500 transition-colors hover:bg-white/10 hover:text-white"
          aria-label="Close panel"
          @pointerdown.stop
          @click.stop="emit('close')"
        >
          <svg
            class="h-2.5 w-2.5"
            viewBox="0 0 12 12"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
          >
            <line x1="1" y1="1" x2="11" y2="11" />
            <line x1="11" y1="1" x2="1" y2="11" />
          </svg>
        </button>
      </div>
    </div>

    <div
      v-show="!isCollapsed"
      class="max-h-[min(26rem,calc(100dvh-9rem))] overflow-y-auto overscroll-contain px-4 py-3"
    >
      <slot />
    </div>
  </div>
</template>
