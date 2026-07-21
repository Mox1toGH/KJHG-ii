import { describe, expect, it } from 'vitest'

import { notificationKeys } from '../keys'

describe('notificationKeys', () => {
  it('builds stable keys for notification queries', () => {
    expect(notificationKeys.all).toEqual(['notifications'])
    expect(notificationKeys.list()).toEqual(['notifications', 'list'])
    expect(notificationKeys.preferences()).toEqual(['notifications', 'preferences'])
  })
})
