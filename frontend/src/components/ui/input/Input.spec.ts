import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import Input from './Input.vue'

describe('Input', () => {
  it('renders with default props', () => {
    const wrapper = mount(Input)

    expect(wrapper.find('input').exists()).toBe(true)
    expect(wrapper.find('input').attributes('data-slot')).toBe('input')
  })

  it('renders with default value', () => {
    const wrapper = mount(Input, {
      props: {
        defaultValue: 'default value',
      },
    })

    expect(wrapper.find('input').element.value).toBe('default value')
  })

  it('renders with v-model', async () => {
    const wrapper = mount(Input, {
      props: {
        modelValue: 'initial',
      },
    })

    expect(wrapper.find('input').element.value).toBe('initial')

    await wrapper.find('input').setValue('updated')
    expect(wrapper.emitted('update:modelValue')).toBeTruthy()
    expect(wrapper.emitted('update:modelValue')?.[0]).toEqual(['updated'])
  })

  it('applies custom class', () => {
    const wrapper = mount(Input, {
      props: {
        class: 'custom-class',
      },
    })

    expect(wrapper.find('input').classes()).toContain('custom-class')
  })

  it('has correct base classes', () => {
    const wrapper = mount(Input)

    const input = wrapper.find('input')
    expect(input.classes()).toContain('h-9')
    expect(input.classes()).toContain('w-full')
    expect(input.classes()).toContain('rounded-md')
    expect(input.classes()).toContain('border')
  })

  it('can be disabled', () => {
    const wrapper = mount(Input, {
      props: {
        disabled: true,
      },
    })

    expect(wrapper.find('input').attributes('disabled')).toBeDefined()
  })

  it('supports number values', async () => {
    const wrapper = mount(Input, {
      props: {
        modelValue: 42,
      },
    })

    expect(wrapper.find('input').element.value).toBe('42')

    await wrapper.find('input').setValue('100')
    expect(wrapper.emitted('update:modelValue')?.[0]).toEqual(['100'])
  })
})
