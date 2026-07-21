<script setup lang="ts">
import { ref } from 'vue'
import { Globe, ChevronDown } from '@lucide/vue'
import { setLanguage, getCurrentLanguage, SUPPORTED_LANGUAGES } from '@/lib/i18n'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()
const currentLanguage = getCurrentLanguage()
const isOpen = ref(false)

const languages = [
  { code: 'uk', name: 'Українська', flag: '🇺🇦' },
  { code: 'en', name: 'English', flag: '🇬🇧' },
]

function changeLanguage(lang: string) {
  setLanguage(lang as typeof SUPPORTED_LANGUAGES[number])
  isOpen.value = false
}

function toggleDropdown() {
  isOpen.value = !isOpen.value
}
</script>

<template>
  <div class="relative">
    <button
      type="button"
      class="flex items-center gap-2 px-3 py-2 rounded-lg hover:bg-accent transition-colors"
      :aria-label="t('language.selectLanguage')"
      @click="toggleDropdown"
    >
      <Globe class="h-4 w-4" />
      <span class="text-sm font-medium">{{ languages.find(l => l.code === currentLanguage)?.flag }}</span>
      <ChevronDown class="h-4 w-4" />
    </button>

    <div
      v-if="isOpen"
      class="absolute right-0 top-full mt-1 bg-background border border-border rounded-lg shadow-lg z-50 min-w-[140px]"
    >
      <div class="py-1">
        <button
          v-for="lang in languages"
          :key="lang.code"
          type="button"
          class="w-full flex items-center gap-2 px-3 py-2 text-sm hover:bg-accent transition-colors text-left"
          :class="{ 'bg-accent': lang.code === currentLanguage }"
          @click="changeLanguage(lang.code)"
        >
          <span>{{ lang.flag }}</span>
          <span>{{ lang.name }}</span>
        </button>
      </div>
    </div>
  </div>
</template>
