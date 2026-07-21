import { createI18n } from 'vue-i18n'
import en from './lib/locales/en.json'
import uk from './lib/locales/uk.json'

declare global {
  var __VUE_I18N__: any
}

class ResizeObserverStub {
  observe() {}
  unobserve() {}
  disconnect() {}
}

if (!('ResizeObserver' in globalThis)) {
  globalThis.ResizeObserver = ResizeObserverStub as unknown as typeof ResizeObserver
}

// Create i18n instance for tests
const i18n = createI18n({
  legacy: false,
  locale: 'en',
  fallbackLocale: 'en',
  messages: {
    en,
    uk,
  },
})

// Make i18n available globally for tests
globalThis.__VUE_I18N__ = i18n
