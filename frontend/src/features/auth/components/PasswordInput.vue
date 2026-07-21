<script setup lang="ts">
import { ref, type HTMLAttributes } from 'vue'
import { Eye, EyeOff } from '@lucide/vue'

import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'

defineOptions({
  inheritAttrs: false,
})

const props = defineProps<{
  modelValue?: string | number
  class?: HTMLAttributes['class']
}>()

const emit = defineEmits<{
  (event: 'update:modelValue', value: string | number): void
}>()

const isVisible = ref(false)
</script>

<template>
  <div class="relative">
    <Input
      v-bind="$attrs"
      :model-value="props.modelValue"
      :type="isVisible ? 'text' : 'password'"
      :class="['pr-10', props.class]"
      @update:model-value="emit('update:modelValue', $event)"
    />

    <Button
      type="button"
      variant="ghost"
      size="icon-sm"
      class="absolute top-1/2 right-1 -translate-y-1/2 text-muted-foreground hover:text-foreground"
      :aria-label="isVisible ? 'Hide password' : 'Show password'"
      :title="isVisible ? 'Hide password' : 'Show password'"
      @click="isVisible = !isVisible"
    >
      <EyeOff v-if="isVisible" />
      <Eye v-else />
    </Button>
  </div>
</template>
