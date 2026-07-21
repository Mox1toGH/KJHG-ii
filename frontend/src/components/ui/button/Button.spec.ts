import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import Button from './Button.vue'

describe('Button', () => {
  it('renders with default props', () => {
    const wrapper = mount(Button, {
      slots: {
        default: 'Click me',
      },
    })

    expect(wrapper.text()).toBe('Click me')
    expect(wrapper.find('button').exists()).toBe(true)
  })

  it('renders with custom variant', () => {
    const wrapper = mount(Button, {
      props: {
        variant: 'destructive',
      },
      slots: {
        default: 'Delete',
      },
    })

    expect(wrapper.find('button').attributes('data-variant')).toBe('destructive')
  })

  it('renders with custom size', () => {
    const wrapper = mount(Button, {
      props: {
        size: 'lg',
      },
      slots: {
        default: 'Large Button',
      },
    })

    expect(wrapper.find('button').attributes('data-size')).toBe('lg')
  })

  it('renders as a different element when as prop is provided', () => {
    const wrapper = mount(Button, {
      props: {
        as: 'a',
      },
      slots: {
        default: 'Link',
      },
    })

    expect(wrapper.find('a').exists()).toBe(true)
  })

  it('applies custom class', () => {
    const wrapper = mount(Button, {
      props: {
        class: 'custom-class',
      },
      slots: {
        default: 'Button',
      },
    })

    expect(wrapper.find('button').classes()).toContain('custom-class')
  })

  it('emits click event', async () => {
    const wrapper = mount(Button, {
      slots: {
        default: 'Click me',
      },
    })

    await wrapper.find('button').trigger('click')
    expect(wrapper.emitted('click')).toBeTruthy()
  })

  it('is disabled when disabled attribute is set', () => {
    const wrapper = mount(Button, {
      props: {
        disabled: true,
      },
      slots: {
        default: 'Disabled',
      },
    })

    expect(wrapper.find('button').attributes('disabled')).toBeDefined()
  })
})
