import { createI18n } from 'vue-i18n'
import en from './locales/en.json'
import uk from './locales/uk.json'

const SUPPORTED_LANGUAGES = ['en', 'uk'] as const
type SupportedLanguage = (typeof SUPPORTED_LANGUAGES)[number]

function getInitialLanguage(): SupportedLanguage {
  // Check localStorage first
  const saved = localStorage.getItem('app-language') as SupportedLanguage | null
  if (saved && SUPPORTED_LANGUAGES.includes(saved)) {
    return saved
  }

  // Check browser language
  const browserLang = navigator.language.split('-')[0] as SupportedLanguage
  if (SUPPORTED_LANGUAGES.includes(browserLang)) {
    return browserLang
  }

  // Fallback to English
  return 'en'
}

const i18n = createI18n({
  legacy: false,
  locale: getInitialLanguage(),
  fallbackLocale: 'en',
  messages: {
    en,
    uk,
  },
})

export function setLanguage(lang: SupportedLanguage) {
  i18n.global.locale.value = lang
  localStorage.setItem('app-language', lang)
  // Reload page to update all translations and API headers
  window.location.reload()
}

export function getCurrentLanguage(): SupportedLanguage {
  return i18n.global.locale.value as SupportedLanguage
}

export { SUPPORTED_LANGUAGES }
export default i18n
