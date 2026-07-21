import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createMemoryHistory, createRouter } from 'vue-router'
import { VueQueryPlugin, QueryClient } from '@tanstack/vue-query'
import SignupPage from '../SignupPage.vue'
import i18n from '@/lib/i18n'

// Mock the auth composables
vi.mock('@/features/auth', () => ({
  useRegister: () => ({
    mutate: vi.fn(),
    isPending: { value: false },
    error: { value: null },
  }),
  getAuthErrorMessage: () => null,
  validateSignupForm: () => ({
    success: true,
    errors: {},
  }),
}))

// Mock PasswordInput component
vi.mock('../components/PasswordInput.vue', () => ({
  default: {
    name: 'PasswordInput',
    template: '<input type="password" />',
  },
}))

describe('SignupPage', () => {
  it('renders signup form', () => {
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

    const wrapper = mount(SignupPage, {
      global: {
        plugins: [router, [VueQueryPlugin, { queryClient }], i18n],
        stubs: {
          RouterLink: true,
        },
      },
    })

    expect(wrapper.text()).toContain('Sign Up')
    expect(wrapper.text()).toContain('Email')
  })

  it('renders all form fields', () => {
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

    const wrapper = mount(SignupPage, {
      global: {
        plugins: [router, [VueQueryPlugin, { queryClient }], i18n],
        stubs: {
          RouterLink: true,
        },
      },
    })

    expect(wrapper.find('#firstName').exists()).toBe(true)
    expect(wrapper.find('#lastName').exists()).toBe(true)
    expect(wrapper.find('#username').exists()).toBe(true)
    expect(wrapper.find('#email').exists()).toBe(true)
    expect(wrapper.find('#password').exists()).toBe(true)
    expect(wrapper.find('#confirmPassword').exists()).toBe(true)
  })

  it('renders sign in link', () => {
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

    const wrapper = mount(SignupPage, {
      global: {
        plugins: [router, [VueQueryPlugin, { queryClient }], i18n],
        stubs: {
          RouterLink: {
            template: '<a><slot /></a>',
          },
        },
      },
    })

    expect(wrapper.text()).toContain('Login?')
    expect(wrapper.text()).toContain('Login')
  })

  it('has submit button', () => {
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

    const wrapper = mount(SignupPage, {
      global: {
        plugins: [router, [VueQueryPlugin, { queryClient }], i18n],
        stubs: {
          RouterLink: true,
        },
      },
    })

    const submitButton = wrapper.find('button[type="submit"]')
    expect(submitButton.exists()).toBe(true)
    expect(submitButton.text()).toContain('Sign Up')
  })

  it('shows success message when registered', async () => {
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

    const wrapper = mount(SignupPage, {
      global: {
        plugins: [router, [VueQueryPlugin, { queryClient }], i18n],
        stubs: {
          RouterLink: true,
        },
      },
    })

    await wrapper.setData({ isRegistered: true, email: 'test@example.com' })

    expect(wrapper.text()).toContain('If an unverified account exists, a verification email has been sent.')
    expect(wrapper.text()).toContain('test@example.com')
  })

  it('has correct autocomplete attributes', () => {
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

    const wrapper = mount(SignupPage, {
      global: {
        plugins: [router, [VueQueryPlugin, { queryClient }], i18n],
        stubs: {
          RouterLink: true,
        },
      },
    })

    expect(wrapper.find('#firstName').attributes('autocomplete')).toBe('given-name')
    expect(wrapper.find('#lastName').attributes('autocomplete')).toBe('family-name')
    expect(wrapper.find('#username').attributes('autocomplete')).toBe('username')
    expect(wrapper.find('#email').attributes('autocomplete')).toBe('email')
  })
})
