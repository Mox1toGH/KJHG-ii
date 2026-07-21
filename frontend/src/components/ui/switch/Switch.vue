<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  checked?: boolean
  disabled?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  checked: false,
  disabled: false,
})

const emit = defineEmits<{
  'update:checked': [value: boolean]
}>()

const isChecked = computed({
  get: () => props.checked,
  set: (value) => emit('update:checked', value),
})

const toggle = () => {
  if (!props.disabled) {
    isChecked.value = !isChecked.value
  }
}
</script>

<template>
  <button
    type="button"
    role="switch"
    :aria-checked="isChecked"
    :disabled="disabled"
    @click="toggle"
    class="relative inline-flex h-6 w-11 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
    :class="isChecked ? 'bg-primary' : 'bg-input'"
  >
    <span
      class="pointer-events-none inline-block h-5 w-5 transform rounded-full bg-background shadow ring-0 transition duration-200 ease-in-out"
      :class="isChecked ? 'translate-x-5' : 'translate-x-0'"
    />
  </button>
</template>
