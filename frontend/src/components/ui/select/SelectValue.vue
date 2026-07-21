<script setup lang="ts">
import { SelectValue } from 'reka-ui'

defineProps<{
  placeholder?: string
}>()
</script>

<template>
  <SelectValue :placeholder="placeholder" />
</template>
