<script setup lang="ts">
defineProps<{
  status: string
}>()
</script>

<template>
  <div class="flex items-center justify-between gap-3 text-sm">
    <span class="text-slate-300">Current status</span>
    <span class="flex items-center gap-1.5 text-[11px] font-medium text-emerald-300">
      <span class="h-1.5 w-1.5 rounded-full bg-emerald-400 shadow-[0_0_8px_#34d399]" />
      {{ status }}
    </span>
  </div>
</template>
