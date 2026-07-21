import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'
import tailwindcss from '@tailwindcss/vite'

// https://vite.dev/config/
export default defineConfig({
  // Keep the single root .env used by both local and Docker workflows.
  envDir: '..',
  plugins: [vue(), vueDevTools(), tailwindcss()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
  server: {
    host: '0.0.0.0',
    port: 5173,
  },
  build: {
    chunkSizeWarningLimit: 1100,
    rollupOptions: {
      output: {
        manualChunks(id) {
          if (!id.includes('node_modules')) return
          if (id.includes('maplibre-gl')) return 'vendor-maplibre'
          if (id.includes('@mapbox') || id.includes('@maplibre')) return 'vendor-map-data'
          if (id.includes('@zxing')) return 'vendor-zxing'
          if (id.includes('h3-js')) return 'vendor-h3'
          if (id.includes('reka-ui')) return 'vendor-reka'
          if (id.includes('@tanstack')) return 'vendor-query'
          if (id.includes('@lucide')) return 'vendor-icons'
          if (id.includes('vue')) return 'vendor-vue'
        },
      },
    },
  },
})
