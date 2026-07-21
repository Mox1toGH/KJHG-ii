import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createMemoryHistory, createRouter } from 'vue-router'
import { VueQueryPlugin, QueryClient } from '@tanstack/vue-query'
import BottomNav from '../BottomNav.vue'
import i18n from '@/lib/i18n'

describe('BottomNav', () => {
  let router: ReturnType<typeof createRouter>
  let queryClient: QueryClient

  beforeEach(() => {
    router = createRouter({
      history: createMemoryHistory(),
      routes: [
        { path: '/', component: { template: '<div>home</div>' } },
        { path: '/activities', component: { template: '<div>activities</div>' } },
        { path: '/profile', component: { template: '<div>profile</div>' } },
      ],
    })

    queryClient = new QueryClient({
      defaultOptions: {
        queries: {
          retry: false,
        },
      },
    })

    // Mock localStorage
    const localStorageMock = {
      getItem: vi.fn(),
      setItem: vi.fn(),
      removeItem: vi.fn(),
      clear: vi.fn(),
    }
    global.localStorage = localStorageMock as any
  })

  it('renders navigation items', async () => {
    await router.push('/')
    await router.isReady()

    const wrapper = mount(BottomNav, {
      global: {
        plugins: [router, [VueQueryPlugin, { queryClient }], i18n],
      },
    })

    expect(wrapper.text()).toContain('Home')
    expect(wrapper.text()).toContain('Activities')
    expect(wrapper.text()).toContain('Profile')
  })

  it('highlights active route', async () => {
    await router.push('/')
    await router.isReady()

    const wrapper = mount(BottomNav, {
      global: {
        plugins: [router, [VueQueryPlugin, { queryClient }], i18n],
      },
    })

    const homeLink = wrapper.find('a[href="/"]')
    expect(homeLink.classes()).toContain('bg-primary')
  })

  it('does not highlight non-active routes', async () => {
    await router.push('/activities')
    await router.isReady()

    const wrapper = mount(BottomNav, {
      global: {
        plugins: [router, [VueQueryPlugin, { queryClient }], i18n],
      },
    })

    const homeLink = wrapper.find('a[href="/"]')
    expect(homeLink.classes()).not.toContain('bg-primary')
  })

  it('renders SOS button', async () => {
    await router.push('/')
    await router.isReady()

    const wrapper = mount(BottomNav, {
      global: {
        plugins: [router, [VueQueryPlugin, { queryClient }], i18n],
      },
    })

    const sosButton = wrapper.find('button[aria-label*="SOS"]')
    expect(sosButton.exists()).toBe(true)
    expect(sosButton.text()).toContain('SOS')
  })

  it('renders hide navigation button', async () => {
    await router.push('/')
    await router.isReady()

    const wrapper = mount(BottomNav, {
      global: {
        plugins: [router, [VueQueryPlugin, { queryClient }], i18n],
      },
    })

    const hideButton = wrapper.find('button[aria-label="Hide bottom navigation"]')
    expect(hideButton.exists()).toBe(true)
  })

  it('toggles navigation state when hide button is clicked', async () => {
    await router.push('/')
    await router.isReady()

    const wrapper = mount(BottomNav, {
      global: {
        plugins: [router, [VueQueryPlugin, { queryClient }], i18n],
      },
    })

    const hideButton = wrapper.find('button[aria-label="Hide bottom navigation"]')
    await hideButton.trigger('click')

    // After hiding, should show open button
    await wrapper.vm.$nextTick()
    const openButton = wrapper.find('button[aria-label="Open bottom navigation"]')
    expect(openButton.exists()).toBe(true)
  })

  it('saves navigation state to localStorage', async () => {
    await router.push('/')
    await router.isReady()

    const wrapper = mount(BottomNav, {
      global: {
        plugins: [router, [VueQueryPlugin, { queryClient }], i18n],
      },
    })

    const hideButton = wrapper.find('button[aria-label="Hide bottom navigation"]')
    await hideButton.trigger('click')

    expect(global.localStorage.setItem).toHaveBeenCalledWith('mdvl-bottom-nav-state', 'hidden')
  })

  it('loads navigation state from localStorage', async () => {
    vi.mocked(global.localStorage.getItem).mockReturnValue('hidden')

    await router.push('/')
    await router.isReady()

    const wrapper = mount(BottomNav, {
      global: {
        plugins: [router, [VueQueryPlugin, { queryClient }], i18n],
      },
    })

    // Should start in hidden state
    await wrapper.vm.$nextTick()
    const openButton = wrapper.find('button[aria-label="Open bottom navigation"]')
    expect(openButton.exists()).toBe(true)
  })
})
