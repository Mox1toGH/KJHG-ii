<script setup lang="ts">
defineProps<{
  title: string
}>()

const emit = defineEmits<{
  close: []
}>()
</script>

<template>
  <div
    class="w-64 rounded-2xl border border-white/15 bg-slate-950/80 p-4 text-white shadow-2xl shadow-slate-950/20 backdrop-blur-xl"
  >
    <div class="mb-3 flex items-center justify-between gap-3">
      <span class="text-[10px] font-semibold uppercase tracking-[0.18em] text-slate-400">{{
        title
      }}</span>
      <button
        type="button"
        class="text-slate-400 transition-colors hover:text-white"
        aria-label="Close panel"
        @click="emit('close')"
      >
        ✕
      </button>
    </div>
    <slot />
  </div>
</template>
