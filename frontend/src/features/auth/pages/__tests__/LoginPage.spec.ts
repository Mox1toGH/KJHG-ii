import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createMemoryHistory, createRouter } from 'vue-router'
import { VueQueryPlugin, QueryClient } from '@tanstack/vue-query'
import LoginPage from '../LoginPage.vue'
import i18n from '@/lib/i18n'

// Mock the auth composables
vi.mock('@/features/auth', () => ({
  useLogin: () => ({
    mutate: vi.fn(),
    isPending: { value: false },
    error: { value: null },
  }),
  useGoogleLogin: () => ({
    mutate: vi.fn(),
    isPending: { value: false },
    error: { value: null },
  }),
  getAuthErrorMessage: () => null,
}))

// Mock Google auth
vi.mock('@/lib/googleAuth', () => ({
  renderGoogleButton: vi.fn(),
}))

// Mock PasswordInput component
vi.mock('../components/PasswordInput.vue', () => ({
  default: {
    name: 'PasswordInput',
    template: '<input type="password" />',
  },
}))

describe('LoginPage', () => {
  it('renders login form', () => {
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

    const wrapper = mount(LoginPage, {
      global: {
        plugins: [router, [VueQueryPlugin, { queryClient }], i18n],
        stubs: {
          RouterLink: true,
        },
      },
    })

    expect(wrapper.text()).toContain('Login')
    expect(wrapper.text()).toContain('Email or Username')
    expect(wrapper.text()).toContain('Password')
  })

  it('renders sign up link', () => {
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

    const wrapper = mount(LoginPage, {
      global: {
        plugins: [router, [VueQueryPlugin, { queryClient }], i18n],
        stubs: {
          RouterLink: {
            template: '<a><slot /></a>',
          },
        },
      },
    })

    expect(wrapper.text()).toContain('Sign Up?')
    expect(wrapper.text()).toContain('Sign Up')
  })

  it('renders Google auth section', () => {
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

    const wrapper = mount(LoginPage, {
      global: {
        plugins: [router, [VueQueryPlugin, { queryClient }], i18n],
        stubs: {
          RouterLink: true,
        },
      },
    })

    expect(wrapper.text()).toContain('or')
  })

  it('has identifier input field', () => {
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

    const wrapper = mount(LoginPage, {
      global: {
        plugins: [router, [VueQueryPlugin, { queryClient }], i18n],
        stubs: {
          RouterLink: true,
        },
      },
    })

    const identifierInput = wrapper.find('#identifier')
    expect(identifierInput.exists()).toBe(true)
    expect(identifierInput.attributes('type')).toBe('text')
    expect(identifierInput.attributes('autocomplete')).toBe('username')
  })

  it('has password input field', () => {
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

    const wrapper = mount(LoginPage, {
      global: {
        plugins: [router, [VueQueryPlugin, { queryClient }], i18n],
        stubs: {
          RouterLink: true,
        },
      },
    })

    const passwordInput = wrapper.find('#password')
    expect(passwordInput.exists()).toBe(true)
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

    const wrapper = mount(LoginPage, {
      global: {
        plugins: [router, [VueQueryPlugin, { queryClient }], i18n],
        stubs: {
          RouterLink: true,
        },
      },
    })

    const submitButton = wrapper.find('button[type="submit"]')
    expect(submitButton.exists()).toBe(true)
    expect(submitButton.text()).toContain('Login')
  })
})
