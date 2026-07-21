import { describe, expect, it } from 'vitest'
import { computed, ref } from 'vue'

import { unwrapRefPayload } from '../refPayload'

describe('unwrapRefPayload', () => {
  it('unwraps refs, getters, arrays, and nested object values', () => {
    const payload = {
      title: ref('Morning route'),
      location: () => ({
        latitude: ref(50.45),
        longitude: computed(() => 30.52),
      }),
      tags: [ref('public'), () => 'featured'],
    }

    expect(unwrapRefPayload(payload)).toEqual({
      title: 'Morning route',
      location: {
        latitude: 50.45,
        longitude: 30.52,
      },
      tags: ['public', 'featured'],
    })
  })

  it('preserves binary payload objects', () => {
    const blob = new Blob(['avatar'], { type: 'text/plain' })
    const formData = new FormData()
    formData.append('avatar', blob)

    expect(unwrapRefPayload(ref(blob))).toBe(blob)
    expect(unwrapRefPayload({ formData }).formData).toBe(formData)
  })
})
