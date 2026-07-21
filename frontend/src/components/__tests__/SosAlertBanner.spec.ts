import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createMemoryHistory, createRouter } from 'vue-router'
import { VueQueryPlugin, QueryClient } from '@tanstack/vue-query'
import { ref } from 'vue'
import i18n from '@/lib/i18n'

// Mock the composables
vi.mock('@/features/auth', () => ({
  useCurrentUser: () => ({
    data: ref({ id: '123', username: 'testuser' }),
  }),
}))

vi.mock('@/features/activities', () => ({
  useActivityTracking: () => ({
    participants: ref({}),
  }),
  currentActivityId: ref('activity-1'),
  sosActive: ref(false),
  sosActivityId: ref(null),
  requestSosParticipantFocus: vi.fn(),
}))

import SosAlertBanner from '../SosAlertBanner.vue'

describe('SosAlertBanner', () => {
  it('does not render when no SOS is active', () => {
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

    const wrapper = mount(SosAlertBanner, {
      global: {
        plugins: [router, [VueQueryPlugin, { queryClient }], i18n],
      },
    })

    expect(wrapper.find('button').exists()).toBe(false)
  })
})
