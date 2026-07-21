<script setup lang="ts">
import { SelectRoot } from 'reka-ui'

defineProps<{
  modelValue?: string | null
  disabled?: boolean
}>()

const emit = defineEmits<{
  'update:modelValue': [value: string]
}>()
</script>

<template>
  <SelectRoot
    :model-value="modelValue"
    :disabled="disabled"
    @update:model-value="emit('update:modelValue', $event as string)"
  >
    <slot />
  </SelectRoot>
</template>
