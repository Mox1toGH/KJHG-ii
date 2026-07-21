<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Moon, Sun } from '@lucide/vue'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()
const isDark = ref(false)

function toggleTheme() {
  isDark.value = !isDark.value
  if (isDark.value) {
    document.documentElement.classList.add('dark')
    localStorage.setItem('theme', 'dark')
  } else {
    document.documentElement.classList.remove('dark')
    localStorage.setItem('theme', 'light')
  }
}

onMounted(() => {
  const savedTheme = localStorage.getItem('theme')
  if (savedTheme === 'dark') {
    isDark.value = true
    document.documentElement.classList.add('dark')
  } else if (savedTheme === 'light') {
    isDark.value = false
    document.documentElement.classList.remove('dark')
  } else {
    // Check system preference
    if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
      isDark.value = true
      document.documentElement.classList.add('dark')
    }
  }
})
</script>

<template>
  <button
    type="button"
    class="flex items-center gap-2 px-3 py-2 rounded-lg hover:bg-accent transition-colors"
    :aria-label="t('common.toggleTheme')"
    @click="toggleTheme"
  >
    <Sun v-if="isDark" class="h-4 w-4" />
    <Moon v-else class="h-4 w-4" />
    <span class="text-sm font-medium">{{ isDark ? t('common.dark') : t('common.light') }}</span>
  </button>
</template>
