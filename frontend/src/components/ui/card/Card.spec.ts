import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import Card from './Card.vue'

describe('Card', () => {
  it('renders with default props', () => {
    const wrapper = mount(Card, {
      slots: {
        default: '<p>Card content</p>',
      },
    })

    expect(wrapper.text()).toBe('Card content')
    expect(wrapper.find('[data-slot="card"]').exists()).toBe(true)
  })

  it('applies custom class', () => {
    const wrapper = mount(Card, {
      props: {
        class: 'custom-class',
      },
      slots: {
        default: 'Content',
      },
    })

    expect(wrapper.find('[data-slot="card"]').classes()).toContain('custom-class')
  })

  it('renders multiple children', () => {
    const wrapper = mount(Card, {
      slots: {
        default: '<p>First</p><p>Second</p>',
      },
    })

    expect(wrapper.findAll('p')).toHaveLength(2)
  })

  it('has correct base classes', () => {
    const wrapper = mount(Card, {
      slots: {
        default: 'Content',
      },
    })

    const card = wrapper.find('[data-slot="card"]')
    expect(card.classes()).toContain('bg-card')
    expect(card.classes()).toContain('rounded-xl')
    expect(card.classes()).toContain('border')
  })
})
