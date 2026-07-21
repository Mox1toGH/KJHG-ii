<script setup lang="ts">
const emit = defineEmits<{
  locate: []
}>()
</script>

<template>
  <button
    class="group inline-flex h-11 w-11 items-center justify-center rounded-2xl border border-white/20 bg-slate-950/80 text-white shadow-2xl shadow-slate-950/30 backdrop-blur-xl transition-all duration-200 hover:scale-105 hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-400 focus:ring-offset-2 focus:ring-offset-transparent active:scale-95"
    aria-label="Locate me"
    title="Locate me"
    @click="emit('locate')"
  >
    <svg
      xmlns="http://www.w3.org/2000/svg"
      class="h-5 w-5 transition-transform duration-200 group-hover:rotate-45"
      viewBox="0 0 20 20"
      fill="currentColor"
    >
      <path
        d="M10 3a1 1 0 011 1v1.07a5 5 0 010 9.86V16a1 1 0 11-2 0v-1.07a5 5 0 010-9.86V4a1 1 0 011-1z"
      />
    </svg>
  </button>
</template>
