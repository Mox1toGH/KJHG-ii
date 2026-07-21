import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createMemoryHistory, createRouter } from 'vue-router'
import { VueQueryPlugin, QueryClient } from '@tanstack/vue-query'
import { createPinia } from 'pinia'
import CheckpointQrManager from '../CheckpointQrManager.vue'

// Use vi.hoisted to create refs before mock hoisting
const { mockCodes, mockIsLoading, mockError, mockIsMutating } = vi.hoisted(() => ({
  mockCodes: { value: [] as unknown[] },
  mockIsLoading: { value: false },
  mockError: { value: null as unknown },
  mockIsMutating: { value: false },
}))

// Mock the QR store
vi.mock('../qr/qr.store', () => ({
  useCheckpointQrStore: () => ({
    codes: mockCodes,
    error: mockError,
    isLoading: mockIsLoading,
    isMutating: mockIsMutating,
    load: vi.fn(),
    clear: vi.fn(),
    create: vi.fn(),
    remove: vi.fn(),
  }),
}))

// Mock the QR API
vi.mock('../qr/qr.api', () => ({
  checkpointQrApi: {
    downloadImage: vi.fn(),
    downloadPdf: vi.fn(),
  },
}))

// Mock the QR scanner component
vi.mock('../CheckpointQrScanner.vue', () => ({
  default: {
    name: 'CheckpointQrScanner',
    template: '<div>QR Scanner</div>',
  },
}))

describe('CheckpointQrManager', () => {
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

    return mount(CheckpointQrManager, {
      props: {
        checkpointId: 'checkpoint-1',
        checkpointName: 'Test Checkpoint',
        canManage: true,
        location: {
          latitude: 50.45,
          longitude: 30.52,
          accuracy: 0,
        },
        ...props,
      },
      global: {
        plugins: [router, [VueQueryPlugin, { queryClient }], pinia],
      },
    })
  }

  it('renders QR codes section', () => {
    const wrapper = createWrapper()

    expect(wrapper.text()).toContain('QR Codes')
    expect(wrapper.text()).toContain('Find and scan the hidden codes at this checkpoint')
  })

  it('renders scan QR code button', () => {
    const wrapper = createWrapper()

    expect(wrapper.text()).toContain('Scan QR code')
  })

  it('renders management buttons when canManage is true', () => {
    const wrapper = createWrapper()

    expect(wrapper.text()).toContain('Create QR Code')
    expect(wrapper.text()).toContain('Download PDF')
  })

  it('does not render management buttons when canManage is false', () => {
    const wrapper = createWrapper({ canManage: false })

    expect(wrapper.text()).not.toContain('Create QR Code')
    expect(wrapper.text()).not.toContain('Download PDF')
  })

  it('renders QR codes section content', () => {
    const wrapper = createWrapper()

    expect(wrapper.text()).toContain('QR Codes')
    expect(wrapper.text()).toContain('Find and scan the hidden codes at this checkpoint')
  })
})
