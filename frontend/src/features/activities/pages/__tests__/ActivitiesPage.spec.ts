import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createMemoryHistory, createRouter } from 'vue-router'
import { VueQueryPlugin, QueryClient } from '@tanstack/vue-query'
import ActivitiesPage from '../ActivitiesPage.vue'
import i18n from '@/lib/i18n'

// Mock the auth composables
vi.mock('@/features/auth', () => ({
  useCurrentUser: () => ({
    data: { value: { id: '123', username: 'testuser' } },
    error: { value: null },
  }),
}))

// Mock the activities composables
vi.mock('@/features/activities', () => ({
  useActivities: () => ({
    data: { value: [] },
    isPending: { value: false },
    isFetching: { value: false },
    error: { value: null },
    refetch: vi.fn(),
  }),
  useCreateActivity: () => ({
    mutate: vi.fn(),
    isPending: { value: false },
    error: { value: null },
  }),
  useDeleteActivity: () => ({
    mutate: vi.fn(),
    isPending: { value: false },
  }),
  useJoinActivity: () => ({
    mutate: vi.fn(),
    isPending: { value: false },
    error: { value: null },
  }),
  useLeaveActivity: () => ({
    mutate: vi.fn(),
    isPending: { value: false },
  }),
  useJoinRequests: () => ({
    data: { value: [] },
    isPending: { value: false },
    isFetching: { value: false },
    refetch: vi.fn(),
  }),
  useApproveJoinRequest: () => ({
    mutate: vi.fn(),
    isPending: { value: false },
  }),
  useRejectJoinRequest: () => ({
    mutate: vi.fn(),
    isPending: { value: false },
  }),
}))

describe('ActivitiesPage', () => {
  it('renders page header', () => {
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

    const wrapper = mount(ActivitiesPage, {
      global: {
        plugins: [router, [VueQueryPlugin, { queryClient }], i18n],
        stubs: {
          RouterLink: true,
        },
      },
    })

    expect(wrapper.text()).toContain('My Activities')
    expect(wrapper.text()).toContain('Create Activity')
  })

  it('renders create activity card', () => {
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

    const wrapper = mount(ActivitiesPage, {
      global: {
        plugins: [router, [VueQueryPlugin, { queryClient }], i18n],
        stubs: {
          RouterLink: true,
        },
      },
    })

    expect(wrapper.text()).toContain('Create room')
    expect(wrapper.text()).toContain('Activity Title')
    expect(wrapper.find('#activity-title').exists()).toBe(true)
  })

  it('renders join activity card', () => {
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

    const wrapper = mount(ActivitiesPage, {
      global: {
        plugins: [router, [VueQueryPlugin, { queryClient }], i18n],
        stubs: {
          RouterLink: true,
        },
      },
    })

    expect(wrapper.text()).toContain('Join')
    expect(wrapper.text()).toContain('Room ID')
    expect(wrapper.find('#room-id').exists()).toBe(true)
  })

  it('renders refresh button', () => {
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

    const wrapper = mount(ActivitiesPage, {
      global: {
        plugins: [router, [VueQueryPlugin, { queryClient }], i18n],
        stubs: {
          RouterLink: true,
        },
      },
    })

    const refreshButton = wrapper.find('button')
    expect(refreshButton.exists()).toBe(true)
  })

  it('renders empty state when no activities', () => {
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

    const wrapper = mount(ActivitiesPage, {
      global: {
        plugins: [router, [VueQueryPlugin, { queryClient }], i18n],
        stubs: {
          RouterLink: true,
        },
      },
    })

    expect(wrapper.text()).toContain('No rooms yet')
    expect(wrapper.text()).toContain('Create the first one or join by ID')
  })
})
