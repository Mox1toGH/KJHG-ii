import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createMemoryHistory, createRouter } from 'vue-router'
import { VueQueryPlugin, QueryClient } from '@tanstack/vue-query'
import { createPinia } from 'pinia'
import { ref } from 'vue'
import CheckpointQrScanner from '../CheckpointQrScanner.vue'

// Mock the QR store
vi.mock('../qr/qr.store', () => ({
  useCheckpointQrStore: () => ({
    scan: vi.fn(),
  }),
}))

// Mock the QR scanner composable with a mutable mock
const mockScanner = {
  video: { value: null },
  isActive: { value: false },
  isStarting: { value: false },
  error: null,
  start: vi.fn(),
  stop: vi.fn(),
}

vi.mock('../composables/useQrScanner', () => ({
  useQrScanner: () => mockScanner,
}))

describe('CheckpointQrScanner', () => {
  const createWrapper = (props = {}) => {
    const router = createRouter({
      history: createMemoryHistory(),
      routes: [],
    })

    const queryClient = new QueryClient({
      defaultOptions: {
        queries: {
          retry: false,
        },
      },
    })

    const pinia = createPinia()

    return mount(CheckpointQrScanner, {
      props: {
        location: { latitude: 50.45, longitude: 30.52, accuracy: 10 },
        ...props,
      },
      global: {
        plugins: [router, [VueQueryPlugin, { queryClient }], pinia],
      },
    })
  }

  it('renders video element', () => {
    const wrapper = createWrapper()

    expect(wrapper.find('video').exists()).toBe(true)
  })

  it('renders open scanner button when inactive', () => {
    const wrapper = createWrapper()

    expect(wrapper.text()).toContain('Open scanner')
  })

  it('renders instruction text when scanner is inactive', () => {
    const wrapper = createWrapper()

    expect(wrapper.text()).toContain('Open the camera and point it at a QR code')
  })
})
