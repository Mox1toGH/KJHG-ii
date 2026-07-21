import { describe, expect, it } from 'vitest'

import { getAuthErrorMessage } from '../core/auth.errors'

describe('getAuthErrorMessage', () => {
  it('formats axios field errors', () => {
    const error = {
      isAxiosError: true,
      response: {
        data: {
          email: ['Enter a valid email.'],
          first_name: 'This field is required.',
        },
      },
      message: 'Request failed',
    } as unknown as Error

    expect(getAuthErrorMessage(error)).toBe(
      'email: Enter a valid email. first name: This field is required.',
    )
  })

  it('uses a friendly label for non-field axios errors', () => {
    const error = {
      isAxiosError: true,
      response: { data: { non_field_errors: ['Invalid credentials.'] } },
      message: 'Request failed',
    } as unknown as Error

    expect(getAuthErrorMessage(error)).toBe('Error: Invalid credentials.')
  })

  it('falls back to the plain error message', () => {
    expect(getAuthErrorMessage(new Error('Something went wrong.'))).toBe('Something went wrong.')
  })
})
