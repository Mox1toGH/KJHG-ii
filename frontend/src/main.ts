import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { VueQueryPlugin } from '@tanstack/vue-query'
import App from './App.vue'
import router from './router'
import i18n from './lib/i18n'
import './style.css'

const getInitialTheme = () => {
  const savedTheme = localStorage.getItem('theme')
  if (savedTheme === 'light' || savedTheme === 'dark') {
    return savedTheme
  }
  return 'dark'
}

const applyTheme = (theme: string) => {
  if (theme === 'dark') {
    document.documentElement.classList.add('dark')
  } else {
    document.documentElement.classList.remove('dark')
  }
  localStorage.setItem('theme', theme)
}

const initialTheme = getInitialTheme()
applyTheme(initialTheme)

declare global {
  interface Window {
    setTheme: (theme: string) => void
  }
}

window.setTheme = (theme: string) => {
  applyTheme(theme)
}

const app = createApp(App)

app.use(router)
app.use(VueQueryPlugin)
app.use(createPinia())
app.use(i18n)

app.mount('#app')
